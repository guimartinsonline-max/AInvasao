// Resolução interna fixa. Tudo no jogo é desenhado nesse tamanho e ampliado.
// Era 384x216; subiu 1/0,7 para os personagens ficarem 30% menores na tela,
// com pixels menores, como no Metal Slug.
export const LARGURA = 548;
export const ALTURA = 308;
// O mundo continua com o chão em y = 192; a tela mostra DY pixels a mais de céu
// em cima (a câmera começa em y = -DY). Coisas presas à tela descem DY.
export const DY = ALTURA - 216;

// Versão dos arquivos de assets/. Entra no endereço (?v=) para o navegador
// nunca usar uma cópia velha guardada em cache. Aumentar a cada mudança em assets/.
export const VERSAO = 117;
