"""Folhas ampliadas para aprovação: Maria Bonita, inimigos, reféns e efeitos."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import inimigos as ini  # noqa: E402
import personagens as pg  # noqa: E402

SAIDA = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SAIDA.mkdir(parents=True, exist_ok=True)
FUNDO = (79, 154, 214, 255)
ESCALA = 4

PASSOS = [[(0, 0), (0, 0)], [(-3, 2), (3, 0)], [(0, 0), (0, 0)], [(3, 0), (-3, 2)]]

linhas = [
    ("Maria Bonita", [pg.maria_bonita({"pernas": k}) for k in ("parado", "corre1", "corre2", "corre3", "pulo", "agachado")]
     + [pg.maria_bonita({"mira": "cima"}), pg.maria_bonita({"boca": "grito"})]),
    ("Soldado xeremita (anda, atira) e soldado da Volante", [pg.alien({"pes": p, "dy": -1 if k % 2 else 0}) for k, p in enumerate(PASSOS)]
     + [pg.alien({"tiro": True, "boca": "grito"})]
     + [ini.volante({"pernas": k}) for k in ("parado", "anda1", "anda2")] + [ini.volante({"tiro": True, "boca": "grito"})]),
    ("Disco abdutor e raio, bode Fubá, refém amarrado e solto", [ini.disco(0), ini.disco(1), ini.feixe(0, h=60),
     ini.bode("parado"), ini.bode("mastiga"), ini.bode("abduzido"),
     ini.refem("amarrado1"), ini.refem("amarrado2"), ini.refem("solto1"), ini.refem("solto2")]),
    ("Explosão animada e mortes: queimado, derretendo", [ini.explosao(k) for k in range(7)]
     + [ini.carbonizar(pg.alien({"boca": "grito"}))] + [ini.derretendo(k) for k in range(3)]),
]

blocos = []
for titulo, quadros in linhas:
    w = sum(q.w for q in quadros) + 4 * (len(quadros) - 1)
    h = max(q.h for q in quadros)
    img = Image.new("RGBA", (w, h), FUNDO)
    x = 0
    for q in quadros:
        img.alpha_composite(q.imagem(), (x, h - q.h))
        x += q.w + 4
    blocos.append((titulo, img.resize((w * ESCALA, h * ESCALA), Image.NEAREST)))

largura = max(b.width for _, b in blocos) + 20
altura = sum(b.height + 34 for _, b in blocos) + 10
folha = Image.new("RGBA", (largura, altura), (35, 35, 58, 255))
d = ImageDraw.Draw(folha)
fonte = ImageFont.load_default(15)
y = 10
for titulo, b in blocos:
    d.text((10, y), titulo, fill=(243, 241, 234, 255), font=fonte)
    folha.alpha_composite(b, (10, y + 18))
    y += b.height + 34
folha.save(SAIDA / "proposta_inimigos.png")
print(SAIDA / "proposta_inimigos.png")

# ---- Cena de exemplo com tudo junto (384x216).
import cenario as cn  # noqa: E402

cena = Image.new("RGBA", (384, 216))


def colar(img, x, y):
    cena.alpha_composite(img, (int(x), int(y)))


def faixa(img, x, y):
    x = x % img.width - img.width
    while x < 384:
        colar(img, x, y)
        x += img.width


colar(cn.ceu().imagem(), 0, 0)
colar(cn.nuvens().imagem(), 0, 6)
faixa(cn.serras().imagem(), 0, 96)
faixa(cn.paredoes().imagem(), -120, 86)
faixa(cn.planicie().imagem(), 0, 168)
faixa(cn.caatinga().imagem(), -150, 122)
chao = cn.chao_tile().imagem()
for x in range(0, 384, chao.width):
    colar(chao, x, 192)
# Disco puxando o Fubá.
raio = ini.feixe(1, h=118).imagem()
raio.putalpha(raio.getchannel("A").point(lambda a: a * 0.55))
colar(raio, 268, 66)
colar(ini.disco(0).imagem(), 257, 50)
colar(ini.bode("abduzido").imagem(), 265, 118)
colar(ini.refem("amarrado1").imagem(), 220, 154)
colar(pg.lampiao({"boca": "grito", "pernas": "corre1"}).imagem(), 30, 142)
colar(pg.maria_bonita({"mira": "cima"}).imagem(), 0, 142)
colar(pg.alien({"tiro": True, "pes": PASSOS[1]}).imagem(), 150, 150)
colar(ini.explosao(3).imagem(), 108, 140)
colar(ini.volante({"tiro": True, "boca": "grito"}).imagem(), 330, 142)
colar(ini.derretendo(1).imagem(), 186, 150)
cena.save(SAIDA / "cena_inimigos_1x.png")
cena.resize((384 * 4, 216 * 4), Image.NEAREST).save(SAIDA / "cena_inimigos.png")
print(SAIDA / "cena_inimigos.png")
