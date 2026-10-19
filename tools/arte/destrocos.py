"""Carcaças destroçadas dos veículos (caminhão, blindado, trem e biplano), no
jeito do Metal Slug: não só queimadas, mas arrebentadas.

destrocar(t): pega o quadro queimado de um veículo e
- afunda o teto (a lataria amassa para dentro),
- parte o corpo num ponto e deixa a ponta caída (o eixo quebrou),
- abre rasgos: os de cima atravessam (vê o céu), os do meio mostram o escuro de
  dentro com as cavernas; a borda do rasgo é chapa virada (clara) e brasa,
- espalha fuligem, cinza e brasas, e larga pedaços de chapa no chão.
Os quadros continuam do mesmo tamanho (a folha é uniforme).
Usado por tools/arte/exportar.py e tools/arte/aviao.py.
"""
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from motor import IDX, RGB, VAZIO, Tela  # noqa: E402
from blindagem import ESC  # noqa: E402

LUM = RGB.astype(float) @ np.array([0.3, 0.59, 0.11])

CHAPA = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]


def _caixa(px):
    ys, xs = np.where(px != VAZIO)
    return ys.min(), ys.max(), xs.min(), xs.max()


def _deslocar_colunas(px, desloc, ate):
    """Desce cada coluna x de desloc[x] px, só a parte acima de y=ate (o chassi fica)."""
    h, w = px.shape
    novo = px.copy()
    for x in range(w):
        d = int(round(desloc[x]))
        if d <= 0:
            continue
        col = px[:ate, x]
        novo[:ate, x] = VAZIO
        alvo = np.full(ate, VAZIO, dtype=px.dtype)
        if d < ate:
            alvo[d:] = col[:ate - d]
        m = alvo != VAZIO
        novo[:ate, x][m] = alvo[m]
    return novo


def _borda_rasgo(px, buraco, rng, brasa=0.35):
    """Borda de um rasgo: chapa virada clara, com brasas."""
    borda = ndimage.binary_dilation(buraco) & ~buraco & (px != VAZIO)
    ys, xs = np.where(borda)
    for y, x in zip(ys, xs):
        r = rng.random()
        px[y, x] = IDX["laranja_fogo" if r < brasa * 0.5 else "laranja_escuro" if r < brasa else
                       "cinza_luz" if r < 0.75 else "cinza"]


def destrocar(t, semente=0, quebra=0.62, afunda=8, tomba=10, chassi=0.72, rasgos=4, pedacos=5, partir=True):
    """Devolve uma Tela nova com a carcaça arrebentada.
    quebra: onde o corpo parte (fração da largura); afunda: px do teto amassado;
    tomba: px que a ponta depois da quebra cai; chassi: fração da altura (de cima)
    abaixo da qual nada se mexe (rodas e chassi)."""
    rng = np.random.default_rng(semente * 13 + 5)
    px = t.px.copy()
    h, w = px.shape
    top, bot, esq, dir_ = _caixa(px)
    alt = bot - top
    ate = int(top + alt * chassi)
    larg = dir_ - esq
    xs = np.arange(w)
    # 1. Teto amassado: duas cavas em sino.
    desloc = np.zeros(w)
    for k in range(2):
        cx = esq + larg * rng.uniform(0.2, 0.8)
        sig = larg * rng.uniform(0.08, 0.16)
        desloc += afunda * (1 if k == 0 else 0.55) * np.exp(-((xs - cx) / sig) ** 2)
    # 2. Quebra: depois do ponto, a ponta cai inclinada.
    xb = int(esq + larg * quebra)
    if partir:
        desloc += np.where(xs > xb, tomba * (xs - xb) / max(1, dir_ - xb) + 2, 0)
    px = _deslocar_colunas(px, desloc, ate)
    # Tudo que ainda brilha (dourado, vermelho, tinta clara) escurece queimado.
    cheio = px != VAZIO
    for _ in range(3):
        claro = cheio & (LUM[np.clip(px, 0, None)] > 75)
        px[claro] = ESC[px[claro]]
    # Dourados e vermelhos da pintura viram metal chamuscado (as brasas entram depois).
    quentes = [IDX[c] for c in ("amarelo_fogo", "amarelo_claro", "laranja_fogo", "laranja_escuro", "ouro_escuro",
                                "vermelho", "vermelho_medio")]
    m = np.isin(px, quentes)
    px[m] = IDX["couro_profundo"]
    px[m & ((np.indices(px.shape).sum(0)) % 3 == 0)] = IDX["sombra_media"]
    if partir:
        # Fenda da quebra em V, aberta de cima: dentes irregulares e brasa na borda.
        fenda = np.zeros_like(px, dtype=bool)
        fundo = top + (ate - top) * 0.85
        for y in range(top, int(fundo)):
            meia = 1 + 5 * (1 - (y - top) / max(1, fundo - top)) + rng.integers(0, 2)
            dx = int(rng.integers(-1, 2)) + int((y - top) * 0.15)
            fenda[y, max(0, int(xb + dx - meia)):min(w, int(xb + dx + meia))] = True
        fenda &= px != VAZIO
        px[fenda] = VAZIO
        _borda_rasgo(px, fenda, rng, brasa=0.45)
    # 3. Rasgos: os de cima atravessam; os do meio mostram o escuro de dentro e uma aba de chapa virada.
    yy, xx = np.mgrid[0:h, 0:w]
    ruido = ndimage.gaussian_filter(rng.standard_normal((h, w)), 1.0)
    for k in range(rasgos):
        cx = esq + larg * rng.uniform(0.1, 0.9)
        cy = top + alt * rng.uniform(0.1, 0.55)
        r = rng.uniform(4.5, 9)
        blob = (((xx - cx) / (r * 1.4)) ** 2 + ((yy - cy) / r) ** 2 + ruido * 1.4) < 1
        blob &= (px != VAZIO) & (yy < ate)
        if blob.sum() < 6:
            continue
        atravessa = cy < top + alt * 0.32 and k % 2 == 0
        if atravessa:
            px[blob] = VAZIO
        else:
            px[blob] = IDX["preto"]
            fundo_ = blob & (yy > cy + r * 0.3)
            px[fundo_ & ((xx + yy) % 2 == 0)] = IDX["marrom_noite"]
        _borda_rasgo(px, blob, rng)
        # Aba de chapa arrancada para fora, presa na borda de cima.
        ax = int(cx + rng.uniform(-r, r) * 0.5)
        ay = int(cy - r * 0.8)
        lado = 1 if rng.random() < 0.5 else -1
        for i in range(int(r * 0.9)):
            x_ = ax + lado * i
            y_ = ay - i // 2
            if 0 <= x_ < w and 0 <= y_ < h:
                px[y_, x_] = IDX["cinza"]
                if y_ + 1 < h:
                    px[y_ + 1, x_] = IDX["sombra"]
    cheio = px != VAZIO
    # 4. Fuligem, cinza e brasas.
    fuligem = (ndimage.gaussian_filter(rng.standard_normal((h, w)), 2.5) > 0.55) & cheio
    px[fuligem & (rng.random((h, w)) < 0.7)] = IDX["preto"]
    for _ in range(int(larg * 0.25)):
        x = int(rng.integers(esq, dir_ + 1))
        y = int(rng.integers(top, ate))
        if px[y, x] != VAZIO:
            px[y, x] = IDX[rng.choice(["laranja_fogo", "amarelo_fogo", "cinza", "cinza_medio"], p=[0.3, 0.15, 0.3, 0.25])]
    # 5. Pedaços de chapa largados no chão, onde estiver vazio embaixo.
    for _ in range(pedacos):
        for _t in range(20):
            x = int(rng.integers(2, w - 8))
            pw, ph = int(rng.integers(5, 11)), int(rng.integers(2, 5))
            area = px[h - ph - 1:h, x:x + pw]
            if (area == VAZIO).all():
                inclina = rng.integers(0, 2)
                for i in range(pw):
                    yb = h - 1 - (i * inclina // 3)
                    px[yb - ph + 1:yb + 1, x + i] = IDX["cinza_escuro"]
                    px[yb - ph + 1, x + i] = IDX["cinza"]
                px[h - 1, x] = IDX["sombra"]
                break
    n = Tela(w, h)
    n.px = px
    return n
