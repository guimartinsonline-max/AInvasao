import { LARGURA, ALTURA } from './config.js';
import { ligarEscala } from './escala.js';
import { BootScene } from './scenes/BootScene.js';
import { MenuScene } from './scenes/MenuScene.js';
import { PaletaScene } from './scenes/PaletaScene.js';
import { CampoScene } from './scenes/CampoScene.js';
import { Fase1Scene } from './scenes/Fase1Scene.js';
import { Fase2Scene } from './scenes/Fase2Scene.js';
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
    // Passo variável: a física anda junto com cada quadro da tela, então nada
    // treme em monitores de 120/144/240 Hz.
    arcade: { gravity: { y: 900 }, debug: false, fixedStep: false },
  },
  fps: { target: 60 },
  scene: [BootScene, MenuScene, Fase1Scene, Fase2Scene, CampoScene, HudScene, PaletaScene],
};

// Espera a fonte pixel carregar (no máximo 3 s) para o texto não sair com a fonte errada.
const fonte = document.fonts ? document.fonts.load('8px "Press Start 2P"') : Promise.resolve();
const limite = new Promise((ok) => setTimeout(ok, 3000));
Promise.race([fonte, limite]).catch(() => {}).finally(() => {
  const game = new Phaser.Game(config);
  game.controles = new Controles();
  game.events.once('ready', () => {
    ligarEscala(game);
    const aviso = document.getElementById('aviso');
    if (aviso.className !== 'erro') aviso.style.display = 'none';
  });
  window.jogo = game;
});
