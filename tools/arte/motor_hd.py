"""Motor de alta definição: desenha 4x maior com sombreamento suave e reduz
para o tamanho do jogo, convertendo para a paleta com pontilhado ordenado.

O resultado tem mais tons e volume (estilo Metal Slug) do que o motor de
faixas, mantendo só cores da paleta.
"""
import numpy as np
from scipy import ndimage

from motor import BAYER4, IDX, VAZIO, Tela

# Rampas do escuro para o claro, com mais degraus.
RAMPAS_HD = {
    "pele": ["pele_escura", "pele", "pele", "pele_clara", "pele_clara"],
    "caqui": ["terra", "barro", "areia", "areia", "areia_clara"],
    "couro": ["couro_escuro", "couro", "couro", "couro_claro", "barro"],
    "chapeu": ["couro", "couro_claro", "couro_claro", "barro", "areia"],
    "mescla": ["azul_sombra", "cinza_escuro", "cinza_escuro", "cinza", "cinza_claro"],
    "metal": ["preto", "sombra", "cinza_escuro", "cinza", "cinza_claro", "branco"],
    "madeira": ["couro_escuro", "couro", "couro", "couro_claro", "barro"],
    "vermelho": ["sombra", "vermelho_esc", "vermelho", "laranja_fogo", "amarelo_fogo"],
    "ouro": ["couro", "laranja_fogo", "amarelo_fogo", "branco"],
    "cabelo": ["preto", "sombra", "azul_sombra", "cinza_escuro"],
    "azul": ["sombra", "azul_sombra", "ceu_escuro", "ceu", "ceu_claro"],
    "oliva": ["sombra", "caatinga_esc", "caatinga", "mandacaru", "areia_clara"],
    "alien": ["sombra", "alien_esc", "alien", "alien_brilho", "branco"],
    "branco": ["azul_sombra", "cinza", "cinza_claro", "branco"],
    "vidro": ["ceu_escuro", "ceu", "ceu_claro", "horizonte", "branco"],
    "preto": ["preto", "sombra", "azul_sombra"],
}


class TelaHD:
    """Coordenadas sempre no tamanho final (1x); internamente usa escala E."""

    def __init__(self, w, h, escala=4):
        self.w, self.h, self.E = w, h, escala
        W, H = w * escala, h * escala
        self.mat = np.full((H, W), -1, dtype=np.int16)
        self.lum = np.zeros((H, W), dtype=np.float32)
        self.materiais = []
        yy, xx = np.mgrid[0:H, 0:W]
        self.xx = (xx + 0.5) / escala
        self.yy = (yy + 0.5) / escala
        self.extras = []  # pixels fixos aplicados depois da redução

    # ---- formas (mesma API do motor 1x)
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
        return np.hypot(px - t * vx, py - t * vy) <= r0 + (r1 - r0) * t

    def poligono(self, pts):
        x, y = self.xx, self.yy
        dentro = np.zeros_like(x, dtype=bool)
        n = len(pts)
        for k in range(n):
            xa, ya = pts[k]
            xb, yb = pts[(k + 1) % n]
            cond = (ya > y) != (yb > y)
            xint = (xb - xa) * (y - ya) / ((yb - ya) + 1e-9) + xa
            dentro ^= cond & (x < xint)
        return dentro

    def retangulo(self, x, y, w, h):
        return (self.xx >= x) & (self.xx < x + w) & (self.yy >= y) & (self.yy < y + h)

    # ---- pintura
    def pintar(self, mascara, rampa, achatado=1.6, suave=0.9, luz=(-0.6, -0.8), brilho=0.0,
               dobras=0.0, dobras_ang=0.0, textura=0.0, semente=0, oclusao=0.35):
        """Pinta uma peça com volume. Parâmetros em pixels finais (1x)."""
        if not mascara.any():
            return mascara
        E = self.E
        if rampa not in self.materiais:
            self.materiais.append(rampa)
        mid = self.materiais.index(rampa)
        dist = ndimage.distance_transform_edt(np.pad(mascara, 1))[1:-1, 1:-1] / E
        altura = ndimage.gaussian_filter(np.minimum(dist, achatado), suave * E)
        gy, gx = np.gradient(altura * E)
        lx, ly = luz
        lz = 0.75
        nl = np.sqrt(lx * lx + ly * ly + lz * lz)
        n = np.sqrt(gx * gx + gy * gy + 1.0)
        lum = (-gx * lx - gy * ly + lz) / (n * nl)
        # Reflexo especular duro, típico do Metal Slug.
        lum = lum + np.clip(lum - 0.9, 0, 1) * 2.5
        if dobras:
            # Dobras de roupa: listras suaves na direção dada.
            c, s = np.cos(dobras_ang), np.sin(dobras_ang)
            u = self.xx * c + self.yy * s
            lum = lum + np.sin(u * 2.1 + semente) * dobras * (ndimage.gaussian_filter(
                np.random.default_rng(semente).standard_normal(mascara.shape), 3 * E) * 8)
        if textura:
            r = np.random.default_rng(semente + 1).standard_normal(mascara.shape)
            lum = lum + ndimage.gaussian_filter(r, 0.35 * E) * textura * 6
        # Oclusão: escurece onde a peça encosta em algo já pintado embaixo dela.
        if oclusao:
            ja = self.mat >= 0
            perto = ndimage.gaussian_filter((ja & ~mascara).astype(np.float32), 0.6 * E)
            lum = lum - perto * oclusao
        self.mat[mascara] = mid
        self.lum[mascara] = (lum + brilho)[mascara]
        return mascara

    def ponto(self, x, y, cor):
        self.extras.append((int(x), int(y), cor))

    def pontos(self, lista, cor):
        for x, y in lista:
            self.ponto(x, y, cor)

    def linha(self, x0, y0, x1, y1, cor):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for t in np.linspace(0, 1, n):
            self.ponto(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), cor)

    def chapado(self, mascara, cor):
        """Área de cor fixa (olhos, botões): aplicada depois da redução."""
        E = self.E
        H, W = self.h, self.w
        m = mascara.reshape(H, E, W, E).mean(axis=(1, 3)) >= 0.5
        for y, x in zip(*np.where(m)):
            self.extras.append((x, y, cor))

    # ---- redução para 1x
    def reduzir(self, contorno="sombra", linhas_internas=True, contraste=1.0):
        E, H, W = self.E, self.h, self.w
        t = Tela(W, H)
        mat_bloco = self.mat.reshape(H, E, W, E).transpose(0, 2, 1, 3).reshape(H, W, E * E)
        lum_bloco = self.lum.reshape(H, E, W, E).transpose(0, 2, 1, 3).reshape(H, W, E * E)
        cobertura = (mat_bloco >= 0).mean(axis=2)
        cheio = cobertura >= 0.45
        # Material: o mais frequente no bloco.
        mat1 = np.full((H, W), -1, dtype=int)
        lum1 = np.zeros((H, W))
        for y, x in zip(*np.where(cheio)):
            m = mat_bloco[y, x]
            m = m[m >= 0]
            vals, cont = np.unique(m, return_counts=True)
            mm = vals[np.argmax(cont)]
            mat1[y, x] = mm
            lum1[y, x] = lum_bloco[y, x][mat_bloco[y, x] == mm].mean()
        limiar = np.tile(BAYER4, (H // 4 + 1, W // 4 + 1))[:H, :W]
        for mid, rampa in enumerate(self.materiais):
            nomes = RAMPAS_HD[rampa] if isinstance(rampa, str) else rampa
            k = len(nomes)
            m = mat1 == mid
            v = np.clip((lum1 - 0.6) * 1.25 * contraste + 0.62, 0, 0.999) * k
            base = np.floor(v)
            frac = v - base
            sobe = (frac > 0.8) & (limiar < (frac - 0.8) * 5)
            nivel = np.clip(base + sobe, 0, k - 1).astype(int)
            idx = np.array([IDX[c] for c in nomes])[nivel]
            t.px[m] = idx[m]
            if linhas_internas:
                # Linha escura onde este material encosta em outro desenhado por cima/baixo.
                borda = m & ~ndimage.binary_erosion(m)
                vizinho_outro = ndimage.binary_dilation((mat1 >= 0) & ~m)
                linha = borda & vizinho_outro & (nivel <= 1)
                t.px[linha] = IDX[nomes[0]]
        for x, y, cor in self.extras:
            if 0 <= x < W and 0 <= y < H:
                t.px[y, x] = IDX[cor]
        if contorno:
            t.contorno(contorno)
        return t
