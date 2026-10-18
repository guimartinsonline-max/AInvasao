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
           "pulo", "agachado", "mira_cima", "susto"]
ROSTO = {"parado": "serio", "agachado": "serio", "susto": "susto"}

# Pose de cada arma (coordenadas do bloco, antes do deslocamento dy):
# punho: onde a mão de trás fecha no punho da arma.
# cot_tras / cot_frente: cotovelos. apoio: se a mão da frente segura o apoio da arma.
# recorte: (x0, x1) parte do desenho da arma que vai na mão; costas: parte nas costas.
POSES = {
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
    """Braço de manga de algodão em dois segmentos, com a mão fechada na ponta."""
    forma = (lp.H, lp.W)
    c1, l1 = lp.segmento(forma, (ombro[0] + 0.5, ombro[1] + 0.5), (cotovelo[0] + 0.5, cotovelo[1] + 0.5), 2.3)
    c2, l2 = lp.segmento(forma, (cotovelo[0] + 0.5, cotovelo[1] + 0.5), (mao[0] + 0.5, mao[1] + 0.5), 2.0)
    lp.pintar_tons(g, c1, l1, MANGA, escurecer)
    lp.pintar_tons(g, c2 & ~c1, l2, MANGA, escurecer)
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]]
    punho = ((xx + 0.5 - (mao[0] + 0.5)) / 1.8) ** 2 + ((yy + 0.5 - (mao[1] + 0.5)) / 1.6) ** 2 <= 1
    for y, x in zip(*np.where(punho)):
        g[y][x] = "5" if y <= mao[1] - 1 else ("4" if x <= mao[0] else "3")
    contornar(g, c1 | c2 | punho)


def mao_solta(g, x, y):
    """Só a mão (a do braço escondido atrás da arma), segurando por baixo."""
    for k, l in enumerate(["O56O", "O443O", ".OOO"]):
        lp.pintar(g, y + k, x, l)


def base(nome):
    """Pernas, tronco, rosto e chapéu, sem braços nem arma."""
    rosto = ROSTO.get(nome, "grito")
    pernas = nome if nome.startswith("corre") or nome in ("pulo", "agachado") else "parado"
    g = [["."] * lp.W for _ in range(lp.H)]
    tras, frente, dy = lp.POSES_PERNAS[pernas]
    dy += lp.MARGEM
    qy = lp.QUADRIL_Y + dy
    lp.perna(g, (11, qy), *tras, atras=True)
    lp.perna(g, (16, qy), *frente, atras=False)
    return g, dy, rosto


def cabeca(g, dy, rosto):
    for y, x, txt in lp.TRONCO:
        lp.pintar(g, y + dy, x, txt)
    for k, txt in enumerate(lp.ROSTOS[rosto]):
        lp.pintar(g, 8 + k + dy, 7, txt)
    for k, txt in enumerate(lp.CHAPEU):
        lp.pintar(g, 1 + k + dy, 4, txt)


def quadro(nome, arma, bocas=None):
    tela = ar.ARMAS[arma]()
    px, py = ar.PUNHO[arma]
    ax, ay = ar.APOIO[arma]
    bx, by = ar.BOCA[arma]
    pose = POSES[arma]
    g, dy, rosto = base(nome)

    if nome == "mira_cima":
        # Arma de pé nas duas mãos, na frente do rosto.
        cabeca(g, dy, rosto)
        linhas = linhas_da_arma(tela, girar=True, recorte=pose.get("recorte"))
        gx, gy = py, ar.W - 1 - px  # o punho depois de girar
        mx, my = 23, 14 + dy
        for k, l in enumerate(linhas):
            lp.pintar(g, my - gy + k, mx - gx, l)
        braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (15, 24 + dy), (mx - 1, my + 6))
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (21, 22 + dy), (mx, my))
        if bocas is not None:
            # Boca depois de girar: (by, W - 1 - bx).
            bocas["cima"] = [mx - gx + by - PE[0], PE[1] - (my - gy + ar.W - 1 - bx)]
        return pixel.de_texto("\n".join("".join(l) for l in g), w=lp.W, h=lp.H)

    gx, gy = pose["punho"]
    gy += dy
    ox, oy = gx - px, gy - py  # canto do desenho da arma no quadro
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
    if not pose.get("um_braco"):
        braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (pose["cot_tras"][0], pose["cot_tras"][1] + dy), (gx, gy),
              escurecer=1)
    linhas = linhas_da_arma(tela, recorte=pose.get("recorte"))
    for k, l in enumerate(linhas):
        lp.pintar(g, oy + k, ox, l)
    if pose.get("um_braco"):
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (pose["cot_frente"][0], pose["cot_frente"][1] + dy), (gx, gy))
        if pose.get("puxa"):
            # Baladeira: a outra mão puxa a liga até perto do rosto.
            pxa, pya = pose["puxa"]
            braco(g, (OMBRO_TRAS[0], OMBRO_TRAS[1] + dy), (13, 26 + dy), (pxa, pya + dy), escurecer=1)
            for tx, ty in ((ox + 9, oy + 1), (ox + 15, oy + 1)):
                n = max(abs(tx - pxa), abs(ty - pya - dy))
                for s in range(1, n):
                    x = round(pxa + (tx - pxa) * s / n)
                    y = round(pya + dy + (ty - pya - dy) * s / n)
                    if g[y][x] not in "O5434":
                        g[y][x] = "E"
    else:
        # A mão da frente segura o apoio da arma, com o braço vindo do ombro.
        braco(g, (OMBRO_FRENTE[0], OMBRO_FRENTE[1] + dy), (pose["cot_frente"][0], pose["cot_frente"][1] + dy),
              (ox + ax, oy + ay))
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
        for n in ("parado", "agachado", "mira_cima"):
            quadro(n, arma, b)
        todas[arma] = b
    linhas = ["// Gerado por tools/arte/lampiao_armas.py (exportar.py). Não editar à mão.",
              "// Boca do cano de cada arma pesada nas mãos do Lampião, em relação ao pé",
              "// (x para a frente, y para cima), em pé, agachado e mirando para cima.",
              "export const BOCAS = {"]
    for arma, b in todas.items():
        linhas.append(f"  {arma}: {{ frente: {b['frente']}, agachado: {b['agachado']}, cima: {b['cima']} }},")
    linhas.append("};")
    Path(caminho).write_text("\n".join(linhas).replace("[", "[").replace(", ", ", ") + "\n")
