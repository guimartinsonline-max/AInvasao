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
import numpy as _np  # noqa: E402


def ajoelhar(tela):
    """Morte na peixeira, 2º tempo: as pernas dobram e ele cai de joelhos (o corpo desce 8 px)."""
    t = _Tela(tela.w, tela.h)
    h = tela.h
    t.px[8:h - 4] = tela.px[0:h - 12]
    pes = tela.px[h - 4:h]
    t.px[h - 4:h] = _np.where(pes >= 0, pes, t.px[h - 4:h])
    return t


def deitar(tela):
    """Morte na peixeira, 3º tempo: desaba de cara no chão (girado em pixel, sem borrar)."""
    rot = _np.rot90(tela.px, -1)  # horário: a cabeça vai para a frente, o rosto para baixo
    ys, xs = _np.where(rot >= 0)
    t = _Tela(tela.w, tela.h)
    alt, larg = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
    dy = tela.h - 1 - ys.max()
    dx = max(0, (tela.w - larg) // 2) - xs.min()
    for y, x in zip(ys, xs):
        if 0 <= y + dy < t.h and 0 <= x + dx < t.w:
            t.px[y + dy, x + dx] = rot[y, x]
    return t
import repintar as rp  # noqa: E402
import mortos as mo  # noqa: E402
# Morte por arma: os dois últimos quadros de cada folha são o corpo tombando (no meio da
# queda) e o corpo estirado de costas, 100% no chão (tools/arte/mortos.py).
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
    # Depois da morte na peixeira: de bruços com a mão na cabeça (granada perto) e,
    # na Volante comum, as cenas cômicas (truco, cozinhando, foto da noiva).
    comicos = [d[n] for n in ("cartas1", "cartas2", "mexe1", "mexe2", "foto1", "foto2") if n in d]
    folha([d[n] for n in ordem] + [tostar(d["morte"])] + extra + [ajoelhar(d["morte"]), mo.estirar(d["morte"], False)]
          + [mo.estirar(d["grito" if nome == "xeremita" else "panico"], False)] + comicos
          + [mo.tombar(d["morte"]), mo.estirar(d["morte"])],
          SAIDA / f"{nome}.png")
d = {k: rp.repintar_tela(v) for k, v in pixel.ler("refem.txt").items()}
folha([d[n] for n in ["amarrado1", "amarrado2", "amarrado3", "solto", "procura", "entrega", "continencia",
                      "corre1", "corre2", "corre3", "corre4", "pendurado1", "pendurado2"]], SAIDA / "refem.png")
import inimigos as ini  # noqa: E402
folha([ini.disco(0), ini.disco(1)], SAIDA / "disco.png")
folha([ini.feixe(0, h=160), ini.feixe(1, h=160)], SAIDA / "feixe.png")
folha([ini.bode(n) for n in ("parado", "mastiga", "abduzido", "anda1", "anda2", "anda3", "anda4")], SAIDA / "bode.png")
folha([pg.maria_bonita()], SAIDA / "maria_bonita.png")
folha([pg.alien(), pg.alien({"olho": "fechado"})], SAIDA / "alien.png")
# Aliens da fase 2 (tools/arte/aliens.py). Mesma ordem dos inimigos (parado, atira, grito,
# anda1-4, morte, tostado, joelhos, caído, de bruços) e um extra no fim: o cérebro pulsando
# no cerebrão e o olho acendendo (aviso do raio) no olheiro.
import aliens as al  # noqa: E402
for nome, f, extra in (("cerebrao", al.cerebrao, al.cerebrao(fase=1.0)), ("olheiro", al.olheiro, al.olheiro(pose="mira"))):
    d = {p: f(pose=p) for p in ("parado", "atira", "grito", "morte")}
    anda = [f(pose="anda", k=k) for k in range(4)]
    if nome == "cerebrao":
        # Lesma: já morre rente ao chão, o cérebro rachado desaba ali mesmo.
        caido = [d["morte"], d["morte"], d["morte"], d["morte"]]
    else:
        g = d["grito"].copy() if hasattr(d["grito"], "copy") else d["grito"]
        limpo = _Tela(g.w, g.h)
        limpo.px = g.px.copy()
        limpo.px[-3:] = -1  # sem a sombra do chão antes de girar
        caido = [mo.estirar(limpo, False), mo.estirar(limpo, False), mo.tombar(limpo), mo.estirar(limpo)]
    folha([d["parado"], d["atira"], d["grito"]] + anda + [d["morte"], tostar(d["morte"]),
           ajoelhar(d["morte"]), caido[0], caido[1], extra, caido[2], caido[3]], SAIDA / f"{nome}.png")
# Soldado contaminado (tools/arte/contaminado.py): mesma ordem dos inimigos; a morte na
# peixeira e a de bala usam o corpo sem cabeça. Extras: 12 mordida, 13-14 andando sem cabeça.
import contaminado as ct  # noqa: E402
sem = [ct.contaminado("anda", k, cabeca=False) for k in (0, 2)]
folha([ct.contaminado("parado"), ct.contaminado("vomita"), ct.contaminado("grito")]
      + [ct.contaminado("anda", k) for k in range(4)]
      + [ct.contaminado("morte"), tostar(ct.contaminado("morte")), ajoelhar(sem[0]), mo.estirar(sem[0], False),
         mo.estirar(ct.contaminado("grito"), False), ct.contaminado("morde")] + sem
      + [mo.tombar(ct.contaminado("morte")), mo.estirar(ct.contaminado("morte"))], SAIDA / "contaminado.png")
ct.cabeca_solta().salvar(SAIDA / "cabeca_contaminado.png")
# Soldado de máscara contra gás (tools/arte/mascarado.py): mesmos quadros da Volante comum
# (sem as cenas cômicas), com a máscara posta antes de gerar tostado, joelhos, caído e de bruços.
import mascarado as mc  # noqa: E402
d = {k: mc.mascarar(rp.repintar_tela(v)) for k, v in pixel.ler("volante.txt").items()}
folha([d[n] for n in ["parado", "atira", "panico", "anda1", "anda2", "anda3", "anda4", "morte"]] + [tostar(d["morte"])]
      + [d["sentado1"], d["sentado2"], ajoelhar(d["morte"]), mo.estirar(d["morte"], False), mo.estirar(d["panico"], False),
         mo.tombar(d["morte"]), mo.estirar(d["morte"])],
      SAIDA / "mascarado.png")
# Lampião zumbi (tools/arte/lampiao_zumbi.py): folha, golfada grande (tiro dele) e o
# vômito pequeno do contaminado, todos animados.
import lampiao_zumbi as lz  # noqa: E402
folha(lz.folha(), SAIDA / "lampiao_zumbi.png")
folha([lz.golfada(k) for k in range(3)], SAIDA / "golfada.png")
folha([lz.gota(k, 14, 12) for k in range(3)], SAIDA / "vomito.png")
folha([lz.gota(k, 22, 18, semente=5) for k in range(3)], SAIDA / "gota_golfada.png")

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
folha([fx.galinha(q) for q in range(6)], SAIDA / "galinha.png")
folha([fx.galinha_assada()], SAIDA / "comida_galinha.png")
folha([fx.roupa(q) for q in range(3)], SAIDA / "roupa.png")
folha([fx.varal(q) for q in range(2)], SAIDA / "varal.png")
for k, (_x, w_, h_, sem, buraco) in enumerate(fase1.FASE["casas"]):
    folha([fx.casa_vila(w_, h_, sem, buraco), fx.casa_vila(w_, h_, sem, buraco, destelhada=True)], SAIDA / f"casa_vila_{k}.png")
folha([fx.ponte_segmento(fase1.FASE["ponte"][3], semente=2), fx.ponte_segmento(fase1.FASE["ponte"][3], quebrada=True, semente=2)],
      SAIDA / "ponte_seg.png")
import trem as tr  # noqa: E402
import blindagem as bl  # noqa: E402
import destrocos as ds  # noqa: E402
folha([bl.danificar(bl.blindar(tr.locomotiva(k % 2, giro=k * 0.5, biela=k), semente=2, painel=26), e, 2) for e in range(4) for k in range(4)]
      + [ds.destrocar(bl.blindar(tr.locomotiva(2), semente=2, painel=26), 3, afunda=12, rasgos=6, chassi=0.62)],
      SAIDA / "trem_loco.png")
folha([bl.danificar(bl.blindar(tr.vagao(0, giro=k * 0.5), semente=5, painel=26), e, 5) for e in range(4) for k in range(4)]
      + [ds.destrocar(bl.blindar(tr.vagao(1), semente=5, painel=26), 4, rasgos=5)], SAIDA / "trem_vagao.png")
folha([tr.mg(q) for q in range(3)], SAIDA / "trem_mg.png")
folha([bl.blindar(tr.chamine(q), semente=6, lama=False) for q in range(3)], SAIDA / "trem_chamine.png")
folha([bl.blindar(tr.torre(q), semente=7, lama=False) for q in range(3)], SAIDA / "trem_torre.png")
folha([tr.porta(q) for q in range(2)], SAIDA / "trem_porta.png")
folha([tr.carvao(q) for q in range(2)], SAIDA / "carvao.png")
import jumento as jm  # noqa: E402
folha(jm.QUADROS, SAIDA / "jumento.png")
folha([jm.metralhadora()], SAIDA / "metralha_jumento.png")
import cenas_comicas as ccm  # noqa: E402
folha([ccm.mesa_truco(q) for q in range(2)], SAIDA / "mesa_truco.png")
folha([ccm.panela(q) for q in range(3)], SAIDA / "panela.png")
folha([ccm.carta_voa(q) for q in range(2)], SAIDA / "carta_voa.png")
folha([ccm.foto_voa(q) for q in range(2)], SAIDA / "foto_voa.png")
import aviao as av  # noqa: E402
folha([bl.danificar(av.biplano(q), e, 4) for e in range(4) for q in range(4)] + [av.destrocado()], SAIDA / "biplano.png")
folha([av.artilheiro(q) for q in range(4)], SAIDA / "artilheiro.png")
folha([av.bomba(q) for q in range(2)], SAIDA / "bomba_av.png")
folha([av.biruta(q) for q in range(3)], SAIDA / "biruta.png")
import vila_campo as vca  # noqa: E402
for nome in ("cacimba", "ninho", "canoa"):
    folha([getattr(vca, nome)(q) for q in range(2)], SAIDA / f"segredo_{nome}.png")
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
import fase2  # noqa: E402
fase2.exportar(SAIDA, RAIZ)
import objetos as obj  # noqa: E402
folha([obj.barril(0), obj.barril(1)], SAIDA / "barril.png")
folha([obj.escudo(0), obj.escudo(1)], SAIDA / "escudo.png")
import veiculos as vc  # noqa: E402
folha([bl.danificar(bl.blindar(q, semente=3), e, 3) for e in range(4)
       for q in [vc.caminhao(k % 2, giro=k * 0.5) for k in range(4)] + [vc.caminhao(2)]]
      + [ds.destrocar(bl.blindar(vc.caminhao(3), semente=3), 1)], SAIDA / "caminhao.png")
folha([bl.danificar(bl.blindar(q, semente=1), e, 1) for e in range(4)
       for q in [vc.blindado(k % 2, giro=k * 0.5) for k in range(4)] + [vc.blindado(2)]
       + [vc.blindado(3, giro=k * 0.5) for k in range(4)]]
      + [ds.destrocar(bl.blindar(vc.blindado(4), semente=1), 2, quebra=0.3)], SAIDA / "blindado.png")

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
