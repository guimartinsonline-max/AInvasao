// Paleta fixa do jogo. Os valores vivem em assets/paleta.json, que também é
// lido pelos scripts de geração de sprites em tools/.
export const P = {};

export function carregarPaleta(json) {
  for (const [nome, hex] of Object.entries(json.cores)) {
    P[nome] = parseInt(hex.slice(1), 16);
  }
}

export function hex(nome) {
  return '#' + P[nome].toString(16).padStart(6, '0');
}
