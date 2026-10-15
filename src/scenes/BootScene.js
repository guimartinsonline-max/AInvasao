import { carregarPaleta } from '../paleta.js';
import { carregarSprites, gerarSprites } from '../sprites.js';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    this.load.json('paleta', 'assets/paleta.json');
    carregarSprites(this);
  }

  create() {
    carregarPaleta(this.cache.json.get('paleta'));
    gerarSprites(this);
    this.scene.start('Menu');
  }
}
