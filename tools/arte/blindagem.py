"""Acabamento de lataria no nível do Metal Slug para veículos e o trem:
pintura lisa em faixas (sem granulado), chapas com emenda e rebite, quinas
com brilho em cima e sombra embaixo, tinta descascada mostrando o metal,
escorrido de ferrugem saindo dos rebites e lama subindo das rodas.
"""
import numpy as np
from scipy import ndimage

from motor import IDX, RGB, VAZIO, BAYER4

VERDES = [IDX[n] for n in ("caatinga_esc", "caatinga_media", "caatinga", "mandacaru", "mandacaru_luz")]


def _mapa(mais_claro):
    """Para cada cor, a mais parecida um degrau mais escura (ou mais clara)."""
    lum = RGB.astype(float) @ np.array([0.3, 0.59, 0.11])
    mapa = np.arange(len(RGB))
    for i in range(len(RGB)):
        melhor, dist = i, 1e9
        for j in range(len(RGB)):
            if mais_claro:
                if lum[j] <= lum[i] * 1.08 or lum[j] > lum[i] * 1.7 + 20:
                    continue
                alvo = lum[i] * 1.25 + 6
            else:
                if lum[j] >= lum[i] * 0.88 or lum[j] < lum[i] * 0.45:
                    continue
                alvo = lum[i] * 0.74
            ci = RGB[i] / max(lum[i], 1)
            cj = RGB[j] / max(lum[j], 1)
            d = np.sum((ci - cj) ** 2) * 900 + (alvo - lum[j]) ** 2 * 0.02
            if d < dist:
                melhor, dist = j, d
        mapa[i] = melhor
    return mapa


ESC = _mapa(False)
CLA = _mapa(True)
ESC[IDX["preto"]] = IDX["preto"]


def _moda(px, m):
    """Cada pixel da máscara fica com a cor que mais aparece em volta (tira o granulado)."""
    out = px.copy()
    h, w = px.shape
    for y, x in zip(*np.where(m)):
        viz = px[max(0, y - 1):y + 2, max(0, x - 1):x + 2].ravel()
        viz = viz[np.isin(viz, VERDES)]
        if len(viz):
            v, c = np.unique(viz, return_counts=True)
            if c.max() >= 5:
                out[y, x] = v[c.argmax()]
    return out


def blindar(t, semente=0, painel=24, lama=True, chao=None):
    """Aplica o acabamento numa Tela de veículo (in place). chao: linha das rodas no chão."""
    rng = np.random.default_rng(semente)
    px = t.px
    h, w = px.shape
    verde = np.isin(px, VERDES)
    px[:] = _moda(px, verde)
    verde = np.isin(px, VERDES)
    rot, n = ndimage.label(verde)
    rebites = []
    for i in range(1, n + 1):
        m = rot == i
        ys, xs = np.where(m)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        larg, alt = x1 - x0 + 1, y1 - y0 + 1
        if larg < 20 or alt < 8 or m.sum() < 160:
            continue
        miolo = ndimage.binary_erosion(m, iterations=3)
        # Emendas verticais das chapas: vão escuro com aresta clara à direita.
        xs_em = list(range(x0 + painel // 2 + int(rng.integers(-3, 4)), x1 - 4, painel))
        for xe in xs_em:
            col = m[:, xe] & miolo[:, xe]
            if col.sum() < 6:
                continue
            px[col, xe] = ESC[px[col, xe]]
            dir_ = np.zeros_like(m)
            dir_[:, xe + 1] = col
            px[dir_ & m] = CLA[px[dir_ & m]]
            for y in np.where(col)[0][2::6]:
                rebites.append((y, xe - 2))
                rebites.append((y, xe + 3))
        # Emenda horizontal nas chapas altas.
        if alt >= 22:
            ye = y0 + int(alt * 0.42)
            lin = m[ye] & miolo[ye]
            px[ye, lin] = ESC[px[ye, lin]]
            lin2 = m[ye + 1] & miolo[ye + 1]
            px[ye + 1, lin2] = CLA[px[ye + 1, lin2]]
            for x in np.where(lin)[0][3::7]:
                rebites.append((ye - 2, x))
        # Quinas: borda de cima clara, de baixo escura.
        cima = m & ~np.vstack([np.zeros((1, w), bool), m[:-1]])
        baixo = m & ~np.vstack([m[1:], np.zeros((1, w), bool)])
        px[cima] = CLA[px[cima]]
        px[baixo & ~cima] = ESC[px[baixo & ~cima]]
        # Tinta descascada mostrando o metal (lasquinhas de 2 a 4 px).
        cand = np.argwhere(miolo)
        for _ in range(max(1, int(m.sum() / 900))):
            y, x = cand[rng.integers(len(cand))]
            lasca = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1)][:int(rng.integers(4, 8))]
            for dy, dx in lasca:
                if m[y + dy, x + dx]:
                    px[y + dy, x + dx] = IDX["cinza_medio"]
            px[y, x] = IDX["cinza_luz"]
            for dy, dx in lasca:  # borda escura de tinta embaixo da lasca
                if (dy + 1, dx) not in lasca and y + dy + 1 < h and m[y + dy + 1, x + dx]:
                    px[y + dy + 1, x + dx] = IDX["caatinga_esc"]
    # Rebites: ponto claro com sombra embaixo à direita; alguns soltam ferrugem.
    ok = np.isin(px, VERDES + [ESC[v] for v in VERDES] + [CLA[v] for v in VERDES])
    for y, x in rebites:
        if 0 < y < h - 2 and 0 < x < w - 2 and ok[y, x] and ok[y + 1, x + 1]:
            px[y, x] = IDX["mandacaru_luz"]
            px[y + 1, x + 1] = IDX["sombra"]
            if rng.random() < 0.18:
                for d in range(2, int(rng.integers(4, 10))):
                    if y + d < h and ok[y + d, x] and (d < 4 or rng.random() < 0.75):
                        px[y + d, x] = IDX["couro" if d < 5 else "couro_escuro"]
    if lama:
        _lama(t, rng, chao)
    return t


def _lama(t, rng, chao=None):
    """Lataria suja de terra na parte de baixo (faixa escura lisa) e respingos de lama.
    Só na pintura: rodas, ferragens e detalhes ficam limpos."""
    px = t.px
    h, w = px.shape
    pintura = np.isin(px, VERDES + [int(ESC[v]) for v in VERDES] + [int(CLA[v]) for v in VERDES])
    cheio = px != VAZIO
    linhas = np.where(cheio.any(1))[0]
    if not len(linhas):
        return
    fundo = chao if chao is not None else linhas[-1]
    faixa = max(8, int((fundo - linhas[0]) * 0.3))
    for k in range(faixa):
        y = fundo - k
        if not 0 <= y < h:
            continue
        p = 1 - k / faixa
        if p > 0.45:
            sel = pintura[y]
            px[y, sel] = ESC[px[y, sel]]
        respingo = pintura[y] & (rng.random(w) < p * 0.07)
        px[y, respingo] = IDX["terra" if rng.random() < 0.5 else "terra_media"]


def danificar(t, nivel, semente=0):
    """Lataria ficando arrebentada conforme leva tiro (nível 0 a 3), sempre nos
    mesmos lugares para os quadros de uma etapa baterem entre si:
    1: furos de bala (miolo preto e borda de metal claro) e amassados;
    2: mais furos, chamuscado de fumaça e rachaduras;
    3: rasgos abertos com a chapa virada para fora, fuligem e tinta queimada."""
    if nivel <= 0:
        return t
    px = t.px
    h, w = px.shape
    cheio = px != VAZIO
    miolo = ndimage.binary_erosion(cheio, iterations=2)
    pintura = np.isin(px, VERDES + [int(ESC[v]) for v in VERDES] + [int(CLA[v]) for v in VERDES]) & miolo
    alvo = pintura if pintura.sum() > 40 else miolo
    if not alvo.any():
        return t
    ys_, xs_ = np.where(alvo)
    top, bot, esq, dir_ = ys_.min(), ys_.max(), xs_.min(), xs_.max()
    area = int(alvo.sum())
    # Lugares sorteados em frações da caixa do veículo: a mesma sequência em todos
    # os quadros (o dano não pula quando a carroceria balança) e em todas as etapas
    # (o dano só acumula).
    rng = np.random.default_rng(semente * 31 + 7)
    fr = rng.random((4000, 2))
    i = 0

    def pega():
        nonlocal i
        for _ in range(60):
            fy, fx = fr[i % len(fr)]
            i += 1
            y = int(top + fy * (bot - top))
            x = int(esq + fx * (dir_ - esq))
            if alvo[y, x]:
                return y, x
        return y, x

    def ok(y, x):
        return 0 <= y < h and 0 <= x < w and miolo[y, x]

    # Chamuscado (nível 2+): manchas escuras de borda irregular.
    if nivel >= 2:
        for k in range(2 if nivel == 2 else 4):
            y, x = pega()
            r = 5 + area / 700 + k
            m = t.elipse(x, y, r * 1.4, r) & cheio
            borda = m & ~ndimage.binary_erosion(m, iterations=2)
            lim = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
            sel = m & ~(borda & (lim < 0.5))
            px[sel] = ESC[px[sel]]
            nucleo = t.elipse(x, y, r * 0.85, r * 0.6) & cheio
            px[nucleo] = ESC[px[nucleo]]
            if nivel == 3:
                px[t.elipse(x, y, r * 0.45, r * 0.3) & cheio] = IDX["preto"]
    # Rachaduras (nível 2+): linha quebrada escura com brilho de um lado.
    for _ in range({1: 0, 2: 2, 3: 4}[nivel]):
        y, x = pega()
        for _ in range(int(rng.integers(5, 10))):
            if ok(y, x):
                px[y, x] = IDX["preto"]
                if ok(y, x + 1):
                    px[y, x + 1] = CLA[px[y, x + 1]]
            y += int(rng.choice([-1, 0, 1]))
            x += int(rng.choice([1, 1, 2]))
    # Amassados: meia-lua escura com brilho embaixo.
    for _ in range({1: 2, 2: 3, 3: 4}[nivel]):
        y, x = pega()
        for dx in range(-2, 3):
            if ok(y - 1 + abs(dx) // 2, x + dx):
                px[y - 1 + abs(dx) // 2, x + dx] = ESC[px[y - 1 + abs(dx) // 2, x + dx]]
            if ok(y + 1, x + dx):
                px[y + 1, x + dx] = CLA[px[y + 1, x + dx]]
    # Furos de bala.
    n_furos = int({1: 8, 2: 16, 3: 26}[nivel] * max(1.0, area / 2500))
    for _ in range(n_furos):
        y, x = pega()
        if not ok(y, x):
            continue
        px[y, x] = IDX["preto"]
        if ok(y, x + 1) and rng.random() < 0.6:
            px[y, x + 1] = IDX["preto"]
        for dy, dx in ((-1, 0), (0, -1), (-1, -1)):
            if ok(y + dy, x + dx) and px[y + dy, x + dx] != IDX["preto"]:
                px[y + dy, x + dx] = IDX["cinza_luz"]
        for dy, dx in ((1, 0), (1, 1)):
            if ok(y + dy, x + dx) and px[y + dy, x + dx] != IDX["preto"]:
                px[y + dy, x + dx] = IDX["cinza_medio"]
    # Rasgos (nível 3): buraco aberto na chapa com as pontas viradas para fora.
    if nivel == 3:
        for _ in range(2 if area < 3000 else 3):
            y, x = pega()
            r = min(4.5, 3 + area / 2500)
            buraco = t.elipse(x, y, r * 1.3, r) & miolo
            jag = rng.random(buraco.shape) < 0.25
            buraco &= ~(jag & ~ndimage.binary_erosion(buraco))
            borda = ndimage.binary_dilation(buraco) & ~buraco & cheio
            px[borda] = IDX["cinza_medio"]
            cima = borda & np.vstack([buraco[1:], np.zeros((1, w), bool)])
            px[cima] = IDX["cinza_luz"]
            px[buraco] = IDX["preto"]
            # Brasa lá dentro.
            if buraco.sum() > 6:
                ys, xs = np.where(buraco)
                k = len(ys) // 2
                px[ys[k], xs[k]] = IDX["laranja_escuro"]
            # Pontas da chapa arrancada saindo do buraco.
            for _ in range(3):
                a = rng.uniform(0, 2 * np.pi)
                xx, yy = int(x + np.cos(a) * (r + 2)), int(y + np.sin(a) * (r + 1.5))
                if ok(yy, xx):
                    px[yy, xx] = IDX["cinza_claro"]
    return t
