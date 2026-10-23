import json
import os

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# --- Configuração -----------------------------------------------------------
# A chave NUNCA vai no código: ela vem da variável de ambiente GROQ_API_KEY
# (na Vercel: Settings -> Environment Variables).
# Se a chave existir, usa o LLAMA hospedado na Groq (grátis, funciona na Vercel).
# Senão, tenta o LLAMA local via Ollama (só funciona rodando na sua máquina).
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:Q4_K_M")

IDIOMAS = ["Português", "Inglês", "Espanhol", "Francês", "Italiano",
           "Alemão", "Japonês", "Latim"]
COMPORTAMENTOS = ["Alegre", "Triste", "Piadista", "Irritado", "Formal",
                  "Romântico", "Sarcástico", "Pirata"]


def montar_prompt(idioma: str, comportamento: str) -> str:
    return (
        f"Gere uma frase curta (até 100 palavras) em {idioma} que seja {comportamento}. "
        "Depois traduza essa frase para português do Brasil. "
        'Responda SOMENTE com JSON no formato: '
        '{"frase": "...", "traducao": "..."}'
    )


def chamar_groq(prompt: str) -> dict:
    """LLAMA hospedado na Groq (API compatível com o formato da OpenAI)."""
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 1.0,
        },
        timeout=30,
    )
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def chamar_ollama(prompt: str) -> dict:
    """LLAMA rodando local na sua máquina."""
    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "format": "json",
            "stream": False,
        },
        timeout=120,
    )
    r.raise_for_status()
    return json.loads(r.json()["message"]["content"])


@app.get("/")
def index():
    return render_template(
        "index.html",
        idiomas=IDIOMAS,
        comportamentos=COMPORTAMENTOS,
        provedor=f"Groq ({GROQ_MODEL})" if GROQ_API_KEY else f"Ollama ({OLLAMA_MODEL})",
    )


@app.post("/api/gerar")
def gerar():
    dados = request.get_json(force=True, silent=True) or {}
    idioma = dados.get("idioma", "Inglês")
    comportamento = dados.get("comportamento", "Alegre")
    prompt = montar_prompt(idioma, comportamento)
    try:
        resultado = chamar_groq(prompt) if GROQ_API_KEY else chamar_ollama(prompt)
    except requests.ConnectionError:
        return jsonify(
            erro="Não consegui conectar no LLAMA. Defina a variável GROQ_API_KEY "
                 "ou rode o Ollama na sua máquina."
        ), 502
    except Exception as e:  # noqa: BLE001
        return jsonify(erro=f"Falha ao gerar: {e}"), 500

    return jsonify(
        idioma=idioma,
        comportamento=comportamento,
        prompt=prompt,
        frase=resultado.get("frase", ""),
        traducao=resultado.get("traducao", ""),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
