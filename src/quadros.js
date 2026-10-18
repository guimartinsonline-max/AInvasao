// Ordem dos quadros das folhas geradas por tools/arte/exportar.py.

// Lampião pixel a pixel (tools/arte/pixel/lampiao.txt), ordem de tools/arte/exportar.py.
const QUADROS_LAMPIAO = ['parado', 'atirando', 'corre1', 'corre2', 'corre3', 'corre4', 'corre5', 'corre6',
  'pulo', 'agachado', 'mira_cima', 'susto'];

export const LAMPIAO = { largura: 44, altura: 46, peX: 14, peY: 45 };
QUADROS_LAMPIAO.forEach((nome, i) => { LAMPIAO[nome] = i; });
LAMPIAO.corrida = ['corre1', 'corre2', 'corre3', 'corre4', 'corre5', 'corre6'];
// Boca do cano em relação ao pé (x para a frente, y para cima).
LAMPIAO.cano = { frente: [29, 15], agachado: [29, 10], cima: [10, 45] };

// Inimigos pixel a pixel (tools/arte/pixel/*.txt), ordem de tools/arte/exportar.py.
const ANDAR = [3, 4, 5, 6];
export const INIMIGOS = {
  volante: { largura: 44, altura: 46, peX: 14, peY: 45, corpoL: 14, corpoA: 34,
    parado: 0, atira: 1, panico: 2, morte: 2, andar: ANDAR, cano: [29, 15] },
  xeremita: { largura: 44, altura: 46, peX: 15, peY: 45, corpoL: 12, corpoA: 32,
    parado: 0, atira: 1, panico: 2, morte: 2, andar: ANDAR, cano: [15, 14] },
};

export const REFEM = { largura: 32, altura: 36, peX: 15, peY: 35, amarrado: [0, 1], continencia: 2, corrida: [3, 4, 5, 6] };
export const DISCO = { largura: 48, altura: 24 };
export const FEIXE = { largura: 14, altura: 120 };
export const BODE = { largura: 32, altura: 26, peX: 16, peY: 25, parado: 0, mastiga: 1, abduzido: 2 };

export const ALIEN = { largura: 40, altura: 44, peX: 20, peY: 42, aberto: 0, fechado: 1 };

export const TOUCEIRA = { largura: 14, altura: 10, quantidade: 4 };
