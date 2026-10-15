// Ordem dos quadros das folhas geradas por tools/arte/exportar.py.

// Lampião pixel a pixel (tools/arte/pixel/lampiao.txt), ordem de tools/arte/exportar.py.
const QUADROS_LAMPIAO = ['parado', 'atirando', 'corre1', 'corre2', 'corre3', 'corre4', 'corre5', 'corre6',
  'pulo', 'agachado', 'mira_cima', 'susto'];

export const LAMPIAO = { largura: 44, altura: 46, peX: 14, peY: 45 };
QUADROS_LAMPIAO.forEach((nome, i) => { LAMPIAO[nome] = i; });
LAMPIAO.corrida = ['corre1', 'corre2', 'corre3', 'corre4', 'corre5', 'corre6'];
// Boca do cano em relação ao pé (x para a frente, y para cima).
LAMPIAO.cano = { frente: [29, 15], agachado: [29, 10], cima: [10, 45] };

export const ALIEN = { largura: 40, altura: 44, peX: 20, peY: 42, aberto: 0, fechado: 1 };

export const TOUCEIRA = { largura: 14, altura: 10, quantidade: 4 };
