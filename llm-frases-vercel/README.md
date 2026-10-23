# 🦙 Lhama Falante (Python / Flask + LLAMA + Vercel)

Ao abrir o link, a página mostra um **GIF animado de uma lhama** e, no balão de fala,
um texto **gerado pelo LLAMA** (frase + tradução para português). Você pode escolher
**Idioma** e **Comportamento** e clicar em **Run** para gerar outro texto.

## Arquitetura (jornada dos dados)

```
Navegador ──(1) GET /──────────────► Flask (app.py) devolve index.html + /static/llama.gif
Navegador ──(2) POST /api/gerar ───► Flask monta o prompt
           {"idioma","comportamento"}        │
                                             ▼
                              (3) POST https://api.groq.com/openai/v1/chat/completions
                                  Header: Authorization: Bearer GROQ_API_KEY
                                  Modelo: llama-3.1-8b-instant  (LLAMA hospedado)
                                             │
                                             ▼
                              (4) LLAMA responde JSON: {"frase": "...", "traducao": "..."}
Navegador ◄─(5) JSON ──────────── Flask valida e devolve {idioma, comportamento, prompt, frase, traducao}
   └─ JavaScript escreve frase/tradução no balão sobre o GIF
```

1. **Click / carga da página**: o JavaScript chama `fetch("/api/gerar")` ao abrir o link e a cada clique em *Run*.
2. **API (Flask)**: `app.py` recebe o JSON, monta o prompt e chama o LLAMA.
3. **Chave**: `GROQ_API_KEY` fica só em variável de ambiente (Vercel → Settings → Environment Variables). Nunca no código nem no navegador.
4. **LLAMA**: pedimos `response_format: json_object` para ele responder só JSON.
5. **Volta**: o Flask devolve o JSON; o front usa `textContent` (seguro contra HTML injetado) para trocar o texto do GIF.
6. **Publicação**: GitHub → Vercel (`vercel.json` usa `@vercel/python`; `includeFiles` leva `templates/` e `static/` junto).

## Arquivos

| Arquivo | Função |
|---|---|
| `app.py` | Servidor Flask: rota `/` (página) e `POST /api/gerar` (chama o LLAMA) |
| `templates/index.html` | Página: GIF, balão de fala, selects, botão Run |
| `static/llama.gif` | GIF animado (gerado por `tools/gerar_gif.py` com Pillow) |
| `vercel.json` | Configuração de deploy Python na Vercel |
| `requirements.txt` | `flask`, `requests` |

## Rodar na sua máquina

```bash
pip install -r requirements.txt
python app.py
```
Abra http://localhost:5000

- **LLAMA hospedado (Groq, grátis):** crie a chave em https://console.groq.com/keys
  - PowerShell: `$env:GROQ_API_KEY="sua-chave"`
  - Linux/Mac: `export GROQ_API_KEY="sua-chave"`
- **LLAMA local (sem chave):** instale o [Ollama](https://ollama.com), rode `ollama pull llama3.2:1b` e deixe `ollama serve` aberto.

## Publicar na Vercel

1. Suba a pasta para um repositório no GitHub (o `.env` está no `.gitignore`).
2. Em vercel.com: **Add New → Project**, escolha o repositório e **Import**.
3. Em **Environment Variables**, crie `GROQ_API_KEY` com a sua chave.
4. **Deploy**. (Se mudar a variável depois, faça *Redeploy*.)

Online só funciona com a Groq, pois o Ollama roda apenas na sua máquina.

## Trocar o GIF

Rode `pip install pillow && python tools/gerar_gif.py` para regerar, ou substitua `static/llama.gif` por qualquer GIF 640×360 (o balão fica por cima, no canto superior esquerdo).
