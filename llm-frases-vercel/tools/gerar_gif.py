"""Gera static/llama.gif (uma lhama animada). Rode: python tools/gerar_gif.py
Requer: pip install pillow  (só para gerar o GIF; o app em si não precisa)."""
import colorsys
import math
import os

from PIL import Image, ImageDraw

W, H, S = 640, 360, 3          # tamanho final e fator de supersampling
FRAMES = 20


def fundo(d, t):
    # gradiente vertical que muda de matiz ao longo da animação
    h0 = (0.62 + 0.12 * math.sin(2 * math.pi * t)) % 1
    for y in range(H * S):
        k = y / (H * S)
        r, g, b = colorsys.hsv_to_rgb((h0 + 0.18 * k) % 1, 0.55, 0.95 - 0.35 * k)
        d.line([(0, y), (W * S, y)], fill=(int(r * 255), int(g * 255), int(b * 255)))
    # estrelinhas piscando
    for i in range(14):
        x = (i * 97 + 40) % W
        y = (i * 53 + 20) % 150 + 150
        r = 3 + 2 * math.sin(2 * math.pi * (t * 2 + i / 14))
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(255, 255, 255))
    # chão
    d.rectangle([0, 300 * S, W * S, H * S], fill=(70, 160, 90))


def elipse(d, cx, cy, rx, ry, cor, borda=None):
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S],
              fill=cor, outline=borda, width=3 * S if borda else 0)


def lhama(d, t):
    lã, sombra, escuro = (250, 244, 230), (225, 214, 190), (60, 45, 40)
    pulo = -10 * abs(math.sin(2 * math.pi * t))          # quica
    balanço = 6 * math.sin(2 * math.pi * t)               # cabeça balança
    ox, oy = 410, 300 + pulo

    # pernas
    for dx in (-70, -35, 35, 70):
        d.rounded_rectangle([(ox + dx - 9) * S, (oy - 60) * S, (ox + dx + 9) * S, (oy + 2 - pulo) * S],
                            radius=6 * S, fill=sombra, outline=escuro, width=2 * S)
    # corpo
    elipse(d, ox, oy - 95, 100, 58, lã, escuro)
    for dx, dy in ((-50, -110), (0, -125), (45, -105), (-20, -80), (30, -75)):
        elipse(d, ox + dx, oy + dy, 22, 18, sombra)       # tufos de lã
    # rabinho
    elipse(d, ox - 100, oy - 110, 14, 12, lã, escuro)
    # pescoço
    nx = ox + 70 + balanço
    d.polygon([((ox + 40) * S, (oy - 120) * S), ((ox + 85) * S, (oy - 125) * S),
               ((nx + 25) * S, (oy - 205) * S), ((nx - 12) * S, (oy - 205) * S)],
              fill=lã, outline=escuro)
    # cabeça
    hx, hy = nx + 12, oy - 220
    elipse(d, hx, hy, 34, 28, lã, escuro)
    elipse(d, hx + 26, hy + 8, 22, 17, sombra, escuro)    # focinho
    elipse(d, hx + 36, hy + 6, 3, 3, escuro)              # narina
    # orelhas (mexem)
    mex = 5 * math.sin(2 * math.pi * t * 2)
    for ex in (-14, 6):
        d.polygon([((hx + ex) * S, (hy - 20) * S), ((hx + ex + 12) * S, (hy - 20) * S),
                   ((hx + ex + 10 + mex) * S, (hy - 52) * S)], fill=lã, outline=escuro)
    # olho (pisca)
    piscando = (t % 0.5) > 0.44
    if piscando:
        d.line([(hx + 4) * S, (hy - 6) * S, (hx + 18) * S, (hy - 6) * S], fill=escuro, width=3 * S)
    else:
        elipse(d, hx + 11, hy - 6, 5, 6, escuro)
        elipse(d, hx + 13, hy - 8, 2, 2, (255, 255, 255))
    # bochecha
    elipse(d, hx + 8, hy + 10, 6, 4, (255, 170, 170))


def main():
    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        img = Image.new("RGB", (W * S, H * S))
        d = ImageDraw.Draw(img)
        fundo(d, t)
        lhama(d, t)
        img = img.resize((W, H), Image.LANCZOS)
        frames.append(img.quantize(colors=96, method=Image.MEDIANCUT, dither=Image.NONE))
    destino = os.path.join(os.path.dirname(__file__), "..", "static", "llama.gif")
    frames[0].save(destino, save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
    print("OK:", os.path.getsize(destino) // 1024, "KB")


if __name__ == "__main__":
    main()
