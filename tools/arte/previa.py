"""Gera prévias ampliadas dos personagens para conferir à vista."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import personagens as pg  # noqa: E402

SAIDA = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SAIDA.mkdir(parents=True, exist_ok=True)

quadros = [
    pg.lampiao(),
    pg.lampiao({"pernas": "corre1", "dy": -1}),
    pg.lampiao({"pernas": "corre2"}),
    pg.lampiao({"pernas": "agachado"}),
    pg.lampiao({"pernas": "pulo", "boca": "grito"}),
    pg.lampiao({"mira": "cima"}),
    pg.maria_bonita(),
]
alien = pg.alien()
escala = 6
w = sum(q.w for q in quadros) + alien.w
img = Image.new("RGBA", (w * escala, 52 * escala), (79, 154, 214, 255))
x = 0
for q in quadros + [alien]:
    im = q.imagem().resize((q.w * escala, q.h * escala), Image.NEAREST)
    img.alpha_composite(im, (x * escala, (52 - q.h) * escala))
    x += q.w
img.save(SAIDA / "personagens.png")
print(SAIDA / "personagens.png")
