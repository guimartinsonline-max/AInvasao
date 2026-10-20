"""Cientista refém do laboratório da base (fase 2, trecho 2).

Parte dos quadros do romeiro (pixel/refem.txt, mesma ordem e tamanho, então o jogo usa o
mesmo comportamento do refém): tira o chapéu de palha e as fitas, põe a cabeça careca
com tufos brancos espetados de cientista maluco, óculos redondos de aro grosso e troca a
roupa de romeiro por jaleco branco sujo (o bornal de couro continua).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import pixel  # noqa: E402
from motor import IDX, VAZIO, Tela  # noqa: E402

PELE = [IDX[c] for c in ("pele_sombra", "pele_escura", "pele_media", "pele", "pele_luz", "pele_clara", "pele_brilho")]
CHAPEU = [IDX[c] for c in ("areia_clara", "areia", "areia_media", "terra", "vermelho", "sombra", "areia_luz",
                            "terra_escura", "terra_media")]
FITAS = [IDX[c] for c in ("amarelo_fogo", "mandacaru", "ceu", "vermelho")]
JALECO = {"areia_clara": "branco", "areia_luz": "cinza_claro", "areia": "cinza_claro", "areia_media": "cinza_luz",
          "terra_escura": "cinza", "terra_media": "cinza_medio", "terra": "cinza_medio", "barro": "cinza_escuro"}


def cientista(q, cru=None):
    """q: quadro repintado; cru: o mesmo quadro antes da repintura (para achar o chapéu)."""
    t = Tela(q.w, q.h)
    t.px = q.px.copy()
    ref = cru if cru is not None else q
    pele = np.isin(ref.px, PELE)
    ys, xs = np.where(pele)
    if not len(ys):
        return t
    # Rosto: a pele mais alta do quadro; o chapéu é tudo de palha acima e em volta dele.
    topo = ys.min()
    cab = pele & (t.yy < topo + 9)
    cx = xs[ys < topo + 9].mean()
    chapeu = np.isin(ref.px, CHAPEU) & (t.yy < topo + 1) & (np.abs(t.xx - cx) < 14)
    fitas = np.isin(ref.px, FITAS) & (t.yy < topo + 14) & (t.xx < cx - 3)
    t.px[chapeu | fitas] = VAZIO
    # Contorno que sobrou do chapéu, solto no ar, sai também.
    from scipy import ndimage
    cheio = t.px != VAZIO
    rot, n = ndimage.label(cheio)
    if n > 1:
        tam = ndimage.sum(cheio, rot, range(1, n + 1))
        maior = 1 + int(np.argmax(tam))
        t.px[(rot != maior) & (rot > 0) & (t.yy < topo + 3)] = VAZIO
    # Contornos que ficaram sem nada dentro (fitas e aba arrancadas) saem também.
    escuro = [IDX["sombra"], IDX["preto"]]
    for _ in range(4):
        cor = (t.px != VAZIO) & ~np.isin(t.px, escuro)
        perto = ndimage.binary_dilation(cor, structure=np.ones((3, 3)))
        t.px[np.isin(t.px, escuro) & ~perto] = VAZIO
    # Roupa vira jaleco (só abaixo do rosto).
    corpo = t.yy > topo + 8
    for a, b in JALECO.items():
        t.px[corpo & (t.px == IDX[a])] = IDX[b]
    # Careca brilhante com tufos brancos espetados dos lados e atrás.
    hx, hy = cx, topo + 1
    careca = t.elipse(hx, hy + 1, 5.2, 4.0) & (t.yy <= topo + 2)
    t.cel(careca, ["pele_media", "pele", "pele_luz", "pele_clara", "pele_brilho"], sombra=1)
    t.ponto(hx - 1.5, hy - 1.5, "pele_brilho")
    for (dx, dy, ang) in ((-6, 1, -1), (-7, 3, -1), (6, 2, 1), (5, 0, 1), (-5, -1, -1)):
        x, y = hx + dx, hy + dy
        t.ponto(x, y, "branco")
        t.ponto(x + ang, y - 1, "cinza_claro")
        t.ponto(x + ang * 2, y - 1, "branco")
    # Óculos redondos de aro grosso no olho (o ponto preto mais alto do rosto).
    olho = (t.px == IDX["preto"]) & (t.yy > topo) & (t.yy < topo + 9) & (np.abs(t.xx - cx) < 9)
    oy, ox = np.where(olho)
    if len(oy):
        ex, ey = ox.mean(), oy.min() + 0.3
        aro = t.elipse(ex, ey, 2.6, 2.4) & ~t.elipse(ex, ey, 1.5, 1.4)
        t.chapado(aro, "cinza_escuro")
        t.ponto(ex - 0.8, ey - 0.8, "branco")
        t.linha(ex - 3, ey, ex - 5, ey - 0.5, "cinza_escuro")  # haste
    t.contorno("sombra")
    return t


def folha():
    d = pixel.ler("refem.txt")
    ordem = ["amarrado1", "amarrado2", "amarrado3", "solto", "procura", "entrega", "continencia",
             "corre1", "corre2", "corre3", "corre4", "pendurado1", "pendurado2"]
    import repintar as rp
    return [cientista(d[n], d[n]) for n in ordem]


if __name__ == "__main__":
    from PIL import Image
    fr = folha()
    o = Image.new("RGBA", (52 * len(fr), 46), (150, 170, 200, 255))
    for k, q in enumerate(fr):
        o.alpha_composite(q.imagem(), (k * 52, 0))
    o.resize((o.width * 3, 46 * 3), Image.NEAREST).save(sys.argv[1])
