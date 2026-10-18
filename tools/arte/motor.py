"""Motor de pixel art por script.

Desenha formas (elipses, cápsulas, polígonos), dá volume com luz vinda de cima
à esquerda, contorna e aplica textura, sempre só com cores da paleta.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = Path(__file__).resolve().parents[2]
CORES = json.loads((RAIZ / "assets/paleta.json").read_text())["cores"]
NOMES = list(CORES)
IDX = {n: i for i, n in enumerate(NOMES)}
RGB = np.array([[int(CORES[n][i:i + 2], 16) for i in (1, 3, 5)] for n in NOMES], dtype=np.uint8)
VAZIO = -1

# Rampas do escuro para o claro.
RAMPAS = {
    "pele": ["couro", "pele_escura", "pele", "pele_clara"],
    "couro": ["couro_escuro", "couro", "couro_claro", "barro"],
    "chapeu": ["couro_escuro", "couro", "couro_claro", "barro", "areia"],
    "caqui": ["terra_escura", "terra", "barro", "areia", "areia_clara"],
    "mescla": ["sombra", "azul_sombra", "cinza_escuro", "cinza"],
    "metal": ["sombra", "cinza_escuro", "cinza", "cinza_claro", "branco"],
    "aco": ["sombra", "azul_sombra", "cinza_escuro", "cinza"],
    "vermelho": ["vermelho_esc", "vermelho", "laranja_fogo"],
    "ouro": ["couro", "laranja_fogo", "amarelo_fogo", "branco"],
    "alien": ["sombra", "alien_esc", "alien", "alien_brilho"],
    "cabelo": ["preto", "sombra", "couro_escuro", "couro"],
    "azul": ["sombra", "azul_sombra", "ceu_escuro", "ceu"],
    "pedra": ["sombra", "azul_sombra", "cinza_escuro", "cinza", "cinza_claro"],
    "terra": ["terra_escura", "terra", "barro", "areia", "areia_clara"],
    "verde": ["sombra", "caatinga_esc", "caatinga", "mandacaru"],
    "nuvem": ["ceu_claro", "horizonte", "branco"],
    "branco": ["cinza_claro", "branco"],
    "escuro": ["preto", "sombra"],
}

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def i(nome):
    return IDX[nome]


class Tela:
    """Imagem de índices da paleta; -1 é transparente."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = np.full((h, w), VAZIO, dtype=np.int16)
        self.dono = np.zeros((h, w), dtype=np.int16)  # qual camada pintou cada pixel
        self.camadas = 0
        yy, xx = np.mgrid[0:h, 0:w]
        self.xx, self.yy = xx + 0.5, yy + 0.5

    # ---------- máscaras ----------
    def elipse(self, cx, cy, rx, ry, ang=0.0):
        c, s = np.cos(-ang), np.sin(-ang)
        dx, dy = self.xx - cx, self.yy - cy
        u, v = dx * c - dy * s, dx * s + dy * c
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1.0

    def capsula(self, x0, y0, x1, y1, r0, r1=None):
        r1 = r0 if r1 is None else r1
        px, py = self.xx - x0, self.yy - y0
        vx, vy = x1 - x0, y1 - y0
        L2 = max(vx * vx + vy * vy, 1e-6)
        t = np.clip((px * vx + py * vy) / L2, 0, 1)
        d = np.hypot(px - t * vx, py - t * vy)
        return d <= r0 + (r1 - r0) * t

    def poligono(self, pts):
        x, y = self.xx, self.yy
        dentro = np.zeros_like(x, dtype=bool)
        n = len(pts)
        for k in range(n):
            xa, ya = pts[k]
            xb, yb = pts[(k + 1) % n]
            cond = ((ya > y) != (yb > y))
            xint = (xb - xa) * (y - ya) / ((yb - ya) + 1e-9) + xa
            dentro ^= cond & (x < xint)
        return dentro

    def retangulo(self, x, y, w, h):
        return (self.xx >= x) & (self.xx < x + w) & (self.yy >= y) & (self.yy < y + h)

    # ---------- pintura ----------
    def cel(self, mascara, rampa, sombra=2, luz=1, linha=True, deslocar=0, rebaixo=False):
        """Sombreamento em faixas: luz vem de cima à esquerda.

        A rampa vai do escuro ao claro: [..., sombra, base, luz]. "deslocar"
        escurece (negativo) ou clareia a peça inteira em degraus da rampa.
        """
        if not mascara.any():
            return mascara
        rampa = RAMPAS[rampa] if isinstance(rampa, str) else rampa
        k = len(rampa)
        def dentro(dx, dy):
            m = np.pad(mascara, 4)
            h, w = mascara.shape
            return m[4 + dy:4 + dy + h, 4 + dx:4 + dx + w]
        base = k - 2
        nivel = np.full(mascara.shape, base, dtype=int)
        if sombra:
            somb = np.zeros_like(mascara)
            for s_ in range(1, sombra + 1):
                somb |= ~dentro(s_, s_) | ~dentro(0, s_)
            nivel[somb] = base - 1
            if rebaixo:
                fundo = ~dentro(1, 1) | ~dentro(0, 1)
                nivel[fundo] = max(base - 2, 0)
        if luz:
            ilum = np.zeros_like(mascara)
            for l_ in range(1, luz + 1):
                ilum |= ~dentro(-l_, -l_) & dentro(l_, l_) & dentro(0, l_)
            nivel[ilum & mascara] = base + 1
        nivel = np.clip(nivel + int(deslocar), 0, k - 1)
        cores = np.array([IDX[c] for c in rampa])[nivel]
        self.camadas += 1
        if linha:
            borda = mascara & ~ndimage.binary_erosion(mascara)
            ja = self.px != VAZIO
            vizinho = ndimage.binary_dilation(ja & ~mascara)
            cores = np.where(borda & vizinho, IDX[rampa[0]], cores)
        self.px[mascara] = cores[mascara]
        self.dono[mascara] = self.camadas
        return mascara

    def volume(self, mascara, rampa, luz=(-0.55, -0.75), achatado=3.0, suave=1.2,
               ambiente=0.2, brilho=1.0, linha=True, textura=0.0, semente=0, deslocar=0.0):
        """Pinta a máscara com volume (normal estimada pela distância à borda)."""
        if not mascara.any():
            return mascara
        rampa = RAMPAS[rampa] if isinstance(rampa, str) else rampa
        dist = ndimage.distance_transform_edt(np.pad(mascara, 1))[1:-1, 1:-1]
        altura = np.minimum(dist, achatado)
        altura = ndimage.gaussian_filter(altura, suave)
        gy, gx = np.gradient(altura)
        lx, ly = luz
        lz = 0.7
        nl = np.sqrt(lx * lx + ly * ly + lz * lz)
        n = np.sqrt(gx * gx + gy * gy + 1.0)
        lum = (-gx * lx - gy * ly + lz) / (n * nl)
        lum = (lum - 0.35) * 1.6 * brilho + ambiente + deslocar
        if textura:
            rng = np.random.default_rng(semente)
            ruido = ndimage.gaussian_filter(rng.standard_normal(mascara.shape), 0.7)
            lum = lum + ruido * textura
        k = len(rampa)
        v = np.clip(lum, 0, 0.999) * k
        base = np.floor(v)
        frac = v - base
        h, w = mascara.shape
        limiar = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
        # Dither só numa faixa estreita da transição, para não virar ruído.
        sobe = (frac > 0.78) & (limiar < (frac - 0.78) * 4.5)
        nivel = np.clip(base + sobe, 0, k - 1).astype(int)
        cores = np.array([IDX[c] for c in rampa])[nivel]

        self.camadas += 1
        if linha:
            # Borda da camada encostando em algo já pintado vira linha interna escura.
            borda = mascara & ~ndimage.binary_erosion(mascara)
            ja = self.px != VAZIO
            vizinho = ndimage.binary_dilation(ja & ~mascara)
            cores = np.where(borda & vizinho, IDX[rampa[0]], cores)
        self.px[mascara] = cores[mascara]
        self.dono[mascara] = self.camadas
        return mascara

    def chapado(self, mascara, cor):
        self.px[mascara] = IDX[cor]
        return mascara

    def ponto(self, x, y, cor):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y, x] = IDX[cor]

    def pontos(self, lista, cor):
        for x, y in lista:
            self.ponto(x, y, cor)

    def linha(self, x0, y0, x1, y1, cor):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for t in np.linspace(0, 1, n):
            self.ponto(int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)), cor)

    def contorno(self, cor="sombra", fundo_escuro=None):
        """Contorno externo de 1 px em volta de tudo."""
        cheio = self.px != VAZIO
        fora = ndimage.binary_dilation(cheio, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & ~cheio
        self.px[fora] = IDX[cor]

    def colar(self, outra, x, y):
        h, w = outra.px.shape
        for yy in range(h):
            ty = y + yy
            if not 0 <= ty < self.h:
                continue
            for xx in range(w):
                tx = x + xx
                if 0 <= tx < self.w and outra.px[yy, xx] != VAZIO:
                    self.px[ty, tx] = outra.px[yy, xx]

    def espelhar(self):
        t = Tela(self.w, self.h)
        t.px = self.px[:, ::-1].copy()
        return t

    def imagem(self):
        rgba = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        m = self.px != VAZIO
        rgba[m, :3] = RGB[self.px[m]]
        rgba[m, 3] = 255
        return Image.fromarray(rgba, "RGBA")

    def salvar(self, caminho, escala=1):
        img = self.imagem()
        if escala != 1:
            img = img.resize((self.w * escala, self.h * escala), Image.NEAREST)
        img.save(caminho)


def folha(quadros, caminho):
    """Junta quadros do mesmo tamanho lado a lado numa spritesheet."""
    w, h = quadros[0].w, quadros[0].h
    img = Image.new("RGBA", (w * len(quadros), h))
    for k, q in enumerate(quadros):
        img.paste(q.imagem(), (k * w, 0))
    img.save(caminho, optimize=True)
