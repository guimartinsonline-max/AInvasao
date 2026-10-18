// Tabela de armas. A padrão é infinita; as outras vêm em itens com letra (src/sprites.js).
// cadencia: ms entre tiros segurando; toque: ms mínimo apertando repetido.
// bala: tipo usado por src/objetos/Balas.js.
export const ARMAS = {
  padrao: { nome: 'FUZIL', letra: '', municao: Infinity, cadencia: 150, toque: 70, bala: 'comum', tiros: 1 },
  madsen: {
    nome: 'METRALHADORA MADSEN', letra: 'M', municao: 200, cadencia: 60, toque: 50, bala: 'comum', tiros: 1,
    espalha: 0.06, cor: 'vermelho',
  },
  bacamarte: {
    nome: 'BACAMARTE', letra: 'B', municao: 30, cadencia: 420, toque: 300, bala: 'chumbo', tiros: 5,
    leque: 0.5, cor: 'couro_claro', tranco: 3,
  },
  rojao: {
    nome: 'ROJÃO DE SÃO JOÃO', letra: 'R', municao: 15, cadencia: 450, toque: 350, bala: 'rojao', tiros: 1,
    cor: 'laranja_fogo', tranco: 2,
  },
  desintegrador: {
    nome: 'RAIO DESINTEGRADOR', letra: 'D', municao: 60, cadencia: 120, toque: 100, bala: 'desintegra', tiros: 1,
    cor: 'alien',
  },
};

// Comportamento de cada tipo de bala.
export const BALAS = {
  comum: { textura: 'bala', velocidade: 380, dano: 1 },
  chumbo: { textura: 'chumbo', velocidade: 330, dano: 1, vida: 190 },
  rojao: { textura: 'rojao', velocidade: 140, acelera: 900, maxima: 420, dano: 0, explode: { raio: 34, dano: 4 } },
  desintegra: { textura: 'desintegra', velocidade: 460, dano: 2, atravessa: true, morte: 'derrete' },
};
