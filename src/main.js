import { LARGURA, ALTURA } from './config.js';
import { ligarEscala } from './escala.js';
import { BootScene } from './scenes/BootScene.js';
import { MenuScene } from './scenes/MenuScene.js';
import { TesteScene } from './scenes/TesteScene.js';

const config = {
  type: Phaser.AUTO,
  parent: 'jogo',
  width: LARGURA,
  height: ALTURA,
  backgroundColor: '#0d0b0f',
  pixelArt: true,
  scale: {
    mode: Phaser.Scale.NONE,
    fullscreenTarget: 'jogo',
  },
  input: {
    activePointers: 4,
    gamepad: true,
  },
  physics: {
    default: 'arcade',
    arcade: { gravity: { y: 900 }, debug: false },
  },
  fps: { target: 60 },
  scene: [BootScene, MenuScene, TesteScene],
};

// Espera a fonte pixel carregar para o texto não aparecer com a fonte errada.
const fonte = document.fonts ? document.fonts.load('8px "Press Start 2P"') : Promise.resolve();
fonte.catch(() => {}).finally(() => {
  const game = new Phaser.Game(config);
  game.events.once('ready', () => ligarEscala(game));
  window.jogo = game;
});
