// Tabela de armas. A padrão é infinita; as outras vêm em itens com letra (src/sprites.js).
// cadencia: ms entre tiros segurando; toque: ms mínimo apertando repetido.
// bala: tipo usado por src/objetos/Balas.js. clarao: 'normal', 'grande' ou nenhum.
// capsula: solta cápsula de bala. tranco: px que o Lampião recua no chão.
export const ARMAS = {
  // Pistola Mauser, infinita (a "handgun" do Metal Slug).
  padrao: { nome: 'PISTOLA', municao: Infinity, cadencia: 150, toque: 90, bala: 'comum', tiros: 1, clarao: 'normal',
    capsula: true, semi: true },
  madsen: {
    nome: 'METRALHADORA MADSEN', municao: 200, cadencia: 60, toque: 50, bala: 'pesada', tiros: 1,
    espalha: 0.06, clarao: 'normal', capsula: true,
  },
  // Como a shotgun do Metal Slug: rajada larga e curta que pega o grupo todo.
  bacamarte: {
    nome: 'BACAMARTE', municao: 30, cadencia: 520, toque: 380, tiros: 0,
    rajada: { alcance: 66, abertura: 0.42, dano: 4 }, tranco: 4, tremor: 0.007,
  },
  rojao: {
    nome: 'ROJÃO DE SÃO JOÃO', municao: 15, cadencia: 450, toque: 350, bala: 'rojao', tiros: 1,
    tranco: 2, clarao: 'normal', fumaca: 2,
  },
  // Pistola de raio de latão: semiautomática (um tiro por toque) e o raio para no
  // primeiro que acerta (inimigo, caixote ou parede).
  desintegrador: {
    nome: 'RAIO DESINTEGRADOR', municao: 40, cadencia: 260, toque: 200, bala: 'desintegra', tiros: 1,
    clarao: 'verde', semi: true,
  },
  // Como o Flame Shot do Metal Slug: labareda grande que sobe num arco raso.
  candeeiro: {
    nome: 'CANDEEIRO', municao: 150, cadencia: 50, toque: 50, bala: 'chama', tiros: 1, espalha: 0.05, tremor: 0.0015,
  },
  papo_amarelo: {
    nome: 'PAPO-AMARELO', municao: 20, cadencia: 550, toque: 420, bala: 'papo', tiros: 1,
    tranco: 3, clarao: 'grande', capsula: true, tremor: 0.005,
  },
  estilingue: {
    nome: 'BALADEIRA', municao: 40, cadencia: 260, toque: 200, bala: 'pedra', tiros: 1,
  },
  buscape: {
    nome: 'FOGOS BUSCAPÉ', municao: 18, cadencia: 600, toque: 450, bala: 'buscape', tiros: 3,
    leque: 0.7, clarao: 'normal', fumaca: 1,
  },
};

// Itens que reféns e caixotes podem soltar.
export const PREMIOS = ['madsen', 'bacamarte', 'rojao', 'desintegrador', 'candeeiro', 'papo_amarelo', 'estilingue',
  'buscape', 'granadas'];

// Comportamento de cada tipo de bala. textura: folha de src/quadros.js (EFEITOS).
// atravessa: passa pelos inimigos (acerta cada um uma vez). morte: jeito de morrer.
// impacto: efeito no acerto ('comum', 'verde' ou nenhum). pausa: ms de pausa no impacto.
export const BALAS = {
  comum: { textura: 'tracer', velocidade: 380, dano: 1, impacto: 'comum' },
  // Bala grossa (Madsen e metralhadora do jumento), como a da metralhadora pesada do Metal Slug.
  pesada: { textura: 'bala_grossa', velocidade: 400, dano: 1, impacto: 'comum' },
  chumbo: { textura: 'chumbo', velocidade: 330, dano: 1, vida: 230, impacto: 'comum', morte: 'arremessa' },
  rojao: { textura: 'foguete', velocidade: 140, acelera: 900, maxima: 420, dano: 0, rastro: 'fumaca',
    explode: { raio: 36, dano: 4, tamanho: 1 } },
  desintegra: { textura: 'anel', velocidade: 460, dano: 2, morte: 'derrete', impacto: 'verde' },
  // Bola de fogo que cresce, perde força e sobe; deixa o inimigo pegando fogo.
  chama: { textura: 'labareda', velocidade: 330, freio: 0.975, sobe: 70, levanta: 25, vida: 640, dano: 0.7,
    atravessa: true, queima: true, morte: 'fogo', corpo: 18, porIdade: true },
  // Golfada do Lampião zumbi: onda grossa de vômito que atravessa a fila e derrete.
  // Gotas do jato do Lampião zumbi (como no Metal Slug 3): saem em leque para o alto e
  // caem em arco, atravessando quem estiver no caminho; no chão espirram gosma.
  golfada: { textura: 'gota_golfada', velocidade: 270, dano: 2, atravessa: true, vida: 1500, morte: 'derrete',
    impacto: 'verde', gravidade: 760, corpo: 12, respingo: true, porCima: true },
  papo: { textura: 'bala_papo', velocidade: 700, dano: 6, atravessa: true, impacto: 'comum', pausa: 50, morte: 'costas' },
  pedra: { textura: 'pedra', velocidade: 250, levanta: 130, gravidade: 500, quica: 2, vida: 1600, dano: 1, impacto: 'comum' },
  buscape: { textura: 'buscape_tiro', velocidade: 170, busca: 4.5, ziguezague: 9, vida: 1700, dano: 0, rastro: 'faisca',
    explode: { raio: 22, dano: 3, tamanho: 0.5 } },
};
