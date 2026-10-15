// Estilo padrão de texto: fonte pixel em múltiplos de 8 px para ficar nítida.
export function estiloTexto(cor = '#f4efe6', tamanho = 8) {
  return {
    fontFamily: '"Press Start 2P", monospace',
    fontSize: `${tamanho}px`,
    color: cor,
    resolution: 1,
    // Sombra dura de 1 px para ler bem sobre o cenário.
    shadow: { offsetX: 1, offsetY: 1, color: '#23233a', blur: 0, fill: true },
  };
}
