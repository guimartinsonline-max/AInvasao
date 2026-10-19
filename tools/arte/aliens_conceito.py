"""Conceitos de alienígenas bizarros (para o Guilherme aprovar a direção antes de
virar sprite de jogo). Inspiração no clima do Metal Slug (carne, olhos demais,
corpo errado), mas desenhos nossos.

- cerebrao: cabeça de cérebro exposto e pulsando, cara pequena com três olhos e
  mandíbulas, corpo de lesma verde babando, bracinhos finos com a pistola de raio.
- olheiro: magrelo de pele cinza-areia com as costelas aparecendo, pescoço comprido
  terminando num olho gigante com pálpebras e veias, dedos longos, pernas viradas
  para trás.
- rastejador: larva de carne segmentada com uma boca de dentes humanos na frente,
  perninhas de inseto e pústulas verdes brilhando. Pula no Lampião.
Gera uma folha de prévia em tools/arte/pixel/conceito_aliens.png.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela, IDX, RAIZ  # noqa: E402

CARNE = ["roxo_escuro", "rosa_poeira", "pele_media", "pele", "pele_luz"]
CEREBRO = ["roxo_escuro", "roxo", "lilas", "rosa_poeira", "pele_brilho"]
LESMA = ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz"]
CINZA = ["sombra", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza", "areia_luz"]
OSSO = ["cinza_escuro", "cinza", "cinza_luz", "cinza_claro"]
PUS = ["alien_esc", "alien", "alien_luz", "alien_brilho"]


def olho(t, cx, cy, r, olhar=(0.5, 0), veias=True, palpebra=0.0):
    """Olho úmido com íris verde, pupila, brilho, veias vermelhas e pálpebra."""
    t.volume(t.elipse(cx, cy, r, r), ["cinza", "cinza_luz", "cinza_claro", "branco"], achatado=1.5, suave=0.5, ambiente=0.5)
    if veias:
        rng = np.random.default_rng(int(cx * 7 + cy))
        for k in range(5):
            a = rng.uniform(0, 2 * math.pi)
            x, y = cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.95
            for _ in range(int(r * 0.6)):
                x += (cx - x) * 0.18 + rng.uniform(-0.6, 0.6)
                y += (cy - y) * 0.18 + rng.uniform(-0.6, 0.6)
                t.ponto(x, y, "vermelho_medio")
    ix, iy = cx + olhar[0] * r * 0.35, cy + olhar[1] * r * 0.35
    t.chapado(t.elipse(ix, iy, r * 0.5, r * 0.5), "alien_medio")
    t.chapado(t.elipse(ix, iy, r * 0.42, r * 0.42), "alien")
    t.chapado(t.elipse(ix, iy, r * 0.22, r * 0.3), "preto")
    t.ponto(ix - r * 0.25, iy - r * 0.25, "branco")
    if palpebra > 0:
        pal = t.elipse(cx, cy, r + 0.6, r + 0.6) & (t.yy < cy - r + 2 * r * palpebra)
        t.volume(pal, CARNE, achatado=1.5, suave=0.4, ambiente=0.3)


def membro(t, pts, r, rampa):
    for a, b in zip(pts, pts[1:]):
        t.volume(t.capsula(a[0], a[1], b[0], b[1], r), rampa, achatado=1.2, suave=0.4, ambiente=0.3)


def cerebrao():
    t = Tela(56, 56)
    chao = 55
    # Corpo de lesma babando, com dobras e gosma escorrendo no chão.
    lesma = t.elipse(26, 46, 18, 10) & (t.yy < chao)
    t.volume(lesma, LESMA, achatado=4, suave=1.2, ambiente=0.3, textura=0.15, semente=3)
    for k in range(4):
        t.linha(12 + k * 8, 40, 14 + k * 8, 52, "alien_esc")
    t.chapado(t.elipse(26, 54.5, 22, 1.5), "alien_medio")
    for x in (10, 22, 37):
        t.linha(x, 53, x, 55, "alien_luz")
    # Bracinhos finos e a pistola de raio.
    membro(t, [(34, 40), (40, 36), (46, 37)], 1.3, LESMA)
    t.volume(t.retangulo(44, 34, 9, 4), ["sombra", "cinza_escuro", "cinza", "cinza_luz"], achatado=1, suave=0.3)
    t.chapado(t.elipse(53, 36, 1.5, 1.5), "alien_brilho")
    membro(t, [(18, 40), (13, 35), (10, 38)], 1.2, LESMA)
    # Cara pequena: três olhos e mandíbulas de inseto.
    cara = t.elipse(30, 30, 10, 7)
    t.volume(cara, CARNE, achatado=2.5, suave=0.8, ambiente=0.3)
    for (x, y, r) in ((25, 29, 2.6), (31, 27, 3.2), (37, 30, 2.3)):
        olho(t, x, y, r, olhar=(0.8, 0.2), veias=False)
    for lado in (-1, 1):
        membro(t, [(30 + lado * 3, 35), (30 + lado * 6, 39), (30 + lado * 4, 42)], 0.9, OSSO)
    t.chapado(t.elipse(30, 37, 3, 1.5), "preto")
    t.ponto(30, 38, "alien_luz")
    # Cérebro exposto enorme, com os sulcos e veias, pulsando.
    cer = t.elipse(27, 14, 17, 13) & (t.yy < 26)
    t.volume(cer, CEREBRO, achatado=5, suave=1.4, ambiente=0.35, textura=0.1, semente=8)
    rng = np.random.default_rng(4)
    for _ in range(16):
        x, y = rng.uniform(13, 41), rng.uniform(4, 22)
        a = rng.uniform(0, math.pi)
        for k in range(7):
            xx, yy = x + math.cos(a + k * 0.5) * k, y + math.sin(a + k * 0.5) * k * 0.6
            if cer[int(np.clip(yy, 0, 55)), int(np.clip(xx, 0, 55))]:
                t.ponto(xx, yy, "roxo")
    for k in range(5):
        t.linha(14 + k * 7, 22, 16 + k * 6, 10, "vermelho_medio")
    t.contorno("sombra")
    return t


def olheiro():
    t = Tela(56, 64)
    # Pernas viradas para trás, finas e nodosas.
    for lado, dx in ((-1, 0), (1, 6)):
        membro(t, [(22 + dx, 40), (17 + dx, 50), (24 + dx, 62)], 1.6, CINZA)
        t.volume(t.elipse(17 + dx, 50, 2.4, 2.4), CINZA, achatado=1, suave=0.3)
        t.chapado(t.retangulo(21 + dx, 61.5, 7, 2), "cinza_escuro")
    # Tronco magrelo com costelas e barriga murcha.
    tronco = t.elipse(26, 32, 7, 11)
    t.volume(tronco, CINZA, achatado=3, suave=1.0, ambiente=0.35, textura=0.1, semente=2)
    for k in range(5):
        t.linha(20, 25 + k * 3, 32, 26 + k * 3, "cinza_escuro")
        t.linha(21, 24 + k * 3, 31, 25 + k * 3, "areia_luz")
    # Braços compridos com dedos de quatro juntas.
    membro(t, [(31, 25), (38, 34), (44, 42)], 1.4, CINZA)
    for k in range(3):
        membro(t, [(44, 42), (47 + k, 47), (46 + k * 2, 51)], 0.6, CINZA)
    membro(t, [(21, 25), (15, 34), (11, 41)], 1.3, CINZA)
    # Pescoço comprido e curvado terminando no olho gigante.
    membro(t, [(26, 22), (25, 15), (29, 9)], 2.2, CINZA)
    olho(t, 33, 9, 8.5, olhar=(1, 0.3), palpebra=0.25)
    # Baba escorrendo do canto do olho.
    t.linha(27, 15, 26, 19, "alien_luz")
    t.ponto(26, 20, "alien_brilho")
    t.contorno("sombra")
    return t


def rastejador():
    t = Tela(60, 36)
    chao = 35
    # Segmentos de carne do rabo para a cabeça, com pústulas verdes brilhando.
    for k in range(5):
        cx = 8 + k * 9
        r = 6 + k * 0.9
        seg = t.elipse(cx, chao - r, r * 0.9, r)
        t.volume(seg, CARNE, achatado=3, suave=0.9, ambiente=0.3, textura=0.15, semente=k)
        t.linha(cx - r * 0.8, chao - r, cx - r * 0.4, chao - 2 * r + 1, "roxo_escuro")
        for (dx, dy) in ((0.2, 0.5), (-0.3, 1.2)):
            px, py = cx + dx * r, chao - r - dy * r * 0.6
            t.volume(t.elipse(px, py, 1.6, 1.4), PUS, achatado=1, suave=0.3, ambiente=0.6)
        # Perninhas de inseto.
        membro(t, [(cx, chao - 3), (cx - 2, chao - 1), (cx - 3, chao)], 0.6, OSSO)
    # Cabeça com boca de dentes humanos arreganhada e gengiva.
    cab = t.elipse(50, chao - 11, 9, 10)
    t.volume(cab, CARNE, achatado=3, suave=0.9, ambiente=0.3, semente=9)
    boca = t.elipse(55, chao - 9, 5, 5.5)
    t.chapado(boca, "vermelho_esc")
    t.chapado(t.elipse(55, chao - 9, 3.5, 4) & boca, "preto")
    for k in range(4):
        t.chapado(t.retangulo(52 + k * 2, chao - 14, 1.6, 2.2), "cinza_claro")
        t.chapado(t.retangulo(52 + k * 2, chao - 6, 1.6, 2), "cinza_luz")
    olho(t, 47, chao - 16, 2.6, olhar=(1, 0), veias=False)
    olho(t, 51, chao - 19, 1.8, olhar=(1, 0.3), veias=False)
    t.contorno("sombra")
    return t


if __name__ == "__main__":
    from PIL import Image
    ims = [cerebrao().imagem(), olheiro().imagem(), rastejador().imagem()]
    W = sum(i.width for i in ims) + 40
    H = max(i.height for i in ims) + 8
    o = Image.new("RGBA", (W, H), (150, 120, 90, 255))
    x = 8
    for i in ims:
        o.alpha_composite(i, (x, H - 4 - i.height))
        x += i.width + 12
    o = o.resize((W * 4, H * 4), Image.NEAREST)
    saida = RAIZ / "tools/arte/pixel/conceito_aliens.png"
    o.save(saida)
    print(saida)
