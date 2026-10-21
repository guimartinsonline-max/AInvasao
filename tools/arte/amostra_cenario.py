"""Amostra (para aprovar) da 1ª tela da fase 1 pintada no jeito do Metal Slug.

O que muda em relação ao cenário atual (ver ESTILO.md e o diagnóstico de 20/10):
- Cenário SEM contorno: só luz e sombra. Contorno escuro fica para personagem e inimigo.
- Uma cor de ambiente para a cena toda (sertão de tarde: tudo puxa para o ocre quente,
  sombra puxando para o roxo), com rampas próprias `amb_*`.
- Formas grandes com textura dentro (reboco, trama da taipa, telha canal, lajedo),
  em vez de muitas peças pequenas.
- Fundo enevoado e chapado (menos contraste) e uma camada de frente escura.

Uso: python3 tools/arte/amostra_cenario.py saida.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = Path(__file__).resolve().parents[2]
W, H = 548, 308
CHAO = 284  # y do chão na tela (mundo 192 + DY)

# Rampas da cena (escuro -> claro). Cada degrau gira o matiz: sombra roxa, luz amarela.
AMB = {
    "terra": ["#2b1d26", "#46292e", "#663a34", "#8a5039", "#ad6c43", "#c98a52", "#e0a866", "#f0c886"],
    "cal": ["#7a6062", "#9a7c72", "#b89a84", "#d2b796", "#e6d0aa", "#f4e4c2"],
    "telha": ["#3a1a22", "#5e2629", "#86372e", "#a84c34", "#c6663e", "#dc8650", "#eca86a"],
    "madeira": ["#24181e", "#3e2826", "#5c3c30", "#7c543c", "#9c6e4a", "#ba8a5c"],
    "verde": ["#1e2422", "#2e3a2a", "#465230", "#626c38", "#7f8642", "#a2a058", "#c4bc76"],
    "longe": ["#a08680", "#a88c82", "#b09384", "#b89a87", "#c0a18a", "#c8a88e", "#cfb092", "#d6b897", "#dcbf9c"],
    "serra": ["#9a909c", "#a297a0", "#aa9da3", "#b2a3a5", "#baa9a7", "#c2afa9", "#cab5ab", "#d1bbad"],
    "meio": ["#6a4e52", "#82604e", "#9c744e", "#b48a58", "#c8a066", "#d8b478"],
    "ceu": ["#868ca6", "#8f93a9", "#9799ab", "#a09fad", "#a9a5ae", "#b2abad", "#bab0ad", "#c3b6ac", "#cbbbab", "#d3c0ab", "#dac6ad", "#e0cbb0"],
    "nuvem": ["#6f7392", "#82829e", "#9692aa", "#aaa3b4", "#bdb3bc", "#cfc2c2", "#dfd0c8", "#ecdccc",
              "#f6e8d4", "#fcf2e0"],
    "frente": ["#1a1218", "#2a1c20", "#3c2826", "#52362c"],
    # tinta desbotada das fachadas da vila alta, na luz da tarde
    "azul": ["#3e3448", "#54485c", "#6c6274", "#887e8c", "#a49aa4", "#c0b6b8"],
    "rosa": ["#4e2830", "#6e3a3c", "#8e5250", "#ac6c62", "#c48a78", "#d8a690"],
}
RGB = {k: np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in v], np.uint8) for k, v in AMB.items()}
RNG = np.random.default_rng(7)
YY, XX = np.mgrid[0:H, 0:W]


def ruido(escala, sem=None, h=H, w=W):
    r = (RNG if sem is None else np.random.default_rng(sem)).random((h, w))
    r = ndimage.gaussian_filter(r, escala, mode="wrap")
    return (r - r.mean()) / (r.std() + 1e-9)


def fbm(escalas=(12, 5, 2), pesos=(0.6, 0.3, 0.15), sem=None):
    return sum(p * ruido(e, None if sem is None else sem + k) for k, (e, p) in enumerate(zip(escalas, pesos)))


class Tela:
    def __init__(self):
        self.img = np.zeros((H, W, 3), np.uint8)
        self.ocupado = np.zeros((H, W), bool)

    def pinta(self, mascara, rampa, luz):
        """luz 0..1 por pixel -> degrau da rampa."""
        r = RGB[rampa]
        k = np.clip((luz * len(r)).astype(int), 0, len(r) - 1)
        self.img[mascara] = r[k[mascara]]
        self.ocupado |= mascara


def limpa(m, n=1):
    """Tira pixel solto: manchas de tom em blocos limpos, como pintado à mão."""
    return ndimage.median_filter(m, size=3) if n else m


def quantiza_limpo(luz, niveis):
    """Quantiza e limpa manchas de 1 px (moda 3x3)."""
    k = np.clip((luz * niveis).astype(int), 0, niveis - 1)
    return ndimage.median_filter(k, size=3) / niveis + 0.5 / niveis


# ---------------- céu ----------------
def campo(sy, sx, sem):
    r = ndimage.gaussian_filter(np.random.default_rng(sem).random((H, W)), (sy, sx), mode="wrap")
    return (r - r.mean()) / r.std()


def ceu(t):
    """Céu do jeito dos prints (ruínas do MS): degradê longo e suave, azul-acinzentado em
    cima virando pêssego enevoado no horizonte, com faixas finas de estrato de pouco
    contraste. Nada de nuvem branca recortada: o fundo fica quieto para a frente aparecer."""
    y = np.clip(YY / 200.0, 0, 1) ** 0.9
    borda = 0.012 * campo(1.5, 18, 70)                  # degraus do degradê irregulares
    nivel = np.clip(y + borda, 0, 0.999)
    k = np.clip((nivel * 12).astype(int), 0, 11)
    # estratos: fiapos longos e finos, um tom mais escuro em cima e um mais claro perto do horizonte
    fio = campo(1.2, 45, 71) + 0.6 * campo(3, 70, 72)
    faixa = np.exp(-((YY - 40) / 28.0) ** 2) + 0.7 * np.exp(-((YY - 105) / 16.0) ** 2)
    est = (fio * faixa) > 0.9
    k = np.where(est & (YY < 80), k - 1, k)
    k = np.where(est & (YY >= 80), k + 1, k)
    k = ndimage.median_filter(np.clip(k, 0, 11), size=3)
    t.img[:] = RGB["ceu"][k]


# ---------------- serra ao longe e chapada (névoa) ----------------
def montanha(t, picos, base, rampa, claro, escuro, sem):
    """Montanhas como formas: cada pico com uma face acesa (esquerda, para o sol) e uma
    face na sombra, divididas pela crista; grotões leves; o pé some na névoa."""
    rng = np.random.default_rng(sem)
    alt = np.full(W, base, float)
    lado = np.zeros((H, W))
    for (px, ph, pw) in picos:
        perfil = base - ph * np.clip(1 - np.abs(XX[0] - px) / pw, 0, 1) ** 1.15
        perfil += 1.5 * campo(1, 3, sem + px)[0] * (perfil < base)
        alt = np.minimum(alt, perfil)
    m = YY >= alt[None, :]
    # face: pela inclinação da crista em cada coluna (subindo para a direita = virada para o sol)
    inc = -np.gradient(ndimage.uniform_filter1d(alt, 3))
    face = np.where(inc > 0.05, claro, np.where(inc < -0.05, escuro, (claro + escuro) / 2))
    # a crista desce torta pela encosta: a divisão de luz inclina para baixo
    deslocada = np.zeros((H, W))
    for dy in range(0, 60, 4):
        deslocada[np.clip(alt.astype(int) + dy, 0, H - 1), np.clip(np.arange(W) + dy // 3, 0, W - 1)] = 1
    luz = np.broadcast_to(face[None, :], (H, W)).copy()
    grotao = campo(5, 0.8, sem + 1)
    luz += 0.06 * (grotao > 1.2) * (face[None, :] > 0.5) - 0.06 * (grotao > 1.2) * (face[None, :] <= 0.5)
    prof = YY - alt[None, :]
    luz += 0.35 * np.clip((prof - 10) / 50, 0, 1) * (1 - luz)       # névoa no pé
    t.pinta(m, rampa, np.clip(luz, 0, 0.999))


def serra(t):
    montanha(t, [(40, 30, 70), (130, 44, 80), (250, 26, 60), (360, 38, 90), (470, 50, 85), (548, 30, 60)],
             150, "serra", 0.72, 0.42, 80)


def chapada(t):
    """Mesas de arenito no fundo, pintadas como planos grandes: topo aceso, face quase lisa
    (clara na quina esquerda, mais escura à direita), poucas fendas, estratos leves e
    névoa no pé. Pouco contraste, para não brigar com a frente."""
    for fileira, (base_topo, amp, sem, desl) in enumerate(((140, 14, 3, 0.10), (160, 10, 6, 0.0))):
        perfil = base_topo + amp * ruido(40, sem, 1, W)[0]
        degrau = np.round(perfil / 10) * 10
        corte = np.r_[0, np.flatnonzero(np.diff(degrau)) + 1, W]
        # encostas inclinadas entre uma mesa e outra e borda de cima gasta (não é caixa)
        topo = np.round(ndimage.uniform_filter1d(degrau, 9))
        m = YY >= topo[None, :]
        inc = -np.gradient(ndimage.uniform_filter1d(topo, 3))
        u = np.zeros(W)
        for a, b in zip(corte[:-1], corte[1:]):
            u[a:b] = (np.arange(b - a) + 0.5) / (b - a)
        prof = YY - topo[None, :]
        luz = 0.62 - 0.22 * u[None, :] + 0.12 * (u < 0.08)[None, :]       # plano da face
        luz = luz + (0.18 * (inc > 0.6) - 0.18 * (inc < -0.6))[None, :] * (prof < 40)  # encostas: luz/sombra
        fenda = (campo(14, 0.6, sem + 10) > 1.9) & (prof > 6)
        luz = np.where(fenda, luz - 0.12, luz)
        luz = np.where((prof % 19 == 0) & (prof > 4), luz - 0.06, luz)    # estratos leves
        luz = np.where(prof < 2, 0.90, luz)                                # topo
        luz = np.where((prof >= 3) & (prof < 5), luz - 0.10, luz)          # sombra da aba
        luz += 0.30 * np.clip((prof - 30) / 50, 0, 1) * (1 - luz) + desl  # névoa no pé
        t.pinta(m, "longe", np.clip(luz, 0, 0.999))


def morros(t):
    topo = 214 + 9 * ruido(30, 8, 1, W)[0]
    m = YY >= topo[None, :]
    prof = (YY - topo[None, :])
    # capim em riscos inclinados (vento), mais escuro descendo
    risco = ((XX + YY // 2 + (ruido(1.5, 9) * 2).astype(int)) % 5 == 0) & (ruido(2, 19) > -0.2)
    luz = 0.66 - 0.006 * prof + 0.12 * risco + 0.30 * (prof < 3)
    t.pinta(m, "meio", quantiza_limpo(np.clip(luz, 0, 0.999), 6))
    # moitas redondas no morro: luz cima-esquerda, base escura (sem contorno)
    rng = np.random.default_rng(11)
    for _ in range(26):
        cx = rng.uniform(0, W); r = rng.uniform(4, 9)
        cy = np.interp(cx, np.arange(W), topo) + rng.uniform(2, 20)
        d = np.hypot(XX - cx, (YY - cy) * 1.4) / r + 0.15 * ruido(1, int(cx))
        mm = (d < 1) & (YY < cy + 2)
        lz = 0.5 - 0.35 * (XX - cx) / r - 0.45 * (YY - cy) / r
        t.pinta(mm, "verde", np.clip(lz * 0.55 + 0.18, 0, 0.999))


# ---------------- casa de taipa grande ----------------
def casa(t):
    x0, x1 = 236, 432      # parede da frente
    yb, yt = CHAO, 186     # base e beiral
    lado = 30              # parede lateral em escorço (à direita, na sombra)
    # parede da frente
    m = (XX >= x0) & (XX < x1) & (YY >= yt) & (YY < yb)
    luz = 0.86 - 0.12 * (XX - x0) / (x1 - x0) + 0.03 * ruido(14, 12)
    luz = np.where(ruido(0.7, 11) > 2.3, luz - 0.2, luz)  # furinhos e pedrinhas no reboco
    racha = np.zeros((H, W), bool)
    for rx, ry, n in ((262, 196, 30), (414, 232, 22), (344, 190, 16)):
        x, y = float(rx), float(ry)
        rr = np.random.default_rng(rx)
        for _ in range(n):
            racha[int(y), int(x)] = True
            x += rr.choice([-1, 0, 1]) * 0.8; y += 1
    luz = np.where(racha, 0.35, luz)
    luz -= 0.30 * np.clip((YY - (yb - 22)) / 22, 0, 1) * (0.6 + 0.4 * ruido(3, 13) > 0)  # barro subindo
    luz -= 0.25 * np.clip(1 - (YY - yt) / 14, 0, 1)                                        # sombra do beiral
    # escorridos do beiral
    esc = (ruido(1.2, 14, 1, W)[0] > 1.4)[None, :] & (YY < yt + 30 + 20 * ruido(8, 15))
    luz = np.where(esc & m, luz - 0.18, luz)
    t.pinta(m, "cal", quantiza_limpo(np.clip(luz, 0, 0.999), 6))
    # reboco caído mostrando a trama da taipa (varas e barro)
    buraco = (fbm(sem=20) > 0.95) & m & (YY > yt + 18) & (YY < yb - 10)
    buraco = ndimage.binary_opening(buraco, np.ones((3, 3)))
    vara = ((XX % 7) < 2) | ((YY % 9) < 2)
    luz_b = np.where(vara, 0.62, 0.30) + 0.08 * ruido(1.5, 21)
    borda = buraco & ~ndimage.binary_erosion(buraco)
    luz_b = np.where(borda & ((YY > YY.mean())), 0.18, luz_b)
    t.pinta(buraco, "terra", np.clip(luz_b, 0, 0.999))
    # borda de cima do buraco: reboco grosso acende (espessura)
    lab = ndimage.binary_dilation(buraco) & ~buraco & m
    acima = np.zeros_like(buraco); acima[:-1] = buraco[1:]
    t.pinta(lab & acima, "cal", np.full((H, W), 0.999))
    # parede lateral em sombra (fundo para a direita)
    ml = (XX >= x1) & (XX < x1 + lado) & (YY >= yt + (XX - x1) * 0.25) & (YY < yb)
    luz = 0.30 + 0.06 * ruido(2.5, 16) - 0.15 * np.clip((YY - (yb - 20)) / 20, 0, 1)
    t.pinta(ml, "cal", quantiza_limpo(np.clip(luz, 0, 0.999), 6))
    # porta de tábuas (vão escuro no alto: porta entreaberta)
    px0, px1, pyt = 300, 328, 236
    mp = (XX >= px0) & (XX < px1) & (YY >= pyt) & (YY < yb)
    tab = (XX - px0) % 7
    luz = 0.45 + 0.12 * (tab == 1) - 0.25 * (tab == 6) + 0.08 * ruido(1.0, 17) + 0.1 * (YY < pyt + 3)
    luz = np.where((XX > px1 - 9), 0.06, luz)  # fresta escura
    t.pinta(mp, "madeira", np.clip(luz, 0, 0.999))
    batente = (((XX == px0 - 1) | (XX == px0 - 2) | (XX == px1)) & (YY >= pyt - 2) & (YY < yb)) | \
              ((YY >= pyt - 3) & (YY < pyt) & (XX >= px0 - 2) & (XX <= px1))
    t.pinta(batente, "madeira", np.full((H, W), 0.25))
    # janela com folha aberta
    jx0, jx1, jy0, jy1 = 360, 384, 212, 236
    mj = (XX >= jx0) & (XX < jx1) & (YY >= jy0) & (YY < jy1)
    luz = np.where(XX < jx0 + 8, 0.02, 0.15)  # escuro de dentro, luz entrando de lado
    t.pinta(mj, "madeira", luz)
    fol = (XX >= jx1) & (XX < jx1 + 10) & (YY >= jy0 - 1 + (XX - jx1) // 4) & (YY < jy1 + 1 - (XX - jx1) // 4)
    t.pinta(fol, "madeira", 0.5 + 0.2 * ((XX - jx1) % 5 == 0) - 0.15 * (XX - jx1) / 10)
    peit = (XX >= jx0 - 2) & (XX < jx1 + 2) & (YY >= jy1) & (YY < jy1 + 3)
    t.pinta(peit, "cal", np.where(YY == jy1, 0.99, 0.55))
    t.pinta(peit & (YY == jy1 + 2), "cal", np.full((H, W), 0.2))
    # telhado de telha canal: canais verticais (cilindros) em fileiras sobrepostas
    ry0 = 132
    beiral_esq, beiral_dir = x0 - 14, x1 + lado + 4
    mt = (YY >= ry0 + 0) & (YY < yt + 6)
    inclin = (XX >= beiral_esq + (yt + 6 - YY) * 0.35) & (XX < beiral_dir - (yt + 6 - YY) * 0.1)
    mt &= inclin
    u = (XX - beiral_esq) % 9 / 9.0                  # posição dentro do canal
    fil = (YY - ry0) // 11                           # fileira
    v = ((YY - ry0) % 11) / 11.0
    cil = np.cos((u - 0.38) * np.pi)                 # luz cima-esquerda no canal
    luz = 0.30 + 0.55 * cil - 0.22 * v + 0.10 * ruido(1.2, 30)
    luz = np.where(v > 0.86, 0.10, luz)              # sombra da fileira de cima
    luz = np.where((u > 0.88) | (u < 0.05), 0.12, luz)  # junta entre canais
    luz += 0.08 * (fil % 2)
    musgo = (fbm(sem=31) > 1.15) & mt
    t.pinta(mt, "telha", quantiza_limpo(np.clip(luz, 0, 0.999), 7))
    t.pinta(musgo, "verde", np.clip(0.35 + 0.2 * ruido(1, 32), 0, 0.999))
    # telha quebrada / faltando: mostra ripa e o escuro
    falta = (fbm((4, 2), (0.7, 0.3), sem=33) > 1.6) & mt & (YY < yt - 4)
    t.pinta(falta, "madeira", np.where((YY % 6) < 2, 0.35, 0.03))
    # beiral: boca das telhas (meias-luas) e sombra embaixo
    boca = (YY >= yt + 4) & (YY < yt + 8) & inclin.any(axis=0)[None, :] & (XX >= beiral_esq) & (XX < beiral_dir)
    t.pinta(boca, "telha", np.where(np.hypot(u - 0.45, (YY - yt - 4) / 6) < 0.35, 0.05, 0.45))
    # cumeeira
    cume = (YY >= ry0 - 4) & (YY < ry0 + 2) & (XX >= beiral_esq + 50) & (XX < beiral_dir - 16)
    t.pinta(cume, "telha", np.where(YY < ry0 - 1, 0.9, 0.35))
    # alpendre à esquerda: puxado de palha/telha sobre forquilhas
    ax0, ax1 = 168, x0 - 4
    for px in (172, 214):
        mpost = (XX >= px) & (XX < px + 6) & (YY >= 214) & (YY < yb)
        luz = 0.25 + 0.5 * np.cos(((XX - px) / 6 - 0.3) * np.pi) + 0.08 * ruido(1, 40 + px)
        t.pinta(mpost, "madeira", np.clip(luz, 0, 0.999))
        forq = (np.abs(XX - px - 3) - (214 - YY) * 0.6 < 2) & (np.abs(XX - px - 3) - (214 - YY) * 0.6 > -1) & (YY >= 206) & (YY < 216)
        t.pinta(forq, "madeira", np.full((H, W), 0.5))
    mal = (YY >= 196 + (XX - ax0) * -0.05) & (YY < 208) & (XX >= ax0 - 6) & (XX < ax1 + 8)
    luz = 0.55 + 0.25 * ((XX + YY // 2) % 4 == 0) - 0.3 * (YY > 205) + 0.1 * ruido(1.2, 41)
    t.pinta(mal, "madeira", np.clip(luz, 0, 0.999))
    viga = (YY >= 207) & (YY < 211) & (XX >= ax0 - 2) & (XX < ax1 + 4)
    t.pinta(viga, "madeira", np.where(YY == 207, 0.75, 0.3))
    # sombra do alpendre no chão e na parede
    return (ax0, ax1)


# ---------------- árvore da caatinga e mandacaru ----------------
def galho(t, x, y, ang, comp, larg, prof, sem):
    rng = np.random.default_rng(sem)
    pts = []
    for k in range(int(comp)):
        ang += rng.normal(0, 0.10)
        x += np.cos(ang); y += np.sin(ang)
        pts.append((x, y, larg * (1 - 0.6 * k / comp)))
    for (px, py, r) in pts:
        m = np.hypot(XX - px, YY - py) <= r
        nx = (XX - px) / max(r, 0.5)
        luz = 0.48 - 0.45 * nx + 0.14 * np.sin((XX - px) * 2.2 + (YY - py) * 0.3)
        t.pinta(m, "madeira", np.clip(luz, 0, 0.999))
    if prof > 0:
        for d in (-0.5, 0.45):
            galho(t, x, y, ang + d + rng.normal(0, 0.15), comp * 0.65, larg * 0.6, prof - 1, sem * 3 + int(d * 10))
    return pts


def arvore(t, x, chao):
    galho(t, x, chao, -np.pi / 2 - 0.15, 56, 7.5, 3, 51)
    galho(t, x + 2, chao - 30, -np.pi / 2 + 0.7, 40, 3.5, 2, 77)
    # copa em cachos: muitos tufos pequenos, cada um com luz própria (cima-esquerda),
    # os de trás mais escuros. Assim lê como folhagem, não como mancha.
    rng = np.random.default_rng(5)
    nuvens = ((x - 30, chao - 104, 17), (x + 2, chao - 122, 21), (x + 32, chao - 108, 16),
              (x - 8, chao - 96, 13), (x + 52, chao - 84, 11))
    tufos = []
    for cx, cy, r in nuvens:
        for _ in range(int(r * 1.3)):
            a = rng.uniform(0, 2 * np.pi); d = r * np.sqrt(rng.uniform(0, 1))
            tufos.append((cx + d * np.cos(a), cy + d * np.sin(a) * 0.8, rng.uniform(3.5, 6.5)))
    tufos.sort(key=lambda p: p[1] - p[0] * 0.3)  # de trás (baixo-direita) para a frente
    for k, (cx, cy, r) in enumerate(tufos):
        d = np.hypot(XX - cx, (YY - cy) * 1.2) / r
        m = d < 1
        lz = 0.62 - 0.35 * (XX - cx) / r - 0.45 * (YY - cy) / r
        lz -= 0.25 * (1 - k / len(tufos))  # os de trás no escuro
        t.pinta(m, "verde", np.clip(lz, 0.02, 0.999))


def mandacaru(t, x, chao, alt=78):
    def braco(x0, y0, y1, r):
        m = (np.abs(XX - x0) <= r) & (YY >= y0) & (YY < y1)
        topo = np.hypot(XX - x0, (YY - y0) * 1.0) <= r
        m |= topo & (YY < y0 + r)
        u = (XX - x0) / r
        gomo = np.cos(u * np.pi * 2.0)  # gomos verticais
        luz = 0.48 - 0.38 * u + 0.16 * gomo
        luz = np.where(np.abs(np.sin(u * np.pi * 2.0)) < 0.25, luz - 0.2, luz)
        spines = ((YY + (XX * 3)) % 6 == 0) & (np.abs(gomo) > 0.9)
        luz = np.where(spines, 0.95, luz)
        t.pinta(m, "verde", np.clip(luz, 0, 0.999))
    braco(x, chao - alt, chao, 7)
    # braços: cotovelo e subida
    for dx, yb, yt in ((-15, chao - 34, chao - 64), (15, chao - 44, chao - 70)):
        cot = (YY >= yb - 5) & (YY < yb + 4) & (XX >= min(x, x + dx)) & (XX < max(x, x + dx))
        t.pinta(cot, "verde", np.clip(0.45 + 0.25 * ((yb - YY) / 5) - 0.2 * (dx > 0), 0, 0.999))
        braco(x + dx, yt, yb + 4, 5)


# ---------------- chão: terra batida e lajedo ----------------
def chao(t):
    topo = CHAO - 2 + (1.5 * ruido(8, 60, 1, W)[0]).round()
    m = YY >= topo[None, :]
    luz = 0.64 - 0.30 * np.clip((YY - CHAO) / 24, 0, 1) + 0.05 * ruido(6, 61)
    luz = np.where(YY < topo[None, :] + 2, 0.88, luz)
    t.pinta(m, "terra", quantiza_limpo(np.clip(luz, 0, 0.999), 8))
    rng = np.random.default_rng(63)
    # pedras encaixadas no chão em corte: cada uma com topo aceso, base escura e sombra
    for _ in range(70):
        px = rng.uniform(0, W); py = rng.uniform(CHAO + 2, H + 2)
        rx = rng.uniform(2.5, 7) * (1 + (py - CHAO) / 30); ry = rx * rng.uniform(0.45, 0.7)
        d = np.hypot((XX - px) / rx, (YY - py) / ry) + 0.12 * ruido(0.8, int(px))
        sombra = (np.hypot((XX - px - 1.5) / rx, (YY - py - 1.5) / ry) < 1) & (YY > py)
        t.img[sombra & m] = (t.img[sombra & m] * 0.7).astype(np.uint8)
        pm = d < 1
        lz = 0.55 - 0.35 * (XX - px) / rx - 0.5 * (YY - py) / ry
        t.pinta(pm, "terra", quantiza_limpo(np.clip(lz, 0, 0.999), 8))
    # lajedo: placas grandes de arenito aflorando, com face de cima clara, frente e racha
    for (lx, lw, lh) in ((20, 70, 10), (118, 44, 7), (448, 96, 13)):
        top = CHAO - lh
        mt = (XX >= lx) & (XX < lx + lw) & (YY >= top) & (YY < top + 4) & \
             (np.abs(XX - lx - lw / 2) < lw / 2 - (top + 4 - YY))
        mf = (XX >= lx) & (XX < lx + lw) & (YY >= top + 4) & (YY < CHAO + 6)
        canto = (XX - lx < 3) & (YY > top + 4 + (XX - lx))
        mf &= ~canto
        t.pinta(mt, "terra", np.clip(0.9 + 0.08 * ruido(1, lx), 0, 0.999))
        luz = 0.52 + 0.08 * np.sin((XX - lx) / 3.0) - 0.18 * ((YY - top) / (lh + 6))
        racha = (np.abs(XX - lx - lw * 0.37 - 3 * np.sin(YY / 3.0)) < 0.8)
        luz = np.where(racha, 0.12, luz)
        luz = np.where(XX > lx + lw - 6, luz - 0.15, luz)
        luz = np.where((YY - top) % 5 == 0, luz - 0.08, luz)  # camadas do arenito
        t.pinta(mf, "terra", np.clip(luz, 0, 0.999))
    # tufos de capim seco no pé das coisas (folhas finas, ponta clara)
    for _ in range(40):
        cx = rng.uniform(0, W); alt = rng.uniform(4, 9)
        for k in range(5):
            ang = -np.pi / 2 + (k - 2) * 0.35
            for s_ in range(int(alt)):
                px, py = int(cx + np.cos(ang) * s_), int(CHAO + np.sin(ang) * s_)
                if 0 <= px < W and 0 <= py < H:
                    t.img[py, px] = RGB["terra"][min(7, 3 + int(4 * s_ / alt))]


def sombras_contato(t, faixas):
    """Sombra no chão ao pé das peças (para nada flutuar)."""
    for x0, x1 in faixas:
        m = (XX >= x0) & (XX < x1) & (YY >= CHAO - 1) & (YY < CHAO + 3)
        t.img[m] = (t.img[m] * 0.72).astype(np.uint8)


# ---------------- frente (parallax 1,1): xique-xique e capim escuros ----------------
def frente(t):
    for cx, alt in ((14, 40), (536, 52), (60, 22), (500, 26)):
        for k in range(7):
            ang = -np.pi / 2 + (k - 3) * 0.22
            for s in range(alt):
                px = cx + np.cos(ang) * s + 1.5 * np.sin(s / 5 + k)
                py = H + 4 + np.sin(ang) * s
                m = np.hypot(XX - px, YY - py) < max(1.2, 3.2 - s / alt * 2)
                t.pinta(m, "frente", np.where(XX < px, 0.6, 0.2) + 0.15 * (s > alt * 0.7))


def personagem(t, folha, quadro, fw, fh, x, pe_y, pe_x):
    img = np.array(Image.open(RAIZ / f"assets/sprites/{folha}.png").convert("RGBA"))
    q = img[:, quadro * fw:(quadro + 1) * fw]
    y0, x0 = pe_y - q.shape[0] + (fh - pe_y if False else 0), x
    for yy in range(q.shape[0]):
        for xx in range(q.shape[1]):
            if q[yy, xx, 3] > 0:
                ty, tx = CHAO - pe_y + yy, x - pe_x + xx
                if 0 <= ty < H and 0 <= tx < W:
                    t.img[ty, tx] = q[yy, xx, :3]


def montar():
    t = Tela()
    ceu(t)
    serra(t)
    chapada(t)
    morros(t)
    arvore(t, 128, CHAO)
    mandacaru(t, 500, CHAO)
    casa(t)
    chao(t)
    sombras_contato(t, [(236, 462), (120, 136), (493, 508), (172, 220)])
    personagem(t, "lampiao", 0, 60, 72, 92, 63, 14)
    personagem(t, "volante", 0, 52, 46, 250, 45, 26)
    frente(t)
    return Image.fromarray(t.img)


if __name__ == "__main__":
    montar().save(sys.argv[1] if len(sys.argv) > 1 else "amostra.png")
