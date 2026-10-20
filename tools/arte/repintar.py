"""Repintura do Lampião no nível do Metal Slug: mais tons por material,
volume com luz de cima e da esquerda, dobras na roupa, couro gasto e brilho
no chapéu. Trabalha na grade de caracteres (legenda em pixel.py) e só mexe nos
pixels marcados (corpo), deixando a arma e o contorno como estão.
"""
import numpy as np
from scipy import ndimage

# Rampas do escuro para o claro, em caracteres da legenda.
RAMPAS = {
    "caqui": "qwetyui",   # camisa: terra escura até areia clara
    "couro": "asdfgh",    # chapéu, alpercata, cinturão, bornal
    "calca": "ZxXcCv",    # calça de mescla
    "farda": "jJkP",      # farda verde da Volante
}
LAMPIAO = ("caqui", "couro", "calca")
INIMIGO = ("farda", "couro", "caqui")
MATERIAL = {ch: nome for nome, r in RAMPAS.items() for ch in r}
LUZ = (-0.6, -0.8)  # de cima e da esquerda


def _volume(m, achatado=2.2, suave=0.7):
    """Luz de 0 a 1 por pixel da máscara, pela normal estimada da borda."""
    dist = ndimage.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
    alt = ndimage.gaussian_filter(np.minimum(dist, achatado), suave)
    gy, gx = np.gradient(alt)
    lx, ly = LUZ
    lz = 0.75
    n = np.sqrt(gx * gx + gy * gy + 1.0)
    lum = (-gx * lx - gy * ly + lz) / (n * np.sqrt(lx * lx + ly * ly + lz * lz))
    return np.clip((lum - 0.45) * 2.2 + 0.5, 0, 1)


def repintar(g, alvo, materiais=LAMPIAO, inteiro=False):
    """g: grade (lista de listas de caracteres); alvo: máscara bool do que pode ser repintado."""
    a = np.array(g)
    h, w = a.shape
    yy = np.mgrid[0:h, 0:w][0]
    novo = a.copy()
    for nome in materiais:
        rampa = RAMPAS[nome]
        m = alvo & np.isin(a, list(rampa))
        if not m.any():
            continue
        k = len(rampa)
        orig = np.vectorize(lambda c: rampa.find(c))(np.where(m, a, rampa[0])) / (k - 1)
        # inteiro: luz calculada no corpo todo (fecha as linhas internas), sem
        # manchas em cada pedacinho entre contornos (inimigos e refém).
        base = ndimage.binary_closing(m, iterations=2) | m if inteiro else m
        rot, n = ndimage.label(base)
        luz = np.zeros(m.shape)
        for i in range(1, n + 1):
            p = rot == i
            ys, xs = np.where(p)
            # Gradiente do volume inteiro: claro em cima à esquerda, escuro embaixo à direita.
            gx = (xs - xs.mean()) / max(4, np.ptp(xs) + 1)
            gyv = (ys - ys.mean()) / max(4, np.ptp(ys) + 1)
            luz[p] = (_volume(p, achatado=3.5, suave=1.2)[p] * 0.6 + 0.2 if inteiro else _volume(p)[p]) - 0.45 * gx - 0.4 * gyv
        peso = {'caqui': 0.7, 'couro': 0.55, 'calca': 0.5, 'farda': 0.65}[nome] * (0.75 if inteiro else 1)
        v = (1 - peso) * orig + peso * luz
        if nome == 'calca':
            v = v - 0.12
        if nome in ("caqui", "farda"):
            v = v + _dobras_camisa(m, yy) * (0.6 if inteiro else 1)
        nivel = np.clip(np.round(v * (k - 1)), 0, k - 1).astype(int)
        # Tira pixel solto: fica com o nível da maioria dos vizinhos do mesmo material.
        nivel = _limpar(nivel, m)
        # Como no Metal Slug: a beirada que encosta no contorno em cima ou à esquerda acende
        # forte; a que encosta embaixo ou à direita afunda (miolo de sombra).
        o = (a == "O") | (a == ".")
        cima = np.zeros_like(m)
        cima[1:] = o[:-1]
        esq = np.zeros_like(m)
        esq[:, 1:] = o[:, :-1]
        baixo = np.zeros_like(m)
        baixo[:-1] = o[1:]
        dir_ = np.zeros_like(m)
        dir_[:, :-1] = o[:, 1:]
        luz_b = m & (cima | esq) & (nivel >= (k - 1) * 0.35)
        nivel[luz_b] = np.minimum(k - 1, nivel[luz_b] + (2 if nome != "calca" else 1))
        somb_b = m & (baixo | dir_) & ~(cima | esq)
        nivel[somb_b] = np.maximum(0, nivel[somb_b] - 1)
        cores = np.array(list(rampa))[nivel]
        novo[m] = cores[m]
        if nome == "couro":
            _couro_gasto(novo, m, rampa)
    return [list(l) for l in novo]


def _limpar(nivel, m):
    out = nivel.copy()
    h, w = nivel.shape
    for y, x in zip(*np.where(m)):
        viz = [nivel[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
               if 0 <= yy < h and 0 <= xx < w and m[yy, xx]]
        if len(viz) >= 3 and all(v != nivel[y, x] for v in viz):
            out[y, x] = max(set(viz), key=viz.count)
    return out


def _dobras_camisa(m, yy):
    """Panos da camisa: vinco curvo puxado pelo cinturão (escuro com borda clara
    em cima) e uma dobra vertical descendo do peito."""
    d = np.zeros(m.shape)
    rot, n = ndimage.label(m)
    xx = np.mgrid[0:m.shape[0], 0:m.shape[1]][1]
    for i in range(1, n + 1):
        p = rot == i
        ys, xs = np.where(p)
        if len(ys) < 40:  # manga: só volume
            continue
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        cx = (x0 + x1) / 2
        # Vinco curvo perto da barra: sobe nas pontas (tecido puxado pelo cinto).
        for k, off in enumerate((3, 6)):
            curva = y1 - off - ((xx - cx) / max(1, (x1 - x0) / 2)) ** 2 * 1.5
            vinco = p & (np.abs(yy - curva) < 0.55) & (np.abs(xx - cx) < (x1 - x0) * (0.32 - k * 0.08))
            d[vinco] -= 0.3
            d[np.roll(vinco, -1, axis=0) & p & ~vinco] += 0.18
        # Dobra vertical no peito, levemente inclinada.
        xv = x0 + (x1 - x0) * 0.62 + (yy - y0) * 0.15
        vert = p & (np.abs(xx - xv) < 0.5) & (yy > y0 + 3) & (yy < y1 - 2)
        d[vert] -= 0.22
        d[np.roll(vert, -1, axis=1) & p & ~vert] += 0.15
    return d


def _couro_gasto(a, m, rampa):
    """Couro: borda de cima brilhando do lado da luz, borda de baixo mais escura,
    costura clara na faixa do chapéu e marcas claras de uso."""
    k = len(rampa)
    nv = lambda c: rampa.find(c)
    cima = np.zeros_like(m)
    cima[1:] = ~m[:-1]
    cima[0] = True
    baixo = np.zeros_like(m)
    baixo[:-1] = ~m[1:]
    rot, n = ndimage.label(m)
    for i in range(1, n + 1):
        p = rot == i
        ys, xs = np.where(p)
        lim = xs.min() + np.ptp(xs) * 0.65
        for y, x in zip(ys, xs):
            if cima[y, x] and x <= lim:
                a[y, x] = rampa[min(k - 1, nv(a[y, x]) + 2)]
            elif baixo[y, x] and not cima[y, x]:
                a[y, x] = rampa[max(0, nv(a[y, x]) - 1)]
    # Costura: faixa comprida de couro escuro ganha pontinhos claros.
    h, w = m.shape
    for y in range(h):
        run = 0
        for x in range(w + 1):
            if x < w and m[y, x] and nv(a[y, x]) <= 1:
                run += 1
                continue
            if run >= 8:
                for xx in range(x - run + 1, x - 1, 2):
                    a[y, xx] = rampa[3]
            run = 0
    rng = np.random.default_rng(3)
    interior = ndimage.binary_erosion(m)
    for y, x in zip(*np.where(interior)):
        if rng.random() < 0.05 and 2 <= nv(a[y, x]) <= 3:
            a[y, x] = rampa[min(k - 1, nv(a[y, x]) + 2)]


def repintar_tela(tela, materiais=INIMIGO):
    """Repinta uma Tela inteira (inimigos e refém: arma e rosto ficam como estão)."""
    import pixel
    g = [list(l) for l in pixel.para_texto(tela).split("\n")]
    g = repintar(g, np.array(g) != ".", materiais, inteiro=True)
    return pixel.de_texto("\n".join("".join(l) for l in g), w=tela.w, h=tela.h)
