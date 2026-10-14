"""Monta uma tela de exemplo (384x216) com cenário e personagens para aprovação."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import cenario as cn  # noqa: E402
import personagens as pg  # noqa: E402

SAIDA = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SAIDA.mkdir(parents=True, exist_ok=True)
W, H = 384, 216
CHAO = 192

tela = Image.new("RGBA", (W, H))


def colar(img, x, y):
    tela.alpha_composite(img, (int(x), int(y)))


colar(cn.ceu().imagem(), 0, 0)
colar(cn.nuvens().imagem(), 0, 6)
def faixa(img, x, y):
    x = x % img.width - img.width
    while x < W:
        colar(img, x, y)
        x += img.width


faixa(cn.serras().imagem(), 0, 96)
faixa(cn.paredoes().imagem(), -40, 86)
faixa(cn.planicie().imagem(), 0, 168)
faixa(cn.caatinga().imagem(), -60, 122)
chao = cn.chao_tile().imagem()
for x in range(0, W, chao.width):
    colar(chao, x, CHAO)
for k, x in enumerate((10, 70, 150, 230, 330, 365)):
    colar(cn.touceira(k).imagem(), x, CHAO - 8)
colar(cn.caixote().imagem(), 252, CHAO - 18)
laje = cn.laje().imagem()
for k in range(3):
    colar(laje, 290 + k * 32, 150)

lamp = pg.lampiao({"boca": "grito"}).imagem()
colar(lamp, 60, CHAO - 50)
colar(pg.maria_bonita().imagem(), 16, CHAO - 50)
alien = pg.alien().imagem()
colar(alien, 196, CHAO - 42)
colar(pg.alien({"olho": "fechado"}).imagem(), 300, 150 - 42)

tela.save(SAIDA / "mockup_1x.png")
tela.resize((W * 4, H * 4), Image.NEAREST).save(SAIDA / "mockup.png")
print(SAIDA / "mockup.png")
