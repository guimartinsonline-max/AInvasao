// Ordem dos quadros das folhas geradas por tools/arte/exportar.py.

const PERNAS = ['parado', 'corre1', 'corre2', 'corre3', 'pulo'];

export const LAMPIAO = { largura: 56, altura: 52, peX: 24, peY: 50 };
PERNAS.forEach((p, i) => {
  LAMPIAO[p] = i;
  LAMPIAO[`${p}_cima`] = i + PERNAS.length;
});
LAMPIAO.agachado = PERNAS.length * 2;
LAMPIAO.grito = PERNAS.length * 2 + 1;
LAMPIAO.corrida = ['corre1', 'corre2', 'corre3', 'corre2'];

export const ALIEN = { largura: 40, altura: 44, peX: 20, peY: 42, aberto: 0, fechado: 1 };

export const TOUCEIRA = { largura: 14, altura: 10, quantidade: 4 };
