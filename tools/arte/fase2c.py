"""Fase 2, trecho 3: a descida da cratera no elevador de carga (amostra para aprovar).

A plataforma desce e a câmera vai junto: o fundo sobe. Na parede de perto, andaimes de
toras com lampiões e soldados que pulam para a plataforma; ao fundo, a parede do outro
lado da cratera virada vidro, com veios verdes acesos, e lá embaixo o casco enorme do
disco meio enterrado, com as runas acesas e a fumaça verde subindo.
Prévia: python3 tools/arte/fase2c.py saida.png
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from motor import IDX, VAZIO, Tela  # noqa: E402
from fase2 import ruido, pintar_niveis  # noqa: E402
import base_detalhe as bd  # noqa: E402
from base_detalhe import pintar, cilindro  # noqa: E402

W, H = 548, 308
ROCHA = ["preto", "marrom_noite", "couro_profundo", "roxo_escuro", "chao_n3", "chao_n4", "chao_n5"]
VIDRO = ["preto", "alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz"]
CASCO = ["preto", "sombra", "sombra_media", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "aco_brilho"]


def parede(w, h, semente=0, perto=False, brilho_baixo=True, tam=18):
    """Parede da cratera em blocos de rocha fundida (como as paredes de pedra do Metal
    Slug): cada bloco é um gomo irregular levemente abaulado, com a beirada de baixo acesa
    de verde pela luz que sobe do disco, a de cima em sombra, junta escura entre eles;
    alguns blocos viraram vidro verde-escuro com o brilho na quina."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    n = int(w * h / (tam * tam))
    sx = rng.uniform(-tam, w + tam, n)
    sy = rng.uniform(-tam, h + tam, n)
    # Mistura blocos grandes e pequenos: tira sementes ao acaso (fica mais espaço).
    manter = rng.random(n) < 0.7
    sx, sy = sx[manter], sy[manter]
    n = len(sx)
    sy_ = sy + (sx * 0.25)  # bancadas levemente inclinadas
    from scipy.spatial import cKDTree
    arv = cKDTree(np.c_[sx * 0.8, sy_ * 1.25])
    pts = np.c_[t.xx.ravel() * 0.8, (t.yy.ravel() + t.xx.ravel() * 0.25) * 1.25]
    d, idx = arv.query(pts, k=2)
    idx = idx[:, 0].reshape(h, w)
    borda = (d[:, 1] - d[:, 0]).reshape(h, w)
    cx, cy = sx[idx], sy[idx]
    dx, dy = (t.xx - cx) / tam, (t.yy - cy) / tam
    vidro = rng.random(n)[idx] < 0.12
    tom = rng.uniform(-0.08, 0.08, n)[idx]
    v = 0.4 + dy * 0.4 - dx * 0.15 + tom + (t.yy / h) * (0.2 if brilho_baixo else 0) + (0.06 if perto else -0.08)
    v = v + ruido(h, w, (1.2, 2.5), semente + 7) * 0.07  # grão e lascas dentro do bloco
    v = np.where(borda < 0.8, 0.05, v)
    v = np.where((borda >= 0.8) & (borda < 2.0) & (dy > 0.1), v + 0.28, v)
    v = np.where((borda >= 0.8) & (borda < 1.8) & (dy < -0.3), v - 0.12, v)
    pintar(t, ~vidro, v, ROCHA)
    pintar(t, vidro, v * 0.8 + 0.05, VIDRO)
    quina = vidro & (borda >= 1.2) & (borda < 2.2) & (dy > 0.2)
    t.px[quina] = IDX["alien_luz"]
    t.px[(borda < 0.8)] = IDX["preto"]
    return t


def andaime(w, h, semente=0):
    """Andaime de toras preso na parede: montantes, travessas em X amarradas, pisos de
    tábua em dois níveis com guarda-corpo, escada de mão, lampião aceso e sacos."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    for x in (4, w // 2, w - 5):
        cilindro(t, x, h - 1, x + rng.uniform(-1, 1), 0, 1.8, 1.6, semente=semente + x, rachas=1, nos=1)
    pisos = [h // 3, int(h * 0.72)]
    for y0 in pisos:
        for k, x in enumerate(range(0, w, 4)):
            bd.tabua(t, x, y0, 4, 3, semente=semente + y0 + k, vertical=True)
        t.linha(0, y0, w - 1, y0, "mad_n6")
        cilindro(t, 0, y0 - 9, w - 1, y0 - 9, 0.9, 0.9, semente=y0, rachas=0, nos=0)
    for a, b in ((0, pisos[0]), (pisos[0] + 3, pisos[1])):
        cilindro(t, 4, a + 2, w // 2, b - 1, 0.9, 0.9, semente=a + 1, rachas=0, nos=0, escurecer=0.12)
        cilindro(t, w // 2, a + 2, w - 5, b - 1, 0.9, 0.9, semente=a + 2, rachas=0, nos=0, escurecer=0.12)
        bd.amarracao(t, w // 2, a + 3, 1.6)
    for x in (w - 14, w - 9):
        cilindro(t, x, pisos[1], x, pisos[0], 0.7, 0.7, semente=x, rachas=0, nos=0)
    for y in range(pisos[0] + 4, pisos[1], 5):
        t.linha(w - 14, y, w - 9, y, "mad_n5")
    bd.lampiao(t, w // 2 + 6, pisos[0] + 8)
    bd.saco(t, 2, pisos[1], 14, 6, semente=semente)
    bd.saco(t, 12, pisos[1], 13, 6, semente=semente + 1)
    bd.caixote(t, w - 30, pisos[0], 16, 9, semente=semente + 2)
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


def casco_disco(w, h):
    """O topo do disco meio enterrado lá embaixo: cúpula de liga com o reflexo do céu,
    nervuras, faixa de runas acesas, escotilhas e um rasgo em brasa verde."""
    t = Tela(w, h)
    cx, cy = w / 2, h + w * 0.18
    m = t.elipse(cx, cy, w * 0.52, w * 0.36)
    d = ((t.xx - cx) / (w * 0.52)) ** 2 + ((t.yy - cy) / (w * 0.36)) ** 2
    v = 0.25 + (1 - d) * 0.5 - (t.xx - cx) / w * 0.4
    v = np.where(np.abs(d - 0.82) < 0.02, v + 0.35, v)
    for k in range(-6, 7):
        v = np.where(np.abs((t.xx - cx) - k * w / 14 * (1 - d * 0.3)) < 0.6, v - 0.2, v)
    pintar(t, m, v, CASCO)
    faixa = m & (np.abs(d - 0.66) < 0.025)
    t.px[faixa] = IDX["sombra"]
    xs = np.where(faixa.any(0))[0]
    for x in xs[::5]:
        ys = np.where(faixa[:, x])[0]
        if len(ys):
            t.ponto(x, ys[0], "alien_luz")
            t.ponto(x + 1, ys[0] + 1, "alien")
    for k in range(5):
        ex = cx - w * 0.32 + k * w * 0.16
        ey = cy - w * 0.36 * math.sqrt(max(0, 1 - ((ex - cx) / (w * 0.52)) ** 2 * 1.4)) + 14
        e = t.elipse(ex, ey, 6, 4) & m
        t.chapado(e, "alien_esc")
        t.chapado(t.elipse(ex - 1, ey - 1, 3, 2) & m, "alien_luz")
    rasgo = t.poligono([(cx + 40, h * 0.55), (cx + 70, h * 0.45), (cx + 95, h * 0.7), (cx + 60, h * 0.85)]) & m
    t.chapado(rasgo, "alien_esc")
    t.chapado(ndimage.binary_erosion(rasgo, iterations=2), "alien_brilho")
    return t


def plataforma(w=150):
    """Plataforma do elevador: estrado de chapa xadrez com viga de ferro rebitada,
    guarda-corpo de cano dos dois lados, correntes subindo dos cantos até o gancho,
    caixotes e um tambor amarrados no canto."""
    h = 120
    t = Tela(w, h)
    base = h - 1
    deck = t.retangulo(0, base - 12, w, 8)
    v = 0.55 - (t.yy - (base - 12)) / 14 + (((t.xx.astype(int) // 3 + t.yy.astype(int)) % 2) == 0) * 0.08
    pintar(t, deck, v, bd.FERRO)
    t.linha(0, base - 12, w - 1, base - 12, "cinza_luz")
    viga = t.retangulo(4, base - 4, w - 8, 5)
    pintar(t, viga, 0.4 - (t.yy - (base - 4)) / 8, bd.FERRO)
    for x in range(6, w - 4, 7):
        t.ponto(x, base - 2, "aco_brilho")
    for x in (3, w - 4):
        cilindro(t, x, base - 12, x, base - 30, 1.1, 1.1, rampa=bd.FERRO, rachas=0, nos=0, casca=False)
    t.linha(3, base - 30, w - 4, base - 30, "cinza_medio")
    t.linha(3, base - 21, w - 4, base - 21, "sombra_media")
    # Correntes dos cantos até o gancho no alto (o cabo continua para fora da tela).
    gx, gy = w / 2, 6
    for x in (3, w - 4):
        n = 40
        for k in range(n):
            f = k / n
            px = x + (gx - x) * f
            py = (base - 30) + (gy - (base - 30)) * f
            t.ponto(px, py, "cinza_medio" if k % 2 else "sombra")
    t.chapado(t.retangulo(gx - 4, 0, 8, 8), "sombra_media")
    t.ponto(gx - 2, 1, "cinza_luz")
    t.linha(gx, 0, gx, -1, "sombra")
    bd.caixote(t, 10, base - 12, 22, 14, "TNT", semente=4)
    bd.caixote(t, 14, base - 26, 16, 10, semente=5)
    tb = t.retangulo(w - 26, base - 28, 12, 16)
    pintar(t, tb, 0.25 + np.clip(1 - np.abs((t.xx - (w - 22)) / 6), 0, 1) * 0.6, bd.VERMELHO + ["laranja_escuro"])
    bd.lampiao(t, w - 8, base - 34)
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


def guias(h):
    """Guias do poço: duas toras grossas com o trilho de ferro pregado, travadas em X."""
    t = Tela(W, h)
    for x in (182, 366):
        cilindro(t, x, h - 1, x, 0, 3.2, 3.2, semente=x, rachas=3, nos=2)
        t.linha(x + (3 if x < 300 else -3), 0, x + (3 if x < 300 else -3), h - 1, "cinza_medio")
        for y in range(6, h, 22):
            t.chapado(t.retangulo(x - 3, y, 7, 2), "sombra_media")
            t.ponto(x - 1, y, "cinza_luz")
    return t


def amostra(caminho):
    from PIL import Image
    bd.NOITE = 0.08
    fundo = Image.new("RGBA", (W, H))
    # Céu de noite lá no alto (só uma faixa, estamos dentro da cratera).
    import fase2b as f2b
    fundo.alpha_composite(f2b.ceu_noite().imagem())
    longe = parede(W, H, semente=3, tam=30)
    # Boca da cratera aberta em cima: a parede do outro lado só começa abaixo do recorte.
    perfil = 18 + ruido(1, W, 18, 4)[0] * 6
    longe.px[longe.yy < perfil[None, :]] = VAZIO
    from caatinga_detalhe import nevoa
    fundo.alpha_composite(nevoa(longe, 0.45, "sombra").imagem())
    disco = casco_disco(360, 96)
    fundo.alpha_composite(disco.imagem(), (-60, H - 96))
    # Fumaça verde subindo do disco (no jogo vira sprite animado).
    fum = Tela(W, H)
    for k, x0 in enumerate((70, 200)):
        for j in range(30):
            y = H - 60 - j * 7
            r = 6 + j * 0.6
            x = x0 + math.sin(j / 3 + k) * 6
            e = fum.elipse(x, y, r, r * 0.8) & (fum.px == VAZIO)
            pintar(fum, e, 0.5 - j / 60 + 0 * fum.yy, ["alien_profundo", "alien_esc", "alien_medio", "alien"])
    fumi = fum.imagem()
    a = np.array(fumi)
    a[..., 3] = (a[..., 3] * 0.55).astype(np.uint8)
    fundo.alpha_composite(Image.fromarray(a))
    # Andaimes nas paredes de perto (esquerda e direita).
    for (x, w_, h_, s_) in ((0, 120, 200, 1), (430, 118, 180, 2)):
        pd = parede(w_, H, semente=10 + s_, perto=True, tam=22)
        corte = 60 + ruido(H, 1, 10, s_)[:, 0] * 12
        if x == 0:
            pd.px[pd.xx > corte[:, None]] = VAZIO
        else:
            pd.px[pd.xx < w_ - corte[:, None]] = VAZIO
        fundo.alpha_composite(pd.imagem(), (x, 0))
        an = andaime(w_ - 20, h_, semente=s_)
        fundo.alpha_composite(an.imagem(), (x + (10 if x == 0 else 10), 40 + s_ * 20))
    fundo.alpha_composite(guias(H).imagem())
    pl = plataforma(170)
    py = H - 30 - pl.h
    fundo.alpha_composite(pl.imagem(), (274 - 85, py + 30))
    # Personagens para dar a escala: o Lampião na plataforma e um soldado pulando nela.
    A = "/home/claude/ainvasao/assets/sprites/"
    lamp = Image.open(A + "lampiao.png").convert("RGBA").crop((60, 0, 120, 72))
    fundo.alpha_composite(lamp, (250, py + 30 + pl.h - 12 - 70))
    vol = Image.open(A + "volante.png").convert("RGBA").crop((52 * 2, 0, 52 * 3, 46))
    fundo.alpha_composite(vol, (360, py - 20))
    fundo.save(caminho)
    bd.NOITE = 0.0


if __name__ == "__main__":
    amostra(sys.argv[1] if len(sys.argv) > 1 else "/tmp/f2c.png")
