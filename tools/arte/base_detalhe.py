"""Peças do acampamento da base no nível de detalhe do Metal Slug (estudo: MS2 missão 3,
MS6 missão 2 com o acampamento de torres e paliçada).

O que o Metal Slug faz e as peças daqui seguem:
- cada material tem a própria rampa de 5 a 7 tons (madeira, lona, corda, ferro, terra),
  com luz de cima à esquerda calculada pela forma (cilindro, plano caído, dobra);
- textura em tudo: veio e rachadura na madeira, casca, nó; costura, remendo, mancha d'água,
  dobra puxada pela corda e barra suja de barro na lona; farpa e brilho no arame;
- contato com o chão escurecido, sombra projetada e pequenos objetos de apoio
  (estaca, corda com esticador, saco de areia, caixote, garrafão);
- letreiro grande e pintado à mão, com sombra, que dá para ler (fonte 5x7).

As cores de crepúsculo (mad_n*, lona_n*, lona_q*, oliva_n*, chao_n*, corda_n*) já são da
hora do acampamento: as peças daqui não passam pelo anoitecer() por troca de cor.
"""
import math

import numpy as np
from scipy import ndimage

from motor import IDX, VAZIO, Tela
from fase2 import ruido, pintar_niveis

MAD = ["mad_n1", "mad_n2", "mad_n3", "mad_n4", "mad_n5", "mad_n6"]
LONA = ["lona_n1", "lona_n2", "lona_n3", "lona_n4", "lona_n5", "lona_n6"]
QUENTE = ["mad_n3", "lona_q1", "lona_q2", "lona_q3", "lona_q4"]
OLIVA = ["mad_n1", "oliva_n1", "oliva_n2", "oliva_n3", "oliva_n4", "oliva_n5"]
CORDA = ["mad_n2", "corda_n1", "corda_n2", "corda_n3"]
FERRO = ["preto", "sombra", "sombra_media", "cinza_escuro", "cinza_medio", "cinza_luz"]
CHAO = ["chao_n1", "chao_n2", "chao_n3", "chao_n4", "chao_n5", "chao_n6"]
VERMELHO = ["mad_n1", "vermelho_esc", "vermelho_medio", "vermelho"]
LUZ = np.array([-0.62, -0.55, 0.56])
LUZ = LUZ / np.linalg.norm(LUZ)


def pintar(t, m, v, rampa):
    pintar_niveis(t, m, v, rampa)


# ------------------------------------------------------------------ fonte de letreiro
FONTE5 = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00000", "00100"],
    "0": ["01110", "10011", "10101", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    " ": ["00000"] * 7,
}
ACENTOS = {"Ó": ("O", "agudo"), "Á": ("A", "agudo"), "É": ("E", "agudo"), "Í": ("I", "agudo"),
           "Ã": ("A", "til"), "Õ": ("O", "til"), "Ç": ("C", "cedilha")}


def largura_texto(texto, esp=1):
    return len(texto) * (5 + esp) - esp


def letreiro(t, texto, x, y, cor, sombra="mad_n1", esp=1, gasto=0.0, semente=0):
    """Escreve em letras 5x7 pintadas à mão, com sombra embaixo à direita. Os acentos
    ficam nas 2 linhas acima (y-2). gasto: fração da tinta descascada."""
    rng = np.random.default_rng(semente)
    pts = []
    cx = x
    for ch in texto:
        base, ac = ACENTOS.get(ch, (ch, None))
        g = FONTE5.get(base, FONTE5[" "])
        for j, l in enumerate(g):
            for i, b in enumerate(l):
                if b == "1":
                    pts.append((cx + i, y + j))
        if ac == "agudo":
            pts += [(cx + 2, y - 1), (cx + 3, y - 2)]
        elif ac == "til":
            pts += [(cx + 1, y - 1), (cx + 2, y - 2), (cx + 3, y - 1), (cx + 4, y - 2)]
        elif ac == "cedilha":
            pts += [(cx + 2, y + 7), (cx + 1, y + 8)]
        cx += 5 + esp
    if sombra:
        for (px, py) in pts:
            t.ponto(px + 1, py + 1, sombra)
    for (px, py) in pts:
        if gasto and rng.random() < gasto:
            continue
        t.ponto(px, py, cor)


# ------------------------------------------------------------------ madeira roliça
def cilindro(t, x0, y0, x1, y1, r0, r1=None, rampa=MAD, semente=0, casca=True, rachas=2, nos=1,
             topo_cortado=False, escurecer=0.0):
    """Tora/mourão roliço de (x0,y0) a (x1,y1): luz de cilindro, veio e casca ao longo do
    eixo, rachaduras, nós e, se pedido, o topo cortado com os anéis."""
    r1 = r0 if r1 is None else r1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-9
    ax, ay = dx / L, dy / L
    nx, ny = -ay, ax  # perpendicular
    px, py = t.xx - x0, t.yy - y0
    s = px * ax + py * ay
    d = px * nx + py * ny
    r = r0 + (r1 - r0) * np.clip(s / L, 0, 1)
    m = (s >= -0.5) & (s <= L + 0.5) & (np.abs(d) <= r)
    if not m.any():
        return m
    u = np.clip(d / np.maximum(r, 0.5), -1, 1)
    # Normal do cilindro: lateral (u na direção perpendicular) + frente.
    nz = np.sqrt(np.clip(1 - u * u, 0, 1))
    lum = (u * nx * LUZ[0] + u * ny * LUZ[1] + nz * LUZ[2])
    v = 0.12 + np.clip(lum, 0, 1) * 0.78
    # Veio: listras finas ao longo do eixo, quebradas.
    rng = np.random.default_rng(semente)
    ncol = 9
    G = ndimage.gaussian_filter(rng.standard_normal((int(L) + 3, ncol)), (2.5, 0.6))
    G /= G.std() + 1e-9
    si = np.clip(s, 0, L + 1).astype(int)
    ui = np.clip(((u + 1) / 2 * (ncol - 1)).round(), 0, ncol - 1).astype(int)
    v = v + G[si, ui] * (0.09 if casca else 0.05) - escurecer
    pintar(t, m, v, rampa)
    # Rachaduras escuras compridas ao longo do eixo.
    for _ in range(rachas):
        uu = rng.uniform(-0.5, 0.4)
        a = rng.uniform(0.05, 0.5) * L
        b = a + rng.uniform(0.25, 0.5) * L
        for ss in np.arange(a, min(b, L), 0.7):
            rr = r0 + (r1 - r0) * ss / L
            w = uu + math.sin(ss / 5 + uu * 9) * 0.12
            qx, qy = x0 + ax * ss + nx * w * rr, y0 + ay * ss + ny * w * rr
            t.ponto(qx, qy, rampa[0])
            if rng.random() < 0.5:
                t.ponto(qx - nx * 0.9 * np.sign(LUZ[0] * nx + 1e-9), qy, rampa[min(3, len(rampa) - 1)])
    # Nós: olho escuro com borda clara.
    for _ in range(nos):
        ss = rng.uniform(0.2, 0.85) * L
        uu = rng.uniform(-0.3, 0.3)
        rr = r0 + (r1 - r0) * ss / L
        qx, qy = x0 + ax * ss + nx * uu * rr, y0 + ay * ss + ny * uu * rr
        e = t.elipse(qx, qy, max(1.0, rr * 0.45), max(1.0, rr * 0.35)) & m
        t.px[e] = IDX[rampa[1]]
        t.ponto(qx, qy, rampa[0])
        t.ponto(qx - 1, qy - 1, rampa[-2])
    if topo_cortado:
        cx_, cy_ = x1, y1
        e = t.elipse(cx_, cy_, r1 + 0.2, max(1.0, r1 * 0.45))
        t.px[e] = IDX[rampa[-1]]
        t.px[t.elipse(cx_, cy_, r1 * 0.55, max(0.6, r1 * 0.25))] = IDX[rampa[-2]]
        t.ponto(cx_, cy_, rampa[2])
    return m


def corda(t, x0, y0, x1, y1, flecha=1.0, rampa=CORDA, torcida=True):
    """Corda de sisal: 1 px com a torção marcada (claro/escuro alternando) e caimento."""
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.3) + 2
    pts = []
    for k in range(n + 1):
        f = k / n
        x = x0 + (x1 - x0) * f
        y = y0 + (y1 - y0) * f + math.sin(f * math.pi) * flecha
        pts.append((x, y))
    for k, (x, y) in enumerate(pts):
        cor = rampa[2] if (not torcida or (k // 2) % 2 == 0) else rampa[1]
        t.ponto(x, y, cor)
    for k, (x, y) in enumerate(pts[::3]):
        t.ponto(x, y - 1, rampa[3]) if torcida and k % 3 == 0 else None
    return pts


def amarracao(t, x, y, r=2.0):
    """Voltas de corda amarrando duas peças, com as pontas soltas."""
    for k in range(-1, 2):
        yy = y + k * 1.4
        for xx in np.arange(x - r - 0.5, x + r + 1, 0.5):
            f = (xx - (x - r)) / (2 * r)
            t.ponto(xx, yy + f * 1.2, CORDA[2] if f < 0.6 else CORDA[1])
        t.ponto(x - r - 0.5, yy, CORDA[0])
    t.ponto(x + r + 1, y + 2.5, CORDA[2])
    t.ponto(x + r + 1.5, y + 3.8, CORDA[1])


def estaca(t, x, chao, h=7, semente=0):
    """Estaca de madeira cravada no chão (com a cabeça amassada de marreta)."""
    cilindro(t, x, chao, x - 0.6, chao - h, 1.4, 1.1, semente=semente, rachas=0, nos=0, topo_cortado=True)
    t.ponto(x - 2, chao, "chao_n1")
    t.ponto(x + 2, chao, "chao_n1")


def esticador(t, pts, f=0.55):
    """Esticador de madeira (taquinho com dois furos) na corda."""
    x, y = pts[int(len(pts) * f)]
    t.chapado(t.retangulo(x - 1.5, y - 1, 4, 2.5), MAD[3])
    t.ponto(x - 1, y - 1, MAD[5])
    t.ponto(x + 2, y + 1, MAD[1])


# ------------------------------------------------------------------ objetos de apoio
def garrafao(t, x, chao, semente=0):
    """Garrafão de vidro num cesto de vime (reagente do laboratório), líquido verde."""
    corpo = t.elipse(x, chao - 7, 5.5, 6.5)
    v = 0.55 - (t.xx - x) / 12 - (t.yy - (chao - 7)) / 18
    pintar(t, corpo, v, ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz"])
    t.chapado(t.retangulo(x - 1.5, chao - 17, 3, 4), "cinza_luz")
    t.ponto(x - 1, chao - 17, "branco")
    t.chapado(t.retangulo(x - 2, chao - 18, 4, 1.2), "mad_n3")
    # Cesto de vime trançado na metade de baixo.
    cesto = corpo & (t.yy > chao - 8)
    vv = 0.5 + ((t.xx.astype(int) + t.yy.astype(int)) % 3 == 0) * 0.25 - (t.xx - x) / 14
    pintar(t, cesto, vv, MAD)
    t.ponto(x - 3, chao - 11, "branco")
    t.ponto(x - 3, chao - 10, "alien_luz")


def caixote(t, x, chao, w=20, h=14, texto="", semente=0, rampa=MAD):
    """Caixote de tábuas com face de cima em perspectiva, tábuas, pregos e estêncil."""
    topo_h = 3
    frente = t.retangulo(x, chao - h, w, h)
    rng = np.random.default_rng(semente)
    v = 0.48 + ruido(t.h, t.w, (0.5, 3), semente) * 0.07
    for k in range(1, 3):
        v = np.where(np.abs(t.yy - (chao - h + k * h / 3)) < 0.6, 0.18, v)
    v = np.where((t.xx < x + 1.2) | (t.xx > x + w - 1.2), 0.62, v)
    pintar(t, frente, v, rampa)
    t.px[frente & (t.xx > x + w - 1.2)] = IDX[rampa[1]]
    tampa = t.poligono([(x, chao - h), (x + 2, chao - h - topo_h), (x + w + 2, chao - h - topo_h), (x + w, chao - h)])
    pintar(t, tampa & ~frente, 0.8 + ruido(t.h, t.w, (0.4, 3), semente + 1) * 0.06, rampa)
    for (px, py) in ((x + 1, chao - h + 1), (x + w - 2, chao - h + 1), (x + 1, chao - 2), (x + w - 2, chao - 2)):
        t.ponto(px, py, "cinza_luz")
    if texto:
        lx = x + w / 2 - largura_texto(texto) / 2
        letreiro(t, texto, int(lx), int(chao - h + (h - 7) / 2 + 1), "corda_n3", sombra="mad_n1", gasto=0.04,
                 semente=semente)
    # Contorno escuro na silhueta.
    m = frente | tampa
    borda = ndimage.binary_dilation(m) & ~m & (t.px == VAZIO)
    t.px[borda] = IDX["mad_n1"]
    _ = rng


def saco(t, x, chao, w=16, h=8, semente=0):
    """Saco de areia estufado com costura e orelha amarrada."""
    m = t.elipse(x + w / 2, chao - h / 2, w / 2, h / 2)
    m |= t.retangulo(x + 2, chao - h + 1, w - 4, h - 1)
    v = 0.6 - (t.yy - (chao - h)) / h * 0.4 - (t.xx - x) / w * 0.18 + ruido(t.h, t.w, 0.8, semente) * 0.05
    pintar(t, m, v, ["corda_n1", "chao_n5", "corda_n2", "chao_n6", "corda_n3"])
    for xx in range(int(x + 3), int(x + w - 3), 2):
        t.ponto(xx, chao - h + 2, "corda_n1")
    t.ponto(x + w - 1, chao - h / 2 - 1, "corda_n3")
    t.ponto(x + w, chao - h / 2 - 2, "corda_n2")
    borda = ndimage.binary_dilation(m) & ~m & (t.px == VAZIO)
    t.px[borda] = IDX["mad_n1"]


def lampiao(t, x, y, aceso=True):
    """Lampião de querosene de lata pendurado: alça, chaminé de vidro com a chama."""
    t.linha(x - 2, y - 3, x, y - 5, "cinza_escuro")
    t.linha(x + 2, y - 3, x, y - 5, "cinza_escuro")
    t.chapado(t.retangulo(x - 2.5, y - 3, 5, 1.5), "cinza_medio")
    vidro = t.elipse(x, y + 0.5, 2.4, 3)
    t.chapado(vidro, "amarelo_claro" if aceso else "sombra_media")
    if aceso:
        t.chapado(t.elipse(x, y + 1, 0.9, 1.6), "branco")
    t.chapado(t.retangulo(x - 3, y + 3, 6, 2), "cinza_escuro")
    t.ponto(x - 2, y + 3, "cinza_luz")


# ------------------------------------------------------------------ barraca do laboratório
def barraca_lab(semente=0):
    """Barraca-laboratório de lona (190x104): parede e teto com caimento entre os paus,
    costuras, remendo, manchas d'água, cruz vermelha pintada e descascada, sanefa recortada,
    porta com as abas enroladas mostrando o laboratório aceso por dentro (mesa com
    frascos verdes, garrafão, vidro com um bicho conservado, lampião), janela de tela com
    luz, cordas com esticadores até as estacas, barra suja de barro, sacos de areia e o
    letreiro LABORATÓRIO pendurado."""
    W, H = 196, 108
    t = Tela(W, H)
    rng = np.random.default_rng(semente)
    chao = H - 1
    xa, xb = 30, 166            # parede
    beiral = 54                 # altura do beiral
    cume = 13
    ra, rb = 46, 150            # pontas do cume
    paus = (ra, (ra + rb) / 2, rb)
    porta = (110, 136)
    # ---------- teto
    yy, xx = t.yy, t.xx
    f_esq = np.clip((xx - (ra - (ra - (xa - 6)) * (yy - cume) / (beiral - cume))), 0, None)
    borda_e = (xa - 6) + (ra - (xa - 6)) * (beiral - yy) / (beiral - cume)
    borda_d = (xb + 6) + (rb - (xb + 6)) * (beiral - yy) / (beiral - cume)
    # Cume com caimento entre os paus; beiral também cai entre as cordas.
    def caida(x, pontos, amp):
        x = np.asarray(x, float)
        out = np.zeros_like(x)
        for a, b in zip(pontos[:-1], pontos[1:]):
            sel = (x >= a) & (x <= b)
            out[sel] = np.sin((x[sel] - a) / (b - a) * math.pi) * amp
        return out
    cordas_beiral = (xa - 6, 72, 104, 142, xb + 6)
    cume_y = cume + caida(xx, paus, 2.2)
    beiral_y = beiral + caida(xx, cordas_beiral, 1.6)
    teto = (yy >= cume_y) & (yy <= beiral_y) & (xx >= borda_e) & (xx <= borda_d)
    # Luz: plano inclinado para a frente (claro), mais escuro embaixo, caimento entre paus.
    prof = (yy - cume_y) / (beiral_y - cume_y + 1e-9)
    entre = np.zeros_like(xx)
    for a, b in zip(paus[:-1], paus[1:]):
        sel = (xx >= a) & (xx <= b)
        entre[sel] = np.sin((xx[sel] - a) / (b - a) * math.pi)
    v = 0.86 - prof * 0.3 - entre * np.sin(prof * math.pi) * 0.34 - (xx - W / 2) / W * 0.2
    # Luz batendo forte perto de cada pau do cume (lona esticada) e brilho na aresta do cume.
    for px_ in paus:
        v = v + np.clip(1 - np.abs(xx - px_) / 7, 0, 1) * (1 - prof) * 0.12
    v = np.where(yy < cume_y + 1.5, v + 0.1, v)
    # Rugas puxadas das cordas do beiral, curtas e tortas, subindo em leque.
    rugas = np.zeros_like(xx, dtype=bool)
    for cxb in cordas_beiral[1:-1]:
        for k, alvo in enumerate((cxb - 14, cxb + 2, cxb + 15)):
            comp = rng.uniform(0.22, 0.42)
            fase = rng.uniform(0, 6)
            for f in np.linspace(0, comp, 50):
                rx = cxb + (alvo - cxb) * f + math.sin(f * 14 + fase) * 1.1
                ry = beiral - (beiral - cume) * f
                ix, iy = int(round(rx)), int(round(ry))
                if 0 <= ix < W and 0 <= iy < H:
                    rugas[iy, ix] = True
    # Vincos grandes descendo de cada pau do cume até o beiral (lado claro e lado escuro).
    for px_ in paus:
        for alvo in (px_ - 26, px_ + 26):
            if not (xa - 6 <= alvo <= xb + 6):
                continue
            ax_, ay_ = alvo - px_, beiral - cume
            Lv = math.hypot(ax_, ay_)
            nxv, nyv = -ay_ / Lv, ax_ / Lv
            if nxv > 0:
                nxv, nyv = -nxv, -nyv
            sv = ((xx - px_) * ax_ + (yy - cume) * ay_) / Lv
            dv = (xx - px_) * nxv + (yy - cume) * nyv
            perto = (sv > 2) & (sv < Lv * 0.8)
            forca = np.clip(1 - sv / Lv, 0, 1) * 0.22
            v = np.where(perto & (dv > -2.2) & (dv <= 0), v + forca, v)
            v = np.where(perto & (dv > 0) & (dv < 2.5), v - forca * 1.1, v)
    v = np.where(rugas, v - 0.14, v)
    v = np.where(np.roll(rugas, 1, 1) & ~rugas, v + 0.08, v)
    # Costura horizontal no meio do teto (linha escura + linha clara embaixo).
    cost_y = cume_y + (beiral_y - cume_y) * 0.52
    v = np.where(np.abs(yy - cost_y) < 0.5, v - 0.2, v)
    v = np.where(np.abs(yy - cost_y - 1) < 0.5, v + 0.1, v)
    v = v + ruido(H, W, (0.6, 2.5), semente) * 0.035
    # Manchas d'água: borrão mais escuro com borda.
    for (mx, my, rx_, ry_) in ((126, 44, 8, 3), (74, 22, 5, 2.5)):
        e = ((xx - mx) / rx_) ** 2 + ((yy - my) / ry_) ** 2 + ruido(H, W, 1.2, mx) * 0.3
        v = np.where(e < 1, v - 0.06, v)
        v = np.where((e >= 1) & (e < 1.3), v - 0.12, v)
    pintar(t, teto, v, LONA)
    # Remendo costurado no canto esquerdo do teto.
    rem = t.retangulo(54, 36, 12, 9) & teto
    pintar(t, rem, 0.42 + ruido(H, W, 0.6, 9) * 0.04 - (yy - 36) / 40, LONA)
    for k in range(0, 12, 2):
        t.ponto(54 + k, 35, "lona_n2")
        t.ponto(54 + k, 45, "lona_n2")
    for k in range(0, 9, 2):
        t.ponto(53, 36 + k, "lona_n2")
        t.ponto(66, 36 + k, "lona_n2")
    # Cruz vermelha pintada num círculo branco, com a dobra do teto passando por cima.
    cx, cy = 98, 33
    circ = t.elipse(cx, cy, 11, 9) & teto
    tinta = ruido(H, W, 0.7, 31) > -1.3
    pintar(t, circ & tinta, v + 0.2, LONA)
    cruz = (t.retangulo(cx - 2, cy - 7, 4, 14) | t.retangulo(cx - 7, cy - 2, 14, 4)) & teto
    pintar(t, cruz & (ruido(H, W, 0.6, 33) > -1.3), v * 0.9, VERMELHO)
    # ---------- sanefa recortada ao longo do beiral (com sombra embaixo dela na parede)
    sanefa = (yy > beiral_y) & (yy <= beiral_y + 5 + (np.sin(xx / 4.5 * math.pi) > 0) * 1.5) & \
             (xx >= xa - 6) & (xx <= xb + 6)
    # ---------- parede
    hem = chao - 2 - caida(xx, np.arange(xa, xb + 1, 22.6), 1.4)
    parede = (xx >= xa) & (xx <= xb) & (yy > beiral_y) & (yy <= hem)
    dobras = np.sin(xx / 3.1 + ruido(1, W, 6, 5)[0][None, :] * 2) * np.clip((yy - beiral) / 46, 0, 1)
    vp = 0.62 + dobras * 0.13 - (xx - xa) / (xb - xa) * 0.16
    # Dobras puxadas pelas estacas (V invertido subindo de cada estaca).
    for px_ in np.arange(xa, xb + 1, 22.6):
        for k in range(1, 12):
            for sgn in (-1, 1):
                ix, iy = int(round(px_ + sgn * k * 0.7)), int(round(chao - 3 - k))
                if 0 <= ix < W:
                    vp[iy, ix] -= 0.12
    # Costuras verticais.
    for cxs in (64, 98, 148):
        vp = np.where(np.abs(xx - cxs) < 0.5, vp - 0.2, vp)
        vp = np.where(np.abs(xx - cxs - 1) < 0.5, vp + 0.08, vp)
    # Sombra da sanefa e do beiral na parede.
    vp = np.where(yy < beiral_y + 10, vp - 0.2, vp)
    vp = np.where(yy < beiral_y + 7.5, vp - 0.14, vp)
    # Barro subindo da barra (manchado).
    barro = (yy > hem - 7 + ruido(H, W, (1, 3), 41) * 2.2)
    vp = vp + ruido(H, W, (0.6, 2), semente + 3) * 0.035
    pintar(t, parede, vp, LONA)
    pintar(t, parede & barro, vp * 0.9 + 0.05, CHAO)
    for _ in range(26):
        sx, sy = rng.uniform(xa, xb), rng.uniform(chao - 16, chao - 8)
        t.ponto(sx, sy, "chao_n4" if rng.random() < 0.5 else "chao_n3")
    # Sanefa por cima.
    vs = 0.86 - (yy - beiral_y) / 7 * 0.3 + np.sin(xx / 4.5 * math.pi) * 0.06
    vs = np.where(np.abs(yy - beiral_y - 0.5) < 0.6, 0.2, vs)
    pintar(t, sanefa, vs, LONA)
    fundo_san = sanefa & ~np.roll(sanefa, -1, 0)
    t.px[fundo_san] = IDX["lona_n1"]
    # ---------- janela de tela com luz
    jx, jy, jw, jh = 42, 76, 20, 13
    jan = t.retangulo(jx, jy, jw, jh)
    t.chapado(jan, "lona_q1")
    t.chapado(t.retangulo(jx + 2, jy + 2, jw - 4, jh - 5), "lona_q2")
    t.chapado(t.elipse(jx + jw * 0.45, jy + jh * 0.45, 4, 3), "lona_q3")
    for k in range(jx, jx + jw, 2):
        t.linha(k, jy, k, jy + jh - 1, "lona_q1")
    t.chapado(t.retangulo(jx + 12, jy + 3, 2, 8), "mad_n2")  # vulto de vidraria
    t.chapado(t.elipse(jx + 13, jy + 3, 2, 1.4), "mad_n2")
    for (a, b) in ((jx - 1, jx + jw), ):
        t.linha(a, jy - 1, b, jy - 1, "lona_n2")
        t.linha(a, jy + jh, b, jy + jh, "lona_n2")
        t.linha(a, jy - 1, a, jy + jh, "lona_n2")
        t.linha(b, jy - 1, b, jy + jh, "lona_n2")
    rolo = t.capsula(jx - 1, jy - 3, jx + jw, jy - 3, 1.8)
    pintar(t, rolo, 0.75 - (yy - (jy - 4)) / 5, LONA)
    for k in (jx + 3, jx + jw - 4):
        corda(t, k, jy - 5, k, jy - 1, 0)
    # ---------- porta aberta com o laboratório aceso dentro
    pa, pb = porta
    vao = (xx >= pa) & (xx <= pb) & (yy > beiral_y + 4) & (yy <= hem)
    dentro = 0.35 + (1 - np.hypot((xx - (pa + pb) / 2) / 16, (yy - (beiral + 14)) / 22)) * 0.55
    pintar(t, vao, dentro, ["mad_n1", "mad_n2", "lona_q1", "lona_q2", "lona_q3"])
    # Prateleira com vidros.
    t.chapado(t.retangulo(pa + 2, beiral + 17, pb - pa - 4, 1.2), "mad_n2")
    for k, cor in enumerate(("alien_medio", "lona_q4", "alien", "vermelho_medio", "alien_luz")):
        bx = pa + 4 + k * 4.3
        t.chapado(t.retangulo(bx, beiral + 12 + (k % 2), 2.4, 5 - (k % 2)), cor)
        t.ponto(bx, beiral + 12 + (k % 2), "branco")
    # Vidro grande com um bicho conservado (olho boiando no líquido verde).
    vx_, vy_ = pb - 7, chao - 21
    t.chapado(t.retangulo(vx_ - 4, vy_ - 9, 8, 11), "alien_esc")
    t.chapado(t.retangulo(vx_ - 3, vy_ - 7, 6, 8), "alien_medio")
    t.chapado(t.elipse(vx_, vy_ - 3, 2.2, 2.2), "lona_n6")
    t.ponto(vx_ + 0.5, vy_ - 3, "preto")
    t.linha(vx_ - 1, vy_ - 1, vx_ - 2, vy_ + 1, "vermelho_medio")
    t.chapado(t.retangulo(vx_ - 4, vy_ - 10, 8, 1.4), "cinza_medio")
    t.linha(vx_ - 3, vy_ - 7, vx_ - 3, vy_, "alien_luz")
    # Mesa com frascos e o lampião em cima.
    t.chapado(t.retangulo(pa + 1, chao - 14, 17, 2), "mad_n4")
    t.linha(pa + 1, chao - 14, pa + 17, chao - 14, "mad_n5")
    t.chapado(t.retangulo(pa + 2, chao - 12, 2, 10), "mad_n2")
    t.chapado(t.retangulo(pa + 15, chao - 12, 2, 10), "mad_n2")
    t.chapado(t.elipse(pa + 6, chao - 17, 2, 2.4), "alien")
    t.chapado(t.retangulo(pa + 5.5, chao - 22, 1.2, 4), "cinza_luz")
    t.ponto(pa + 5, chao - 18, "alien_brilho")
    t.chapado(t.retangulo(pa + 9, chao - 19, 2, 5), "lona_q4")
    lampiao(t, pa + 14, chao - 19)
    # Abas da porta amarradas para os lados (triângulos dobrados) e o rolo em cima.
    for lado, x0_ in ((-1, pa), (1, pb)):
        aba = t.poligono([(x0_, beiral_y.min() + 6), (x0_ + lado * 9, beiral + 9), (x0_ + lado * 4, chao - 22),
                          (x0_, chao - 10)])
        va = 0.66 + np.sin((xx - x0_) * lado / 2.2) * 0.07 - (yy - beiral) / 120
        pintar(t, aba, va, LONA)
        t.linha(x0_, beiral + 6, x0_, chao - 10, "lona_n1")
        t.ponto(x0_ + lado * 4, chao - 22, "lona_n2")
        corda(t, x0_ + lado * 2, beiral + 22, x0_ + lado * 8, beiral + 20, 0.6)
    rolo = t.capsula(pa - 2, beiral + 6, pb + 2, beiral + 6, 2.4)
    pintar(t, rolo, 0.78 - (yy - (beiral + 4)) / 6, LONA)
    t.linha(pa - 1, beiral + 8, pb + 1, beiral + 8, "lona_n2")
    # ---------- paus: pontas do cume com a ponteira e os montantes da porta
    for px_ in (ra, rb):
        cilindro(t, px_, cume + 3, px_, cume - 6, 1.5, 1.2, semente=int(px_), rachas=0, nos=0)
        t.chapado(t.elipse(px_, cume - 7, 1.8, 1.4), "cinza_medio")
        t.ponto(px_ - 0.6, cume - 7.6, "cinza_luz")
    for px_ in porta:
        cilindro(t, px_, chao - 1, px_, beiral + 4, 1.3, 1.2, semente=int(px_) + 5, rachas=1, nos=0)
    # ---------- contorno escuro da silhueta da barraca
    corpo = t.px != VAZIO
    borda = ndimage.binary_dilation(corpo) & ~corpo
    t.px[borda] = IDX["mad_n1"]
    # ---------- cordas até as estacas (dos dois lados e da frente) com esticador
    for (x0_, y0_, x1_, y1_, fl) in ((xa - 6, beiral + 1, 6, chao, 2.0), (xb + 6, beiral + 1, W - 7, chao, 2.0),
                                     (72, beiral + 4, 64, chao, 0.5), (142, beiral + 4, 152, chao, 0.5)):
        pts = corda(t, x0_, y0_, x1_, y1_, fl)
        esticador(t, pts, 0.62)
        estaca(t, x1_, chao, semente=int(x1_))
    for px_ in np.arange(xa, xb + 1, 22.6):
        estaca(t, px_, chao, 5, semente=int(px_) + 1)
    # ---------- letreiro LABORATÓRIO pendurado no beiral
    _placa_lab(t, 34, beiral + 8)
    # ---------- sacos de areia na quina e garrafões ao lado da porta
    saco(t, xa - 12, chao, 16, 8, semente=3)
    saco(t, xa - 4, chao, 15, 8, semente=4)
    saco(t, xa - 9, chao - 7, 15, 7, semente=5)
    garrafao(t, pb + 9, chao, semente=2)
    garrafao(t, pb + 19, chao, semente=3)
    caixote(t, 68, chao, 38, 15, "FRÁGIL", semente=6)
    return t


def _placa_lab(t, x, y):
    """Tábua com LABORATÓRIO pintado em branco, pendurada por dois arames."""
    txt = "LABORATÓRIO"
    w = largura_texto(txt) + 8
    h = 13
    p = Tela(w, h)
    m = p.retangulo(0, 0, w, h)
    v = 0.55 + ruido(h, w, (0.4, 3.5), 12) * 0.08
    v = np.where(np.abs(p.yy - h / 2) < 0.5, 0.2, v)          # junta entre as duas tábuas
    v = np.where(p.yy < 1.2, 0.85, v)
    v = np.where(p.yy > h - 1.2, 0.25, v)
    pintar(p, m, v, MAD)
    letreiro(p, txt, 4, 4, "lona_n6", sombra="mad_n1")
    for (a, b) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
        p.ponto(a, b, "cinza_luz")
    p.contorno("mad_n1")
    t.colar(p, x, y)
    for k in (x + 5, x + w - 6):
        t.linha(k, y - 7, k, y, "cinza_escuro")
        t.ponto(k, y - 7, "cinza_luz")


# ------------------------------------------------------------------ cerca de arame farpado
def cerca(w, h=46, semente=0, placas=(("ÁREA MILITAR", 40),)):
    """Cerca da base: mourões de aroeira tortos e rachados com o topo cortado, escora em
    diagonal a cada tanto, quatro fios de arame farpado com caimento, farpas e brilho,
    latas de alarme penduradas, trapo preso no arame e placa pregada num mourão."""
    t = Tela(w, h + 2)
    chao = h + 1
    rng = np.random.default_rng(semente)
    xs = [6]
    while xs[-1] < w - 10:
        xs.append(xs[-1] + int(rng.integers(30, 40)))
    topos = {}
    for k, x in enumerate(xs):
        incl = rng.uniform(-1.6, 1.6)
        alt = h - rng.integers(0, 6)
        topos[x] = (x + incl, chao - alt)
        cilindro(t, x, chao, x + incl, chao - alt, 2.4, 1.9, semente=semente + k, rachas=2, nos=1,
                 topo_cortado=True)
        t.chapado(t.elipse(x, chao, 4, 1.2), "chao_n1")
        if k % 4 == 2:
            # Escora: tora mais fina em diagonal até o chão.
            cilindro(t, x + incl * 0.6, chao - alt * 0.55, x + 16, chao, 1.4, 1.6, semente=semente + 50 + k,
                     rachas=1, nos=0)
            amarracao(t, x + incl * 0.6, chao - alt * 0.55, 2.4)
    # Fios de arame farpado em quatro alturas.
    for j, hy in enumerate((0.2, 0.42, 0.64, 0.86)):
        for a, b in zip(xs[:-1], xs[1:]):
            ya = chao - (chao - topos[a][1]) * hy
            yb = chao - (chao - topos[b][1]) * hy
            n = b - a
            for k in range(n + 1):
                f = k / n
                x = a + k
                y = ya + (yb - ya) * f + math.sin(f * math.pi) * (1.4 + j * 0.2)
                t.ponto(x, y, "cinza_escuro")
                if k % 3 == 0:
                    t.ponto(x, y - 1, "cinza_luz") if k % 6 == 0 else None
                if k % 7 == 3:  # farpa (X pequeno)
                    t.ponto(x - 1, y - 1, "cinza_medio")
                    t.ponto(x + 1, y + 1, "sombra")
                    t.ponto(x + 1, y - 1, "cinza_medio")
                    t.ponto(x - 1, y + 1, "sombra")
            amarracao(t, a + topos[a][0] - a, ya, 1.2) if j == 3 else None
    # Latas de alarme penduradas no fio do meio.
    for a, b in zip(xs[:-1], xs[1:]):
        if rng.random() < 0.45:
            x = a + (b - a) * rng.uniform(0.3, 0.7)
            y = chao - (chao - topos[a][1]) * 0.64 + 1.6
            t.linha(x, y, x, y + 3, "cinza_escuro")
            lata = t.retangulo(x - 2, y + 3, 4, 5)
            pintar(t, lata, 0.6 - (t.xx - x) / 6, FERRO)
            t.ponto(x - 1, y + 3, "aco_brilho")
            t.ponto(x, y + 8, "mad_n1")
    # Trapo de farda preso no arame de cima.
    x = xs[min(2, len(xs) - 1)] + 14
    y = chao - (chao - topos[xs[min(2, len(xs) - 1)]][1]) * 0.86 + 1
    trapo = t.poligono([(x, y), (x + 6, y + 1), (x + 4, y + 5), (x + 6, y + 9), (x + 1, y + 6)])
    pintar(t, trapo, 0.55 - (t.yy - y) / 20, OLIVA)
    # Placas pregadas.
    for txt, xp in placas:
        k = int(np.argmin([abs(x - xp) for x in xs]))
        x0 = int(xs[k] - largura_texto(txt) / 2 - 4)
        pw = largura_texto(txt) + 8
        p = Tela(pw, 13)
        m = p.retangulo(0, 0, pw, 13)
        v = 0.52 + ruido(13, pw, (0.4, 3), 3) * 0.08
        v = np.where(p.yy < 1.2, 0.8, v)
        pintar(p, m, v, ["vermelho_esc", "vermelho_esc", "vermelho_medio", "vermelho_medio", "vermelho"])
        letreiro(p, txt, 4, 4, "lona_n6", sombra="mad_n1")
        p.ponto(2, 2, "cinza_luz")
        p.ponto(pw - 3, 2, "cinza_luz")
        p.contorno("mad_n1")
        t.colar(p, x0, int(chao - h * 0.62))
    return t
