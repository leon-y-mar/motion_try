"""Empaqueta src.html + assets/ en index.html autocontenido (assets como data URI)."""
import base64, io, re, pathlib
from PIL import Image

root = pathlib.Path(__file__).parent
src = (root / "src.html").read_text()
MAXW = {"banner_halloween.png": 722}


def data_uri(name):
    p = root / "assets" / name
    if p.suffix == ".svg":
        return "data:image/svg+xml;base64," + base64.b64encode(p.read_bytes()).decode()
    im = Image.open(p).convert("RGBA")
    if name in MAXW and im.width > MAXW[name]:
        im = im.resize((MAXW[name], round(im.height * MAXW[name] / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=88, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


cache = {}


def sub(m):
    n = m.group(1)
    if n not in cache:
        cache[n] = data_uri(n)
    return cache[n]


out = re.sub(r"assets/([\w@.-]+\.(?:png|svg))", sub, src)
(root / "index.html").write_text(out)
print("assets:", len(cache), "size KB:", round(len(out) / 1024))
