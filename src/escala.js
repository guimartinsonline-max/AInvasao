import { LARGURA, ALTURA } from './config.js';

// Amplia o canvas sem borrar. Usa proporção inteira em pixels reais da tela
// sempre que ela ocupa pelo menos 85% do espaço; senão, usa o maior encaixe.
const APROVEITAMENTO_MINIMO = 0.85;

export function calcularEscala(largura, altura, dpr) {
  const ajuste = Math.min((largura * dpr) / LARGURA, (altura * dpr) / ALTURA);
  const inteira = Math.floor(ajuste);
  const fator = inteira >= 1 && inteira / ajuste >= APROVEITAMENTO_MINIMO ? inteira : ajuste;
  return fator / dpr;
}

export function ligarEscala(game) {
  const ajustar = () => {
    const vv = window.visualViewport;
    const largura = vv ? vv.width : window.innerWidth;
    const altura = vv ? vv.height : window.innerHeight;
    const escala = calcularEscala(largura, altura, window.devicePixelRatio || 1);
    const canvas = game.canvas;
    canvas.style.width = `${LARGURA * escala}px`;
    canvas.style.height = `${ALTURA * escala}px`;
    game.scale.refresh();
  };

  window.addEventListener('resize', ajustar);
  window.addEventListener('orientationchange', () => setTimeout(ajustar, 100));
  if (window.visualViewport) window.visualViewport.addEventListener('resize', ajustar);
  ajustar();
}

// Tela cheia no primeiro toque/clique (o navegador exige um gesto do jogador).
// No iPhone instalado na Tela de Início o app já abre em tela cheia.
export function pedirTelaCheia(game) {
  if (game.scale.isFullscreen || !game.scale.fullscreen.available) return;
  try {
    game.scale.startFullscreen();
    const orientacao = screen.orientation;
    if (orientacao && orientacao.lock) orientacao.lock('landscape').catch(() => {});
  } catch (e) {
    // Sem suporte: segue sem tela cheia.
  }
}
