import { Fase1Scene } from './Fase1Scene.js';
import { LARGURA, DY } from './CenaJogo.js';
import { Caixotes } from '../objetos/Caixotes.js';
import { PREMIOS } from '../armas.js';
import { tocarMusica } from '../som.js';

// Fase 2: a base da cratera. Por enquanto só o trecho 1, a borda da cratera
// (arte e dados em tools/arte/fase2.py, que gera as camadas f2_*.png e assets/fases/fase2.json).
// Usa o mesmo motor de ondas, relógio e "continuar?" da fase 1.
export class Fase2Scene extends Fase1Scene {
  constructor() {
    super('Fase2');
  }

  get missao() {
    return 'MISSÃO 2';
  }

  get premios() {
    return PREMIOS;
  }

  configurar() {
    this.dados = this.cache.json.get('fase2');
    const [x, y] = this.dados.inicio;
    return { largura: this.dados.largura, inicio: { x, y } };
  }

  criarFundo() {
    const d = this.dados.camadas;
    // Céu limpo que vai ficando enfumaçado perto da cratera (o segundo céu aparece aos poucos).
    this.add.image(0, 0, 'ceu').setOrigin(0).setScrollFactor(0).setDepth(-10);
    this.ceuFumaca = this.add.image(0, 0, 'ceu_fumaca').setOrigin(0).setScrollFactor(0).setDepth(-9.5).setAlpha(0);
    this.nuvens = [this.add.tileSprite(0, 6, LARGURA, this.textures.get('nuvens').source[0].height, 'nuvens')
      .setOrigin(0).setScrollFactor(0).setDepth(-9), 0.03];
    this.camadas = [this.nuvens];
    this.ventoNuvens = 0;
    // Camadas pintadas do trecho (nenhuma se repete: o fundo muda ao longo do caminho).
    const pintada = (chave, base, fator, prof) => {
      const h = this.textures.get(chave).source[0].height;
      this.add.image(0, base - h + DY, chave).setOrigin(0).setScrollFactor(fator, 0).setDepth(prof);
    };
    pintada('f2_longe', d.longe.base, d.longe.fator, -4);
    pintada('f2_meio', d.meio.base, d.meio.fator, -3);
    pintada('f2_perto', d.perto.base, d.perto.fator, -2);
    pintada('f2_frente', d.frente.base, d.frente.fator, 25);
  }

  montarCenario() {
    const d = this.dados;
    this.add.image(0, d.camadas.jogo.y, 'f2_jogo').setOrigin(0).setDepth(5);
    for (const [x, y, w, h, umLado] of d.solidos) this.solido(x, y, w, h, !!umLado);
    this.caixotes = new Caixotes(this, d.caixotes);
  }

  povoar() {
    super.povoar();
    this.mostrar('MISSÃO 2', 'BORDA DA CRATERA', 2200);
    tocarMusica('caatinga');
  }

  atualizarFundo(cam, dt) {
    super.atualizarFundo(cam, dt);
    const f = this.dados.camadas.fumaca;
    this.ceuFumaca.setAlpha(Phaser.Math.Clamp((cam.scrollX - f.de) / (f.ate - f.de), 0, 1));
  }

  // Fim do trecho (por enquanto): placar da missão, sem a queda do disco da fase 1.
  quedaDoDisco() {
    this.mostrar('CONTINUA...', 'A DESCIDA DA CRATERA VEM AÍ', 0);
    this.time.delayedCall(2200, () => this.contarPontos());
  }
}
