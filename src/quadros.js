// Ordem dos quadros das folhas geradas por tools/arte/exportar.py.

// Lampião pixel a pixel (tools/arte/pixel/lampiao.txt), ordem de tools/arte/exportar.py.
const QUADROS_LAMPIAO = ['parado', 'atirando', 'corre1', 'corre2', 'corre3', 'corre4', 'corre5', 'corre6',
  'pulo', 'agachado', 'mira_cima', 'susto', 'arremesso', 'facada', 'facada1', 'mira_baixo', 'recarga',
  'morte1', 'morte2', 'morte3', 'espera1', 'espera2', 'espera3'];

export const LAMPIAO = { largura: 60, altura: 72, peX: 14, peY: 63 };
// Lampião gordo (comeu demais): mesmas folhas esticadas 5 px no meio do corpo.
// Lampião zumbi (tools/arte/lampiao_zumbi.py): mesmo tamanho e pé do Lampião.
export const ZUMBI = { parado: 0, andar: [1, 2, 3, 4], pulo: 5, golfada: 6 };
export const LAMPIAO_GORDO = { largura: 65, altura: 72, peX: 16, peY: 63 };
// Comidas que dão pontos (tools/arte/comidas.py), da mais comum à mais rara.
export const COMIDAS = { caja: 100, rapadura: 300, queijo: 500, galinha: 800, cuscuz: 1000, buchada: 2000 };
QUADROS_LAMPIAO.forEach((nome, i) => { LAMPIAO[nome] = i; });
LAMPIAO.corrida = ['corre1', 'corre2', 'corre3', 'corre4', 'corre5', 'corre6'];
// Boca do cano em relação ao pé (x para a frente, y para cima).
LAMPIAO.cano = { frente: [29, 15], agachado: [29, 10], cima: [10, 45] };
// Mão erguida no quadro de arremesso da granada.
LAMPIAO.maoGranada = [-9, 42];

// Inimigos pixel a pixel (tools/arte/pixel/*.txt), ordem de tools/arte/exportar.py.
// Caricatos (tools/arte/caricatos.py): o quadro 7 é a morte e o 8 é o tostado (queimado).
const ANDAR = [3, 4, 5, 6];
export const INIMIGOS = {
  volante: { largura: 52, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [28, 17] },
  xeremita: { largura: 52, altura: 46, peX: 17, peY: 45, corpoL: 14, corpoA: 38,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [23, 16] },
  // Variações da Volante: granadeiro (dinamite), metralhador (rajada) e sargento do facão.
  granadeiro: { largura: 52, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [0, 38] },
  metralhador: { largura: 52, altura: 46, peX: 14, peY: 45, corpoL: 16, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [28, 16] },
  facao: { largura: 52, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [24, 20] },
  // Soldado do lança-rojão (o tubo no ombro, rente ao olho).
  rojao: { largura: 52, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [38, 31] },
};
// Soldados da Volante sentados cochilando (distraídos): quadros 9 e 10.
// Oficial da Volante: espada erguida dando ordem, pistola, chora fugindo.
INIMIGOS.oficial = { largura: 52, altura: 46, peX: 14, peY: 45, corpoL: 16, corpoA: 36,
  parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [33, 19] };
// Soldado de máscara contra gás (fase 2, tools/arte/mascarado.py): quadros da Volante comum.
INIMIGOS.mascarado = { ...INIMIGOS.volante };
for (const tipo of ['volante', 'granadeiro', 'metralhador', 'facao', 'rojao', 'oficial', 'mascarado']) {
  INIMIGOS[tipo].sentado = [9, 10];
  INIMIGOS[tipo].facada = [11, 12]; // morte na peixeira: de joelhos e caído de cara
}
INIMIGOS.xeremita.facada = [9, 10];
// De bruços com a mão na cabeça (granada caiu perto).
for (const tipo of ['volante', 'granadeiro', 'metralhador', 'facao', 'rojao', 'oficial', 'mascarado']) INIMIGOS[tipo].brucos = 13;
INIMIGOS.xeremita.brucos = 11;
// Aliens da fase 2 (tools/arte/aliens.py): mesma ordem de quadros dos inimigos e um extra
// no 12 (cerebrão: cérebro pulsando parado; olheiro: olho acendendo antes do raio).
INIMIGOS.cerebrao = { largura: 60, altura: 52, peX: 30, peY: 50, corpoL: 26, corpoA: 44,
  parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [27, 12],
  facada: [9, 10], brucos: 11, pulsa: 12 };
INIMIGOS.olheiro = { largura: 60, altura: 60, peX: 27, peY: 58, corpoL: 16, corpoA: 50,
  parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [26, 33],
  facada: [9, 10], brucos: 11, mira: 12 };
// Soldado contaminado (tools/arte/contaminado.py): 1 é o vômito, 12 a mordida,
// 13-14 andando sem cabeça; 9-10 (joelhos e caído) já sem cabeça.
INIMIGOS.contaminado = { largura: 52, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
  parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [24, 23],
  facada: [9, 10], brucos: 11, morde: 12, semCabeca: [13, 14] };
// Cenas cômicas da Volante comum antes de ver o Lampião (tools/arte/caricatos.py).
INIMIGOS.volante.cenas = { truco: [14, 15], cozinha: [16, 17], foto: [18, 19] };
// Objetos das cenas cômicas (tools/arte/cenas_comicas.py).
// Subchefe da fase 1: biplano da Aviação Militar (tools/arte/aviao.py). 4 etapas de dano
// com 4 quadros de hélice cada (0 parada, 1-3 girando) e o queimado no fim.
export const AVIAO = {
  biplano: { largura: 132, altura: 60, n: 4, destruido: 16, rodaX: 92 },
  artilheiro: { largura: 28, altura: 24 },
  torreta_mg: { largura: 30, altura: 12 },
  bomba_av: { largura: 14, altura: 8 },
  biruta: { largura: 26, altura: 46 },
};
// Segredos: levam tiro e soltam prêmio (tools/arte/vila_campo.py). Quadro 0 inteiro, 1 aberto.
export const SEGREDOS = {
  segredo_cacimba: { largura: 32, altura: 40, vida: 4 },
  segredo_ninho: { largura: 24, altura: 16, vida: 2 },
  segredo_canoa: { largura: 64, altura: 16, vida: 5 },
};
export const CENAS = {
  mesa_truco: { largura: 36, altura: 22 },
  panela: { largura: 22, altura: 26 },
  carta_voa: { largura: 5, altura: 7 },
  foto_voa: { largura: 8, altura: 9 },
};

// Romeiro do mesmo porte do Lampião (tools/arte/caricatos.py).
export const REFEM = { largura: 52, altura: 46, peX: 17, peY: 45, amarrado: [0, 1, 2], solto: 3, procura: 4,
  entrega: 5, continencia: 6, corrida: [7, 8, 9, 10], pendurado: [11, 12], maosY: 43.5, maosX: 2 };
export const DISCO = { largura: 123, altura: 56 };
export const FEIXE = { largura: 14, altura: 160 };
// Veículos da Volante (tools/arte/veiculos.py), virados para a direita; pé no centro de baixo.
export const VEICULOS = {
  // Cada folha tem 4 etapas de dano (0 inteiro a 3 arrebentado) com n quadros cada,
  // e o quadro destruído no fim. rodas: dx das rodas a partir do centro (desenho virado para a direita).
  caminhao: { largura: 124, altura: 62, n: 5, andar: [0, 1, 2, 3], aberto: 4, destruido: 20, rodas: [-36, 38] },
  blindado: { largura: 132, altura: 90, n: 9, andar: [0, 1, 2, 3], tiro: 4, quebrado: [5, 6, 7, 8], destruido: 36, rodas: [-38, 36] },
};
export const BODE = { largura: 32, altura: 26, peX: 16, peY: 25, parado: 0, mastiga: 1, abduzido: 2, andar: [3, 4, 5, 6] };

export const ALIEN = { largura: 40, altura: 44, peX: 20, peY: 42, aberto: 0, fechado: 1 };

export const TOUCEIRA = { largura: 14, altura: 10, quantidade: 4 };

// Folhas de efeitos de tiro (tools/arte/efeitos_tiro.py): tamanho do quadro e quantidade.
export const EFEITOS = {
  golfada: { largura: 64, altura: 32, quadros: 3 },
  vomito: { largura: 14, altura: 12, quadros: 3 },
  gota_golfada: { largura: 22, altura: 18, quadros: 3 },
  clarao: { largura: 24, altura: 18, quadros: 3 },
  clarao_g: { largura: 33, altura: 25, quadros: 3 },
  tracer: { largura: 12, altura: 3, quadros: 2 },
  bala_pesada: { largura: 22, altura: 10, quadros: 2 },
  obus: { largura: 30, altura: 14, quadros: 3 },
  clarao_canhao: { largura: 50, altura: 37, quadros: 3 },
  bala_papo: { largura: 32, altura: 6, quadros: 2 },
  bala_grossa: { largura: 18, altura: 8, quadros: 2 },
  bala_inimiga: { largura: 12, altura: 7, quadros: 2 },
  chumbo: { largura: 5, altura: 5, quadros: 1 },
  pedra: { largura: 10, altura: 10, quadros: 2 },
  foguete: { largura: 32, altura: 11, quadros: 2 },
  buscape_tiro: { largura: 17, altura: 7, quadros: 2 },
  anel: { largura: 14, altura: 22, quadros: 2 },
  impacto: { largura: 14, altura: 14, quadros: 4 },
  impacto_verde: { largura: 20, altura: 20, quadros: 4 },
  explosao: { largura: 56, altura: 56, quadros: 12 },
  explosao_p: { largura: 34, altura: 34, quadros: 12 },
  poeira_passo: { largura: 20, altura: 10, quadros: 5 },
  fumaca: { largura: 14, altura: 14, quadros: 4 },
  chama: { largura: 22, altura: 22, quadros: 5 },
  rajada: { largura: 68, altura: 40, quadros: 5 },
  labareda: { largura: 34, altura: 34, quadros: 6 },
  granada_g: { largura: 11, altura: 11, quadros: 4 },
  corte_arco: { largura: 34, altura: 40, quadros: 4 },
};

// Peças vivas do acampamento da base (fase 2, trecho 2; tools/arte/fase2b.py e cientista.py).
export const BASE = {
  holofote: { largura: 24, altura: 18 },
  gerador: { largura: 46, altura: 34 },
  jaula: { largura: 40, altura: 44 },
  pedaco_disco: { largura: 56, altura: 40 },
  lampada: { largura: 6, altura: 8 },
  bandeira: { largura: 34, altura: 20 },
  cientista: { largura: 52, altura: 46 },
};
