"""Soldado contaminado da fase 2: soldado da Volante que mexeu na carcaça do disco.

Parte dos quadros do soldado (pixel/volante.txt) para manter porte e estilo, tira o
fuzil, troca a pele por verde doente com veias roxas, olho brilhando, farda podre e
rasgada, e acrescenta as partes bizarras (tumor com olho no ombro, queixo
desencaixado, braços de zumbi). Ataques: mordida de perto e vômito verde em arco.

    python3 tools/arte/contaminado.py   -> prévia em tools/arte/pixel/contaminado_previa.png
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import pixel  # noqa: E402
from motor import IDX, NOMES, RAIZ, VAZIO, Tela  # noqa: E402
from aliens import relevo, suave, domo  # noqa: E402

# Pele: verde doente com sombra roxa (troca índice por índice).
PELE = {
    "pele_sombra": "roxo_escuro", "pele_escura": "alien_profundo", "pele_media": "alien_esc",
    "pele": "alien_medio", "pele_luz": "alien", "pele_clara": "alien_luz", "pele_brilho": "alien_luz",
    "rosa_poeira": "roxo",
}
# Farda: mais escura e encardida.
FARDA = {}
CARNE_V = ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz"]
TUMOR = ["roxo_escuro", "vermelho_esc", "roxo", "rosa_poeira", "pele_luz"]
GOSMA = ["alien_esc", "alien", "alien_luz", "alien_brilho", "amarelo_claro"]
MANGA = ["caatinga_esc", "caatinga_media", "caatinga", "mandacaru", "mandacaru_luz"]


def base(nome):
    """Quadro da Volante sem o fuzil e sem as mãos dele (x >= 23 do peito para baixo)."""
    import repintar as rp
    t = rp.repintar_tela(pixel.ler("volante.txt")[nome])
    t.px[23:33, 22:] = VAZIO
    # Fecha o contorno do peito onde a arma encostava.
    cheio = t.px != VAZIO
    borda = ndimage.binary_dilation(cheio) & ~cheio
    borda[:23] = False
    borda[33:] = False
    t.px[borda] = IDX["sombra"]
    return t


def recolorir(t):
    tab = {IDX[a]: IDX[b] for a, b in {**PELE, **FARDA}.items()}
    px = t.px.copy()
    for a, b in tab.items():
        px[t.px == a] = b
    t.px = px
    return t


def ruido_pele(t, semente=3):
    rng = np.random.default_rng(semente)
    r = ndimage.gaussian_filter(rng.standard_normal((t.h, t.w)), 0.8)
    return r / (np.abs(r).max() + 1e-9)


def tumor(t, pulsa=0.0, morto=False):
    """Tumor de carne saindo da farda rasgada no ombro de trás e subindo pela nuca:
    gomos roxos e rosados molhados com fendas escuras, veias inchadas, pústulas verdes,
    três olhos de tamanhos diferentes (o grande vigia o Lampião) e fiapos pendurados."""
    p = pulsa
    gomos = [(9, 21.5, 5.2 + p, 4.6 + p), (4, 26, 3.6, 3.2), (12, 14.5, 3.6 + p * 0.5, 3.2),
             (3.5, 19, 3.0, 2.8), (13.5, 26.5, 2.8, 2.4), (6.5, 13.5, 2.6, 2.4)]
    ds = [((t.xx - x) / rx) ** 2 + ((t.yy - y) / ry) ** 2 for (x, y, rx, ry) in gomos]
    alturas = np.stack([np.sqrt(np.clip(1 - d, 0, 1)) * (rx * 0.7) for d, (_, _, rx, _) in zip(ds, gomos)])
    m = alturas.max(0) > 0
    rot = alturas.argmax(0)
    # Pano rasgado da farda em volta da base.
    base_ = t.elipse(9, 26, 6.5, 3.2) & ~m & (t.px != VAZIO)
    t.px[base_ & (np.sin(t.xx * 2.1) > 0.2)] = IDX["caatinga_esc"]
    # Cada gomo é uma bola molhada: luz de cima à esquerda, sombra embaixo, reflexo.
    RAMPA = ["roxo_escuro", "vermelho_esc", "vermelho_medio", "roxo", "rosa_poeira", "pele_luz", "pele_brilho"]
    nivel = np.zeros(m.shape, int)
    for i, (x, y, rx, ry) in enumerate(gomos):
        hx, hy = x - rx * 0.35, y - ry * 0.4
        d = np.hypot((t.xx - hx) / rx, (t.yy - hy) / ry)
        v = np.clip(1.05 - d / 1.3, 0, 0.999)
        aqui = m & (rot == i)
        nivel[aqui] = (v[aqui] * len(RAMPA)).astype(int)
        t.ponto(hx, hy, "branco")
    cores = np.array([IDX[c] for c in RAMPA])
    t.px[m] = cores[nivel[m]]
    for i, (x, y, rx, ry) in enumerate(gomos):
        t.ponto(x - rx * 0.35, y - ry * 0.4, "branco")
    # Fendas escuras entre os gomos.
    ordem = np.sort(alturas, axis=0)
    fenda = m & (ordem[-2] > 0.2) & (ordem[-1] - ordem[-2] < 0.35)
    t.px[fenda] = IDX["roxo_escuro"]
    # Veias inchadas: vermelho com brilho em cima.
    for pts in (((5, 28), (6, 25), (7, 23)), ((12.5, 18), (13.5, 16))):
        for (a, b) in zip(pts, pts[1:]):
            n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
            for s_ in np.linspace(0, 1, n * 2):
                x, y = a[0] + (b[0] - a[0]) * s_, a[1] + (b[1] - a[1]) * s_
                xi, yi = int(x), int(y)
                if m[yi, xi]:
                    t.px[yi, xi] = IDX["vermelho_medio"]
                    if m[yi - 1, xi] and not fenda[yi - 1, xi]:
                        t.px[yi - 1, xi] = IDX["vermelho"]
    # Pústulas verdes brilhando.
    for (x, y, r) in ((3, 24.5, 1.1), (13.5, 27, 0.9), (6.5, 14.5, 0.8), (2.5, 19.5, 0.8)):
        pm = t.elipse(x, y, r, r)
        relevo(t, pm, domo(t, x, y, r, r) * 2, ["alien_esc", "alien", "alien_luz", "alien_brilho"],
               ambiente=0.2, brilho=1.5, linha=False)
    # Olhos: o grande no gomo do meio olhando para a frente, dois pequenos.
    for (x, y, r, pupila) in ((10.5, 22, 2.2, True), (13, 14.5, 1.2, True), (4.5, 26.5, 1.0, False)):
        t.chapado(t.elipse(x, y, r + 0.7, r + 0.6), "vermelho_esc")
        if morto:
            t.chapado(t.elipse(x, y, r, r * 0.4), "roxo_escuro")
            continue
        t.chapado(t.elipse(x, y, r, r), "amarelo_claro")
        t.chapado(t.elipse(x + r * 0.3, y, r * 0.75, r * 0.85), "amarelo_fogo")
        if pupila:
            t.chapado(t.elipse(x + r * 0.45, y, max(0.5, r * 0.25), r * 0.7), "preto")
        t.ponto(x - r * 0.4, y - r * 0.4, "branco")
    # Fiapos de carne pendurados com gota.
    for (x, y, L) in ((3, 27, 3), (6, 28.5, 2)):
        t.linha(x, y, x - 0.5, y + L, "roxo")
        t.ponto(x - 0.5, y + L + 1, "alien_luz")
    return m


def capsulas(t, pts, r0, r1, rampa, amb=0.1, br=0.6):
    n = len(pts) - 1
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        ra = r0 + (r1 - r0) * k / n
        rb = r0 + (r1 - r0) * (k + 1) / n
        m = t.capsula(a[0], a[1], b[0], b[1], ra, rb)
        relevo(t, m, suave(m, 0.6) * 2.5, rampa, ambiente=amb, brilho=br, dither=False)


def contaminado(pose="parado", k=0, cabeca=True, tumor_=True, bracos=True):
    """pose: parado, anda (k 0-3), vomita, morde, grito, morte. Olha para a direita.
    cabeca=False: corpo sem cabeça (morte andando), com o toco do pescoço jorrando gosma."""
    nome = f"anda{k + 1}" if pose == "anda" else "parado"
    b0 = base(nome)
    pele0 = np.isin(b0.px, [IDX[c] for c in PELE if c != "rosa_poeira"])
    t = recolorir(b0)
    # Volume no rosto chapado (só nos pixels de pele base; nariz, olho e boca ficam).
    base4 = b0.px == IDX["pele"]
    Hp = suave(pele0, 1.6) * 4 + ruido_pele(t) * 0.35
    relevo(t, base4, Hp, ["alien_esc", "alien_medio", "alien_medio", "alien"], ambiente=0.0,
           contraste=1.2, linha=False, dither=False)
    # Bochecha chupada embaixo do olho.
    t.px[pele0 & t.elipse(18.5, 20.5, 1.6, 1.0)] = IDX["alien_profundo"]
    rng = np.random.default_rng(7 + k)
    cheio = t.px != VAZIO

    # Farda podre: manchas escuras, respingos de vômito e rasgos mostrando a pele.
    farda = np.isin(t.px, [IDX[c] for c in ("caatinga_media", "caatinga", "mandacaru", "mandacaru_luz")])
    for (x, y, r) in ((12, 27, 1.8), (16, 33, 1.5), (10, 38, 1.4)):
        m = t.elipse(x, y, r * 1.3, r) & farda
        t.chapado(m, "caatinga_esc")
        t.ponto(x - r * 0.5, y - r * 0.4, "couro_escuro")
    for (x, y) in ((17, 25), (18, 27), (16, 29), (19, 30)):
        if cheio[y, x]:
            t.ponto(x, y, "alien")
    t.ponto(17, 26, "alien_brilho")
    # Rasgo grande na farda mostrando as costelas: carne escura, ossos e gosma.
    rasgo = (t.elipse(13, 30.5, 3.4, 2.4) | t.elipse(11, 32, 2, 1.4)) & farda
    t.chapado(rasgo, "vermelho_esc")
    t.chapado(rasgo & t.elipse(13, 31, 2.4, 1.5), "roxo_escuro")
    for y in (29.5, 31.2, 33):
        for x in np.arange(10.5, 16, 0.5):
            yy = int(y + (x - 13) * 0.18)
            if rasgo[yy, int(x)]:
                t.px[yy, int(x)] = IDX["cinza_claro"] if x < 13.5 else IDX["cinza_luz"]
    borda = rasgo & ~ndimage.binary_erosion(rasgo)
    t.px[borda & (t.yy < 30.5)] = IDX["mandacaru_luz"]
    t.px[borda & (t.yy >= 30.5)] = IDX["caatinga_esc"]
    t.ponto(14, 34, "alien_luz")
    t.ponto(14, 35, "alien_brilho")

    # Veias roxas saltadas no pescoço.
    pele = np.isin(t.px, [IDX[c] for c in ("alien_medio", "alien", "alien_esc")])
    for (x, y) in ((13, 21), (14, 22), (14, 23), (16, 22), (11, 18), (11, 19), (12, 20)):
        if pele[y, x]:
            t.px[y, x] = IDX["roxo"]

    # Olho do soldado aceso em verde, sem pupila, com o brilho escorrendo.
    olho = t.px == IDX["branco"]
    olho[:, :18] = False
    olho[19:] = False
    t.px[olho] = IDX["alien_brilho"]
    t.ponto(22, 16, "alien_brilho")
    t.ponto(21, 17, "alien_luz")
    t.ponto(21, 18, "alien")

    if tumor_:
        tumor(t, pulsa=0.6 if (pose == "anda" and k % 2) or pose == "vomita" else 0.0, morto=pose == "morte")

    # Boca: queixo desencaixado pendurado, dentes e baba.
    if pose in ("vomita", "morde", "grito", "morte"):
        abre = {"vomita": 4.0, "morde": 3.2, "grito": 3.5, "morte": 3.0}[pose]
        boca = t.elipse(23.5, 20 + abre * 0.4, 2.6, abre)
        t.chapado(boca, "preto")
        t.chapado(t.elipse(23.5, 20.5 + abre * 0.6, 1.6, abre * 0.5) & boca, "vermelho_esc")
        for x in (22, 24, 26):
            t.ponto(x, 19.5 - abre * 0.2, "cinza_claro")
            t.ponto(x - 0.5, 20.5 + abre * 1.1, "cinza_luz")
    else:
        # Mandíbula desencaixada, pendurada torta: vão escuro, dentes de cima,
        # língua roxa caída e o queixo verde lá embaixo.
        t.chapado(t.elipse(24, 22, 2.4, 1.8), "preto")
        t.chapado(t.elipse(24.5, 22.8, 1.3, 0.9), "roxo")
        for x in (22.5, 24, 25.5):
            t.ponto(x, 20.6, "cinza_claro")
        queixo = t.elipse(23.5, 24.3, 2.6, 1.1, ang=0.25)
        relevo(t, queixo, domo(t, 23.5, 24.3, 2.6, 1.1) * 2, CARNE_V, ambiente=0.1, linha=True)
        for x in (22.5, 24.5):
            t.ponto(x, 23.3, "cinza_luz")
    t.linha(26, 24, 26, 27, "alien_luz")
    t.ponto(26, 28, "alien_brilho")

    # Braços de zumbi esticados para a frente (manga rasgada no cotovelo).
    if bracos:
        ofs = {"anda": (0, 1, 0, -1)[k], "morde": -3, "vomita": 2}.get(pose, 0)
        alto = pose in ("grito", "morte")
        for lado, (dx, amb) in enumerate(((0, -0.15), (2, 0.15))):
            om = (18 + dx, 26)
            co = (24 + dx, 27 + ofs * 0.3) if not alto else (25 + dx, 24 - dx)
            mao = (31 + dx, 28 + ofs * 0.5) if not alto else (31 + dx, 18 - dx * 1.5)
            capsulas(t, [om, co], 2.0, 1.7, MANGA, amb=amb)
            capsulas(t, [co, mao], 1.4, 1.0, CARNE_V, amb=amb, br=0.9)
            # Dedos compridos pendurados com unhas escuras.
            hx, hy = mao
            dedos = ((3, 2), (3.5, 3.5), (2.5, 4.5)) if not alto else ((1.5, -3), (3, -2), (3.5, 0))
            for (a, b) in dedos:
                capsulas(t, [(hx, hy), (hx + a, hy + b)], 0.6, 0.45, CARNE_V, amb=amb)
                t.ponto(hx + a * 1.2, hy + b * 1.2, "couro_profundo")
        # Pano rasgado pendurado na manga.
        t.linha(23, 29 + ofs * 0.3, 23, 31 + ofs * 0.3, "caatinga_esc")

    if pose == "vomita":
        # Golfada saindo da boca (o projétil em arco sai no jogo): grossa, em gomos,
        # com pedaços e respingos.
        for (x, y, r) in ((27, 21, 1.8), (29.5, 21, 2.4), (32.5, 21.5, 2.8), (35.5, 22.5, 2.5), (38, 24, 2.0)):
            m = t.elipse(x, y, r, r * 0.85)
            relevo(t, m, domo(t, x, y, r, r * 0.85) * 3, GOSMA, ambiente=0.0, brilho=1.6, linha=False)
        for (x, y) in ((31, 21), (34, 22), (36, 23)):
            t.ponto(x, y, "couro")
        for (x, y) in ((34, 17), (39, 19), (41, 26), (36, 27), (30, 25)):
            t.ponto(x, y, "alien_luz")
        t.ponto(42, 22, "alien_brilho")
        # Bochechas estufadas e o corpo dando o tranco.
        t.chapado(t.elipse(19.5, 19, 1.6, 1.3), "alien_luz")

    if pose == "morte":
        # Olho apagado.
        olho = t.px == IDX["alien_brilho"]
        olho[:, :18] = False
        t.px[olho] = IDX["cinza"]

    if not cabeca:
        # Sem cabeça: apaga do pescoço para cima (o tumor fica, o olho dele ainda vigia)
        # e o toco jorra gosma verde para cima.
        cab = (t.yy < 22.5) & (t.xx > 13.5) | (t.yy < 13)
        tum_m = np.isin(t.px, [IDX[c] for c in ("roxo_escuro", "vermelho_esc", "vermelho_medio", "roxo",
                                                  "rosa_poeira", "pele_luz", "pele_brilho", "amarelo_fogo",
                                                  "amarelo_claro", "preto", "branco", "vermelho")]) & (t.xx < 16)
        t.px[cab & ~tum_m] = VAZIO
        toco = t.elipse(18, 23, 3.2, 1.6)
        relevo(t, toco, domo(t, 18, 23, 3.2, 1.6) * 2, ["roxo_escuro", "vermelho_esc", "vermelho_medio", "rosa_poeira"],
               ambiente=0.1, linha=False)
        t.chapado(t.elipse(18.5, 22.6, 1.0, 0.6), "cinza_claro")
        jato = [(18, 20.5, 2.2), (17.5, 17.5, 2.0), (18.5, 14.5, 1.7), (17.5, 11.5, 1.4), (19, 9, 1.1)]
        for (x, y, r) in jato[: 4 + k % 2]:
            m = t.elipse(x, y + (k % 2), r, r * 1.2)
            relevo(t, m, domo(t, x, y, r, r * 1.2) * 2, GOSMA, ambiente=0.1, brilho=1.5, linha=False)
        for (x, y) in ((15, 13), (21, 15), (14, 17), (22, 10)):
            t.ponto(x, y + k % 2, "alien_luz")

    if pose in ("morde", "vomita"):
        # Bote para a frente: cabeça e ombros avançam (mordida mais, golfada menos).
        d = 3 if pose == "morde" else 1
        topo = t.px[0:25].copy()
        t.px[0:25] = VAZIO
        t.px[0:25, d:] = np.where(topo[:, :-d] != VAZIO, topo[:, :-d], t.px[0:25, d:])
    t.contorno("sombra")
    return t


def cabeca_solta():
    """Cabeça arrancada que voa girando (quepe, olho aceso, mandíbula pendurada e o toco)."""
    c = contaminado("parado", tumor_=False, bracos=False)
    t = Tela(24, 22)
    for y in range(22):
        for x in range(24):
            yy, xx = y + 3, x + 8
            if yy < 24 and (yy < 22 or xx > 14) and c.px[yy, xx] != VAZIO:
                t.px[y, x] = c.px[yy, xx]
    toco = t.elipse(12, 20, 4, 1.4)
    t.chapado(toco & (t.px != VAZIO), "vermelho_esc")
    t.chapado(t.elipse(11, 20, 1.2, 0.6), "cinza_claro")
    t.contorno("sombra")
    return t


def previa(saida):
    from PIL import Image
    import repintar as rp
    sold = rp.repintar_tela(pixel.ler("volante.txt")["parado"]).imagem()
    ims = [sold] + [contaminado(p).imagem() for p in ("parado", "vomita", "morde")] + \
          [contaminado("anda", k).imagem() for k in (0, 2)]
    W = sum(i.width for i in ims) + 8 * (len(ims) + 1)
    H = max(i.height for i in ims) + 8
    o = Image.new("RGBA", (W, H), (176, 142, 102, 255))
    x = 8
    for i in ims:
        o.alpha_composite(i, (x, H - 4 - i.height))
        x += i.width + 8
    o.resize((W * 4, H * 4), Image.NEAREST).save(saida)
    return saida


if __name__ == "__main__":
    print(previa(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "tools/arte/pixel/contaminado_previa.png"))
