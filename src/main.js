import { LARGURA, ALTURA } from './config.js';
import { ligarEscala } from './escala.js';
import { BootScene } from './scenes/BootScene.js';
import { MenuScene } from './scenes/MenuScene.js';
import { PaletaScene } from './scenes/PaletaScene.js';
import { CampoScene } from './scenes/CampoScene.js';
import { HudScene } from './scenes/HudScene.js';
import { Controles } from './controles.js';

const config = {
  type: Phaser.AUTO,
  parent: 'jogo',
  width: LARGURA,
  height: ALTURA,
  backgroundColor: '#0e0d14',
  pixelArt: true,
  scale: {
    mode: Phaser.Scale.NONE,
    fullscreenTarget: 'jogo',
  },
  input: {
    activePointers: 4,
  },
  physics: {
    default: 'arcade',
    arcade: { gravity: { y: 900 }, debug: false },
  },
  fps: { target: 60 },
  scene: [BootScene, MenuScene, CampoScene, HudScene, PaletaScene],
};

// Espera a fonte pixel carregar para o texto não aparecer com a fonte errada.
const fonte = document.fonts ? document.fonts.load('8px "Press Start 2P"') : Promise.resolve();
fonte.catch(() => {}).finally(() => {
  const game = new Phaser.Game(config);
  game.controles = new Controles();
  game.events.once('ready', () => ligarEscala(game));
  window.jogo = game;
});
