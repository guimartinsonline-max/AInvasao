import { Fase1Scene } from './Fase1Scene.js';
import { LARGURA, DY } from './CenaJogo.js';
import { Caixotes } from '../objetos/Caixotes.js';
import { PREMIOS } from '../armas.js';
import { tocarMusica } from '../som.js';
import { VERSAO } from '../config.js';

// Fase 2: a base da cratera. Por enquanto só o trecho 1, a borda da cratera
// (arte e dados em tools/arte/fase2.py, que gera as camadas f2_*.png e assets/fases/fase2.json).
// Usa o mesmo motor de ondas, relógio e "continuar?" da fase 1.
export class Fase2Scene extends Fase1Scene {
  constructor(chave = 'Fase2') {
    super(chave);
  }

  // Cada trecho da fase 2 tem os próprios dados e camadas (f2_* no trecho 1, f2b_* no 2).
  get chaveDados() {
    return 'fase2';
  }

  get pre() {
    return 'f2';
  }

  get missao() {
    return 'MISSÃO 2';
  }

  get premios() {
    return PREMIOS;
  }

  // As colunas de fumaça animadas dependem dos dados do trecho (quantas e de que tamanho).
  preload() {
    const dados = this.cache.json.get(this.chaveDados);
    const fogo = dados.fogo;
    const chaveFogo = `${this.pre}_fogo`;
    if (fogo && !this.textures.exists(chaveFogo)) {
      this.load.spritesheet(chaveFogo, `assets/sprites/${chaveFogo}.png?v=${VERSAO}`, { frameWidth: fogo.w, frameHeight: fogo.h });
    }
    for (const f of dados.fumacas || []) {
      if (!this.textures.exists(f.chave)) {
        this.load.spritesheet(f.chave, `assets/sprites/${f.chave}.png?v=${VERSAO}`, { frameWidth: f.w, frameHeight: f.h });
      }
    }
  }

  configurar() {
    this.dados = this.cache.json.get(this.chaveDados);
    const [x, y] = this.dados.inicio;
    return { largura: this.dados.largura, inicio: { x, y } };
  }

  criarFundo() {
    const d = this.dados.camadas;
    this.criarCeu();
    const pre = this.pre;
    // Camadas pintadas do trecho (nenhuma se repete: o fundo muda ao longo do caminho).
    const pintada = (chave, base, fator, prof) => {
      const h = this.textures.get(chave).source[0].height;
      this.add.image(0, base - h + DY, chave).setOrigin(0).setScrollFactor(fator, 0).setDepth(prof);
    };
    pintada(`${pre}_longe`, d.longe.base, d.longe.fator, -4.6);
    pintada(`${pre}_borda`, d.borda.base, d.borda.fator, -4);
    pintada(`${pre}_meio`, d.meio.base, d.meio.fator, -3);
    // Fumaça subindo sem parar: a do disco entre as serras e a borda da cratera; a dos
    // incêndios atrás dos morros (o morro e a casa tapam a base, como se saísse do fogo).
    for (const f of this.dados.fumacas || []) {
      const c = d[f.camada];
      const h = this.textures.get(`${pre}_${f.camada}`).source[0].height;
      const anim = `${f.chave}_sobe`;
      if (!this.anims.exists(anim)) {
        this.anims.create({ key: anim, frames: this.anims.generateFrameNumbers(f.chave, { start: 0, end: f.n - 1 }),
          frameRate: f.camada === 'longe' ? 5 : 7, repeat: -1 });
      }
      this.add.sprite(f.x, c.base - h + DY + f.y, f.chave, 0).setOrigin(0).setScrollFactor(c.fator, 0)
        .setDepth(f.camada === 'longe' ? -4.3 : -3.3).play({ key: anim, startFrame: Phaser.Math.Between(0, f.n - 1) });
    }
    // Labaredas vivas (casa ardendo, focos no morro, foguinhos na borda da cratera): cada
    // uma com o próprio loop, começando num quadro qualquer para não tremerem juntas.
    const PROF = { longe: -4.55, borda: -3.95, meio: -2.95, perto: -1.95 };
    (this.dados.fogos || []).forEach((f, k) => {
      const c = d[f.camada];
      const h = this.textures.get(`${pre}_${f.camada}`).source[0].height;
      const anim = `${pre}_fogo_${k}`;
      if (!this.anims.exists(anim)) {
        this.anims.create({ key: anim, frames: this.anims.generateFrameNumbers(`${pre}_fogo`, { start: f.q, end: f.q + this.dados.fogo.n - 1 }),
          frameRate: Phaser.Math.Between(10, 13), repeat: -1 });
      }
      this.add.sprite(f.x, c.base - h + DY + f.y, `${pre}_fogo`, f.q).setOrigin(0).setScrollFactor(c.fator, 0)
        .setDepth(PROF[f.camada]).play({ key: anim, startFrame: Phaser.Math.Between(0, this.dados.fogo.n - 1) });
    });
    pintada(`${pre}_perto`, d.perto.base, d.perto.fator, -2);
    pintada(`${pre}_frente`, d.frente.base, d.frente.fator, 25);
  }

  // Céu limpo que vai ficando enfumaçado perto da cratera (o segundo céu aparece aos poucos).
  criarCeu() {
    this.add.image(0, 0, 'ceu').setOrigin(0).setScrollFactor(0).setDepth(-10);
    this.ceuFumaca = this.add.image(0, 0, 'ceu_fumaca').setOrigin(0).setScrollFactor(0).setDepth(-9.5).setAlpha(0);
    this.nuvens = [this.add.tileSprite(0, 6, LARGURA, this.textures.get('nuvens').source[0].height, 'nuvens')
      .setOrigin(0).setScrollFactor(0).setDepth(-9), 0.03];
    this.camadas = [this.nuvens];
    this.ventoNuvens = 0;
  }

  montarCenario() {
    const d = this.dados;
    this.add.image(0, d.camadas.jogo.y, `${this.pre}_jogo`).setOrigin(0).setDepth(5);
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

  // Fim do trecho 1: segue direto para o acampamento da base, levando pontos, vidas e arma.
  quedaDoDisco() {
    this.mostrar('MUITO BEM!', 'RUMO AO ACAMPAMENTO', 0);
    const j = this.jogador;
    const herda = {
      pontos: this.pontos, refensSalvos: this.refensSalvos, tiros: this.tiros, acertos: this.acertos, mortes: this.mortes,
      vidas: j.vidas, arma: j.arma, municao: j.municao, nivel: j.nivel, granadas: j.granadas,
    };
    this.time.delayedCall(1600, () => this.cameras.main.fadeOut(500, 0, 0, 0));
    this.time.delayedCall(2150, () => this.scene.start('Fase2b', herda));
  }
}
