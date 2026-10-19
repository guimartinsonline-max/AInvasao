import { carregarPaleta } from '../paleta.js';
import { VERSAO } from '../config.js';
import { carregarSprites, gerarSprites } from '../sprites.js';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    this.load.json('paleta', `assets/paleta.json?v=${VERSAO}`);
    this.load.json('fase1', `assets/fases/fase1.json?v=${VERSAO}`);
    this.load.json('fase2', `assets/fases/fase2.json?v=${VERSAO}`);
    carregarSprites(this);
  }

  create() {
    carregarPaleta(this.cache.json.get('paleta'));
    gerarSprites(this);
    this.scene.start('Menu');
  }
}
