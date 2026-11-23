"""Prepara las ilustraciones a partir de las referencias del usuario.

Entradas: ref1 (Alejandra con café), ref2 (barista señalando).
Salidas (PNG con fondo transparente, escaladas):
  - barista.png       referencia 2 tal cual, sin el fondo crema.
  - ale_happy.png     referencia 1 tal cual (cierre), sin texto/borde ni fondo.
  - ale_pensive.png   referencia 1 recortada (el café queda fuera de cuadro) y con ojos,
                      cejas y boca borrados; los rasgos pensativos se dibujan en vector
                      encima (ver src.html, #aleFace), alineados en coordenadas del original.
Uso: python3 make_characters.py <ref1.png> <ref2.png> <out_dir>
"""
import sys, pathlib
from collections import deque
from PIL import Image, ImageDraw, ImageFilter

ref1, ref2, out = map(pathlib.Path, sys.argv[1:4])
out.mkdir(parents=True, exist_ok=True)
BG = (241, 237, 226)  # #F1EDE2, fondo de ambas referencias


def key_background(im, seeds, tol=7, soft=10):
    """Flood-fill del fondo plano desde semillas del borde; alfa suave en el contorno."""
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    dist = lambda c: max(abs(c[i] - BG[i]) for i in range(3))
    seen = bytearray(w * h)
    q = deque(s for s in seeds if dist(px[s]) <= tol)
    while q:
        x, y = q.popleft()
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        d = dist(px[x, y])
        if d > tol + soft:
            continue
        r, g, b, _ = px[x, y]
        px[x, y] = (r, g, b, 0 if d <= tol else int(255 * (d - tol) / soft))
        if d <= tol:
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                    q.append((nx, ny))
    return im


def defringe(im):
    """Quita el halo crema del borde: erosiona 1px el alfa y descontamina el color de los
    píxeles semitransparentes respecto al fondo original."""
    im = im.convert("RGBA")
    a = im.getchannel("A").filter(ImageFilter.MinFilter(3))
    px = im.load(); w, h = im.size; ap = a.load()
    for y in range(h):
        for x in range(w):
            al = ap[x, y]
            r, g, b, _ = px[x, y]
            if 0 < al < 255:
                f = al / 255
                r, g, b = [max(0, min(255, round((c - (1 - f) * BG[i]) / f))) for i, c in enumerate((r, g, b))]
            px[x, y] = (r, g, b, al)
    return im


def upscale(im, k):
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))


def patch(im, box, color, blur=1.2, ss=8):
    """Cubre un rasgo con color de piel (elipse con borde suave)."""
    x0, y0, x1, y1 = box
    pad = 2
    W, H = (x1 - x0 + 2 * pad) * ss, (y1 - y0 + 2 * pad) * ss
    m = Image.new("L", (W, H), 0)
    r = (H - 2 * pad * ss) // 2
    ImageDraw.Draw(m).rounded_rectangle((pad * ss, pad * ss, W - pad * ss, H - pad * ss), radius=r, fill=255)
    m = m.resize((x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur))
    im.paste(Image.new("RGB", m.size, color), (x0 - pad, y0 - pad), m)


# ── Barista (ref 2): solo se quita el fondo ──
b = Image.open(ref2).convert("RGB")
w, h = b.size
seeds = [(x, 0) for x in range(w)] + [(0, y) for y in range(330)] + [(w - 1, y) for y in range(330)]
b = key_background(b, seeds)
upscale(defringe(b), 2).save(out / "barista.png")

# ── Alejandra feliz (ref 1): cierre ──
a = Image.open(ref1).convert("RGB").crop((0, 0, 384, 482))
ImageDraw.Draw(a).rectangle((0, 0, 75, 72), fill=BG)  # fuera el texto "s por" y el chip
w, h = a.size
seeds = [(x, 0) for x in range(w)] + [(0, y) for y in range(h)] + [(w - 1, y) for y in range(240)]
upscale(defringe(key_background(a, seeds)), 2).save(out / "ale_happy.png")

# ── Alejandra pensativa: sin café (recorte) y sin rasgos ──
p = Image.open(ref1).convert("RGB").crop((104, 0, 384, 482))  # coords origen: x-104
SKIN = (254, 188, 127)  # #FEBC7F muestreado de la mejilla
o = 104
for bx in [(136, 102, 158, 116), (170, 100, 207, 117),      # cejas
           (135, 119, 159, 136), (172, 116, 203, 136),      # ojos cerrados
           (140, 164, 196, 194)]:                            # sonrisa
    patch(p, (bx[0] - o, bx[1], bx[2] - o, bx[3]), SKIN)
w, h = p.size
seeds = [(x, 0) for x in range(w)] + [(0, y) for y in range(h)] + [(w - 1, y) for y in range(240)]
upscale(defringe(key_background(p, seeds)), 3).save(out / "ale_pensive.png")
print("ok")
