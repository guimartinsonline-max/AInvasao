"""Soldado da Volante de máscara contra gás (fase 2, guarda a cerca e a cancela da base).

Parte dos quadros do soldado (pixel/volante.txt): o rosto vira a máscara de borracha
com dois óculos redondos de vidro (reflexo do céu), aro de metal, filtro de lata no
focinho com furinhos e a mangueira sanfonada descendo até a bolsa do filtro no peito,
correias passando por trás da cabeça. O bigode e o narigão ficam escondidos; o quepe fica.
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import pixel  # noqa: E402
from motor import IDX, VAZIO, Tela  # noqa: E402
from aliens import relevo, domo  # noqa: E402

BORRACHA = ["sombra", "sombra_media", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza"]
LATA = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "aco_brilho"]
LONA = ["caatinga_esc", "caatinga_media", "caatinga", "mandacaru"]
PELE = {IDX[c] for c in ("pele_sombra", "pele_escura", "pele_media", "pele", "pele_luz", "pele_clara", "pele_brilho",
                         "rosa_poeira")}
BIGODE = {IDX["couro_profundo"], IDX["couro_escuro"], IDX["preto"], IDX["branco"]}


def mascarar(t):
    """Põe a máscara contra gás no rosto do quadro (Tela 52x46 do soldado)."""
    t = _copia(t)
    antes = t.px != VAZIO
    pele = np.isin(t.px, list(PELE)) & (t.yy < 27) & (t.xx > 8)
    if pele.sum() < 12:
        return t
    ys, xs = np.where(pele)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    # Borracha cobre a pele do rosto e o bigode/olho dentro do rosto.
    caixa = (t.yy >= y0) & (t.yy <= y1 + 1) & (t.xx >= x0) & (t.xx <= x1 + 1)
    rosto = (pele | (caixa & np.isin(t.px, list(BIGODE)))) & caixa
    rosto = ndimage.binary_closing(rosto, iterations=1) & (t.px != VAZIO)
    # Só a frente do rosto: a nuca e a orelha continuam de pele, com as correias por cima.
    corte = x0 + (x1 - x0) * 0.38 + np.abs(t.yy - (y0 + y1) / 2) * 0.25
    rosto &= t.xx > corte
    H = np.minimum(ndimage.distance_transform_edt(np.pad(rosto, 1))[1:-1, 1:-1], 3)
    relevo(t, rosto, H + domo(t, x1 - (x1 - x0) * 0.3, (y0 + y1) / 2, (x1 - x0) * 0.4 + 1, (y1 - y0) / 2 + 1) * 1.5,
           BORRACHA, ambiente=0.15, contraste=1.1, brilho=1.4, linha=False)
    # Borda da máscara apertada na pele (linha escura).
    t.px[rosto & ~ndimage.binary_erosion(rosto) & (t.xx < x1 - 2)] = IDX["sombra"]
    # Costuras da borracha (linha clara curva).
    for k in range(x1 - x0):
        x = x0 + k
        y = y0 + 1 + (k / max(1, x1 - x0)) * 2
        if rosto[int(y), int(x)]:
            t.ponto(x, y, "cinza_medio")
    # Correias passando por trás da cabeça até a nuca.
    xc = int(x0 + (x1 - x0) * 0.4)
    for dy in (2, 6):
        t.linha(x0, y0 + dy + 1, xc, y0 + dy, "couro_escuro")
        t.ponto(x0 + 2, y0 + dy + 1, "cinza_luz")  # fivela
    # Óculos redondos: aro de lata, vidro escuro com o reflexo do céu.
    ox, oy = x1 - 4, y0 + 4
    aro = t.elipse(ox, oy, 2.8, 2.8)
    relevo(t, aro, domo(t, ox, oy, 2.8, 2.8) * 2, LATA, ambiente=0.2, brilho=1.5, linha=False)
    vidro = t.elipse(ox, oy, 1.9, 1.9)
    t.chapado(vidro, "azul_medio")
    t.chapado(vidro & (t.yy < oy - 0.3), "ceu_medio")
    t.ponto(ox - 0.8, oy - 0.9, "branco")
    t.ponto(ox + 0.8, oy + 0.8, "sombra_media")
    # O óculos de trás aparece só a beirinha.
    t.chapado(t.elipse(ox - 5, oy + 0.5, 1.2, 2.0) & rosto, "cinza_escuro")
    t.ponto(ox - 5.4, oy, "ceu_medio")
    # Filtro de lata no focinho: cilindro com anéis e furinhos, para a frente e para baixo.
    fx, fy = x1 + 1, y1 - 2
    filtro = t.capsula(fx - 2, fy - 1, fx + 3, fy + 1.5, 2.4, 2.2)
    relevo(t, filtro, np.minimum(ndimage.distance_transform_edt(np.pad(filtro, 1))[1:-1, 1:-1], 2), LATA,
           ambiente=0.1, contraste=1.2, brilho=1.8, linha=False)
    for k in (-1, 1.5):
        t.ponto(fx + k, fy - 1.5 + k * 0.5, "sombra")
        t.ponto(fx + k, fy + 1.8 + k * 0.5, "sombra")
    t.chapado(t.elipse(fx + 3.6, fy + 1.6, 1.2, 1.9), "cinza_escuro")
    for (dx_, dy_) in ((3.6, 1), (3.6, 2.4)):
        t.ponto(fx + dx_, fy + dy_, "preto")
    # Mangueira sanfonada descendo do filtro até a bolsa no peito.
    pts = [(fx + 1, fy + 3)]
    for k in range(7):
        x, y = pts[-1]
        pts.append((x - 0.6, y + 1.2))
    for k, (x, y) in enumerate(pts):
        t.chapado(t.elipse(x, y, 1.3, 0.9), "cinza_escuro" if k % 2 else "sombra_media")
        t.ponto(x - 0.6, y - 0.3, "cinza_medio")
    bx_, by_ = pts[-1]
    bolsa = t.retangulo(bx_ - 4, by_, 7, 5)
    relevo(t, bolsa, np.minimum(ndimage.distance_transform_edt(np.pad(bolsa, 1))[1:-1, 1:-1], 2), LONA,
           ambiente=0.1, linha=False)
    t.linha(bx_ - 4, by_ + 1, bx_ + 2, by_ + 1, "caatinga_esc")
    t.ponto(bx_ - 1, by_ + 2, "ouro_escuro")
    _contorno_novo(t, antes)
    return t


def _copia(t):
    c = Tela(t.w, t.h)
    c.px = t.px.copy()
    return c


def _contorno_novo(t, antes):
    """Contorno escuro só em volta do que a máscara pôs para fora do desenho."""
    cheio = t.px != VAZIO
    novo = cheio & ~antes
    fora = ndimage.binary_dilation(novo, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & ~cheio
    t.px[fora] = IDX["sombra"]


if __name__ == "__main__":
    from PIL import Image
    import repintar as rp
    d = pixel.ler("volante.txt")
    ims = []
    for n in ("parado", "atira", "panico", "anda2", "morte", "sentado1"):
        q = rp.repintar_tela(d[n])
        ims += [q.imagem(), mascarar(q).imagem()]
    W = 52 * len(ims)
    o = Image.new("RGBA", (W, 46), (176, 142, 102, 255))
    for k, i in enumerate(ims):
        o.alpha_composite(i, (k * 52, 0))
    o.resize((W * 3, 46 * 3), Image.NEAREST).save(sys.argv[1])
