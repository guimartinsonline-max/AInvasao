import { carregarPaleta } from '../paleta.js';
import { gerarSprites } from '../sprites.js';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    this.load.json('paleta', 'assets/paleta.json');
  }

  create() {
    carregarPaleta(this.cache.json.get('paleta'));
    gerarSprites(this);
    this.scene.start('Menu');
  }
}
