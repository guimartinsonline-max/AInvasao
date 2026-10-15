"""Teste: Lampião no motor de alta definição, proporções estilo Metal Slug."""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from motor_hd import TelaHD  # noqa: E402

W, H = 56, 58
PE = 56


def lampiao_hd():
    t = TelaHD(W, H)
    P = t.pintar
    # Perna de trás.
    P(t.capsula(21, 38, 18, 46, 3.4, 3.0), "mescla", brilho=-0.25)
    P(t.capsula(18, 46, 17, 53, 3.0, 2.7), "couro", brilho=-0.2)
    P(t.elipse(18.5, 54.3, 4.6, 2.1), "couro", brilho=-0.3)
    # Embornal bordado.
    P(t.elipse(14, 39, 4.6, 5.2), "vermelho", achatado=2.2, textura=0.05)
    t.pontos([(13, 37), (15, 38), (13, 40), (15, 41), (14, 39)], "amarelo_fogo")
    t.linha(18, 27, 15, 34, "couro_escuro")
    # Braço de trás, segurando a telha do fuzil.
    P(t.capsula(27, 26, 31, 31, 3.0, 2.6), "caqui", brilho=-0.25)
    P(t.capsula(31, 31, 35, 32.5, 2.6, 2.3), "caqui", brilho=-0.25)
    P(t.elipse(36, 32.8, 2.3, 2.0), "pele", brilho=-0.15)
    # Perna da frente.
    P(t.capsula(27, 38, 29, 46, 3.5, 3.1), "mescla")
    P(t.capsula(29, 46, 30, 53, 3.1, 2.8), "couro", textura=0.03)
    P(t.elipse(31.5, 54.3, 4.9, 2.2), "couro", brilho=-0.1)
    # Tronco: gibão cáqui atarracado com dobras.
    tronco = t.elipse(24, 31, 8.4, 8.6) | t.retangulo(16.5, 30, 15, 8)
    P(tronco, "caqui", achatado=3.0, oclusao=0.15)
    # Dobras e bolsos desenhados à mão.
    t.linha(19, 32, 21, 35, "terra")
    t.linha(27, 31, 28, 35, "terra")
    t.pontos([(20, 33), (28, 33)], "areia_clara")
    # Cartucheiras cruzadas.
    for a, b in (((17, 26), (30, 37)), ((30, 26), (18, 37))):
        P(t.capsula(*a, *b, 1.6), "couro", achatado=0.8, oclusao=0.2)
    for k in range(6):
        t.ponto(18 + k * 2.2, 27 + k * 1.9, "amarelo_fogo")
        t.ponto(29 - k * 2.2, 27 + k * 1.9, "amarelo_fogo")
    # Cinturão e fivela.
    P(t.retangulo(16.5, 37, 15.5, 3), "couro", achatado=1)
    t.chapado(t.retangulo(23, 37.5, 3, 2), "amarelo_fogo")
    # Lenço vermelho.
    P(t.elipse(26, 24, 5.4, 2.4), "vermelho", achatado=1.2)
    P(t.poligono([(22, 24), (18, 30), (24, 26.5)]), "vermelho", achatado=1)
    # Cabeça: um só volume (crânio + queixo) para não manchar o rosto.
    cabeca = t.elipse(27, 16.2, 5.0, 5.3) | t.elipse(28.6, 19.6, 4.0, 2.9) | t.elipse(32.2, 17.4, 1.8, 1.5)
    P(cabeca, "pele", achatado=2.6, brilho=0.12, oclusao=0)
    # Orelha.
    t.pontos([(23, 16), (23, 17), (23, 18)], "pele_escura")
    t.ponto(24, 17, "couro")
    # Costeleta escura.
    t.pontos([(24, 13), (24, 14), (24, 15), (25, 14)], "preto")
    # Óculos redondos e olho.
    t.pontos([(28, 14), (29, 14), (30, 14), (27, 15), (31, 15), (27, 16), (31, 16), (28, 17), (29, 17), (30, 17)], "sombra")
    t.pontos([(28, 15), (30, 15), (28, 16), (30, 16)], "ceu_claro")
    t.pontos([(29, 15)], "branco")
    t.pontos([(29, 16)], "preto")
    t.linha(25, 15, 26, 15, "sombra")
    # Sobrancelha grossa franzida.
    t.pontos([(28, 12), (29, 12), (30, 13), (31, 13)], "couro_escuro")
    # Nariz: narina e sombra embaixo.
    t.ponto(32, 18, "pele_escura")
    t.ponto(33, 16, "pele_clara")
    # Bigode e boca.
    t.pontos([(29, 19), (30, 19), (31, 19), (32, 19), (30, 20), (31, 20)], "couro_escuro")
    t.pontos([(29, 21), (30, 21)], "couro")
    # Sombra do queixo no pescoço.
    t.pontos([(26, 22), (27, 22), (28, 22)], "couro")
    # Chapéu de couro em meia-lua.
    P(t.elipse(25.5, 9.5, 5.6, 3.4), "chapeu", achatado=2, brilho=-0.2)
    lua = t.elipse(26.5, 6.5, 11.5, 6.8) & ~t.elipse(26, 1.0, 10.2, 7.8) & (t.yy < 12.6)
    P(lua, "chapeu", achatado=1.8, textura=0.03)
    friso = lua & ~t.elipse(26.5, 6.2, 10.6, 6.0)
    t.chapado(friso & (t.yy < 11.5), "couro_escuro")
    sx, sy = 27, 9
    t.pontos([(sx, sy - 1), (sx - 1, sy), (sx, sy), (sx + 1, sy), (sx, sy + 1)], "amarelo_fogo")
    t.ponto(sx, sy, "branco")
    for mx in (19, 22, 32, 35):
        t.ponto(mx, 10 if mx in (22, 32) else 8, "amarelo_fogo")
    # Fuzil: coronha, ferrolho, telha de madeira e cano longo.
    P(t.poligono([(18, 30), (26, 30.5), (26, 33.5), (19, 35.5)]), "madeira", achatado=1.2, textura=0.03)
    P(t.retangulo(25.5, 29.6, 7, 3.2), "metal", achatado=1)
    P(t.retangulo(31, 31.2, 8, 1.8), "madeira", achatado=0.8)
    P(t.retangulo(31, 29.8, 18, 1.5), "metal", achatado=0.7)
    t.ponto(48, 29, "cinza_claro")
    # Braço da frente no gatilho.
    P(t.capsula(22, 26, 23, 32, 3.2, 2.8), "caqui", oclusao=0.1)
    t.linha(22, 30, 24, 31, "terra")
    P(t.capsula(23, 32, 27, 33, 2.8, 2.4), "caqui")
    P(t.elipse(27.8, 32.6, 2.3, 2.1), "pele", achatado=1.2)
    return t.reduzir()


if __name__ == "__main__":
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    hd = lampiao_hd()
    import personagens as pg
    antigo = pg.lampiao()
    img = Image.new("RGBA", (W * 2 + 8, H), (79, 154, 214, 255))
    img.alpha_composite(antigo.imagem(), (0, H - antigo.h - 4))
    img.alpha_composite(hd.imagem(), (W + 8, 0))
    img.resize((img.width * 8, img.height * 8), Image.NEAREST).save(saida / "comparar_hd.png")
    print(saida / "comparar_hd.png")
