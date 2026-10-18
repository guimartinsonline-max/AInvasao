// Ajustes do jogador (volume, tremida de tela, teclas), guardados no aparelho.
// Se o navegador não deixar guardar (aba anônima etc.), valem só nesta sessão.

const CHAVE = 'ainvasao.ajustes';

// Ações que dá para trocar a tecla, na ordem da tela de opções.
export const ACOES_TECLADO = ['esquerda', 'direita', 'cima', 'baixo', 'pular', 'atirar', 'granada'];
export const NOMES_ACOES = {
  esquerda: 'ESQUERDA', direita: 'DIREITA', cima: 'CIMA / MIRA', baixo: 'BAIXO / AGACHA',
  pular: 'PULO', atirar: 'TIRO', granada: 'GRANADA',
};
export const TECLAS_PADRAO = {
  esquerda: 'ArrowLeft', direita: 'ArrowRight', cima: 'ArrowUp', baixo: 'ArrowDown',
  pular: 'KeyX', atirar: 'KeyZ', granada: 'KeyC',
};

const PADRAO = { efeitos: 8, musica: 6, tremida: true, teclas: { ...TECLAS_PADRAO } };

function ler() {
  try {
    const salvo = JSON.parse(localStorage.getItem(CHAVE) || 'null');
    if (salvo && typeof salvo === 'object') {
      return { ...PADRAO, ...salvo, teclas: { ...TECLAS_PADRAO, ...(salvo.teclas || {}) } };
    }
  } catch (e) {
    // Sem armazenamento: usa o padrão.
  }
  return { ...PADRAO, teclas: { ...TECLAS_PADRAO } };
}

export const ajustes = ler();
const ouvintes = new Set();

export function salvarAjustes() {
  try {
    localStorage.setItem(CHAVE, JSON.stringify(ajustes));
  } catch (e) {
    // Sem armazenamento: fica só nesta sessão.
  }
  for (const fn of ouvintes) fn(ajustes);
}

export function aoMudarAjustes(fn) {
  ouvintes.add(fn);
  return () => ouvintes.delete(fn);
}

export function restaurarPadrao() {
  Object.assign(ajustes, { efeitos: PADRAO.efeitos, musica: PADRAO.musica, tremida: true, teclas: { ...TECLAS_PADRAO } });
  salvarAjustes();
}

// Nome curto da tecla para mostrar na tela ("KeyX" -> "X", "ArrowLeft" -> "←").
export function nomeTecla(codigo) {
  const setas = { ArrowLeft: '<', ArrowRight: '>', ArrowUp: '^', ArrowDown: 'V' };
  if (setas[codigo]) return `SETA ${setas[codigo]}`;
  if (codigo.startsWith('Key')) return codigo.slice(3);
  if (codigo.startsWith('Digit')) return codigo.slice(5);
  if (codigo.startsWith('Numpad')) return `NUM ${codigo.slice(6)}`;
  const nomes = { Space: 'ESPAÇO', ShiftLeft: 'SHIFT', ShiftRight: 'SHIFT D', ControlLeft: 'CTRL', ControlRight: 'CTRL D',
    AltLeft: 'ALT', AltRight: 'ALT D', Enter: 'ENTER', Tab: 'TAB', Backspace: 'APAGAR' };
  return nomes[codigo] || codigo.toUpperCase();
}
