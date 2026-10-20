"""NPCs no padrão do ESTILO.md (lote 2 de gráficos): cientista refém, bode Fubá,
galinha e urubu.

O cientista usa as poses do romeiro (caricatos.py) com cabeça, jaleco e calça próprios;
os bichos são desenhados aqui, caricatos, com contorno só por fora e volume em 5 a 7 tons.

Uso: python3 tools/arte/npcs.py   (grava pixel/cientista.txt; os PNGs saem no exportar.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import caricatos as ca  # noqa: E402
from caricatos import sombrear, PELE, PELE_CLARA, BARBA, TRAPO  # noqa: E402
from motor import Tela  # noqa: E402

PELO = ["cinza", "cinza_luz", "cinza_claro", "branco", "branco"]
MANCHA = ["couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]
CHIFRE = ["terra_escura", "terra_media", "barro", "areia_media", "areia_luz"]
CASCO = ["preto", "sombra", "cinza_escuro"]
LATAO = ["couro_profundo", "ouro_escuro", "amarelo_fogo", "amarelo_claro"]
PENA = ["couro_profundo", "couro_escuro", "couro", "couro_medio", "barro", "couro_luz"]
PENA_ESC = ["preto", "sombra", "azul_sombra", "sombra_media"]
URUBU = ["preto", "sombra", "azul_sombra", "sombra_media", "cinza_escuro"]
CABECA_URUBU = ["vermelho_esc", "vermelho_medio", "vermelho", "rosa_poeira"]


# ================================================================ cientista
def cabeca_cientista(t, x, y, rosto="triste"):
    """Careca grande com tufos brancos espetados, óculos redondos de aro grosso,
    narigão vermelho e bigodão branco. (x, y) = centro do rosto."""
    # Tufos espetados atrás e dos lados (cientista maluco).
    tufo = t.poligono([(x - 4, y - 7), (x - 10, y - 10), (x - 8, y - 5), (x - 13, y - 5), (x - 9, y - 2),
                       (x - 13, y + 1), (x - 8, y + 1), (x - 10, y + 5), (x - 5, y + 3)])
    sombrear(t, tufo, BARBA)
    sombrear(t, t.elipse(x - 6, y + 1, 1.8, 2.4), PELE)  # orelha
    sombrear(t, t.elipse(x, y - 1, 7.2, 8.4), PELE)
    # Careca: brilho grande no topo e rugas na testa.
    t.pontos([(x - 2, y - 7), (x - 1, y - 7), (x - 3, y - 6)], "pele_brilho")
    t.linha(x + 1, y - 5, x + 4, y - 5, "pele_media")
    t.linha(x + 2, y - 7, x + 4, y - 7, "pele_media")
    # Tufo pequeno espetado na frente da orelha.
    t.pontos([(x - 3, y - 2), (x - 4, y - 3), (x - 2, y - 1)], "cinza_claro")
    # Bigodão branco caído.
    bigode = t.poligono([(x + 1, y + 3), (x + 10, y + 3), (x + 11, y + 7), (x + 7, y + 5), (x + 4, y + 7), (x + 1, y + 6)])
    sombrear(t, bigode, BARBA)
    if rosto == "feliz":
        t.chapado(t.elipse(x + 6, y + 8, 2.4, 1.6), "preto")
        t.chapado(t.elipse(x + 6, y + 9, 1.3, 0.6), "vermelho")
    elif rosto == "chorando":
        t.chapado(t.elipse(x + 6, y + 8, 1.8, 1.5), "preto")
    else:
        t.linha(x + 4, y + 8, x + 7, y + 8, "pele_sombra")
    # Narigão vermelho.
    sombrear(t, t.elipse(x + 8, y + 1, 2.8, 2.4), PELE_CLARA)
    t.ponto(x + 9, y, "pele_brilho")
    # Óculos: lente redonda grande de aro grosso, com o olho atrás e o reflexo.
    ex, ey = x + 4, y - 2
    t.chapado(t.elipse(ex, ey, 3.3, 3.2), "preto")
    t.chapado(t.elipse(ex, ey, 2.3, 2.2), "ceu_claro")
    if rosto == "feliz":
        t.pontos([(ex - 1, ey), (ex, ey - 1), (ex + 1, ey)], "preto")
    elif rosto == "concentrado":
        t.linha(ex - 1, ey, ex + 1, ey, "preto")
    else:
        t.chapado(t.retangulo(ex, ey - 0.5, 1.5, 1.5), "preto")
    t.ponto(ex - 1, ey - 1, "branco")
    t.linha(ex - 4, ey - 1, x - 5, y - 1, "preto")  # haste até a orelha
    # Sobrancelha branca espetada por cima do aro.
    if rosto in ("triste", "chorando"):
        t.linha(ex - 2, ey - 4, ex + 3, ey - 6, "branco")
    else:
        t.linha(ex - 2, ey - 5, ex + 3, ey - 5, "branco")
    if rosto == "chorando":
        t.chapado(t.capsula(ex + 1, ey + 3, ex, ey + 6, 0.7), "ceu_claro")


def peito_cientista(t, x, y):
    """No lugar do terço: gravata-borboleta vermelha, bolso com canetas e mancha de gosma."""
    t.chapado(t.poligono([(x - 2, y - 1), (x + 3, y + 1), (x - 2, y + 2)]), "vermelho")
    t.chapado(t.poligono([(x + 6, y - 1), (x + 3, y + 1), (x + 6, y + 2)]), "vermelho_esc")
    t.ponto(x + 3, y + 1, "vermelho_esc")
    # Bolso com duas canetas.
    t.linha(x - 3, y + 5, x - 1, y + 5, "cinza")
    t.pontos([(x - 3, y + 4), (x - 1, y + 3)], "azul_medio")
    t.ponto(x - 2, y + 4, "vermelho")
    # Respingo de gosma do laboratório.
    t.pontos([(x + 2, y + 7), (x + 3, y + 7), (x + 3, y + 8)], "alien_medio")


def fralda(t, bx, y, pose, passo=0):
    """Aba do jaleco até o meio da coxa, voando para trás quando corre."""
    voa = {"corre": 2 + (passo % 2), "solto": 1}.get(pose, 0)
    m = t.poligono([(bx - 6, y - 2), (bx + 6, y - 2), (bx + 7, y + 5), (bx - 6 - voa * 2, y + 4 + (voa > 0))])
    sombrear(t, m, TRAPO)
    t.linha(bx + 1, y - 1, bx + 1, y + 4, "cinza_luz")  # abertura do jaleco
    t.ponto(bx - 3, y + 3, "cinza")  # barra suja


CIENTISTA = ca.REFEM


# ================================================================ bode Fubá
BODE_W, BODE_H = 40, 32


def bode(quadro="parado"):
    """Bode Fubá caricato: cabeçona de olho esbugalhado com pupila de bode, chifre
    curvo, barbicha, chocalho no pescoço e manchas de fubá. Quadros: parado, mastiga,
    abduzido e anda1-4 (trote: pernas em diagonal juntas, a que avança sobe)."""
    t = Tela(BODE_W, BODE_H)
    pe = BODE_H - 1
    ergue = quadro == "abduzido"
    passo = int(quadro[-1]) - 1 if quadro.startswith("anda") else None
    sobe = 1 if passo in (1, 3) else 0
    # Pernas: as de trás (longe) primeiro, mais escuras.
    pernas = [(12, 1), (25, 1), (15, 0), (28, 0)]  # (x, longe)
    for k, (x, longe) in enumerate(pernas):
        dx, fim = 0, pe - 1
        if passo is not None:
            par = 0 if k in (0, 3) else 1
            fase = (passo + par * 2) % 4
            dx = (-3, 0, 3, 0)[fase]
            fim -= 2 if fase == 1 else 0
        if ergue:  # esperneando no raio
            dx = (-3, 3, -1, 4)[k]
            fim -= (3, 6, 2, 5)[k]
        joelho = (x + dx * 0.4, (20 + fim) / 2)
        sombrear(t, t.capsula(x, 20 - sobe, *joelho, 1.6, 1.3) | t.capsula(*joelho, x + dx, fim - 1, 1.3, 1.0),
                 PELO, deslocar=-1.5 if longe else 0)
        t.ponto(joelho[0], joelho[1], "cinza" if longe else "cinza_luz")
        sombrear(t, t.retangulo(x + dx - 1, fim - 1, 3, 2), CASCO)
    # Corpo barrigudo e rabinho espetado.
    corpo = t.elipse(19, 17 - sobe, 11.5, 6.5)
    sombrear(t, corpo, PELO)
    sombrear(t, t.poligono([(8, 14 - sobe), (4, 8 - sobe), (6, 8 - sobe), (10, 13 - sobe)]), PELO)
    # Manchas de fubá e pelo riscado.
    for (mx, my, rx, ry) in ((14, 14, 3.6, 2.4), (22, 19, 2.6, 1.8), (9, 18, 1.8, 1.6)):
        sombrear(t, t.elipse(mx, my - sobe, rx, ry) & corpo, MANCHA, linha=False)
    for (lx, ly) in ((18, 12), (24, 13), (11, 15), (20, 21)):
        t.linha(lx, ly - sobe, lx + 1, ly + 1 - sobe, "cinza_luz")
    # Pescoço e chocalho.
    hy = 7 - sobe + (2 if ergue else 0)
    sombrear(t, t.capsula(27, 15 - sobe, 31, hy + 4, 3.8, 3.2), PELO)
    t.linha(27, hy + 7, 31, hy + 9, "vermelho")
    sombrear(t, t.poligono([(28, hy + 9), (31, hy + 9), (32, hy + 13), (27, hy + 13)]), LATAO)
    t.ponto(29, hy + 13, "preto")
    # Cabeçona com focinho comprido.
    hx = 32
    sombrear(t, t.capsula(hx - 1, hy, hx + 5, hy + 4, 4.4, 3.0), PELO)
    sombrear(t, t.elipse(hx + 6, hy + 4, 2.4, 2.2), ["pele_escura", "pele_media", "rosa_poeira", "pele_clara"])
    t.ponto(hx + 7, hy + 3, "sombra")  # venta
    # Orelha caída para trás.
    sombrear(t, t.capsula(hx - 3, hy - 1, hx - 8, hy + 3, 1.8, 1.2), PELO, deslocar=-1)
    t.ponto(hx - 7, hy + 3, "rosa_poeira")
    # Chifre curvo para trás.
    sombrear(t, t.capsula(hx - 1, hy - 3, hx - 3, hy - 7, 1.6, 1.2) | t.capsula(hx - 3, hy - 7, hx - 7, hy - 7, 1.2, 0.7),
             CHIFRE)
    t.linha(hx - 2, hy - 5, hx - 1, hy - 5, "terra_escura")
    # Barbicha de fubá.
    sombrear(t, t.poligono([(hx + 2, hy + 6), (hx + 6, hy + 6), (hx + 4, hy + 12), (hx + 2, hy + 10)]), MANCHA)
    # Olho esbugalhado com a pupila de bode (risquinho deitado).
    gx, gy = hx + 1, hy - 1
    if ergue:
        t.chapado(t.elipse(gx, gy, 2.8, 2.8), "preto")
        t.chapado(t.elipse(gx, gy, 1.9, 1.9), "branco")
        t.ponto(gx, gy, "preto")
    else:
        t.chapado(t.elipse(gx, gy, 2.4, 2.2), "preto")
        t.chapado(t.elipse(gx, gy, 1.5, 1.4), "amarelo_claro")
        t.linha(gx - 1, gy, gx + 1, gy, "preto")
        t.linha(gx - 2, gy - 2, gx + 1, gy - 3, "cinza")  # pálpebra pesada, cara de abestado
    # Boca.
    if quadro == "mastiga":
        t.linha(hx + 4, hy + 6, hx + 7, hy + 6, "sombra")
        t.linha(hx + 7, hy + 6, hx + 10, hy + 3, "caatinga")  # capim no canto da boca
        t.ponto(hx + 10, hy + 2, "mandacaru")
    elif ergue:
        t.chapado(t.elipse(hx + 6, hy + 7, 2, 1.6), "preto")
        t.ponto(hx + 6, hy + 7, "vermelho")
    else:
        t.linha(hx + 4, hy + 6, hx + 7, hy + 6, "sombra")
    t.contorno("sombra")
    if ergue:  # gotas de pânico
        t.pontos([(hx - 6, hy - 5), (hx - 7, hy - 4), (hx + 8, hy - 4)], "ceu_claro")
    return t


# ================================================================ galinha
GAL_W, GAL_H = 18, 17


def galinha(quadro=0):
    """Galinha caipira gorducha: 0 parada, 1 bicando, 2-3 correndo de asa aberta
    (olho esbugalhado), 4-5 andando com a cabeça indo e voltando."""
    t = Tela(GAL_W, GAL_H)
    bica, corre, anda = quadro == 1, quadro in (2, 3), quadro in (4, 5)
    pe = GAL_H - 1
    # Pernas amarelas finas com dedos.
    if anda:
        a, b = (6, 9) if quadro == 4 else (9, 6)
        t.linha(8, 12, a, pe, "ouro_escuro")
        t.linha(9, 12, b + 1, pe - 1, "amarelo_fogo")
        t.linha(b + 1, pe - 1, b + 3, pe - 1, "amarelo_fogo")
        t.linha(a - 1, pe, a + 1, pe, "ouro_escuro")
    else:
        pes = (6, 10) if quadro == 2 else (7, 9) if quadro == 3 else (7, 10)
        for k, x in enumerate(pes):
            t.linha(x, 12, x - (1 if corre else 0), pe, "ouro_escuro" if k == 0 else "amarelo_fogo")
            t.linha(x - 1, pe, x + 1, pe, "ouro_escuro" if k == 0 else "amarelo_fogo")
    # Rabo de penas escuras com brilho azulado.
    sombrear(t, t.poligono([(4, 10), (0, 2), (3, 4), (2, 0), (6, 6), (6, 10)]), PENA_ESC)
    # Corpo gorducho.
    sombrear(t, t.elipse(8, 10, 6, 4.5), PENA)
    t.pontos([(6, 12), (9, 13), (11, 11)], "couro_escuro")  # penas riscadas
    # Asa (fechada ou batendo).
    if corre:
        asa = t.poligono([(6, 9), (2, 3) if quadro == 2 else (3, 14), (11, 9)])
    else:
        asa = t.elipse(8, 10, 3.6, 2.2)
    sombrear(t, asa, PENA, deslocar=0.6)
    # Cabeça.
    hx, hy = (13, 11) if bica else (14, 5) if quadro == 4 else (13, 4)
    sombrear(t, t.elipse(hx, hy, 2.8, 2.8), PENA)
    sombrear(t, t.poligono([(hx - 2, hy - 2), (hx - 1, hy - 5), (hx, hy - 3), (hx + 1, hy - 5), (hx + 2, hy - 2)]),
             ["vermelho_esc", "vermelho_medio", "vermelho"])  # crista serrilhada
    t.chapado(t.elipse(hx + 1.5, hy + 3, 0.9, 1.3), "vermelho")  # barbela
    t.chapado(t.poligono([(hx + 2, hy - 0.5), (hx + 5, hy + 0.5), (hx + 2, hy + 1.5)]), "amarelo_fogo")
    if corre:
        t.chapado(t.elipse(hx + 0.5, hy - 0.5, 1.4, 1.4), "branco")
        t.ponto(hx + 1, hy - 1, "preto")
    else:
        t.ponto(hx + 1, hy - 1, "preto")
    t.contorno("sombra")
    if corre:  # pena voando
        t.pontos([(1, 13), (2, 12)], "couro_medio")
    return t


# ================================================================ urubu
URU_W, URU_H = 28, 20


def urubu(quadro=0):
    """Urubu de pescoço pelado: 0 pousado corcunda, 1 asas para cima, 2 asas para
    baixo. Pontas das asas abertas em dedos de pena."""
    t = Tela(URU_W, URU_H)
    if quadro == 0:
        # Corcunda de asa fechada, pescoço pelado esticado e bico de gancho.
        sombrear(t, t.elipse(12, 12, 7, 6.5), URUBU)
        sombrear(t, t.poligono([(6, 14), (2, 18), (8, 17)]), URUBU, deslocar=-1)  # rabo
        sombrear(t, t.elipse(13, 11, 5, 4.5), URUBU, deslocar=0.6)  # asa fechada
        for k in range(3):
            t.linha(9 + k * 2, 14, 7 + k * 2, 16, "cinza_escuro")  # penas da asa
        sombrear(t, t.capsula(16, 7, 19, 5, 1.6, 1.4), CABECA_URUBU)
        sombrear(t, t.elipse(20, 5, 2.6, 2.4), CABECA_URUBU)
        t.linha(15, 8, 18, 8, "cinza_escuro")  # gola de penas
        t.chapado(t.poligono([(21, 4), (25, 5), (24, 7), (21, 6.5)]), "cinza_claro")
        t.ponto(24, 7, "cinza")
        t.chapado(t.elipse(20, 4, 1.2, 1.1), "branco")
        t.ponto(21, 4, "preto")
        t.linha(8, 18, 10, 18, "cinza_luz")
        t.linha(14, 18, 16, 18, "cinza_luz")
    else:
        dy = -7 if quadro == 1 else 6
        for lado in (-1, 1):
            asa = t.poligono([(14, 9), (14 + lado * 13, 9 + dy), (14 + lado * 12, 11 + dy * 0.6), (14 + lado * 3, 12)])
            sombrear(t, asa, URUBU, deslocar=-0.8 if lado < 0 else 0)
            for k in range(3):  # dedos de pena na ponta
                t.ponto(14 + lado * (13 - k), 9 + dy + (k + 1) * (1 if dy < 0 else -1) * 0.8, "cinza_escuro")
        sombrear(t, t.elipse(13, 11, 6.5, 3.2), URUBU)
        sombrear(t, t.poligono([(7, 11), (2, 13), (7, 13)]), URUBU, deslocar=-1)
        sombrear(t, t.elipse(21, 10, 2.4, 2.2), CABECA_URUBU)
        t.chapado(t.poligono([(22, 9), (26, 10), (25, 12), (22, 11.5)]), "cinza_claro")
        t.ponto(21, 9, "preto")
    t.contorno("sombra")
    return t


if __name__ == "__main__":
    ca.FIGURA = "cientista"
    ca.gravar("cientista.txt", CIENTISTA)
    ca.FIGURA = "romeiro"
    print("pixel/cientista.txt atualizado")
