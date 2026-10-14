import { carregarPaleta } from '../paleta.js';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    this.load.json('paleta', 'assets/paleta.json');
  }

  create() {
    carregarPaleta(this.cache.json.get('paleta'));

    // Textura de 1 pixel branco, base para retângulos e partículas provisórias.
    const g = this.make.graphics({ x: 0, y: 0 }, false);
    g.fillStyle(0xffffff, 1).fillRect(0, 0, 1, 1);
    g.generateTexture('px', 1, 1);
    g.destroy();

    this.scene.start('Menu');
  }
}
