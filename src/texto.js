// Estilo padrão de texto: fonte pixel em múltiplos de 8 px para ficar nítida.
export function estiloTexto(cor = '#f4efe6', tamanho = 8) {
  return {
    fontFamily: '"Press Start 2P", monospace',
    fontSize: `${tamanho}px`,
    color: cor,
    resolution: 1,
  };
}
