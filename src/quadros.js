// Ordem dos quadros das folhas geradas por tools/arte/exportar.py.

// Lampião pixel a pixel (tools/arte/pixel/lampiao.txt), ordem de tools/arte/exportar.py.
const QUADROS_LAMPIAO = ['parado', 'atirando', 'corre1', 'corre2', 'corre3', 'corre4', 'corre5', 'corre6',
  'pulo', 'agachado', 'mira_cima', 'susto', 'arremesso', 'facada', 'facada1', 'mira_baixo', 'recarga',
  'morte1', 'morte2', 'morte3'];

export const LAMPIAO = { largura: 44, altura: 46, peX: 14, peY: 45 };
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
  volante: { largura: 44, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [28, 17] },
  xeremita: { largura: 44, altura: 46, peX: 17, peY: 45, corpoL: 14, corpoA: 38,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [23, 16] },
  // Variações da Volante: granadeiro (dinamite), metralhador (rajada) e sargento do facão.
  granadeiro: { largura: 44, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [0, 38] },
  metralhador: { largura: 44, altura: 46, peX: 14, peY: 45, corpoL: 16, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [28, 16] },
  facao: { largura: 44, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [24, 20] },
  // Soldado do lança-rojão (o tubo no ombro, rente ao olho).
  rojao: { largura: 44, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 36,
    parado: 0, atira: 1, panico: 2, morte: 7, tostado: 8, andar: ANDAR, cano: [38, 31] },
};
// Soldados da Volante sentados cochilando (distraídos): quadros 9 e 10.
for (const tipo of ['volante', 'granadeiro', 'metralhador', 'facao', 'rojao']) INIMIGOS[tipo].sentado = [9, 10];

// Romeiro do mesmo porte do Lampião (tools/arte/caricatos.py).
export const REFEM = { largura: 44, altura: 46, peX: 17, peY: 45, amarrado: [0, 1, 2], solto: 3, procura: 4,
  entrega: 5, continencia: 6, corrida: [7, 8, 9, 10], pendurado: [11, 12], maosY: 43.5, maosX: 2 };
export const DISCO = { largura: 123, altura: 56 };
export const FEIXE = { largura: 14, altura: 160 };
// Veículos da Volante (tools/arte/veiculos.py), virados para a direita; pé no centro de baixo.
export const VEICULOS = {
  caminhao: { largura: 124, altura: 62, andar: [0, 1], aberto: 2, destruido: 3 },
  blindado: { largura: 132, altura: 76, andar: [0, 1], tiro: 2, quebrado: 3, destruido: 4 },
};
export const BODE = { largura: 32, altura: 26, peX: 16, peY: 25, parado: 0, mastiga: 1, abduzido: 2 };

export const ALIEN = { largura: 40, altura: 44, peX: 20, peY: 42, aberto: 0, fechado: 1 };

export const TOUCEIRA = { largura: 14, altura: 10, quantidade: 4 };

// Folhas de efeitos de tiro (tools/arte/efeitos_tiro.py): tamanho do quadro e quantidade.
export const EFEITOS = {
  clarao: { largura: 24, altura: 18, quadros: 3 },
  clarao_g: { largura: 33, altura: 25, quadros: 3 },
  tracer: { largura: 12, altura: 3, quadros: 2 },
  bala_pesada: { largura: 26, altura: 8, quadros: 2 },
  obus: { largura: 30, altura: 14, quadros: 3 },
  clarao_canhao: { largura: 50, altura: 37, quadros: 3 },
  bala_papo: { largura: 20, altura: 3, quadros: 2 },
  chumbo: { largura: 3, altura: 3, quadros: 1 },
  pedra: { largura: 7, altura: 7, quadros: 2 },
  foguete: { largura: 22, altura: 7, quadros: 2 },
  buscape_tiro: { largura: 12, altura: 5, quadros: 2 },
  anel: { largura: 10, altura: 16, quadros: 2 },
  impacto: { largura: 14, altura: 14, quadros: 4 },
  impacto_verde: { largura: 20, altura: 20, quadros: 4 },
  explosao: { largura: 40, altura: 40, quadros: 8 },
  explosao_p: { largura: 24, altura: 24, quadros: 8 },
  fumaca: { largura: 14, altura: 14, quadros: 4 },
  chama: { largura: 22, altura: 22, quadros: 5 },
  rajada: { largura: 68, altura: 40, quadros: 5 },
  labareda: { largura: 34, altura: 34, quadros: 6 },
  granada_g: { largura: 11, altura: 11, quadros: 4 },
  corte_arco: { largura: 34, altura: 40, quadros: 4 },
};
