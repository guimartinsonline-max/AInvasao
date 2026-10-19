"""Corpos caídos no chão (morte por arma, como no Metal Slug).

tombar(): o corpo girando no meio da queda (45 graus, só os pés e o ombro tocam o chão).
estirar(): o corpo estendido de costas (ou de cara), 100% apoiado no chão: depois de
girar, cada coluna desce até encostar no chão, então nada fica no ar, e um pouco de
peso achata a barriga e os braços para o lado.
"""
import numpy as np
from scipy import ndimage

from motor import VAZIO, Tela


def _colocar(px, w, h, cx=None):
    """Põe o desenho girado num quadro w x h com a base no chão (última linha)."""
    ys, xs = np.where(px != VAZIO)
    t = Tela(w, h)
    dy = h - 1 - ys.max()
    larg = xs.max() - xs.min() + 1
    dx = (max(0, (w - larg) // 2) if cx is None else int(cx - larg / 2)) - xs.min()
    dx = min(max(dx, -xs.min()), w - 1 - xs.max())
    for y, x in zip(ys, xs):
        if 0 <= y + dy < h and 0 <= x + dx < w:
            t.px[y + dy, x + dx] = px[y, x]
    return t


def tombar(tela, costas=True, graus=50):
    """Meio da queda: o corpo inclinado, girando em volta dos pés."""
    a = tela.px.astype(np.int32) + 1  # VAZIO vira 0 para o giro
    pad = np.pad(a, 16)
    rot = ndimage.rotate(pad, graus if costas else -graus, reshape=True, order=0, cval=0)
    px = rot - 1
    return _colocar(px, tela.w, tela.h, cx=tela.w * 0.42)


def estirar(tela, costas=True):
    """Estendido no chão: girado 90 graus e assentado coluna por coluna."""
    rot = np.rot90(tela.px, 1 if costas else -1)
    ys, xs = np.where(rot != VAZIO)
    rot = rot[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    H, W = rot.shape
    # Assentar: cada coluna desce até o chão (o corpo pesa), sem esticar nada.
    out = np.full((H, W), VAZIO, dtype=rot.dtype)
    for x in range(W):
        col = rot[:, x]
        cheio = np.where(col != VAZIO)[0]
        if not len(cheio):
            continue
        gap = H - 1 - cheio.max()
        out[gap:, x] = col[:H - gap] if gap else col
    # Achatar um pouco: o que sobra muito alto (barriga, braço) desce 1/4.
    alto = H
    ys, _ = np.where(out != VAZIO)
    topo = ys.min()
    if H - topo > 14:
        keep = np.linspace(topo, H - 1, int((H - topo) * 0.78) + 1).round().astype(int)
        out2 = np.full_like(out, VAZIO)
        out2[H - len(keep):] = out[keep]
        out = out2
    t = _colocar(out, tela.w, tela.h)
    # Contorno escuro na base fica: o corpo encosta numa linha só, sem buraco.
    return t
