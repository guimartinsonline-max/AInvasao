"""Gera os PNGs usados pelo jogo em assets/sprites/.

Uso: python3 tools/arte/exportar.py
A ordem dos quadros das folhas está em src/quadros.js e precisa bater com a daqui.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cenario as cn  # noqa: E402
import personagens as pg  # noqa: E402
from motor import RAIZ, folha  # noqa: E402

SAIDA = RAIZ / "assets/sprites"
SAIDA.mkdir(parents=True, exist_ok=True)

PERNAS_LAMPIAO = ["parado", "corre1", "corre2", "corre3", "pulo"]


def lampiao():
    quadros = []
    for mira in ("frente", "cima"):
        for pernas in PERNAS_LAMPIAO:
            boca = "grito" if pernas == "pulo" else "sorriso"
            quadros.append(pg.lampiao({"pernas": pernas, "mira": mira, "boca": boca}))
    quadros.append(pg.lampiao({"pernas": "agachado"}))
    quadros.append(pg.lampiao({"boca": "grito"}))
    return quadros


# Lampião desenhado pixel a pixel (fonte: tools/arte/pixel/lampiao.txt).
import pixel  # noqa: E402
QUADROS_LAMPIAO = ["parado", "atirando", "corre1", "corre2", "corre3", "corre4", "corre5", "corre6",
                   "pulo", "agachado", "mira_cima", "susto"]
desenhos = pixel.ler("lampiao.txt")
# A folha padrão do Lampião é com a pistola (arma inicial), feita como as das armas pesadas.
import lampiao_armas as la  # noqa: E402
folha(la.folha_da_arma("pistola"), SAIDA / "lampiao.png")
# Inimigos pixel a pixel (fonte: tools/arte/pixel/volante.txt e xeremita.txt).
# Inimigos caricatos (fonte: tools/arte/caricatos.py). O último quadro, "tostado",
# é a morte recolorida de carvão, para quem morre queimado pelo Candeeiro.
from motor import IDX as _IDX, Tela as _Tela  # noqa: E402
_CARVAO = {"branco": "branco", "preto": "preto", "vermelho": "laranja_fogo", "vermelho_medio": "laranja_escuro"}


def tostar(tela):
    t = _Tela(tela.w, tela.h)
    t.px = tela.px.copy()
    nomes = {v: k for k, v in _IDX.items()}
    for v in set(t.px.flatten()) - {-1}:
        nome = nomes[v]
        destino = _CARVAO.get(nome)
        if not destino:
            r, g, b = (int(pixel_cor[i:i + 2], 16) for pixel_cor in [CORES[nome]] for i in (1, 3, 5))
            luz = (r + g + b) / 3
            destino = "preto" if luz < 70 else ("sombra" if luz < 120 else ("sombra_media" if luz < 165 else "cinza_escuro"))
        t.px[tela.px == v] = _IDX[destino]
    return t


from motor import CORES  # noqa: E402
import repintar as rp  # noqa: E402
for nome, ordem in {"volante": ["parado", "atira", "panico", "anda1", "anda2", "anda3", "anda4", "morte"],
                    "granadeiro": ["parado", "atira", "panico", "anda1", "anda2", "anda3", "anda4", "morte"],
                    "metralhador": ["parado", "atira", "panico", "anda1", "anda2", "anda3", "anda4", "morte"],
                    "facao": ["parado", "atira", "panico", "anda1", "anda2", "anda3", "anda4", "morte"],
                    "rojao": ["parado", "atira", "panico", "anda1", "anda2", "anda3", "anda4", "morte"],
                    "oficial": ["parado", "atira", "panico", "anda1", "anda2", "anda3", "anda4", "morte"],
                    "xeremita": ["parado", "atira", "grito", "anda1", "anda2", "anda3", "anda4", "morte"]}.items():
    d = pixel.ler(f"{nome}.txt")
    d = {k: rp.repintar_tela(v) for k, v in d.items()}
    # Soldados da Volante também têm os quadros sentados (distraídos) depois do tostado.
    extra = [d["sentado1"], d["sentado2"]] if "sentado1" in d else []
    folha([d[n] for n in ordem] + [tostar(d["morte"])] + extra, SAIDA / f"{nome}.png")
d = {k: rp.repintar_tela(v) for k, v in pixel.ler("refem.txt").items()}
folha([d[n] for n in ["amarrado1", "amarrado2", "amarrado3", "solto", "procura", "entrega", "continencia",
                      "corre1", "corre2", "corre3", "corre4", "pendurado1", "pendurado2"]], SAIDA / "refem.png")
import inimigos as ini  # noqa: E402
folha([ini.disco(0), ini.disco(1)], SAIDA / "disco.png")
folha([ini.feixe(0, h=160), ini.feixe(1, h=160)], SAIDA / "feixe.png")
folha([ini.bode("parado"), ini.bode("mastiga"), ini.bode("abduzido")], SAIDA / "bode.png")
folha([pg.maria_bonita()], SAIDA / "maria_bonita.png")
folha([pg.alien(), pg.alien({"olho": "fechado"})], SAIDA / "alien.png")

# Armas (pixel/armas_mao.txt, lidas por tools/arte/armas.py) e efeitos de tiro (tools/arte/efeitos_tiro.py).
import efeitos_tiro as ef  # noqa: E402
# Lampião segurando cada arma pesada (tools/arte/lampiao_armas.py), mesma ordem de quadros do lampiao.png.
import lampiao_armas as la  # noqa: E402
for arma in la.ar.ARMAS:
    if arma != "pistola":
        folha(la.folha_da_arma(arma), SAIDA / f"lampiao_{arma}.png")
la.gravar_bocas(RAIZ / "src/maos.js")


def engordar_rosto(t):
    """Retrato gordo: bochechas esticadas para os lados."""
    return engordar(t, x0=7, x1=19, extra=4)


def engordar(t, x0=8, x1=20, extra=5):
    """Lampião gordo (comeu demais): estica a faixa do meio do corpo (barriga,
    rosto e pernas) para os lados, sem tocar na arma na frente."""
    import numpy as np
    from motor import Tela as _T
    largura = x1 - x0 + extra
    idx = (np.arange(largura) * (x1 - x0) / largura).astype(int) + x0
    novo = _T(t.w + extra, t.h)
    novo.px = np.concatenate([t.px[:, :x0], t.px[:, idx], t.px[:, x1:]], axis=1)
    return novo


folha([engordar(q) for q in la.folha_da_arma("pistola")], SAIDA / "lampiao_gordo.png")
for arma in la.ar.ARMAS:
    if arma != "pistola":
        folha([engordar(q) for q in la.folha_da_arma(arma)], SAIDA / f"lampiao_{arma}_gordo.png")
import fase1  # noqa: E402
import fase1_extra as fx  # noqa: E402
folha([fx.urubu(q) for q in range(3)], SAIDA / "urubu.png")
folha([fx.galinha(q) for q in range(4)], SAIDA / "galinha.png")
folha([fx.galinha_assada()], SAIDA / "comida_galinha.png")
folha([fx.roupa(q) for q in range(3)], SAIDA / "roupa.png")
folha([fx.varal(q) for q in range(2)], SAIDA / "varal.png")
for k, (_x, w_, h_, sem, buraco) in enumerate(fase1.FASE["casas"]):
    folha([fx.casa_vila(w_, h_, sem, buraco), fx.casa_vila(w_, h_, sem, buraco, destelhada=True)], SAIDA / f"casa_vila_{k}.png")
folha([fx.ponte_segmento(fase1.FASE["ponte"][3], semente=2), fx.ponte_segmento(fase1.FASE["ponte"][3], quebrada=True, semente=2)],
      SAIDA / "ponte_seg.png")
import trem as tr  # noqa: E402
import blindagem as bl  # noqa: E402
folha([bl.danificar(bl.blindar(tr.locomotiva(k % 2, giro=k * 0.5, biela=k), semente=2, painel=26), e, 2) for e in range(4) for k in range(4)]
      + [bl.blindar(tr.locomotiva(2), semente=2, painel=26)], SAIDA / "trem_loco.png")
folha([bl.danificar(bl.blindar(tr.vagao(0, giro=k * 0.5), semente=5, painel=26), e, 5) for e in range(4) for k in range(4)]
      + [bl.blindar(tr.vagao(1), semente=5, painel=26)], SAIDA / "trem_vagao.png")
folha([tr.mg(q) for q in range(3)], SAIDA / "trem_mg.png")
folha([bl.blindar(tr.chamine(q), semente=6, lama=False) for q in range(3)], SAIDA / "trem_chamine.png")
folha([bl.blindar(tr.torre(q), semente=7, lama=False) for q in range(3)], SAIDA / "trem_torre.png")
folha([tr.porta(q) for q in range(2)], SAIDA / "trem_porta.png")
folha([tr.carvao(q) for q in range(2)], SAIDA / "carvao.png")
import jumento as jm  # noqa: E402
folha(jm.QUADROS, SAIDA / "jumento.png")
folha([jm.metralhadora()], SAIDA / "metralha_jumento.png")
import comidas as cm  # noqa: E402
for nome, (fn, _pts) in cm.COMIDAS.items():
    folha([fn()], SAIDA / f"comida_{nome}.png")
folha([la.chapeu()], SAIDA / "chapeu.png")
# Retratos do painel: sério, gritando, susto, dor, morto.
folha([la.retrato(r) for r in ("serio", "grito", "susto", "dor", "morto")], SAIDA / "retrato.png")
folha([engordar_rosto(la.retrato(r)) for r in ("serio", "grito", "susto", "dor", "morto")], SAIDA / "retrato_gordo.png")
for nome, quadros in {
    "clarao": [ef.clarao(k) for k in range(3)],
    "clarao_g": [ef.clarao(k, grande=True) for k in range(3)],
    "tracer": [ef.tracer(k) for k in range(2)],
    "bala_pesada": [ef.bala_pesada(k) for k in range(2)],
    "obus": [ef.obus(k) for k in range(3)],
    "clarao_canhao": [ef.clarao(k, grande=2.1) for k in range(3)],
    "bala_papo": [ef.bala_papo(k) for k in range(2)],
    "chumbo": [ef.chumbo(0)],
    "pedra": [ef.pedra(k) for k in range(2)],
    "foguete": [ef.foguete(k) for k in range(2)],
    "buscape_tiro": [ef.buscape(k) for k in range(2)],
    "anel": [ef.anel(k) for k in range(2)],
    "impacto": [ef.impacto(k) for k in range(4)],
    "impacto_verde": [ef.impacto_verde(k) for k in range(4)],
    "explosao": [ef.explosao_ms(k) for k in range(12)],
    "explosao_p": [ef.explosao_ms(k, tamanho=34) for k in range(12)],
    "poeira_passo": [ef.poeira_passo(k) for k in range(5)],
    "fumaca": [ef.fumaca(k) for k in range(4)],
    "chama": [ef.chama(k) for k in range(5)],
    "rajada": [ef.rajada(k) for k in range(5)],
    "labareda": [ef.labareda(k) for k in range(6)],
    "granada_g": [ef.granada(k) for k in range(4)],
    "corte_arco": [ef.corte(k) for k in range(4)],
}.items():
    folha(quadros, SAIDA / f"{nome}.png")

import fase1  # noqa: E402
fase1.exportar(SAIDA, RAIZ)
import objetos as obj  # noqa: E402
folha([obj.barril(0), obj.barril(1)], SAIDA / "barril.png")
folha([obj.escudo(0), obj.escudo(1)], SAIDA / "escudo.png")
import veiculos as vc  # noqa: E402
folha([bl.danificar(bl.blindar(q, semente=3), e, 3) for e in range(4)
       for q in [vc.caminhao(k % 2, giro=k * 0.5) for k in range(4)] + [vc.caminhao(2)]]
      + [bl.blindar(vc.caminhao(3), semente=3)], SAIDA / "caminhao.png")
folha([bl.danificar(bl.blindar(q, semente=1), e, 1) for e in range(4)
       for q in [vc.blindado(k % 2, giro=k * 0.5) for k in range(4)] + [vc.blindado(2)]
       + [vc.blindado(3, giro=k * 0.5) for k in range(4)]]
      + [bl.blindar(vc.blindado(4), semente=1)], SAIDA / "blindado.png")

for nome, tela in {
    "ceu": cn.ceu(),
    "nuvens": cn.nuvens(),
    "serras": cn.serras(),
    "paredoes": cn.paredoes(),
    "planicie": cn.planicie(),
    "caatinga": cn.caatinga(),
    "chao": cn.chao_tile(),
    "caixote": fase1.caixote_detalhado(),
    "laje": cn.laje(),
}.items():
    tela.imagem().save(SAIDA / f"{nome}.png", optimize=True)
folha([cn.touceira(k) for k in range(4)], SAIDA / "touceiras.png")

# Aumenta a versão dos assets para o navegador não usar cópias velhas.
config = RAIZ / "src/config.js"
texto = config.read_text()
import re  # noqa: E402
versao = int(re.search(r"VERSAO = (\d+)", texto).group(1)) + 1
config.write_text(re.sub(r"VERSAO = \d+", f"VERSAO = {versao}", texto))

total = sum(f.stat().st_size for f in SAIDA.glob("*.png"))
print(f"Sprites em {SAIDA} ({total // 1024} KB), versão {versao}")
