"""Monta desenhos pixel a pixel a partir de trechos (coluna, texto) por linha
e grava em tools/arte/pixel/*.txt. Depois disso, o .txt é a fonte e é
editado à mão."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pixel  # noqa: E402


def montar(linhas, w):
    out = []
    for segs in linhas:
        row = ["."] * w
        for x, s in segs:
            for k, ch in enumerate(s):
                if 0 <= x + k < w and ch != " ":
                    row[x + k] = ch
        out.append("".join(row))
    return "\n".join(out)


W = 46
# Lampião parado, mirando para a frente. Luz de cima à esquerda.
LAMPIAO = [
    [(26, "OOO")],                                                        # 0
    [(25, "OhgO")],                                                       # 1
    [(6, "OO"), (24, "OhgdO")],                                           # 2
    [(5, "OhgO"), (13, "OOOOOOO"), (23, "OhgfdO")],                       # 3
    [(5, "OgfdO"), (11, "OOgggggggOO"), (22, "OhgdfdO")],                 # 4
    [(5, "OgfdsO"), (10, "OgghhhhhggfO"), (21, "OhggAfdsO")],             # 5
    [(5, "OgffdsOOghhhhhhgggffdOOhgAHAfdsO")],                            # 6
    [(6, "OgffddsdggggggggfffddsdhggAffdsO")],                            # 7
    [(7, "OOsfAfddffddddffddddffAffddsOO")],                              # 8
    [(9, "OOsssddddddddddddddsssssOO")],                                  # 9
    [(12, "ONN4555556NNNN5O")],                                           # 10
    [(12, "ONN5666666OOO66O")],                                           # 11
    [(12, "ON45666OOOBWBO7O")],                                           # 12
    [(12, "ON3236665OBKBO65O")],                                          # 13
    [(12, "ON33456666OOO654O")],                                          # 14
    [(12, "O4455566666KKKK3O")],                                          # 15
    [(12, "O34556666KKKKKKO")],                                           # 16
    [(13, "O34566654OWWO4O")],                                            # 17
    [(14, "O3344444443O")],                                               # 18
    [(13, "OOTTU22222TTOO")],                                             # 19
    [(10, "OOOTUUUTTTTTTTEO")],                                           # 20
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
]

TONS_CAQUI = "iuyytew"
TONS_MESCLA = "CccXxZ"
TONS_COURO = "hgffdsa"


def faixa_tons(linha, x0, x1, tons, luz=0.0):
    """Preenche x0..x1 com degradê da esquerda (luz) para a direita (sombra)."""
    n = len(tons)
    for x in range(x0, x1 + 1):
        f = (x - x0) / max(1, x1 - x0) - luz
        linha[x] = tons[min(n - 1, max(0, int(f * n)))]


def pintar(g, y, x, txt):
    for k, ch in enumerate(txt):
        if ch != " " and 0 <= x + k < len(g[y]):
            g[y][x + k] = ch


def corpo_lampiao(g):
    """g é uma grade (lista de listas) já com chapéu e cabeça."""
    # Embornal bordado pendurado atrás (desenhado primeiro, fica atrás).
    for y, txt in {28: "OOOO", 29: "OUUYTO", 30: "OUAUYTRO", 31: "OUUAYTRO", 32: "OYAUAYRO",
                   33: "OYUAYTRO", 34: "OTYYTRO", 35: ".OTTRRO", 36: "..OOOO"}.items():
        pintar(g, y, 1, txt)
    # Tronco do gibão.
    tronco = [(21, 8, 24), (22, 7, 24), (23, 6, 24), (24, 6, 24), (25, 5, 24), (26, 5, 24),
              (27, 5, 24), (28, 5, 24), (29, 5, 24), (30, 5, 24), (31, 6, 23)]
    for y, x0, x1 in tronco:
        faixa_tons(g[y], x0 + 1, x1 - 1, "iuuyyttew", luz=0.08 if y < 24 else 0)
        g[y][x0] = g[y][x1] = "O"
    # Cartucheiras cruzadas: couro de 2 px com balas.
    for y in range(21, 32):
        k = y - 21
        for x in (round(8 + k * 1.2), round(20 - k * 1.2)):
            g[y][x] = "s"
            g[y][x + 1] = "A" if y % 2 == 0 else "G"
            if g[y + 1][x + 1] not in "O":
                g[y + 1][x + 1] = "a"
    # Cinturão com fivela.
    pintar(g, 32, 5, "OssssssssGGGssssssssO")
    pintar(g, 33, 5, "OdfdfdfddAAAdfdfdfdsO")
    # Braço da frente: manga escura (fica na frente do tronco) e mão no gatilho.
    pintar(g, 21, 15, "OyytO")
    pintar(g, 22, 14, "OuyytewO")
    pintar(g, 23, 14, "OyyttewO")
    pintar(g, 24, 15, "OyttewO")
    pintar(g, 25, 15, "OyteewwO")
    pintar(g, 26, 16, "OtteewwOOO")
    pintar(g, 27, 16, "OteewwO5664O")
    pintar(g, 28, 17, "OOOOOO3443O")
    # Fuzil: coronha de madeira sob o braço, ferrolho, cano e telha.
    pintar(g, 28, 8, "Ohhggf")
    pintar(g, 29, 7, "OhggffddddssO")
    pintar(g, 30, 8, "OOddssaOOOOO")
    pintar(g, 25, 27, "OOOOOOOOOOOOOOOOOO")
    pintar(g, 26, 27, "VVVVVVVVVVVVVVVvvO")
    pintar(g, 27, 27, "CcccccOggffdddO")
    pintar(g, 28, 27, "OxXXcOOOOOOOOO")
    pintar(g, 26, 26, "O")
    pintar(g, 25, 44, "O")
    pintar(g, 26, 44, "W")
    # Pernas em base aberta, joelhos marcados (mescla) e perneiras de couro.
    perna_tras = {34: "OCcXxZO", 35: "OCcXxxZO", 36: ".OCcXxZO", 37: ".OCCcXZO", 38: "..OCcXxO",
                  39: "..OhgdsO", 40: "..OhAfsO", 41: "..OhgfsaO", 42: "..OhgfdsO", 43: "..OhgfdsO",
                  44: ".OdhgffdsO", 45: "OdfggffddsO", 46: "OassssssaaO", 47: "OOOOOOOOOOO"}
    perna_frente = {34: "OCcXxZO", 35: "OCccXxZO", 36: "OCcXxZO", 37: "OCCcXZO", 38: "OCcXxO",
                    39: "OhgdsO", 40: "OhAfsO", 41: "OhgfsaO", 42: "OhgfdsO", 43: "OhgfdsO",
                    44: "OhgffdsO", 45: "OdfggffddsO", 46: "OassssssaaO", 47: "OOOOOOOOOOO"}
    for y, txt in perna_tras.items():
        pintar(g, y, 5, txt)
    for y, txt in perna_frente.items():
        pintar(g, y, 15, txt)
    pintar(g, 34, 11, "OOOO")


if __name__ == "__main__":
    grade = [list(l) for l in montar(LAMPIAO, W).split("\n")]
    corpo_lampiao(grade)
    texto = "\n".join("".join(l) for l in grade)
    pixel.PASTA.mkdir(exist_ok=True)
    (pixel.PASTA / "lampiao.txt").write_text(
        "# Legenda em tools/arte/pixel.py. '.' é transparente.\n== parado\n" + texto + "\n")
    print(texto)
