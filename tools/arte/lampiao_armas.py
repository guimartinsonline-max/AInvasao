"""Lampião segurando cada arma pesada do jeito dela, quadro a quadro, no
estilo Metal Slug:

- Madsen: no quadril, com as duas mãos.
- Bacamarte: baixo, na cintura, com as duas mãos.
- Papo-amarelo: no ombro, mirando com o rosto colado na coronha.
- Rojão: apoiado no ombro.
- Desintegrador: numa mão só, braço esticado, como pistola.
- Candeeiro: lata de querosene nas costas e o bico nas mãos.
- Baladeira: braço esticado segurando a forquilha e a outra mão puxando a liga.
- Buscapé: na altura do peito, com as duas mãos.

Mirando para cima, a arma fica de pé nas duas mãos.
Usa os blocos de tools/arte/lampiao_px.py e as armas de tools/arte/armas.py.
Chamado por tools/arte/exportar.py, que gera assets/sprites/lampiao_<arma>.png
e src/maos.js (de onde sai o tiro em cada pose).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import armas as ar  # noqa: E402
import lampiao_px as lp  # noqa: E402
import pixel  # noqa: E402

PE = (14, 45)  # pé do Lampião no quadro
MANGA = "uyytte"  # tons da manga (claro -> escuro)
OMBRO_FRENTE = (17, 22)
OMBRO_TRAS = (11, 22)

QUADROS = ["parado", "atirando", "corre1", "corre2", "corre3", "corre4", "corre5", "corre6",
           "pulo", "agachado", "mira_cima", "susto", "arremesso", "facada", "facada1", "mira_baixo", "recarga",
           "morte1", "morte2", "morte3"]
ROSTO = {"parado": "serio", "agachado": "serio", "susto": "susto", "mira_baixo": "baixo", "mira_cima": "cima"}
# Braço de trás erguido atirando a granada (por cima do ombro, como no Metal Slug).
ARREMESSO = {"cotovelo": (4, 15), "mao": (5, 3)}


def braco_arremesso(g, dy):
    """Braço de trás erguido, com a mão fechada lá em cima (vai antes da cabeça)."""
    braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (ARREMESSO["cotovelo"][0], ARREMESSO["cotovelo"][1] + dy),
          (ARREMESSO["mao"][0], ARREMESSO["mao"][1] + dy), escurecer=1)


def arremesso_base():
    """Quadro de arremesso do Lampião com o fuzil padrão."""
    g, dy, _ = base("parado")
    braco_arremesso(g, dy)
    for y, x, txt in lp.TRONCO + lp.FUZIL_FRENTE:
        lp.pintar(g, y + dy, x, txt)
    for k, txt in enumerate(lp.ROSTOS["grito"]):
        lp.pintar(g, 8 + k + dy, 7, txt)
    for k, txt in enumerate(lp.CHAPEU):
        lp.pintar(g, 1 + k + dy, 4, txt)
    for y, x, txt in lp.BRACO_FRENTE:
        lp.pintar(g, y + dy, x, txt)
    punho_fechado(g, ARREMESSO["mao"][0], ARREMESSO["mao"][1] + dy)
    return pixel.de_texto("\n".join("".join(l) for l in g), w=lp.W, h=lp.H)

# Pose de cada arma (coordenadas do bloco, antes do deslocamento dy):
# punho: onde a mão de trás fecha no punho da arma.
# cot_tras / cot_frente: cotovelos. apoio: se a mão da frente segura o apoio da arma.
# recorte: (x0, x1) parte do desenho da arma que vai na mão; costas: parte nas costas.
POSES = {
    "pistola": {"punho": (27, 22), "cot_frente": (22, 24), "um_braco": True},
    "madsen": {"punho": (25, 27), "cot_tras": (15, 28), "cot_frente": (22, 27), "apoio": True},
    "bacamarte": {"punho": (22, 29), "cot_tras": (13, 29), "cot_frente": (20, 29), "apoio": True},
    "papo_amarelo": {"punho": (19, 22), "cot_tras": (13, 27), "cot_frente": (22, 26), "apoio": True},
    "rojao": {"punho": (14, 26), "cot_tras": (10, 28), "cot_frente": (19, 27), "apoio": True},
    "desintegrador": {"punho": (23, 23), "cot_frente": (20, 24), "um_braco": True},
    "candeeiro": {"punho": (24, 28), "cot_tras": (15, 28), "cot_frente": (21, 28), "apoio": True,
                  "recorte": (9, 30), "costas": (1, 10)},
    "estilingue": {"punho": (27, 21), "cot_frente": (22, 22), "um_braco": True, "puxa": (19, 19), "recorte": (8, 17)},
    "buscape": {"punho": (22, 25), "cot_tras": (14, 28), "cot_frente": (20, 27), "apoio": True},
}


def linhas_da_arma(tela, girar=False, recorte=None):
    linhas = pixel.para_texto(tela).split("\n")
    if recorte:
        x0, x1 = recorte
        linhas = ["." * x0 + l[x0:x1] + "." * (len(l) - x1) for l in linhas]
    if not girar:
        return linhas
    if girar == "baixo":
        # Gira 90 graus no sentido horário: o cano passa a apontar para baixo.
        h = len(linhas)
        return ["".join(linhas[h - 1 - x][y] for x in range(h)) for y in range(len(linhas[0]))]
    # Gira 90 graus no sentido anti-horário: o cano passa a apontar para cima.
    w = len(linhas[0])
    return ["".join(linhas[x][w - 1 - y] for x in range(len(linhas))) for y in range(w)]


def contornar(g, mascara):
    """Contorno de 1 px em volta da peça, inclusive por cima do que já estava pintado."""
    m = np.pad(mascara, 1)
    viz = m[:-2, 1:-1] | m[2:, 1:-1] | m[1:-1, :-2] | m[1:-1, 2:]
    for y, x in zip(*np.where(viz & ~mascara)):
        g[y][x] = "O"


def braco(g, ombro, cotovelo, mao, escurecer=0):
    """Braço de manga de algodão em dois segmentos (sem a mão). Vai atrás da
    arma; a mão fechada é pintada depois, por cima do punho da arma."""
    forma = (lp.H, lp.W)
    c1, l1 = lp.segmento(forma, (ombro[0] + 0.5, ombro[1] + 0.5), (cotovelo[0] + 0.5, cotovelo[1] + 0.5), 1.9)
    c2, l2 = lp.segmento(forma, (cotovelo[0] + 0.5, cotovelo[1] + 0.5), (mao[0] + 0.5, mao[1] + 0.5), 1.6)
    lp.pintar_tons(g, c1, l1, MANGA, escurecer)
    lp.pintar_tons(g, c2 & ~c1, l2, MANGA, escurecer)
    contornar(g, c1 | c2)


def punho_fechado(g, x, y):
    """Mão fechada em volta da arma: dedos por cima, com contorno."""
    for k, l in enumerate(["OOOO", "O556O", "O344O", ".OOO"]):
        lp.pintar(g, y - 1 + k, x - 1, l)


def base(nome):
    """Pernas, tronco, rosto e chapéu, sem braços nem arma."""
    rosto = ROSTO.get(nome, "grito")
    pernas = nome if nome.startswith("corre") or nome in ("pulo", "agachado") else "parado"
    if nome == "mira_baixo":
        pernas = "pulo"
    g = [["."] * lp.W for _ in range(lp.H)]
    tras, frente, dy = lp.POSES_PERNAS[pernas]
    dy += lp.MARGEM
    qy = lp.QUADRIL_Y + dy
    lp.perna(g, (11, qy), *tras, atras=True)
    lp.perna(g, (16, qy), *frente, atras=False)
    return g, dy, rosto


def cabeca(g, dy, rosto, baixa=0):
    """baixa: cabeça curvada para a frente e para baixo (olhando o chão)."""
    for y, x, txt in lp.TRONCO:
        lp.pintar(g, y + dy, x, txt)
    for k, txt in enumerate(lp.ROSTOS[rosto]):
        lp.pintar(g, 8 + k + dy + baixa, 7 + baixa, txt)
    for k, txt in enumerate(lp.CHAPEU):
        lp.pintar(g, 1 + k + dy + baixa, 4 + baixa, txt)


def quadro_morte(nome):
    """Morte do Lampião, sem arma (ela cai da mão), como no Metal Slug:
    morte1: levou o tiro, voa para trás de braços para cima com careta de dor (o chapéu voa à parte);
    morte2 e morte3: estatelado de costas no chão, olhos em X (no 3 com a língua de fora)."""
    if nome == "morte1":
        g, dy, _ = base("pulo")
        braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (6, 15 + dy), (5, 8 + dy), escurecer=1)
        for y, x, txt in lp.TRONCO:
            lp.pintar(g, y + dy, x, txt)
        for k, txt in enumerate(lp.ROSTOS["dor"]):
            lp.pintar(g, 8 + k + dy, 7, txt)
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (25, 15 + dy), (29, 9 + dy))
        punho_fechado(g, 5, 8 + dy)
        punho_fechado(g, 29, 9 + dy)
        return pixel.de_texto("\n".join("".join(l) for l in g), w=lp.W, h=lp.H)
    # Deitado de costas, estatelado: desenhado "em pé" com as pernas esticadas e os
    # braços jogados para trás da cabeça, sem o chapéu (ele cai à parte), e girado
    # 90 graus. Assim as costas ficam retas no chão e as alpercatas apontam para o céu.
    g = [["."] * lp.W for _ in range(lp.H)]
    dy = lp.MARGEM
    qy = lp.QUADRIL_Y + dy
    lp.perna(g, (11, qy), (-1, 5), (-1, 9), atras=True)
    lp.perna(g, (16, qy), (1, 5), (2, 9) if nome == "morte2" else (5, 4), atras=False)
    braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (8, 14 + dy), (7, 6 + dy), escurecer=1)
    for y, x, txt in lp.TRONCO:
        lp.pintar(g, y + dy, x, txt)
    for k, txt in enumerate(lp.ROSTOS["morto" if nome == "morte2" else "morto2"]):
        lp.pintar(g, 8 + k + dy, 7, txt)
    braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (21, 14 + dy), (23, 6 + dy))
    punho_fechado(g, 7, 6 + dy)
    punho_fechado(g, 23, 6 + dy)
    arr = np.array(g)
    rot = np.rot90(arr, 1)  # anti-horário: a cabeça vai para a esquerda, as costas para baixo
    cheio = rot != "."
    linhas, colunas = np.where(cheio)
    saida = np.full((lp.H, lp.W), ".", dtype=rot.dtype)
    desce = (lp.H - 1) - linhas.max()
    esq = (lp.W - (colunas.max() - colunas.min() + 1)) // 2 - colunas.min()
    for y, x in zip(linhas, colunas):
        ny, nx = y + desce, x + esq
        if 0 <= ny < lp.H and 0 <= nx < lp.W:
            saida[ny, nx] = rot[y, x]
    return pixel.de_texto("\n".join("".join(l) for l in saida), w=lp.W, h=lp.H)


def chapeu():
    """Chapéu de couro do Lampião sozinho (voa da cabeça quando ele morre)."""
    return pixel.de_texto("\n".join(lp.CHAPEU), w=len(lp.CHAPEU[0]), h=len(lp.CHAPEU))


def puxa_baladeira(nome, pose):
    """Onde a mão de trás segura a pedra na liga: perto da forquilha (parado), puxada até
    o rosto (recarga, mirando) ou aberta depois de soltar (atirando)."""
    px_, py_ = pose["puxa"]
    if nome == "recarga":
        return px_, py_
    if nome == "atirando":
        return px_ - 2, py_ + 2
    return pose["punho"][0] - 7, pose["punho"][1] + 3


def quadro(nome, arma, bocas=None):
    tela = ar.ARMAS[arma]()
    px, py = ar.PUNHO[arma]
    ax, ay = ar.APOIO[arma]
    bx, by = ar.BOCA[arma]
    pose = POSES[arma]
    g, dy, rosto = base(nome)

    if nome.startswith("morte"):
        return quadro_morte(nome)

    if nome == "mira_cima":
        # Arma de pé nas duas mãos, na frente do rosto, com a cabeça inclinada para trás olhando o alto.
        cabeca(g, dy, rosto, baixa=-2)
        linhas = linhas_da_arma(tela, girar=True, recorte=pose.get("recorte"))
        gx, gy = py, ar.W - 1 - px  # o punho depois de girar
        mx, my = 26, 14 + dy  # arma um pouco à frente do rosto, para o olho para cima aparecer
        braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (15, 25 + dy), (mx - 1, my + 6), escurecer=1)
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (21, 23 + dy), (mx, my))
        for k, l in enumerate(linhas):
            lp.pintar(g, my - gy + k, mx - gx, l)
        punho_fechado(g, mx, my)
        punho_fechado(g, mx - 1, my + 6)
        if bocas is not None:
            # Boca depois de girar: (by, W - 1 - bx).
            bocas["cima"] = [mx - gx + by - PE[0], PE[1] - (my - gy + ar.W - 1 - bx)]
        return pixel.de_texto("\n".join("".join(l) for l in g), w=lp.W, h=lp.H)

    if nome == "mira_baixo":
        # No pulo, apontando a arma para baixo entre as pernas (como no Metal Slug),
        # com a cabeça curvada olhando o chão.
        cabeca(g, dy, rosto, baixa=2)
        linhas = linhas_da_arma(tela, girar="baixo", recorte=pose.get("recorte"))
        gx, gy = ar.H - 1 - py, px  # o punho depois de girar
        mx, my = 21, 27 + dy
        braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (14, 27 + dy), (mx - 1, my - 4), escurecer=1)
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (22, 24 + dy), (mx, my))
        for k, l in enumerate(linhas):
            lp.pintar(g, my - gy + k, mx - gx, l)
        punho_fechado(g, mx, my)
        punho_fechado(g, mx - 1, my - 4)
        if bocas is not None:
            # Boca depois de girar: (H - 1 - by, bx).
            bocas["baixo"] = [mx - gx + ar.H - 1 - by - PE[0], PE[1] - (my - gy + bx)]
        return pixel.de_texto("\n".join("".join(l) for l in g), w=lp.W, h=lp.H)

    arremesso = nome == "arremesso"
    facada = nome in ("facada", "facada1")
    gx, gy = pose["punho"]
    if arma == "estilingue" and nome not in ("recarga", "atirando"):
        # Baladeira descansando na altura do peito; só sobe até o rosto para mirar e soltar.
        gx, gy = gx - 2, gy + 6
    gy += dy
    ox, oy = gx - px, gy - py  # canto do desenho da arma no quadro
    if arremesso:
        braco_arremesso(g, dy)
    # Braço de trás vem antes do tronco (fica escondido atrás do corpo, só aparece a mão).
    if pose.get("costas"):
        # Lata do Candeeiro amarrada nas costas.
        x0, x1 = pose["costas"]
        lata = linhas_da_arma(tela, recorte=(x0, x1))
        for k, l in enumerate(lata):
            lp.pintar(g, 17 + dy + k, 1 - x0, l)
    cabeca(g, dy, rosto)
    if pose.get("costas"):
        # Alça de couro atravessando o peito.
        for k in range(9):
            g[20 + dy + k][9 + k] = "s" if k % 3 else "d"
    # Braços primeiro (ficam atrás da arma); as mãos fechadas vêm por cima dela.
    maos = [(gx, gy)]
    if arremesso or facada:
        # A mão da frente segura a arma sozinha; a de trás arremessa ou dá a facada.
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (pose.get("cot_frente", (20, 27))[0],
              pose.get("cot_frente", (20, 27))[1] + dy), (gx, gy))
        if arremesso:
            maos.append((ARREMESSO["mao"][0], ARREMESSO["mao"][1] + dy))
    elif not pose.get("um_braco"):
        braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (pose["cot_tras"][0], pose["cot_tras"][1] + dy), (gx, gy),
              escurecer=1)
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (pose["cot_frente"][0], pose["cot_frente"][1] + dy),
              (ox + ax, oy + ay))
        maos.append((ox + ax, oy + ay))
    else:
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (pose["cot_frente"][0], pose["cot_frente"][1] + dy), (gx, gy))
        if pose.get("puxa") and not arremesso and not facada:
            pxa, pya = puxa_baladeira(nome, pose)
            braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (13, 26 + dy), (pxa, pya + dy), escurecer=1)
            maos.append((pxa, pya + dy))
    linhas = linhas_da_arma(tela, recorte=pose.get("recorte"))
    for k, l in enumerate(linhas):
        lp.pintar(g, oy + k, ox, l)
    if nome == "facada1":
        # Preparo: o braço sobe para trás, peixeira apontando para cima, pronta para descer.
        fx, fy = 9, 9 + dy
        braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (5, 18 + dy), (fx, fy), escurecer=1)
        for k in range(9):
            x = fx + 1 + k // 3
            y = fy - 2 - k
            if y >= 0:
                g[y][x] = "V" if k < 6 else "v"
                g[y][x + 1] = "c"
                g[y][x - 1] = "O"
                g[y][x + 2] = "O"
        maos.append((fx, fy))
    elif facada:
        # Golpe: braço esticado para a frente, de cima para baixo, peixeira comprida na horizontal.
        fx, fy = 29, 22 + dy
        braco(g, (OMBRO_TRAS[0] + 2, OMBRO_TRAS[1] + dy), (21, 25 + dy), (fx, fy))
        for k in range(12):
            x = fx + 2 + k
            y = fy + k // 6
            if x < lp.W:
                g[y][x] = "V" if k < 9 else "v"
                g[y + 1][x] = "c" if k < 10 else "O"
                g[y - 1][x] = "O"
        maos.append((fx, fy))
    if pose.get("puxa") and not arremesso and not facada:
        # Baladeira: liga de borracha da forquilha até a mão que puxa (solta, ela volta reta entre as pontas).
        pxa, pya = puxa_baladeira(nome, pose)
        if nome == "atirando":
            for x in range(ox + 9, ox + 16):
                g[oy + 1][x] = "E"
        for tx, ty in (((ox + 9, oy + 1), (ox + 15, oy + 1)) if nome != "atirando" else ()):
            n = max(abs(tx - pxa), abs(ty - pya - dy))
            for st in range(1, n):
                x = round(pxa + (tx - pxa) * st / n)
                y = round(pya + dy + (ty - pya - dy) * st / n)
                g[y][x] = "E"
    for mx, my in maos:
        punho_fechado(g, mx, my)
    if bocas is not None:
        chave = "agachado" if nome == "agachado" else ("frente" if nome == "parado" else None)
        if chave:
            bocas[chave] = [ox + bx - PE[0], PE[1] - (oy + by)]
    return pixel.de_texto("\n".join("".join(l) for l in g), w=lp.W, h=lp.H)


def folha_da_arma(arma, bocas=None):
    return [quadro(n, arma, bocas) for n in QUADROS]


def gravar_bocas(caminho):
    """Gera src/maos.js: de onde sai o tiro de cada arma, em relação ao pé."""
    todas = {}
    for arma in ar.ARMAS:
        b = {}
        for n in ("parado", "agachado", "mira_cima", "mira_baixo"):
            quadro(n, arma, b)
        todas[arma] = b
    linhas = ["// Gerado por tools/arte/lampiao_armas.py (exportar.py). Não editar à mão.",
              "// Boca do cano de cada arma pesada nas mãos do Lampião, em relação ao pé",
              "// (x para a frente, y para cima), em pé, agachado e mirando para cima.",
              "export const BOCAS = {"]
    for arma, b in todas.items():
        linhas.append(f"  {arma}: {{ frente: {b['frente']}, agachado: {b['agachado']}, cima: {b['cima']}, baixo: {b['baixo']} }},")
    linhas.append("};")
    Path(caminho).write_text("\n".join(linhas).replace("[", "[").replace(", ", ", ") + "\n")
