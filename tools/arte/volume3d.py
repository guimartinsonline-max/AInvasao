"""Volume de verdade para sprites: monta o boneco com formas 3D (elipsoides e
cápsulas), ilumina com luz de cima-esquerda-frente, divide em faixas de tom e reduz
para o tamanho do sprite em manchas limpas.

É o que dá o "peso de borracha" do Metal Slug: luz grande e contínua de um lado,
sombra do outro, em vez do sombreado de travesseiro (claro na borda toda) que o
sombreado por distância à borda fazia.

Uso:
    c = Cena(40, 32)
    c.elipsoide((18, 16, 0), (12, 6, 6), PELO)
    c.capsula((10, 20, -3), (10, 30, -3), 1.6, 1.2, PELO)
    t = c.render()          # Tela pronta, com contorno
"""
import numpy as np
from scipy import ndimage

from motor import IDX, VAZIO, Tela

S = 4  # supersampling
_L = np.array([-0.55, -0.75, 0.62])
_L = _L / np.linalg.norm(_L)


class Cena:
    def __init__(self, w, h):
        self.w, self.h = w, h
        H, W = h * S, w * S
        self.z = np.full((H, W), -1e9)
        self.n = np.zeros((H, W, 3))
        self.mat = np.full((H, W), -1, dtype=np.int32)
        self.parte = np.full((H, W), -1, dtype=np.int32)
        self.mats = []
        self.np = 0
        yy, xx = np.mgrid[0:H, 0:W]
        self.X = (xx + 0.5) / S
        self.Y = (yy + 0.5) / S

    def _mat(self, rampa, brilho=0.0, escurece=0.0):
        self.mats.append((rampa, brilho, escurece))
        return len(self.mats) - 1

    def _esfera(self, c, r, m, parte, achata=1.0):
        cx, cy, cz = c
        rx, ry, rz = r
        d2 = ((self.X - cx) / rx) ** 2 + ((self.Y - cy) / ry) ** 2
        dentro = d2 < 1
        if not dentro.any():
            return
        dz = np.sqrt(np.clip(1 - d2, 0, 1))
        z = cz + rz * dz
        sel = dentro & (z > self.z)
        nx = (self.X - cx) / rx
        ny = (self.Y - cy) / ry
        nz = dz * achata
        nn = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
        self.z[sel] = z[sel]
        self.n[sel] = np.stack([nx / nn, ny / nn, nz / nn], -1)[sel]
        self.mat[sel] = m
        self.parte[sel] = parte

    def elipsoide(self, c, r, rampa, brilho=0.0, escurece=0.0, achata=1.0):
        m = self._mat(rampa, brilho, escurece)
        self.np += 1
        self._esfera(c, r, m, self.np, achata)
        return self.np

    def capsula(self, a, b, r0, r1, rampa, brilho=0.0, escurece=0.0, passos=None):
        m = self._mat(rampa, brilho, escurece)
        self.np += 1
        a, b = np.array(a, float), np.array(b, float)
        L = np.linalg.norm(b[:2] - a[:2])
        n = passos or max(3, int(L * 2) + 2)
        for k in range(n):
            f = k / (n - 1)
            p = a + (b - a) * f
            r = r0 + (r1 - r0) * f
            self._esfera(p, (r, r, r), m, self.np)
        return self.np

    def caminho(self, pts, raios, rampa, **kw):
        """Cápsulas emendadas (chifre curvo, rabo, barbicha)."""
        m = self._mat(rampa, kw.get("brilho", 0.0), kw.get("escurece", 0.0))
        self.np += 1
        for (a, b), (r0, r1) in zip(zip(pts, pts[1:]), zip(raios, raios[1:])):
            a, b = np.array(a, float), np.array(b, float)
            n = max(3, int(np.linalg.norm(b[:2] - a[:2]) * 2) + 2)
            for k in range(n):
                f = k / (n - 1)
                self._esfera(a + (b - a) * f, (r0 + (r1 - r0) * f,) * 3, m, self.np)
        return self.np

    def render(self, contorno="sombra", linhas=True):
        H, W = self.h, self.w
        luz = np.clip((self.n * _L).sum(-1), 0, 1)
        t = Tela(W, H)
        tom = np.full((H * S, W * S), -1, dtype=np.int32)
        for m, (rampa, brilho, escurece) in enumerate(self.mats):
            sel = self.mat == m
            if not sel.any():
                continue
            k = len(rampa)
            v = np.clip(0.12 + 0.88 * luz[sel] - escurece, 0, 1)
            # Faixas com a luz grande: o tom do meio ocupa mais área (forma lida de longe).
            nivel = np.clip(np.floor(v ** 0.9 * (k - 0.01)), 0, k - 1).astype(int)
            if brilho:
                ref = np.clip(2 * (self.n[sel] @ _L) * self.n[sel][:, 2] - _L[2], 0, 1)
                nivel = np.where(ref > 1 - brilho, k - 1, nivel)
            tom[sel] = np.array([IDX[c] for c in rampa])[nivel]
        # Reduz: em cada bloco SxS vence a cor mais comum (se o bloco estiver meio cheio).
        blocos = tom.reshape(H, S, W, S).transpose(0, 2, 1, 3).reshape(H, W, S * S)
        partes = self.parte.reshape(H, S, W, S).transpose(0, 2, 1, 3).reshape(H, W, S * S)
        zs = self.z.reshape(H, S, W, S).transpose(0, 2, 1, 3).reshape(H, W, S * S)
        parte_px = np.full((H, W), -1)
        zpx = np.full((H, W), -1e9)
        for y in range(H):
            for x in range(W):
                b = blocos[y, x]
                cheio = b >= 0
                if cheio.sum() * 2 < S * S:
                    continue
                vals, cont = np.unique(b[cheio], return_counts=True)
                t.px[y, x] = vals[np.argmax(cont)]
                pv, pc = np.unique(partes[y, x][cheio], return_counts=True)
                parte_px[y, x] = pv[np.argmax(pc)]
                zpx[y, x] = zs[y, x][cheio].max()
        self.parte_px, self.zpx = parte_px, zpx
        if linhas:
            # Linha escura onde uma peça passa na frente de outra (perna sobre barriga etc.).
            escuro = {}
            for rampa, _, _ in self.mats:
                for c in rampa:
                    escuro[IDX[c]] = IDX[rampa[0]]
            novo = t.px.copy()
            for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                p2 = np.roll(parte_px, (dy, dx), (0, 1))
                z2 = np.roll(zpx, (dy, dx), (0, 1))
                atras = (parte_px >= 0) & (p2 >= 0) & (p2 != parte_px) & (zpx < z2 - 1.2)
                for y, x in zip(*np.where(atras)):
                    novo[y, x] = escuro.get(t.px[y, x], t.px[y, x])
            t.px = novo
        self.contorno_cor = contorno
        return t


def contornar(t, base="sombra", lado_luz=None):
    """Contorno de 1 px; no lado de cima/esquerda usa o escuro do material (lado_luz:
    dict cor->cor), embaixo e à direita a cor base."""
    cheio = t.px != VAZIO
    fora = ndimage.binary_dilation(cheio, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & ~cheio
    px = t.px.copy()
    for y, x in zip(*np.where(fora)):
        cor = IDX[base]
        if lado_luz:
            # vizinho de dentro abaixo ou à direita = esta borda é de cima/esquerda
            for dy, dx in ((1, 0), (0, 1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < t.h and 0 <= xx < t.w and t.px[yy, xx] != VAZIO:
                    cor = IDX[lado_luz.get(t.px[yy, xx], base)] if isinstance(lado_luz.get(t.px[yy, xx], base), str) else cor
                    break
        px[y, x] = cor
    t.px = px
    return t


def sombrear2d(t, m, rampa, deslocar=0.0, linha=True):
    """Volume de cúpula numa máscara 2D qualquer (braço, tronco, chapéu), com a mesma
    luz das formas 3D: 4x maior, altura em cúpula pela distância à borda, luz de
    cima-esquerda e redução por maioria. Substitui o sombreado de travesseiro."""
    if not m.any():
        return m
    M = np.kron(m.astype(np.uint8), np.ones((S, S), np.uint8)).astype(bool)
    d = ndimage.distance_transform_edt(np.pad(M, 1))[1:-1, 1:-1]
    R = max(2.0, min(d.max(), 4.5 * S))
    u = np.clip(d / R, 0, 1)
    h = np.sqrt(np.clip(1 - (1 - u) ** 2, 0, 1)) * R
    h = ndimage.gaussian_filter(h, S * 0.5)
    gy, gx = np.gradient(h)
    nz = np.ones_like(h)
    nn = np.sqrt(gx * gx + gy * gy + nz)
    lum = np.clip((-gx * _L[0] - gy * _L[1] + nz * _L[2]) / nn, 0, 1)
    ys, xs = np.where(M)
    gyg = (np.arange(M.shape[0])[:, None] - ys.mean()) / max(4 * S, np.ptp(ys) + 1)
    v = np.clip(0.1 + 0.9 * lum - 0.25 * gyg + deslocar * 0.14, 0, 1)
    k = len(rampa)
    nivel = np.clip(np.floor(v * (k - 0.01)), 0, k - 1).astype(int)
    nivel = np.where(M, nivel, -1)
    H, W = m.shape
    bl = nivel.reshape(H, S, W, S).transpose(0, 2, 1, 3).reshape(H, W, S * S)
    cores = np.array([IDX[c] for c in rampa])
    novo = t.px.copy()
    ja = t.px != VAZIO
    borda = m & ~ndimage.binary_erosion(m)
    viz = ndimage.binary_dilation(ja & ~m)
    for y, x in zip(*np.where(m)):
        b = bl[y, x]
        b = b[b >= 0]
        if not len(b):
            continue
        n = np.bincount(b, minlength=k).argmax()
        novo[y, x] = cores[0] if (linha and borda[y, x] and viz[y, x]) else cores[n]
    t.px = novo
    return m
