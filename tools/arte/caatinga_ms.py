"""Trecho 1 da fase 1 (caatinga) no jeito do Metal Slug aprovado em 20/10 (ESTILO.md, Cenários).

Mesmo jeito da amostra aprovada (`amostra_cenario.py`), agora em todas as camadas do trecho:
- sem contorno: só luz e sombra (contorno é de personagem, inimigo e item);
- uma cor de ambiente (sertão de tarde: ocre quente, sombra arroxeada), rampas `amb_*`;
- formas grandes com textura dentro (casa de taipa, lajedo, barranco, curral);
- céu e serra quietos e enevoados, camada de frente escura.

O trecho vai do começo da fase até CAATINGA_FIM (x do mundo). Cada camada antiga da fase 1
deixa de desenhar as peças desse pedaço (`antigo()`), e o que é contínuo (chão, morros,
chapada) se mistura no estilo antigo em manchas, sem corte reto (`emendar()`).
O céu, as nuvens e a serra são da fase toda e passam inteiros para o jeito novo.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

from amostra_cenario import AMB, RGB

CAATINGA_FIM = 2980          # x do mundo onde começa a passagem para a vila
TELA_W, TELA_H, DY = 548, 308, 92

# Todas as cores das rampas da cena, para encaixar qualquer pixel numa cor com nome.
NOMES_AMB = [f"amb_{r}_{k + 1}" for r, cores in AMB.items() for k in range(len(cores))]
TODAS = np.concatenate([RGB[r] for r in AMB]).astype(int)


# Câmera mais à direita ainda dentro da caatinga: a borda direita da tela chega no começo da vila.
CAMERA_FIM = CAATINGA_FIM - TELA_W
# Perto: para logo antes da 1ª casa antiga da vila (a borda dela só aparece no último pixel da tela).
_LIMITE_FIXO = {0.75: 2360}


def limite(fator):
    """x da camada até onde vai o jeito novo: tudo o que a câmera mostra enquanto está na
    caatinga (até CAMERA_FIM) já é do jeito novo; a emenda com o antigo fica fora da tela
    e só passa a aparecer quando se entra na vila."""
    if fator in _LIMITE_FIXO:
        return _LIMITE_FIXO[fator]
    return int(CAMERA_FIM * fator + TELA_W)


def antigo(x, fator):
    """A peça antiga nessa posição da camada continua (fica depois do trecho)."""
    return x >= limite(fator)


# ---------------------------------------------------------------- quadro RGBA
class Quadro:
    def __init__(self, w, h):
        self.w, self.h = int(w), int(h)
        self.img = np.zeros((self.h, self.w, 3), np.uint8)
        self.a = np.zeros((self.h, self.w), bool)
        self.yy, self.xx = np.mgrid[0:self.h, 0:self.w]

    def pinta(self, m, rampa, luz):
        r = RGB[rampa]
        luz = np.broadcast_to(np.asarray(luz, float), m.shape)
        k = np.clip((luz * len(r)).astype(int), 0, len(r) - 1)
        self.img[m] = r[k[m]]
        self.a |= m

    def colar(self, p, x, y):
        x, y = int(round(x)), int(round(y))
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + p.w), min(self.h, y + p.h)
        if x1 <= x0 or y1 <= y0:
            return
        sub = p.a[y0 - y:y1 - y, x0 - x:x1 - x]
        self.img[y0:y1, x0:x1][sub] = p.img[y0 - y:y1 - y, x0 - x:x1 - x][sub]
        self.a[y0:y1, x0:x1] |= sub

    def assentar(self, p, x, chao, afundar=1, sombra=True):
        """Peça em pé no chão (linha `chao`), com sombra de contato embaixo."""
        if sombra:
            self.sombra(x + p.w / 2, chao + 1, p.w * 1.05)
        self.colar(p, x, chao - p.h + afundar)

    def sombra(self, cx, cy, larg, alt=3.0):
        for f, k in ((1.0, 1), (0.6, 1)):
            m = (((self.xx - cx) / (larg / 2 * f)) ** 2 + ((self.yy - cy) / (alt * f)) ** 2 < 1) & self.a
            self.img[m] = escurecer(self.img[m], k)

    def rgba(self):
        out = np.zeros((self.h, self.w, 4), np.uint8)
        out[..., :3] = encaixar(self.img)
        out[..., 3] = self.a * 255
        return out


def encaixar(img):
    """Leva cada cor para a cor de rampa mais próxima (nenhuma cor sem nome)."""
    flat = img.reshape(-1, 3).astype(int)
    unicas, inv = np.unique(flat, axis=0, return_inverse=True)
    d = ((unicas[:, None, :] - TODAS[None, :, :]) ** 2).sum(-1)
    return TODAS[d.argmin(1)][inv.ravel()].reshape(img.shape).astype(np.uint8)


# Para cada cor das rampas: a mesma rampa um degrau abaixo (sombra de contato sem preto).
_DEGRAU = {}
for _r, _c in RGB.items():
    for _k, _cor in enumerate(_c):
        _DEGRAU[tuple(_cor)] = _c[max(0, _k - 1)]


def escurecer(px, passos=1):
    px = encaixar(px.reshape(-1, 1, 3)).reshape(-1, 3)
    for _ in range(passos):
        px = np.array([_DEGRAU.get(tuple(c), c) for c in px], np.uint8).reshape(-1, 3)
    return px


def ruido(h, w, escala, sem, wrap=True):
    r = np.random.default_rng(sem).random((int(h), int(w)))
    r = ndimage.gaussian_filter(r, escala, mode="wrap" if wrap else "reflect")
    return (r - r.mean()) / (r.std() + 1e-9)


def fbm(h, w, sem, escalas=(12, 5, 2), pesos=(0.6, 0.3, 0.15)):
    return sum(p * ruido(h, w, e, sem + k) for k, (e, p) in enumerate(zip(escalas, pesos)))


def quantiza_limpo(luz, niveis):
    k = np.clip((luz * niveis).astype(int), 0, niveis - 1)
    return ndimage.median_filter(k, size=3) / niveis + 0.5 / niveis


def nevoa(q, k, rampa="longe"):
    """Distância: puxa a peça para a cor da névoa (menos contraste, mais claro)."""
    alvo = RGB[rampa][-2].astype(float)
    q.img[q.a] = encaixar(((q.img[q.a] * (1 - k) + alvo * k)).reshape(-1, 1, 3).astype(np.uint8)).reshape(-1, 3)
    return q


# ---------------------------------------------------------------- céu, nuvens e serra (fase toda)
def _campo(h, w, sy, sx, sem):
    r = ndimage.gaussian_filter(np.random.default_rng(sem).random((h, w)), (sy, sx), mode="wrap")
    return (r - r.mean()) / r.std()


def ceu():
    """Degradê longo e suave (azul-acinzentado em cima, pêssego enevoado no horizonte),
    igual à amostra aprovada; os fiapos de estrato ficam nas nuvens, que andam."""
    h, w = TELA_H, TELA_W
    yy = np.mgrid[0:h, 0:w][0]
    y = np.clip(yy / 200.0, 0, 1) ** 0.9
    nivel = np.clip(y + 0.012 * _campo(h, w, 1.5, 18, 70), 0, 0.999)
    k = ndimage.median_filter(np.clip((nivel * 12).astype(int), 0, 11), size=3)
    return Image.fromarray(RGB["ceu"][k])


def nuvens(L=768, h=110, y0=6):
    """Fiapos finos de estrato, um tom acima ou abaixo do céu (nada de nuvem branca)."""
    yy = np.mgrid[0:h, 0:L][0] + y0
    k = np.clip((np.clip(yy / 200.0, 0, 1) ** 0.9 * 12).astype(int), 0, 11)
    fio = _campo(h, L, 1.2, 45, 71) + 0.6 * _campo(h, L, 3, 70, 72)
    faixa = np.exp(-((yy - 40) / 28.0) ** 2) + 0.7 * np.exp(-((yy - 105) / 16.0) ** 2)
    est = ndimage.median_filter(((fio * faixa) > 0.9).astype(np.uint8), size=3).astype(bool)
    k = np.where(yy < 80, k - 1, k + 1)
    out = np.zeros((h, L, 4), np.uint8)
    out[..., :3] = RGB["ceu"][np.clip(k, 0, 11)]
    out[..., 3] = est * 255
    return Image.fromarray(out, "RGBA")


def serra(w, h=200, sem=80):
    """Serra ao longe por planos: face acesa para o sol, face na sombra, pé na névoa."""
    q = Quadro(w, h)
    rng = np.random.default_rng(sem)
    base = 90
    picos, x = [], -40
    while x < w + 80:
        picos.append((x, rng.uniform(24, 50), rng.uniform(60, 92)))
        x += rng.uniform(80, 130)
    xs = np.arange(w)
    alt = np.full(w, float(base))
    for (px, ph, pw) in picos:
        perfil = base - ph * np.clip(1 - np.abs(xs - px) / pw, 0, 1) ** 1.15
        alt = np.minimum(alt, perfil)
    alt += 1.5 * _campo(1, w, 1, 3, sem)[0] * (alt < base)
    m = q.yy >= alt[None, :]
    inc = -np.gradient(ndimage.uniform_filter1d(alt, 3))
    face = np.where(inc > 0.05, 0.72, np.where(inc < -0.05, 0.42, 0.57))
    luz = np.broadcast_to(face[None, :], (h, w)).copy()
    grotao = _campo(h, w, 5, 0.8, sem + 1)
    luz += 0.06 * (grotao > 1.2) * (face[None, :] > 0.5) - 0.06 * (grotao > 1.2) * (face[None, :] <= 0.5)
    prof = q.yy - alt[None, :]
    luz += 0.35 * np.clip((prof - 10) / 50, 0, 1) * (1 - luz)
    q.pinta(m, "serra", np.clip(luz, 0, 0.999))
    return q


# ---------------------------------------------------------------- paredão: chapadas enevoadas
def chapada(w, h=130):
    """Mesas de arenito no fundo como planos grandes: topo aceso, face quase lisa,
    poucas fendas, estratos leves e névoa no pé (pouco contraste)."""
    q = Quadro(w, h)
    for base_topo, amp, sem, desl in ((10, 10, 3, 0.10), (30, 8, 6, 0.0)):
        perfil = base_topo + amp * ruido(1, w, 40, sem)[0]
        degrau = np.round(perfil / 10) * 10
        corte = np.r_[0, np.flatnonzero(np.diff(degrau)) + 1, w]
        topo = np.maximum(2, np.round(ndimage.uniform_filter1d(degrau, 9)))
        m = q.yy >= topo[None, :]
        inc = -np.gradient(ndimage.uniform_filter1d(topo, 3))
        u = np.zeros(w)
        for a, b in zip(corte[:-1], corte[1:]):
            u[a:b] = (np.arange(b - a) + 0.5) / (b - a)
        prof = q.yy - topo[None, :]
        luz = 0.62 - 0.22 * u[None, :] + 0.12 * (u < 0.08)[None, :]
        luz = luz + (0.18 * (inc > 0.6) - 0.18 * (inc < -0.6))[None, :] * (prof < 40)
        fenda = (_campo(h, w, 14, 0.6, sem + 10) > 1.9) & (prof > 6)
        luz = np.where(fenda, luz - 0.12, luz)
        luz = np.where((prof % 19 == 0) & (prof > 4), luz - 0.06, luz)
        luz = np.where(prof < 2, 0.90, luz)
        luz = np.where((prof >= 3) & (prof < 5), luz - 0.10, luz)
        luz += 0.30 * np.clip((prof - 30) / 50, 0, 1) * (1 - luz) + desl
        q.pinta(m, "longe", np.clip(luz, 0, 0.999))
    return q


# ---------------------------------------------------------------- peças
def arvore(alt=145, sem=0, folhas=True):
    """Árvore da caatinga da amostra: tronco torto de galhos finos e copa em cachos de tufos,
    cada um com luz própria (cima-esquerda), os de trás no escuro."""
    s = alt / 145.0
    q = Quadro(int(150 * s) + 20, alt + 6)
    x0, chao = q.w * 0.42, q.h - 1
    rng = np.random.default_rng(sem)

    def galho(x, y, ang, comp, larg, prof, sm):
        r_ = np.random.default_rng(sm)
        ang0 = ang
        for k in range(int(comp)):
            ang += r_.normal(0, 0.10) + 0.08 * (ang0 - ang)
            x += np.cos(ang); y += np.sin(ang)
            r = larg * (1 - 0.6 * k / comp)
            j0, j1 = int(max(0, y - r - 1)), int(min(q.h, y + r + 2))
            i0, i1 = int(max(0, x - r - 1)), int(min(q.w, x + r + 2))
            if j1 <= j0 or i1 <= i0:
                continue
            yy, xx = q.yy[j0:j1, i0:i1], q.xx[j0:j1, i0:i1]
            m = np.zeros((q.h, q.w), bool)
            m[j0:j1, i0:i1] = np.hypot(xx - x, yy - y) <= r
            nx = (q.xx - x) / max(r, 0.5)
            luz = 0.48 - 0.45 * nx + 0.14 * np.sin((q.xx - x) * 2.2 + (q.yy - y) * 0.3)
            q.pinta(m, "madeira", np.clip(luz, 0, 0.999))
        if prof > 0:
            for d in (-0.5, 0.45):
                galho(x, y, ang + d + r_.normal(0, 0.15), comp * 0.65, larg * 0.6, prof - 1, sm * 3 + int(d * 10))

    galho(x0, chao, -np.pi / 2 - rng.uniform(0.05, 0.25), 56 * s, 7.5 * s, 3, sem + 51)
    galho(x0 + 2, chao - 30 * s, -np.pi / 2 + rng.uniform(0.5, 0.8), 40 * s, 3.5 * s, 2, sem + 77)
    if not folhas:
        return q
    nuv = [(x0 - 30 * s, chao - 104 * s, 17 * s), (x0 + 2 * s, chao - 122 * s, 21 * s),
           (x0 + 32 * s, chao - 108 * s, 16 * s), (x0 - 8 * s, chao - 96 * s, 13 * s),
           (x0 + 52 * s, chao - 84 * s, 11 * s)]
    nuv = [(cx + rng.normal(0, 4 * s), cy + rng.normal(0, 3 * s), r * rng.uniform(0.85, 1.15)) for cx, cy, r in nuv]
    tufos = []
    for cx, cy, r in nuv:
        for _ in range(int(r * 1.3)):
            a = rng.uniform(0, 2 * np.pi); d = r * np.sqrt(rng.uniform(0, 1))
            tufos.append((cx + d * np.cos(a), cy + d * np.sin(a) * 0.8, rng.uniform(3.5, 6.5) * max(s, 0.8)))
    tufos.sort(key=lambda p: p[1] - p[0] * 0.3)
    for k, (cx, cy, r) in enumerate(tufos):
        d = np.hypot(q.xx - cx, (q.yy - cy) * 1.2) / r
        lz = 0.62 - 0.35 * (q.xx - cx) / r - 0.45 * (q.yy - cy) / r - 0.25 * (1 - k / len(tufos))
        q.pinta(d < 1, "verde", np.clip(lz, 0.02, 0.999))
    return q


def mandacaru(alt=78, sem=0, bracos=((-15, 34, 64), (15, 44, 70))):
    """Mandacaru roliço (23/10): cada coluna é um cilindro de gomos (aresta acesa, vale
    escuro, luz da esquerda), topo redondo, cotovelo do braço como um tubo deitado que vira
    para cima, espinhos claros nas arestas; o pé finca num montinho de terra com sombra."""
    s_ = alt / 78.0
    q = Quadro(int(58 * s_) + 12, alt + 4)
    x, chao = q.w // 2, q.h - 2
    X, Y = q.xx.astype(float), q.yy.astype(float)

    def coluna(x0, y0, y1, r):
        u = (X - x0) / r
        topo = y0 + r * 0.9
        m = (np.abs(u) <= 1) & (Y >= topo) & (Y < y1)
        m |= (((X - x0) / r) ** 2 + ((Y - topo) / (r * 0.9)) ** 2 <= 1) & (Y < topo)
        cil = np.sqrt(np.clip(1 - u ** 2, 0, 1))
        gomo = np.cos(u * np.pi * 2.6)
        luz = 0.25 + 0.38 * cil - 0.3 * u + 0.14 * gomo
        luz = np.where(Y < topo, luz + 0.12 * (topo - Y) / r, luz)            # topo redondo aceso
        luz = np.where(gomo < -0.75, luz - 0.16, luz)                          # vale entre gomos
        espinho = (gomo > 0.9) & (((Y + X * 3 + sem) % 5) == 0)
        luz = np.where(espinho, 0.97, luz)
        q.pinta(m, "verde", np.clip(luz, 0.02, 0.97))
        return m

    def cotovelo(x0, x1, yb, r):
        a, b = min(x0, x1), max(x0, x1)
        v = (Y - yb) / r
        m = (X >= a) & (X <= b) & (np.abs(v) <= 1)
        luz = 0.3 + 0.35 * np.sqrt(np.clip(1 - v ** 2, 0, 1)) - 0.25 * v + 0.1 * np.cos(v * np.pi * 2.6)
        q.pinta(m, "verde", np.clip(luz, 0.02, 0.97))

    r0 = 7.5 * max(s_, 0.75)
    for dx, yb, yt in bracos:                                                  # braços atrás do tronco
        dx, yb, yt = dx * s_, chao - yb * s_, chao - yt * s_
        ra = 5.2 * max(s_, 0.75)
        cotovelo(x, x + dx, yb, ra)
        coluna(x + dx, yt, yb + ra * 0.3, ra)
    coluna(x, chao - alt + 2, chao + 1, r0)
    # montinho de terra no pé, com pedrinhas e a sombra de contato
    d = ((X - x) / (r0 * 1.9)) ** 2 + ((Y - chao) / 3.2) ** 2
    mont = (d < 1) & (Y >= chao - 2)
    q.pinta(mont, "terra", np.clip(0.62 - 0.25 * (Y - chao + 2) / 4 - 0.12 * (X - x) / (r0 * 2), 0.05, 0.95))
    for k in (-1, 1):
        pm = np.hypot(X - (x + k * r0 * 1.3), (Y - chao) * 1.4) < 1.6
        q.pinta(pm, "cal", np.where(Y < chao, 0.75, 0.35))
    return q


def xiquexique(w=30, alt=24, sem=0, rampa="verde", escuro=False):
    """Touceira de xique-xique: colunas curtas tortas de gomos, luz da esquerda."""
    q = Quadro(w + 8, alt + 2)
    rng = np.random.default_rng(sem)
    n = max(3, w // 6)
    cols = sorted([(rng.uniform(4, w + 2), rng.uniform(0.45, 1.0) * alt, rng.uniform(2.5, 3.8)) for _ in range(n)],
                  key=lambda c: c[1])
    for k, (cx, ca, r) in enumerate(cols):
        incl = (cx - q.w / 2) / q.w * 0.5
        y0 = q.h - ca
        xc = cx + incl * (q.h - q.yy)
        m = (np.abs(q.xx - xc) <= r) & (q.yy >= y0) & (q.yy < q.h)
        m |= (np.hypot(q.xx - (cx + incl * ca), q.yy - y0) <= r) & (q.yy < y0 + r)
        u = (q.xx - xc) / r
        luz = 0.5 - 0.35 * u + 0.12 * np.cos(u * np.pi * 1.5) - 0.12 * (1 - k / n)
        if escuro:
            luz = np.where(u < -0.2, 0.62, 0.22)
        else:
            luz = np.where(((q.yy * 2 + q.xx + k) % 5 == 0) & (np.abs(u) > 0.55), 0.92, luz)
        q.pinta(m, rampa, np.clip(luz, 0, 0.999))
    return q


def moita(w=40, h=22, sem=0, seca=0.3):
    """Moita redonda em cachos: luz cima-esquerda, base escura, sem contorno."""
    q = Quadro(w, h)
    rng = np.random.default_rng(sem)
    tufos = []
    for _ in range(int(w * h / 40) + 4):
        cx = rng.uniform(w * 0.15, w * 0.85)
        cy = rng.uniform(h * 0.35, h - 3)
        tufos.append((cx, cy, rng.uniform(3.5, 6.5)))
    tufos.sort(key=lambda p: p[1] - p[0] * 0.3)
    for k, (cx, cy, r) in enumerate(tufos):
        d = np.hypot(q.xx - cx, (q.yy - cy) * 1.25) / r
        lz = 0.6 - 0.35 * (q.xx - cx) / r - 0.45 * (q.yy - cy) / r - 0.25 * (1 - k / len(tufos))
        rampa = "madeira" if rng.random() < seca * 0.5 else "verde"
        q.pinta(d < 1, rampa, np.clip(lz * (0.9 if rampa == "madeira" else 1), 0.02, 0.999))
    return q


def capim(alt=8, sem=0, folhas=5, rampa="terra", base=3):
    """Tufo de capim seco: folhas finas, ponta clara."""
    q = Quadro(int(alt * 1.6) + 4, int(alt) + 1)
    rng = np.random.default_rng(sem)
    cx = q.w / 2
    for k in range(folhas):
        ang = -np.pi / 2 + (k - (folhas - 1) / 2) * 0.33 + rng.normal(0, 0.08)
        a_ = alt * rng.uniform(0.6, 1.0)
        for s_ in range(int(a_)):
            px, py = int(cx + np.cos(ang) * s_), int(q.h - 1 + np.sin(ang) * s_)
            if 0 <= px < q.w and 0 <= py < q.h:
                q.img[py, px] = RGB[rampa][min(len(RGB[rampa]) - 1, base + int(4 * s_ / a_))]
                q.a[py, px] = True
    return q


def pedra(w=30, h=18, sem=0, rampa="terra", topo=0.85):
    """Pedra de planos: topo aceso, face da esquerda média, a da direita na sombra,
    uma fenda e manchas de líquen."""
    q = Quadro(w, h)
    rng = np.random.default_rng(sem)
    cx, cy = w * 0.5, h * 0.62
    ang = np.arctan2(q.yy - cy, q.xx - cx)
    raio = 1 + 0.10 * np.sin(ang * 3 + rng.uniform(0, 6)) + 0.06 * np.sin(ang * 5 + rng.uniform(0, 6))
    d = np.hypot((q.xx - cx) / (w * 0.5), (q.yy - cy) / (h * 0.62))
    m = (d < raio) & (q.yy < h)
    # planos: topo (normal para cima), face esquerda, face direita
    nx, ny = (q.xx - cx) / (w * 0.5), (q.yy - cy) / (h * 0.62)
    luz = np.where(ny < -0.45, topo, np.where(nx < 0.15, 0.58, 0.34))
    luz = np.where((ny < -0.45) & (nx > 0.45), topo - 0.18, luz)
    fx = cx + rng.uniform(-0.2, 0.25) * w
    fenda = (np.abs(q.xx - fx - 1.2 * np.sin(q.yy / 2.0)) < 0.7) & (ny > -0.3)
    luz = np.where(fenda, 0.12, luz)
    luz = np.where(q.yy >= h - 2, luz - 0.18, luz)
    q.pinta(m, rampa, np.clip(luz, 0, 0.999))
    liq = (ruido(h, w, 1.2, sem + 3) > 1.3) & m & (ny < 0.2)
    q.pinta(liq, "verde", np.full((h, w), 0.62))
    return q


def lajedo(w, h, sem=0):
    """Lajedo de arenito (plataforma de jogo): laje de cima clara com a beirada gasta e,
    na frente, camadas grossas de pedra (cada uma com a beirada de cima acesa e sombra
    embaixo, recuando ou avançando um pouco), poucas fraturas tortas, lascas e líquen."""
    q = Quadro(w, h)
    rng = np.random.default_rng(sem)
    X, Y = q.xx, q.yy
    m = np.zeros((h, w), bool)
    luz = np.zeros((h, w))
    # laje de cima (onde se pisa): 4 px, quinas arredondadas
    le, ld = int(rng.integers(2, 4)), int(rng.integers(2, 5))
    topo = (Y < 4) & (X >= le - Y) & (X <= w - 1 - ld + Y)
    m |= topo
    luz = np.where(topo, 0.88 - 0.12 * (Y == 3) + 0.05 * ruido(h, w, 1, sem), luz)
    # camadas da frente
    y0 = 4
    while y0 < h:
        alt = int(rng.integers(7, 13))
        e, d = int(rng.integers(0, 4)), int(rng.integers(0, 4))     # recuo das pontas
        sel = (Y >= y0) & (Y < y0 + alt) & (X >= e) & (X < w - d)
        # pontas arredondadas da camada
        sel &= ~((X < e + 2) & ((Y == y0) | (Y == y0 + alt - 1)))
        sel &= ~((X > w - d - 3) & ((Y == y0) | (Y == y0 + alt - 1)))
        v = (Y - y0) / alt
        lz = 0.58 - 0.16 * v + rng.uniform(-0.05, 0.05) + 0.04 * ruido(h, w, 4, sem + y0)
        lz = np.where(Y == y0, 0.76, lz)                              # beirada acesa
        lz = np.where(Y == y0 + alt - 1, 0.30, lz)                    # sombra embaixo
        lz = np.where(X < e + 2, lz + 0.08, lz)
        lz = np.where(X > w - d - 6, lz - 0.14, lz)                   # ponta da direita virando
        # fraturas tortas (poucas): risco escuro com a beira da esquerda acesa
        for _ in range(max(1, w // 50)):
            fx = rng.uniform(0.1, 0.9) * w
            passo = np.cumsum(rng.choice([-1, 0, 0, 1], h)) * 0.6
            xf = fx + passo[np.clip(Y, 0, h - 1)]
            lz = np.where(np.abs(X - xf) < 0.6, 0.14, lz)
            lz = np.where(np.abs(X - xf + 1) < 0.6, lz + 0.12, lz)
        luz = np.where(sel, lz, luz)
        m |= sel
        y0 += alt
    luz = np.where((Y == 4) & m, luz - 0.18, luz)                       # sombra da laje de cima
    lasca = (ruido(h, w, 1.8, sem + 3) > 1.7) & m & (Y > 3)
    luz = np.where(lasca, luz - 0.16, luz)
    q.pinta(m, "terra", np.clip(luz, 0, 0.999))
    liq = (ruido(h, w, 3, sem + 9) > 1.7) & m & (Y > 5)
    liq = ndimage.binary_opening(liq, np.ones((2, 2)))
    q.pinta(liq, "verde", np.where(Y % 3 == 0, 0.55, 0.42))
    return q


def barranco(w, alto, sem=0):
    """Barranco de terra (plataforma): topo plano com capim, encostas em curva espalhando
    terra para fora, camadas de terra acompanhando o corte e raízes penduradas."""
    aba = 22
    q = Quadro(w + 2 * aba, alto + 4)
    xs = np.arange(q.w)
    perfil = np.where(xs < aba, alto * (1 - np.clip((aba - xs) / aba, 0, 1) ** 1.6),
                      np.where(xs >= aba + w, alto * (1 - np.clip((xs - aba - w + 1) / aba, 0, 1) ** 1.6), alto))
    topo = q.h - 1 - perfil
    m = q.yy >= topo[None, :]
    prof = q.yy - topo[None, :]
    lado = np.where(xs < aba, 0.12, np.where(xs >= aba + w, -0.14, 0.0))[None, :]
    camada = np.sin((q.yy + 2 * ruido(1, q.w, 6, sem)[0][None, :]) / 2.6)
    luz = 0.46 + lado + 0.06 * camada - 0.012 * prof + 0.05 * ruido(q.h, q.w, 2, sem + 1)
    luz = np.where(prof < 2, 0.86, luz)
    luz = np.where((prof >= 2) & (prof < 4), 0.62, luz)
    q.pinta(m, "terra", quantiza_limpo(np.clip(luz, 0, 0.999), 8))
    rng = np.random.default_rng(sem)
    for _ in range(w // 9):                                # raízes saindo do corte
        x = rng.uniform(aba + 2, aba + w - 2)
        y = topo[int(x)] + rng.uniform(4, 9)
        for s_ in range(int(rng.uniform(4, 9))):
            if 0 <= int(y) < q.h and q.a[int(y), int(x)]:
                q.img[int(y), int(x)] = RGB["madeira"][1]
            x += rng.normal(0, 0.6); y += 1
    for k in range(w // 6):                                 # capim no topo
        c = capim(rng.uniform(4, 8), sem + 20 + k, folhas=4)
        x = int(rng.uniform(aba - 6, aba + w))
        q.colar(c, x, topo[min(q.w - 1, x + c.w // 2)] - c.h + 1)
    return q


def cerca_varas(w=150, h=40, sem=0):
    """Cerca do curral: varas roliças tortas fincadas, duas travessas amarradas."""
    q = Quadro(w, h + 2)
    rng = np.random.default_rng(sem)
    for k, y in enumerate((int(h * 0.38), int(h * 0.68))):  # travessas atrás das varas
        yc = y + 2.5 * np.sin(q.xx / 40.0 + k) + 0.04 * (q.xx - w / 2)
        m = np.abs(q.yy - yc) <= 1.6
        luz = np.where(q.yy < yc - 0.4, 0.78, np.where(q.yy > yc + 0.6, 0.22, 0.5))
        q.pinta(m, "madeira", luz)
    x = 3.0
    while x < w - 3:
        alt = rng.uniform(0.78, 1.0) * h
        r = rng.uniform(1.6, 2.4)
        incl = rng.normal(0, 0.06)
        xc = x + incl * (q.h - q.yy)
        m = (np.abs(q.xx - xc) <= r) & (q.yy >= q.h - alt)
        u = (q.xx - xc) / r
        luz = 0.62 - 0.40 * u + 0.10 * np.sin(q.yy * 1.3 + x) - 0.2 * (q.yy > q.h - 4)
        luz = np.where(q.yy < q.h - alt + 1.5, 0.85, luz)    # topo cortado
        q.pinta(m, "madeira", np.clip(luz, 0, 0.999))
        for y in (int(h * 0.38), int(h * 0.68)):             # amarração de corda
            mm = (np.abs(q.xx - xc) <= r + 0.6) & (np.abs(q.yy - y) <= 1)
            q.pinta(mm, "cal", np.where(q.yy < y, 0.7, 0.45))
        x += rng.uniform(8, 12)
    return q


def cata_vento(alt=96):
    """Cata-vento do curral: torre de madeira em A com travessas em X, roda de pás
    de chapa velha e o leme; a roda é um disco de planos claros e escuros."""
    q = Quadro(56, alt + 2)
    cx, topo = 26, 18
    chao = q.h - 1
    for pe in (-1, 1):
        xb = cx + pe * 15
        for y in range(topo, chao + 1):
            t = (y - topo) / (chao - topo)
            x = cx + pe * 2 + (xb - cx - pe * 2) * t
            m = (np.abs(q.xx - x) <= 1.4) & (q.yy == y)
            q.pinta(m, "madeira", np.where(q.xx < x, 0.7, 0.35))
    for y0, y1 in ((40, 64), (64, 88)):                       # travessas em X
        if y1 > chao:
            continue
        for a, b in ((y0, y1), (y1, y0)):
            for k in range(60):
                t = k / 59
                y = a + (b - a) * t
                w_ = 2 + 13 * (y - topo) / (chao - topo)
                x = cx - w_ + 2 * w_ * t
                if 0 <= int(y) < q.h:
                    q.img[int(y), int(round(x))] = RGB["madeira"][2]
                    q.a[int(y), int(round(x))] = True
    # leme (cauda) atrás da roda
    leme = (q.xx > cx + 2) & (q.xx < cx + 26) & (np.abs(q.yy - topo) < 1 + (q.xx - cx) * 0.22) & (q.xx > cx + 14) \
        | ((q.xx > cx) & (q.xx <= cx + 14) & (np.abs(q.yy - topo) <= 0.8))
    q.pinta(leme, "cal", np.where(q.yy < topo, 0.62, 0.38))
    # roda de pás: setores alternados (pás inclinadas pegando luz de jeitos diferentes)
    r = np.hypot(q.xx - cx, q.yy - topo)
    ang = np.arctan2(q.yy - topo, q.xx - cx)
    setor = ((ang + np.pi) / (2 * np.pi) * 16).astype(int)
    roda = (r <= 16) & (r >= 3)
    pa = roda & ((ang * 16 / (2 * np.pi)) % 1 < 0.72)
    luz = np.where(np.cos(ang + 2.2) > 0, 0.72, 0.42) + 0.06 * (setor % 2)
    luz = np.where(r > 14.5, luz - 0.18, luz)                 # aro
    q.pinta(pa, "cal", np.clip(luz, 0, 0.999))
    q.pinta((r <= 15) & (r >= 14) & ~pa, "cal", np.full(r.shape, 0.3))
    q.pinta(r < 3, "madeira", np.where(q.xx < cx, 0.6, 0.3))
    return q


def casa(w=196, hp=98, telhado=54, sem=0, alpendre=True, lado=30, porta=None, janela=None, parede="cal",
         rombo=False, destelhada=False, sombra_beiral=False):
    """Casa de taipa grande da amostra aprovada: reboco de cal com barro subindo e
    escorridos, rachaduras, reboco caído mostrando a trama, porta de tábuas entreaberta,
    janela com folha aberta, telha canal em fileiras, parede lateral na sombra e alpendre.
    porta=(x na parede, largura, altura), janela=(x, y na parede, lado) ou False;
    parede="terra": taipa sem reboco (barro com a trama aparecendo);
    rombo: buraco grande no alto da parede; destelhada: só os caibros e ripas;
    sombra_beiral: a sombra dura do beiral na parede (casas de perto)."""
    ox = 74 if alpendre else 16
    q = Quadro(ox + w + lado + 6, telhado + 4 + hp)
    X, Y = q.xx, q.yy
    rz = lambda e, s_: ruido(q.h, q.w, e, sem * 31 + s_)  # noqa: E731
    x0, x1 = ox, ox + w
    yb, yt = q.h, telhado + 4
    ry0 = 4
    rng = np.random.default_rng(sem)
    # parede da frente
    m = (X >= x0) & (X < x1) & (Y >= yt) & (Y < yb)
    luz = 0.86 - 0.12 * (X - x0) / w + 0.03 * rz(14, 12)
    luz = np.where(rz(0.7, 11) > 2.3, luz - 0.2, luz)
    racha = np.zeros((q.h, q.w), bool)
    for fx, fy, n in ((0.13, 10, int(hp * 0.3)), (0.91, int(hp * 0.47), int(hp * 0.22)), (0.55, 4, int(hp * 0.16))):
        x, y = x0 + fx * w, float(yt + fy)
        rr = np.random.default_rng(sem + n)
        for _ in range(n):
            if 0 <= int(y) < q.h:
                racha[int(y), int(x)] = True
            x += rr.choice([-1, 0, 1]) * 0.8; y += 1
    luz = np.where(racha, 0.35, luz)
    luz -= 0.30 * np.clip((Y - (yb - 22)) / 22, 0, 1) * ((0.6 + 0.4 * rz(3, 13)) > 0)
    luz -= 0.25 * np.clip(1 - (Y - yt) / 14, 0, 1)
    esc = (ruido(1, q.w, 1.2, sem + 14)[0] > 1.4)[None, :] & (Y < yt + 30 + 20 * rz(8, 15))
    luz = np.where(esc & m, luz - 0.18, luz)
    if parede == "cal":
        q.pinta(m, "cal", quantiza_limpo(np.clip(luz, 0, 0.999), 6))
    else:
        _parede_barro(q, m, x0, w, yt, yb, sem)
    # reboco caído mostrando a trama da taipa
    buraco = (fbm(q.h, q.w, sem + 20) > (0.95 if parede == "cal" else 9)) & m & (Y > yt + 18) & (Y < yb - 10)
    buraco = ndimage.binary_opening(buraco, np.ones((3, 3)))
    vara = ((X % 7) < 2) | ((Y % 9) < 2)
    luz_b = np.where(vara, 0.62, 0.30) + 0.08 * rz(1.5, 21)
    borda = buraco & ~ndimage.binary_erosion(buraco)
    luz_b = np.where(borda & (Y > Y.mean()), 0.18, luz_b)
    q.pinta(buraco, "terra", np.clip(luz_b, 0, 0.999))
    lab = ndimage.binary_dilation(buraco) & ~buraco & m
    acima = np.zeros_like(buraco); acima[:-1] = buraco[1:]
    q.pinta(lab & acima, parede, np.full((q.h, q.w), 0.999 if parede == "cal" else 0.8))
    # parede lateral na sombra
    ml = (X >= x1) & (X < x1 + lado) & (Y >= yt + (X - x1) * 0.25) & (Y < yb)
    luz = 0.30 + 0.06 * rz(2.5, 16) - 0.15 * np.clip((Y - (yb - 20)) / 20, 0, 1)
    q.pinta(ml, parede, quantiza_limpo(np.clip(luz * (1 if parede == "cal" else 0.8), 0, 0.999), 6))
    # porta de tábuas entreaberta
    pdx, pw, ph = porta or (int(w * 0.33), 28, min(48, hp - 20))
    px0 = x0 + pdx; px1 = px0 + pw; pyt = yb - ph
    mp = (X >= px0) & (X < px1) & (Y >= pyt) & (Y < yb)
    tab = (X - px0) % 7
    luz = 0.45 + 0.12 * (tab == 1) - 0.25 * (tab == 6) + 0.08 * rz(1.0, 17) + 0.1 * (Y < pyt + 3)
    luz = np.where(X > px1 - 9, 0.06, luz)
    q.pinta(mp, "madeira", np.clip(luz, 0, 0.999))
    batente = (((X == px0 - 1) | (X == px0 - 2) | (X == px1)) & (Y >= pyt - 2) & (Y < yb)) | \
              ((Y >= pyt - 3) & (Y < pyt) & (X >= px0 - 2) & (X <= px1))
    q.pinta(batente, "madeira", np.full((q.h, q.w), 0.25))
    # janela com folha aberta
    jdx, jdy, jl = janela or (int(w * 0.63), int(hp * 0.27), 24)
    jx0 = x0 + jdx; jx1 = jx0 + jl; jy0 = yt + jdy; jy1 = jy0 + jl
    if janela is False:
        jx0 = jx1 = jy0 = jy1 = -99
    mj = (X >= jx0) & (X < jx1) & (Y >= jy0) & (Y < jy1)
    q.pinta(mj, "madeira", np.where(X < jx0 + 8, 0.02, 0.15))
    fol = (X >= jx1) & (X < jx1 + 10) & (Y >= jy0 - 1 + (X - jx1) // 4) & (Y < jy1 + 1 - (X - jx1) // 4)
    q.pinta(fol, "madeira", 0.5 + 0.2 * ((X - jx1) % 5 == 0) - 0.15 * (X - jx1) / 10)
    peit = (X >= jx0 - 2) & (X < jx1 + 2) & (Y >= jy1) & (Y < jy1 + 3)
    q.pinta(peit, "cal", np.where(Y == jy1, 0.99, 0.55))
    q.pinta(peit & (Y == jy1 + 2), "cal", np.full((q.h, q.w), 0.2))
    if sombra_beiral:
        # sombra do beiral: faixa dura recortada pelas bocas das telhas, um degrau abaixo
        bico = 2 * (np.cos(((X - (x0 - 14)) % 9 / 9.0 - 0.45) * 2 * np.pi) > 0.2)
        sb = (m | ml) & (Y < yt + 6 + bico) & ~((X >= px0) & (X < px1) & (Y >= pyt))
        q.img[sb] = escurecer(q.img[sb], 2)
    if rombo:
        _rombo(q, x0, w, yt, yb, sem)
    # telhado de telha canal
    beiral_esq, beiral_dir = x0 - 14, x1 + lado + 4
    inclin = (X >= beiral_esq + (yt + 6 - Y) * 0.35) & (X < beiral_dir - (yt + 6 - Y) * 0.1)
    mt = (Y >= ry0) & (Y < yt + 6) & inclin
    u = (X - beiral_esq) % 9 / 9.0
    fil = (Y - ry0) // 11
    v = ((Y - ry0) % 11) / 11.0
    cil = np.cos((u - 0.38) * np.pi)
    luz = 0.30 + 0.55 * cil - 0.22 * v + 0.10 * rz(1.2, 30)
    luz = np.where(v > 0.86, 0.10, luz)
    luz = np.where((u > 0.88) | (u < 0.05), 0.12, luz)
    luz += 0.08 * (fil % 2)
    q.pinta(mt, "telha", quantiza_limpo(np.clip(luz, 0, 0.999), 7))
    musgo = (fbm(q.h, q.w, sem + 31) > 1.15) & mt
    q.pinta(musgo, "verde", np.clip(0.35 + 0.2 * rz(1, 32), 0, 0.999))
    falta = (fbm(q.h, q.w, sem + 33, (4, 2), (0.7, 0.3)) > 1.6) & mt & (Y < yt - 4)
    q.pinta(falta, "madeira", np.where((Y % 6) < 2, 0.35, 0.03))
    boca = (Y >= yt + 4) & (Y < yt + 8) & inclin.any(axis=0)[None, :] & (X >= beiral_esq) & (X < beiral_dir)
    q.pinta(boca, "telha", np.where(np.hypot(u - 0.45, (Y - yt - 4) / 6) < 0.35, 0.05, 0.45))
    cume = (Y >= ry0 - 4) & (Y < ry0 + 2) & (X >= beiral_esq + 50) & (X < beiral_dir - 16)
    q.pinta(cume, "telha", np.where(Y < ry0 - 1, 0.9, 0.35))
    if destelhada:
        _destelhar(q, mt | boca | cume, beiral_esq, yt, sem)
    # alpendre: puxado de palha sobre forquilhas
    if alpendre:
        ax0, ax1 = x0 - 68, x0 - 4
        for px in (x0 - 64, x0 - 22):
            mpost = (X >= px) & (X < px + 6) & (Y >= yt + 28) & (Y < yb)
            luz = 0.25 + 0.5 * np.cos(((X - px) / 6 - 0.3) * np.pi) + 0.08 * rz(1, 40 + px)
            q.pinta(mpost, "madeira", np.clip(luz, 0, 0.999))
            forq = (np.abs(X - px - 3) - (yt + 28 - Y) * 0.6 < 2) & (np.abs(X - px - 3) - (yt + 28 - Y) * 0.6 > -1) & \
                (Y >= yt + 20) & (Y < yt + 30)
            q.pinta(forq, "madeira", np.full((q.h, q.w), 0.5))
        mal = (Y >= yt + 10 - (X - ax0) * 0.05) & (Y < yt + 22) & (X >= ax0 - 6) & (X < ax1 + 8)
        luz = 0.55 + 0.25 * ((X + Y // 2) % 4 == 0) - 0.3 * (Y > yt + 19) + 0.1 * rz(1.2, 41)
        q.pinta(mal, "madeira", np.clip(luz, 0, 0.999))
        viga = (Y >= yt + 21) & (Y < yt + 25) & (X >= ax0 - 2) & (X < ax1 + 4)
        q.pinta(viga, "madeira", np.where(Y == yt + 21, 0.75, 0.3))
    return q


def _parede_barro(q, m, x0, w, yt, yb, sem):
    """Taipa sem reboco: barro amassado à mão em torrões, a trama de varas aparecendo
    onde o barro caiu, mais escuro embaixo (respingo de chuva) e luz da esquerda."""
    X, Y = q.xx, q.yy
    torrao = fbm(q.h, q.w, sem + 50, (8, 4), (0.7, 0.3))
    luz = 0.66 - 0.14 * (X - x0) / w + 0.06 * torrao
    luz -= 0.20 * np.clip((Y - (yb - 18)) / 18, 0, 1)
    luz -= 0.22 * np.clip(1 - (Y - yt) / 12, 0, 1)
    # fiadas de barro amassado: uma linha de sombra torta a cada palmo
    fiada = (Y - yt + np.round(1.5 * ruido(1, q.w, 6, sem + 52)[0])[None, :]) % 11
    luz = np.where(fiada == 0, luz - 0.15, np.where(fiada == 1, luz + 0.07, luz))
    q.pinta(m, "terra", quantiza_limpo(np.clip(luz, 0, 0.999), 6))
    # remendos onde o barro caiu: a trama de varas (em pé) e ripas (deitadas) no fundo escuro
    caiu = (fbm(q.h, q.w, sem + 51, (7, 3), (0.7, 0.3)) > 1.25) & m & (Y > yt + 10) & (Y < yb - 8)
    from scipy import ndimage as _nd
    caiu = _nd.binary_opening(caiu, np.ones((4, 4)))
    vara = ((X - x0) % 6 < 2)
    ripa = ((Y - yt) % 7 < 2)
    lz = np.where(vara, 0.50 - 0.12 * ((X - x0) % 6 == 1), np.where(ripa, 0.36, 0.12))
    q.pinta(caiu, "madeira", lz)
    borda = caiu & ~_nd.binary_erosion(caiu)
    em_baixo = np.zeros_like(caiu); em_baixo[1:] = caiu[:-1]
    q.pinta(_nd.binary_dilation(caiu) & ~caiu & m & em_baixo, "terra", np.full((q.h, q.w), 0.85))


def _rombo(q, x0, w, yt, yb, sem):
    """Buraco grande no alto da parede (tiro de canhão): borda quebrada em degraus,
    o escuro de dentro, a trama de varas partida aparecendo e barro solto na beira."""
    X, Y = q.xx, q.yy
    cx, cy = x0 + w * 0.80, yt + (yb - yt) * 0.30
    r = min(w * 0.17, (yb - yt) * 0.30)
    from scipy import ndimage as _nd
    ang = np.arctan2(Y - cy, X - cx)
    dente = 0.16 * np.sign(np.sin(ang * 7 + sem)) * (np.abs(np.sin(ang * 7 + sem)) > 0.3)
    d = np.hypot((X - cx) / 1.2, Y - cy) / r + dente
    m = (d < 1) & (X >= x0) & (X < x0 + w)
    m = _nd.binary_opening(m, np.ones((2, 2)))
    # espessura da parede: lado de baixo e da direita pegam luz (viram para cima/esquerda)
    desl = np.zeros_like(m); desl[:-3, :-2] = m[3:, 2:]
    esp = m & ~desl
    q.pinta(m, "madeira", np.where(Y < cy, 0.03, 0.09))
    vara = ((X - x0) % 8 < 2) & m & (np.abs(X - cx) < r * 0.9) & (ruido(q.h, q.w, (3, 1), sem + 61) > -0.2)
    q.pinta(vara, "madeira", np.where((X - x0) % 8 == 0, 0.6, 0.38))
    q.pinta(esp & (Y >= cy - r * 0.2), "terra", np.where(X > cx, 0.62, 0.78))
    q.pinta(esp & (Y < cy - r * 0.2), "terra", np.full((q.h, q.w), 0.3))
    beira = _nd.binary_dilation(m, np.ones((3, 3))) & ~m & (X >= x0) & (X < x0 + w) & (Y < cy)
    q.pinta(beira, "terra", np.full((q.h, q.w), 0.45))


def _destelhar(q, mt, beiral_esq, yt, sem):
    """Telhado arrancado: sobra o escuro do vão, os caibros descendo a água,
    as ripas atravessadas, uns cacos de telha presos no beiral."""
    X, Y = q.xx, q.yy
    q.a &= ~mt
    vao = mt & (Y > Y[mt].min() + 3)
    q.pinta(vao, "madeira", np.full((q.h, q.w), 0.03))
    u = (X - beiral_esq) % 18
    rr = np.random.default_rng(sem + 70)
    y0r = Y[mt].min()
    # caibros descendo a água, um ou outro quebrado no meio
    quebra = {c: (y0r + rr.integers(8, 30) if rr.random() < 0.3 else 999) for c in np.unique(X[vao] // 18)}
    qb = np.vectorize(quebra.get)(X // 18)
    caibro = vao & (u < 3) & ((Y < qb) | (Y > qb + 7))
    q.pinta(caibro, "madeira", np.where(u == 0, 0.8, np.where(u == 1, 0.55, 0.28)))
    # ripas finas atravessadas, com falhas
    falha = ruido(q.h, q.w, (1, 6), sem + 72) > 0.7
    ripa = vao & ((Y - yt) % 9 == 0) & ~falha & ~caibro
    q.pinta(ripa, "madeira", np.full((q.h, q.w), 0.45))
    q.pinta(vao & ((Y - yt) % 9 == 1) & ~falha & ~caibro, "madeira", np.full((q.h, q.w), 0.14))
    cume = mt & (Y <= y0r + 3)
    q.pinta(cume, "madeira", np.where(Y == y0r, 0.75, 0.35))
    # telhas que ficaram presas, em grupinhos, e a fileira do beiral
    grupo = (fbm(q.h, q.w, sem + 71, (5, 2), (0.7, 0.3)) > 1.2) & vao
    grupo |= vao & (Y > yt - 2) & (ruido(q.h, q.w, (1, 5), sem + 73) > 0.1)
    tu = (X - beiral_esq) % 9 / 9.0
    tv = ((Y - 4) % 11) / 11.0
    lz = 0.30 + 0.55 * np.cos((tu - 0.38) * np.pi) - 0.22 * tv
    lz = np.where((tu > 0.88) | (tu < 0.05) | (tv > 0.86), 0.1, lz)
    q.pinta(grupo, "telha", quantiza_limpo(np.clip(lz, 0, 0.999), 7))


def casinha_longe(w=40, hp=16, sem=0):
    """Casinha de taipa vista de longe: a mesma casa grande (telha canal, reboco, porta,
    janela, parede lateral na sombra) pintada em tamanho cheio e reduzida pela média,
    com cada pixel encaixado de volta na rampa. Fica com volume e detalhe, só menor."""
    esc = 2.6
    g = casa(int(w * esc), max(46, int(hp * esc)), max(34, int(hp * esc * 0.55)), sem=sem, alpendre=False,
             lado=max(14, int(w * esc / 7)))
    W, H = max(1, int(round(g.w / esc))), max(1, int(round(g.h / esc)))
    rgba = np.dstack([g.img, (g.a * 255).astype(np.uint8)])
    red = np.array(Image.fromarray(rgba, "RGBA").resize((W, H), Image.BOX))  # média com alfa pré-multiplicado
    q = Quadro(W, H)
    q.img = encaixar(red[..., :3])
    q.a = red[..., 3] > 140
    return q


# ---------------------------------------------------------------- peças antigas trazidas para a luz da cena
def ambientar(img):
    """Peça antiga (com contorno, paleta própria) entra na cor de ambiente: cada material
    vai para a rampa da cena pela claridade, e o contorno de fora some (vira o tom do
    vizinho de dentro, um degrau abaixo)."""
    arr = np.array(img.convert("RGBA"))
    a = arr[..., 3] > 0
    rgb = arr[..., :3].astype(float)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / (mx + 1e-9)
    fam = np.full(a.shape, "terra", object)
    fam[((b >= r) | (sat < 0.12)) & (lum >= 165)] = "cal"
    fam[((b >= r) | (sat < 0.12)) & (lum < 165)] = "madeira"
    fam[(r > g) & (g >= b) & (lum < 120) & (sat >= 0.12)] = "madeira"
    fam[(r > g * 1.45) & (sat > 0.45) & (lum > 50)] = "telha"
    fam[(g > r * 0.98) & (g > b * 1.1) & (sat > 0.15)] = "verde"
    out = np.zeros(arr.shape[:2] + (3,), np.uint8)
    idx = np.zeros(a.shape, int)
    for nome in ("terra", "cal", "madeira", "telha", "verde"):
        m = a & (fam == nome)
        rr = RGB[nome]
        lo, hi = {"cal": (120, 245), "madeira": (10, 170), "telha": (30, 200), "verde": (20, 170)}.get(nome, (20, 225))
        k = np.clip(np.round((lum - lo) / (hi - lo) * (len(rr) - 1)), 0, len(rr) - 1).astype(int)
        idx[m] = k[m]
        out[m] = rr[k[m]]
    borda = a & ~ndimage.binary_erosion(a) & (lum < 70)
    dentro = a & ~borda
    if dentro.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~dentro, return_indices=True)
        for nome in ("terra", "cal", "madeira", "telha", "verde"):
            m = borda & (fam[iy, ix] == nome)
            k = np.clip(idx[iy, ix] - 1, 0, len(RGB[nome]) - 1)
            out[m] = RGB[nome][k[m]]
    q = Quadro(arr.shape[1], arr.shape[0])
    q.img, q.a = out, a
    return q


# ---------------------------------------------------------------- camadas do trecho
def _xs(fator, margem=40):
    return limite(fator) - margem


def camada_paredao(h=130, ate=None):
    """`ate`: até onde a camada vai (o trecho seguinte estende a mesma pintura)."""
    return chapada((ate or limite(0.2)) + 200, h)


def _morros(q, base, alt, larg, sem, rampa_luz, desl=0.0, planos=None):
    """Fileira de morros: cada morro é uma forma própria (largura, altura e caimento
    diferentes), iluminada por planos como a serra: encosta virada para o sol clara,
    a outra na sombra, crista acesa. `planos` força trechos planos (x0, x1, y)."""
    rng = np.random.default_rng(sem)
    w = q.w
    xs = np.arange(w, dtype=float)
    topo = np.full(w, float(q.h))
    incl = np.zeros(w)
    x = -rng.uniform(0, 80)
    while x < w + 100:
        lw = rng.uniform(*larg)
        ah = rng.uniform(*alt)
        pico = x + lw * rng.uniform(0.3, 0.7)          # crista fora do meio: um lado mais íngreme
        t = np.where(xs < pico, (pico - xs) / (pico - x), (xs - pico) / (x + lw - pico))
        perfil = base - ah * np.clip(1 - t, 0, 1) ** 1.4 * (1 - 0.15 * np.clip(1 - t, 0, 1))
        perfil = np.where((t >= 0) & (t <= 1), perfil, q.h)
        novo = perfil < topo
        incl = np.where(novo, np.where(xs < pico, 1.0, -1.0) * np.clip(ah / max(1, pico - x), 0, 1), incl)
        topo = np.minimum(topo, perfil)
        x += lw * rng.uniform(0.55, 0.8)
    topo = np.minimum(topo, base + 4)
    if planos:
        for x0, x1, y in planos:
            sel = (xs >= x0) & (xs < x1)
            topo[sel] = y
            incl[sel] = 0
            for lado, x_ in ((-1, x0), (1, x1)):              # ombro descendo para os lados
                d = np.abs(xs - x_)
                ombro = (d < 80) & ((xs < x0) if lado < 0 else (xs >= x1))
                alvo = y + (d / 80) ** 1.3 * 34
                novo = ombro & (alvo < topo)
                incl = np.where(novo, -lado * 0.6, incl)
                topo = np.where(novo, alvo, topo)
    topo = np.round(topo + 0.6 * ruido(1, w, 2, sem + 1)[0])
    m = q.yy >= topo[None, :]
    prof = q.yy - topo[None, :]
    luz = 0.56 + 0.24 * incl[None, :] - 0.004 * prof + desl
    luz = np.where(prof < 2, luz + 0.20, luz)                       # crista acesa
    # grotas descendo a encosta (riscos largos e poucos, não ondas)
    grota = (ruido(q.h, w, (6, 1.2), sem + 2) > 1.5) & (prof > 4)
    luz = np.where(grota, luz - 0.08, luz)
    q.pinta(m, rampa_luz, quantiza_limpo(np.clip(luz, 0, 0.999), 6))
    return topo.astype(int)


def camada_meio(h=90, ate=None, planos_extra=()):
    """Morros baixos ao longe em duas fileiras de formas próprias (por planos, sem ondas),
    caatinga rala, pedras, a vila no alto de um morro e uma casinha sozinha, tudo enevoado."""
    fator = 0.45
    w = limite(fator) + 120          # as contas do sorteio seguem a largura da caatinga
    q = Quadro((ate or limite(fator)) + 120, h)
    oy = h - 90                      # folga em cima (camada mais alta): tudo desce junto, a base não muda
    rng = np.random.default_rng(11)
    lim = limite(fator) - 20
    vila = (int(3190 * fator), int(3560 * fator))
    _morros(q, 40 + oy, (16, 32), (150, 280), 8, "longe", desl=0.10)       # fileira de trás, mais clara
    topo = _morros(q, 60 + oy, (14, 30), (120, 240), 9, "meio",
                   planos=[(vila[0] - 4, vila[1] + 4, 32 + oy), (int(900 * fator) - 4, int(900 * fator) + 50, 42 + oy)]
                   + [(a, b, y + oy) for a, b, y in planos_extra])
    # pedras claras aflorando e moitas miúdas na encosta
    for _ in range(int(w / 548 * 18)):
        cx = rng.uniform(0, lim)
        p = nevoa(pedra(int(rng.uniform(8, 14)), int(rng.uniform(5, 8)), sem=int(cx), topo=0.9), 0.3)
        q.colar(p, cx, topo[int(cx)] + rng.uniform(3, 14))
    for _ in range(int(w / 548 * 30)):
        cx = rng.uniform(0, lim); r = rng.uniform(3, 6)
        cy = topo[int(cx)] + rng.uniform(3, 26)
        d = np.hypot(q.xx - cx, (q.yy - cy) * 1.4) / r
        mm = (d < 1) & (q.yy < cy + 2)
        lz = 0.5 - 0.35 * (q.xx - cx) / r - 0.45 * (q.yy - cy) / r
        q.pinta(mm, "verde", np.clip(lz * 0.5 + 0.2, 0, 0.999))
    # árvores pequenas ao longe, clareadas pela névoa
    x = 30.0
    while x < lim:
        p = nevoa(arvore(int(rng.uniform(34, 50)), sem=int(x), folhas=rng.random() > 0.2), 0.42)
        dentro_vila = vila[0] - 30 < x < vila[1] + 30
        if x + p.w < lim and not dentro_vila:
            q.colar(p, x - p.w / 2, topo[int(x)] + rng.uniform(2, 8) - p.h)
        x += rng.uniform(50, 120)
    # casinha sozinha num patamar e a vila no alto do morro (casas lado a lado, mesma base)
    cx = int(900 * fator)
    c = nevoa(casinha_longe(46, 22, sem=12), 0.36)
    q.colar(c, cx, 42 + oy - c.h + 1)
    x = vila[0] + 4
    k = 0
    while x < min(vila[1], lim - 60):
        c = nevoa(casinha_longe(int(rng.integers(40, 56)), int(rng.integers(18, 28)), sem=70 + k), 0.36)
        q.colar(c, x, 32 + oy - c.h + 1)
        x += c.w + int(rng.integers(4, 16))
        k += 1
    return q


def camada_perto(h=160, ate=None):
    """Plano de trás (0,75): as duas casas de taipa grandes, o curral com o cata-vento,
    árvores e mandacarus grandes, pedras e moitas no pé."""
    fator = 0.75
    lim = limite(fator)
    q = Quadro((ate or lim) + 40, h)
    chao = h - 1
    rng = np.random.default_rng(2)
    lx = lambda wx: int(wx * fator)  # noqa: E731
    pecas = []
    # (posição no mundo, peça): poucas e grandes
    pecas.append((lx(100), pedra(64, 36, 300, topo=0.8)))
    pecas.append((lx(1150), pedra(80, 42, 301, topo=0.8)))
    pecas.append((lx(2180), pedra(56, 30, 302, topo=0.8)))
    for k, (wx, alt) in enumerate(((20, 150), (400, 128), (1000, 156), (1700, 138), (2050, 150), (2700, 140))):
        pecas.append((lx(wx), arvore(alt, sem=100 + k, folhas=k != 3)))
    for k, (wx, alt, br) in enumerate(((250, 84, 2), (880, 96, 2), (1290, 70, 1), (1880, 92, 2), (2560, 80, 2))):
        b = ((-15, 34, 64), (15, 44, 70)) if br == 2 else ((15, 30, 56),)
        pecas.append((lx(wx), mandacaru(alt, sem=200 + k, bracos=b)))
    import pecas25 as p5
    pecas.append((lx(1440), p5.curral(170, 40, 26, sem=9)))   # curral em 2.5D (cerca fugindo para trás)
    pecas.append((lx(1640), cata_vento(100)))
    pecas.append((lx(640), casa(196, 98, 54, sem=5)))
    pecas.append((lx(2380), casa(150, 84, 46, sem=8, alpendre=False, lado=24)))
    # moitas enchendo o pé (atrás de tudo)
    x = 0.0
    while x < lim - 40:
        if rng.random() < 0.72:
            p = moita(int(rng.integers(30, 56)), int(rng.integers(14, 22)), sem=int(x), seca=rng.uniform(0.2, 0.7))
        else:
            p = xiquexique(int(rng.integers(22, 34)), int(rng.integers(16, 24)), sem=int(x) + 1)
        q.colar(p, x, chao - p.h + 3)
        x += rng.integers(26, 64)
    for x, p in sorted(pecas, key=lambda e: -e[1].h):
        if x + p.w <= lim:
            q.colar(p, x, chao - p.h + 2)
    return q


def camada_frente(h=44, ate=None):
    """Na frente do Lampião (1,1): touceiras escuras de xique-xique e capim nos cantos."""
    fator = 1.1
    lim = ate or limite(fator)
    q = Quadro(lim + 40, h)
    rng = np.random.default_rng(4)
    x = 140.0
    while x < lim - 60:
        if rng.random() < 0.5:
            p = xiquexique(int(rng.integers(24, 36)), int(rng.integers(26, 40)), sem=int(x), rampa="frente", escuro=True)
        else:
            p = Quadro(40, h)
            for k in range(int(rng.integers(5, 8))):
                ang = -np.pi / 2 + (k - 3) * 0.22
                alt = rng.uniform(16, 30)
                for s in range(int(alt)):
                    px = 20 + np.cos(ang) * s + 1.5 * np.sin(s / 5 + k)
                    py = h + 2 + np.sin(ang) * s
                    m = np.hypot(p.xx - px, p.yy - py) < max(1.2, 3.0 - s / alt * 2)
                    p.pinta(m, "frente", np.where(p.xx < px, 0.6, 0.2) + 0.15 * (s > alt * 0.7))
        q.colar(p, x, h - p.h + 4)
        x += rng.uniform(300, 560)
    return q


def camada_jogo(fase, alt=140, topo_mundo=76, ate=None):
    """Plano do jogo do trecho: chão de terra batida com pedras encaixadas, lajedos, barranco
    e pedra grande nos sólidos, e os objetos de cena antigos trazidos para a luz da cena."""
    import fase1 as f1
    F = fase.FASE
    CH = f1.CHAO
    w = CAATINGA_FIM + 80            # as contas do sorteio seguem a largura da caatinga
    q = Quadro(max(w, (ate or 0) + 80), alt)
    y = lambda wy: wy - topo_mundo  # noqa: E731
    yc = y(CH) - 1
    rng = np.random.default_rng(63)
    # chão
    topo = np.minimum(y(CH) - 2, y(CH) - 2 + np.round(1.5 * ruido(1, q.w, 8, 60)[0]))
    m = q.yy >= topo[None, :]
    luz = 0.64 - 0.30 * np.clip((q.yy - y(CH)) / 24, 0, 1) + 0.05 * ruido(alt, q.w, 6, 61)
    luz = np.where(q.yy < topo[None, :] + 2, 0.88, luz)
    q.pinta(m, "terra", quantiza_limpo(np.clip(luz, 0, 0.999), 8))
    for _ in range(int(w / 548 * 70)):
        px = rng.uniform(0, w); py = rng.uniform(y(CH) + 2, alt + 2)
        rx = rng.uniform(2.5, 7) * (1 + (py - y(CH)) / 30); ry = rx * rng.uniform(0.45, 0.7)
        j0, j1, i0, i1 = int(max(0, py - ry - 3)), int(min(alt, py + ry + 4)), int(max(0, px - rx - 3)), int(min(w, px + rx + 4))
        if j1 <= j0 or i1 <= i0:
            continue
        sub = Quadro(i1 - i0, j1 - j0)
        sub.img[:] = q.img[j0:j1, i0:i1]; sub.a[:] = q.a[j0:j1, i0:i1]
        X, Y = sub.xx + i0, sub.yy + j0
        d = np.hypot((X - px) / rx, (Y - py) / ry) + 0.12 * ruido(sub.h, sub.w, 0.8, int(px))
        som = (np.hypot((X - px - 1.5) / rx, (Y - py - 1.5) / ry) < 1) & (Y > py) & sub.a
        sub.img[som] = escurecer(sub.img[som], 1)
        lz = 0.55 - 0.35 * (X - px) / rx - 0.5 * (Y - py) / ry
        sub.pinta(d < 1, "terra", np.clip(lz, 0, 0.999))
        q.img[j0:j1, i0:i1] = sub.img
    # capim seco no pé das coisas
    x = 0.0
    while x < w - 100:
        c = capim(rng.uniform(5, 10), int(x), folhas=int(rng.integers(4, 7)))
        q.colar(c, x, yc - c.h + 2)
        x += rng.uniform(14, 40)
    # pedras e xique-xiques soltos
    for k, x in enumerate((120, 380, 690, 1050, 1520, 1990, 2470, 2610, 2850)):
        q.assentar(pedra(int(rng.integers(18, 30)), int(rng.integers(10, 15)), sem=k + 20), x, yc, afundar=2)
    for x in (70, 205, 640, 1590, 1930, 2420, 2700, 2900):   # longe das pedras, giraus e carroças
        q.assentar(xiquexique(int(rng.integers(24, 34)), int(rng.integers(18, 26)), sem=x), x, yc, afundar=2)
    # objetos antigos ambientados (sem contorno, na luz da cena)
    amb = lambda t: ambientar(t.imagem())  # noqa: E731
    for fx, falt in F["forquilhas"]:
        q.assentar(amb(f1.forquilha(falt, semente=fx)), fx, yc)
    for bx in F["buracos"]:
        bu = amb(f1.buraco())
        q.colar(bu, bx - bu.w / 2, yc - bu.h + 3)
    for gx, _ in F["fogueiras"]:
        if gx < CAATINGA_FIM:
            fg = amb(f1.fogueira())
            q.assentar(fg, gx - fg.w / 2, yc)
    for x, peca in ((300, f1.pote_barro(1)), (318, f1.pote_barro(2, 11)), (820, f1.pilao()),
                    (1720, f1.pote_barro(3)), (1910, f1.roda_carroca(8)),
                    (2080, f1.pote_barro(4, 12)), (2450, f1.pilao()),
                    (1880, f1.cranio_boi()), (2540, f1.cranio_boi())):
        q.assentar(amb(peca), x, yc)
    # Lajedos, barranco, pedra grande, trincheira de sacos, giraus e carros de boi agora são
    # peças 2.5D à parte (chao_largo.pecas_fase1), na frente da linha onde se anda.
    if ate:                          # o trecho seguinte continua daqui e faz a passagem
        return q
    # a passagem para a vila: o chão novo some em manchas sobre o antigo
    corte = np.clip((CAATINGA_FIM + 40 - q.xx) / 120.0, 0, 1) + 0.25 * ruido(alt, w, 3, 99)
    q.a &= corte > 0.5
    return q


def emendar(velho, novo, largura=120, sem=0):
    """Junta a camada antiga (PIL RGBA) e a nova (Quadro) alinhadas por baixo: o novo vale
    até o fim dele e some em manchas nos últimos `largura` px, sem corte reto."""
    v = np.array(velho.convert("RGBA"))
    n = novo.rgba()
    h = max(v.shape[0], n.shape[0])
    if v.shape[0] < h:
        v = np.concatenate([np.zeros((h - v.shape[0], v.shape[1], 4), np.uint8), v])
    if n.shape[0] < h:
        n = np.concatenate([np.zeros((h - n.shape[0], n.shape[1], 4), np.uint8), n])
    w = min(v.shape[1], n.shape[1])
    xs = np.arange(w)[None, :]
    # borda torta (onda por coluna e um pouco por linha), não pontilhado
    onda = ruido(1, w, 6, sem)[0][None, :] * 0.18 + ruido(h, w, 5, sem + 1) * 0.07
    t = np.clip((w - xs) / largura, 0, 1) + onda
    usa = (xs < w - largura) | ((t > 0.5) & (n[:, :w, 3] > 0))
    v[:, :w][usa] = n[:, :w][usa]
    return Image.fromarray(v, "RGBA")


def sobrepor(velho, novo):
    """Cola a camada nova por cima da antiga (peças soltas com fundo transparente)."""
    v = velho.convert("RGBA")
    n = Image.fromarray(novo.rgba(), "RGBA")
    if n.height > v.height:
        base = Image.new("RGBA", (v.width, n.height))
        base.paste(v, (0, n.height - v.height))
        v = base
    v.alpha_composite(n, (0, v.height - n.height))
    return v
