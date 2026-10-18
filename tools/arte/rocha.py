"""Rocha e chão no nível de detalhe do Metal Slug: paredão de arenito feito de
blocos (cada um com volume próprio, juntas escuras, rachaduras, líquen e moitas
nas bordas) e chão em corte com estratos, pedras enterradas e lábio iluminado.
Usado por tools/arte/cenario.py (paredões) e tools/arte/fase1.py (chão).
"""
import numpy as np
from scipy import ndimage

from motor import BAYER4, IDX, VAZIO, Tela

ARENITO = ["terra_escura", "terra", "terra_media", "barro", "areia_media", "areia", "areia_luz"]
ARENITO_QUENTE = ["terra_escura", "terra", "terra_media", "barro", "barro", "areia_media", "areia_luz"]
ARENITO_FRIO = ["sombra_media", "terra_escura", "terra", "terra_media", "barro", "areia_media", "areia"]
PEDRA_CHAO = ["sombra", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]
PEDRA_TERRA = ["sombra", "terra_escura", "terra", "terra_media", "barro", "areia_media", "areia"]
MOITA = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru"]

NEBLINA = {
    "sombra": "azul_sombra", "sombra_media": "azul_sombra",
    "terra_escura": "terra", "terra": "terra_media", "caatinga_esc": "caatinga_media",
}

# Escurecer um tom (sombra fria nas faces viradas para a direita).
ESCURECE = {
    "areia_luz": "areia_media", "areia": "barro", "areia_media": "terra_media", "barro": "terra",
    "terra_media": "terra_escura", "laranja_escuro": "terra_escura", "terra": "terra_escura",
    "terra_escura": "azul_sombra", "sombra_media": "sombra", "areia_clara": "areia_media",
}


def ruido(h, w, sigma, semente):
    rng = np.random.default_rng(semente)
    r = ndimage.gaussian_filter(rng.standard_normal((h, w)), sigma, mode="wrap")
    return r / (r.std() + 1e-9)


def _volume_em(t, linhas, cols, mascara, rampa, **kw):
    """Roda Tela.volume num recorte (colunas podem dar a volta na borda) e cola de volta."""
    sub = Tela(len(cols), len(linhas))
    sub.volume(mascara, rampa, linha=False, **kw)
    alvo = t.px[np.ix_(linhas, cols)]
    alvo[mascara] = sub.px[mascara]
    t.px[np.ix_(linhas, cols)] = alvo


def escurecer(t, mascara, passos=1):
    """Um tom mais escuro em cada pixel da máscara (troca simultânea, sem cascata)."""
    for _ in range(passos):
        antes = t.px.copy()
        for de, para in ESCURECE.items():
            t.px[mascara & (antes == IDX[de])] = IDX[para]


def paredoes(L=768, h=130, semente=11):
    """Paredões de arenito: massas de rocha irregulares (cada uma com volume
    próprio), juntas que somem aqui e ali, rachaduras, líquen e moitas na beira.
    Emenda nas bordas (repete sem costura)."""
    t = Tela(L, h)
    rng = np.random.default_rng(semente)
    # Perfil das mesas (topo dos paredões).
    perfil = np.full(L, float(h))
    x = 0
    while x < L:
        largura = int(rng.integers(80, 170))
        topo = int(rng.integers(6, 46))
        rampa = int(rng.integers(3, 9))
        for k in range(largura):
            borda = min(k, largura - 1 - k)
            y = topo + max(0, rampa - borda) * 2.2 + rng.uniform(0, 1.0)
            perfil[(x + k) % L] = min(perfil[(x + k) % L], y)
        x += largura - int(rng.integers(0, 24))
    perfil = ndimage.uniform_filter1d(perfil, 3, mode="wrap")
    yy = t.yy - 0.5
    xx = t.xx - 0.5
    massa = yy >= perfil[None, :]
    # Coordenadas entortadas por ruído: as juntas ficam tortas como pedra de verdade.
    ux = xx + ruido(h, L, (3, 5), semente + 1) * 2.2
    uy = yy + ruido(h, L, (4, 3), semente + 2) * 2.2 + ndimage.gaussian_filter1d(
        rng.standard_normal(L), 14, mode="wrap")[None, :] * 7
    # Cursos (camadas de sedimento) de alturas variadas.
    cortes = [-40.0]
    while cortes[-1] < h + 20:
        cortes.append(cortes[-1] + float(rng.integers(10, 26)))
    cortes = np.array(cortes)
    curso = np.searchsorted(cortes, uy) - 1
    rotulo = np.zeros((h, L), dtype=np.int64)
    for k in range(len(cortes)):
        sel = curso == k
        if not sel.any():
            continue
        juntas = []
        x0 = float(rng.uniform(0, 40))
        while x0 < L:
            juntas.append(x0)
            x0 += float(rng.integers(18, 72))
        juntas = np.array(juntas)
        incl = rng.uniform(-0.6, 0.6)
        u = (ux[sel] + incl * (uy[sel] - cortes[k])) % L
        bloco = np.searchsorted(juntas, u) % len(juntas)
        # Algumas juntas somem: o bloco se funde com o vizinho.
        fundir = rng.random(len(juntas)) < 0.3
        alvo = np.arange(len(juntas))
        for j in range(len(juntas)):
            if fundir[j]:
                alvo[j] = alvo[j - 1]
        rotulo[sel] = k * 1000 + alvo[bloco]
    rotulo[~massa] = -1
    # Juntas: onde o rótulo muda para a direita ou para baixo.
    junta = massa & ((rotulo != np.roll(rotulo, -1, axis=1)) | (rotulo != np.roll(rotulo, -1, axis=0)))
    t.px[massa] = IDX["terra_escura"]
    for r in np.unique(rotulo[massa]):
        m = (rotulo == r) & ~junta
        cols = np.where(m.any(0))[0]
        if len(cols) == 0:
            continue
        desloca = L // 2 if (cols[0] == 0 and cols[-1] == L - 1) else 0
        mm = np.roll(m, desloca, axis=1)
        cc = np.where(mm.any(0))[0]
        rr = np.where(mm.any(1))[0]
        c0, c1 = max(0, cc[0] - 2), min(L, cc[-1] + 3)
        r0, r1 = max(0, rr[0] - 2), min(h, rr[-1] + 3)
        sub_m = mm[r0:r1, c0:c1]
        sub = Tela(c1 - c0, r1 - r0)
        tom = [ARENITO, ARENITO, ARENITO_QUENTE, ARENITO_FRIO][int(rng.integers(0, 4))]
        sub.volume(sub_m, tom, achatado=float(rng.uniform(2.5, 5.0)), suave=1.0, linha=False,
                   ambiente=float(rng.uniform(0.14, 0.3)), textura=0.1, semente=int(r) + semente)
        cheio = np.roll(t.px, desloca, axis=1)
        alvo_px = cheio[r0:r1, c0:c1]
        alvo_px[sub_m] = sub.px[sub_m]
        cheio[r0:r1, c0:c1] = alvo_px
        t.px = np.roll(cheio, -desloca, axis=1)
    # Juntas: as de baixo de cada bloco mais fundas (sombra), as laterais mais leves.
    lateral = massa & (rotulo != np.roll(rotulo, -1, axis=1)) & (rotulo == np.roll(rotulo, -1, axis=0))
    t.px[lateral] = IDX["terra"]
    # Faces viradas para a direita: sombra fria pontilhada.
    desce = np.gradient(perfil) > 0.7
    face = ndimage.binary_dilation(np.repeat(desce[None, :], h, 0), structure=np.ones((1, 9)), origin=(0, -4))
    lim = np.tile(BAYER4, (h // 4 + 1, L // 4 + 1))[:h, :L]
    escurecer(t, face & massa & (yy > perfil[None, :] + 1), 1)
    escurecer(t, face & massa & (yy > perfil[None, :] + 1) & (lim < 0.3), 1)
    # Rachaduras finas com a borda esquerda iluminada.
    for _ in range(30):
        cx_ = int(rng.integers(0, L))
        y = perfil[cx_] + rng.integers(3, 50)
        for _k in range(int(rng.integers(5, 16))):
            if 0 <= int(y) < h and massa[int(y), cx_ % L]:
                t.px[int(y), cx_ % L] = IDX["terra_escura"]
                if massa[int(y), (cx_ - 1) % L]:
                    t.px[int(y), (cx_ - 1) % L] = IDX["areia"]
            y += 1
            if rng.random() < 0.3:
                cx_ += int(rng.choice((-1, 1)))
    # Líquen: manchas pequenas esverdeadas, mais no alto e nas juntas.
    lq = (ruido(h, L, 1.0, semente + 3) > 2.1) & massa & (yy < perfil[None, :] + 50)
    t.px[lq] = IDX["caatinga_media"]
    # Borda de cima iluminada.
    topo = massa & ~np.roll(massa, 1, axis=0)
    t.px[topo] = IDX["areia_clara"]
    t.px[np.roll(topo, 1, axis=0) & massa] = IDX["areia_luz"]
    # Moitas da caatinga na beira de cima e nas saliências.
    x = 0
    while x < L:
        x += int(rng.integers(10, 46))
        larg = int(rng.integers(4, 12))
        for k in range(larg):
            xc = (x + k) % L
            yt = int(perfil[xc])
            alt = int(2 + 2.5 * np.sin(np.pi * (k + 0.5) / larg) + rng.uniform(0, 1.2))
            for d in range(alt):
                y = yt - d + 1
                if 0 <= y < h:
                    cor = MOITA[min(4, 1 + d + (k < larg / 2))] if d < alt - 1 else "caatinga_esc"
                    t.px[y, xc] = IDX[cor]
            if 0 <= yt - alt < h:
                t.px[yt - alt + 1, xc] = IDX["sombra"]
    # Pé do paredão: pedras caídas (tálus) e névoa quente subindo do chão.
    for _ in range(L // 12):
        pw, ph = int(rng.integers(5, 14)), int(rng.integers(3, 8))
        px0 = int(rng.integers(0, L))
        py0 = h - 20 - ph + int(rng.integers(0, 8))
        cols = (px0 + np.arange(pw)) % L
        linhas = np.arange(max(0, py0), min(h, py0 + ph))
        cy = np.arange(len(linhas))[:, None] + 0.5
        cx = np.arange(pw)[None, :] + 0.5
        m = ((cx - pw / 2) / (pw / 2)) ** 2 + ((cy - ph * 0.6) / (ph * 0.6)) ** 2 < 1
        _volume_em(t, linhas, cols, m, PEDRA_TERRA, achatado=2.0, suave=0.6, ambiente=0.2)
    for y in range(h - 16, h):
        f = (y - (h - 16) + 0.5) / 16
        sel = massa[y] & (lim[y] < f * 0.7)
        t.px[y, sel] = IDX["areia"]
    # Perspectiva aérea: de longe as sombras clareiam e puxam para o azul do céu,
    # e o contraste cai (o primeiro plano fica mais forte que o fundo).
    antes = t.px.copy()
    for de, para in NEBLINA.items():
        t.px[antes == IDX[de]] = IDX[para]
    return t


def chao(w, h=26, semente=0, queimado=False):
    """Chão em corte: lábio iluminado, terra em estratos com pontilhado, pedras
    enterradas com volume, pedrisco, raízes e rachaduras, escurecendo para baixo."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    rampa = (["marrom_noite", "sombra", "terra_escura", "terra", "terra_media", "barro"] if queimado
             else ["marrom_noite", "terra_escura", "terra", "terra_media", "barro", "areia_media"])
    n = ndimage.gaussian_filter(rng.standard_normal((h, w)), (1.2, 6), mode="wrap")
    n /= n.std() + 1e-9
    yy = t.yy - 0.5
    lim = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    # Estratos: faixas onduladas alternando tons; escurece com a profundidade.
    faixa = np.floor((yy + n * 1.6) / 5).astype(int)
    alterna = np.where(faixa % 2 == 0, 0.0, -0.7)
    nivel = (len(rampa) - 1.2) - yy / h * (len(rampa) - 1.5) + alterna + n * 0.25
    nivel = np.floor(nivel + (lim - 0.5) * 0.8).clip(0, len(rampa) - 1).astype(int)
    t.px[:, :] = np.array([IDX[c] for c in rampa])[nivel]
    # Pedras enterradas: grandes no fundo, menores em cima, algumas cortadas pela borda de baixo.
    for k in range(w // 13):
        grande = rng.random() < 0.35
        pw = int(rng.integers(10, 22) if grande else rng.integers(4, 10))
        ph = int(rng.integers(6, 11) if grande else rng.integers(3, 6))
        px0 = rng.uniform(-pw / 2, w - pw / 2)
        py0 = rng.uniform(h * 0.45, h - ph * 0.5) if grande else rng.uniform(4, h - ph)
        tm = Tela(pw, ph)
        cy, cx = tm.yy, tm.xx
        ang = np.arctan2(cy - ph / 2, cx - pw / 2)
        borda = 0.92 + 0.08 * np.sin(ang * 3 + rng.uniform(0, 6))
        m = ((cx - pw / 2) / (pw / 2)) ** 2 + ((cy - ph / 2) / (ph / 2)) ** 2 < borda ** 2
        tm.volume(m, PEDRA_CHAO if rng.random() < 0.6 else PEDRA_TERRA, achatado=min(pw, ph) * 0.4,
                  suave=0.8, ambiente=0.15, textura=0.15, semente=k + semente, linha=False)
        tm.contorno("sombra")
        x0, y0 = int(px0), int(py0)
        for yy_ in range(ph):
            for xx_ in range(pw):
                v = tm.px[yy_, xx_]
                X, Y = x0 + xx_, y0 + yy_
                if v != VAZIO and 0 <= X < w and 2 < Y < h:
                    t.px[Y, X] = v
    # Pedrisco e grãos claros.
    for _ in range(w // 3):
        x, y = int(rng.uniform(0, w)), int(rng.integers(3, h))
        cor = rng.choice(["cinza_luz", "cinza_medio", "areia_luz", "terra_escura"])
        if t.px[y, x] not in (IDX["sombra"], IDX["cinza_escuro"]):
            t.px[y, x] = IDX[cor]
    # Raízes finas descendo do topo.
    for _ in range(w // 34):
        x, y = rng.uniform(0, w), 3
        for _k in range(int(rng.integers(5, 13))):
            nx, ny = x + rng.uniform(-1.4, 1.4), y + 1
            if 0 <= int(nx) < w and int(ny) < h:
                t.px[int(ny), int(nx)] = IDX["couro_escuro" if not queimado else "preto"]
            x, y = nx, ny
    # Rachaduras com borda clara.
    for _ in range(w // 26):
        x, y = rng.uniform(0, w), 2
        for _k in range(int(rng.integers(3, 9))):
            nx, ny = x + rng.uniform(-1, 1), y + 1
            X, Y = int(nx) % w, int(ny)
            if Y < h:
                t.px[Y, X] = IDX["sombra"]
                t.px[Y, (X + 1) % w] = IDX[rampa[-2]]
            x, y = nx, ny
    # Lábio de cima: crosta clara, uma linha de sombra logo abaixo e calombos.
    crosta = ["areia_clara", "areia_luz", "areia"] if not queimado else ["terra_media", "terra", "terra_escura"]
    t.px[0, :] = IDX[crosta[0]]
    t.px[1, :] = np.where(lim[1] < 0.5, IDX[crosta[1]], IDX[crosta[2]])
    t.px[2, :] = np.where(lim[2] < 0.25, IDX[crosta[2]], IDX[rampa[1]])
    for _ in range(w // 9):
        x = int(rng.integers(0, w - 4))
        bw = int(rng.integers(2, 6))
        t.px[3, x:x + bw] = IDX[rampa[1]]
    return t
