import { Fase2Scene } from './Fase2Scene.js';
import { DY } from './CenaJogo.js';
import { Base } from '../objetos/Base.js';
import { Refem } from '../objetos/Refem.js';
import { tocarMusica, som } from '../som.js';

// Fase 2, trecho 2: o acampamento da base (arte e dados em tools/arte/fase2b.py, que gera
// as camadas f2b_*.png, as peças vivas e assets/fases/fase2b.json). Anoitece enquanto o
// Lampião avança; holofotes, geradores, jaulas com aliens e o guindaste ficam em
// src/objetos/Base.js. No fim, o elevador de carga desce para dentro da cratera.
export class Fase2bScene extends Fase2Scene {
  constructor() {
    super('Fase2b');
  }

  get chaveDados() {
    return 'fase2b';
  }

  get pre() {
    return 'f2b';
  }

  // Vem do trecho 1 com pontos, vidas e arma (ou direto do menu, sem nada).
  init(dados) {
    this.herda = dados && dados.vidas !== undefined ? dados : null;
  }

  // Céu de fim de tarde que vira noite fechada conforme anda.
  criarCeu() {
    this.add.image(0, 0, 'ceu_tarde').setOrigin(0).setScrollFactor(0).setDepth(-10);
    this.ceuNoite = this.add.image(0, 0, 'ceu_noite').setOrigin(0).setScrollFactor(0).setDepth(-9.5).setAlpha(0);
    this.camadas = [];
    this.nuvens = [{ tilePositionX: 0 }, 0];
    this.ventoNuvens = 0;
  }

  criarFundo() {
    super.criarFundo();
    const d = this.dados;
    // Bandeira da Volante tremulando no mastro da camada de perto.
    if (d.bandeira) {
      const c = d.camadas[d.bandeira.camada];
      const h = this.textures.get(`${this.pre}_${d.bandeira.camada}`).source[0].height;
      if (!this.anims.exists('bandeira_tremula')) {
        this.anims.create({ key: 'bandeira_tremula', frames: this.anims.generateFrameNumbers('bandeira', { start: 0, end: 3 }),
          frameRate: 8, repeat: -1 });
      }
      this.add.sprite(d.bandeira.x, c.base - h + DY + d.bandeira.y, 'bandeira', 0).setOrigin(0).setScrollFactor(c.fator, 0)
        .setDepth(-1.95).play('bandeira_tremula');
    }
    // Fachos de holofote varrendo o céu lá atrás do acampamento.
    this.fachosFundo = this.add.graphics().setScrollFactor(0.45, 0).setDepth(-3.2).setBlendMode(Phaser.BlendModes.ADD);
  }

  montarCenario() {
    super.montarCenario();
    // Plataforma do elevador de carga no fim (desce com o Lampião).
    const e = this.dados.base.elevador;
    this.plataforma = this.add.image(e.x, e.y + 1, 'plataforma_elevador').setOrigin(0.5, 1).setDepth(8.5);
  }

  povoar() {
    super.povoar();
    this.base = new Base(this, this.dados.base);
    // Cientista amarrado na frente do laboratório (solto, dá o Raio Desintegrador).
    for (const [x, pe] of this.dados.cientistas || []) {
      const r = new Refem(this, x, pe, { cientista: true });
      this.alvos.add(r);
      r.reiniciar();
      this.refens.push(r);
    }
    const h = this.herda;
    if (h) {
      this.cameras.main.fadeIn(500, 0, 0, 0);
      const j = this.jogador;
      Object.assign(this, { pontos: h.pontos, refensSalvos: h.refensSalvos, tiros: h.tiros, acertos: h.acertos, mortes: h.mortes });
      j.vidas = h.vidas;
      j.granadas = h.granadas;
      if (h.arma && h.arma !== 'padrao') {
        j.trocarArma(h.arma);
        j.municao = h.municao;
        j.nivel = h.nivel;
      }
    }
    this.mostrar('MISSÃO 2', 'ACAMPAMENTO DA BASE', 2200);
    tocarMusica('caatinga');
  }

  atualizarFundo(cam, dt) {
    const n = this.dados.base.noite;
    this.ceuNoite.setAlpha(Phaser.Math.Clamp((cam.scrollX - n.de) / (n.ate - n.de), 0, 1));
    for (const [camada, fator] of this.camadas) camada.tilePositionX = Math.round(cam.scrollX * fator);
    // Dois fachos de holofote lá longe cruzando o céu.
    const t = this.time.now;
    const g = this.fachosFundo;
    g.clear();
    for (const [x, fase] of [[260, 0], [700, 2.1], [1100, 4]]) {
      const a = -Math.PI / 2 + Math.sin(t / 1700 + fase) * 0.5;
      const y = 150 + DY;
      g.fillStyle(0xf0e0b0, 0.07);
      g.fillTriangle(x, y, x + Math.cos(a - 0.05) * 260, y + Math.sin(a - 0.05) * 260,
        x + Math.cos(a + 0.05) * 260, y + Math.sin(a + 0.05) * 260);
    }
  }

  atualizarFase(t, dt) {
    super.atualizarFase(t, dt);
    if (this.base) this.base.atualizar(t);
  }

  // Fim do trecho: o Lampião sobe na plataforma do elevador e desce para dentro da cratera,
  // com a corrente rangendo e faísca verde subindo do buraco.
  quedaDoDisco() {
    const j = this.jogador;
    const p = this.plataforma;
    const cam = this.cameras.main;
    cam.stopFollow();
    this.tweens.add({ targets: [j.corpo, j.visual], x: p.x - 6, duration: 600, ease: 'Sine.easeInOut' });
    this.time.delayedCall(700, () => {
      j.corpo.body.enable = false;
      this.mostrar('DESCENDO!', '', 1200);
      som('apito');
      const desce = { y: 0 };
      this.tweens.add({
        targets: desce, y: 150, duration: 2600, ease: 'Sine.easeIn',
        onUpdate: () => {
          p.y = this.dados.base.elevador.y + 1 + desce.y;
          j.corpo.y = p.y - 20;
          j.visual.y = p.y - 1;
          if (Math.random() < 0.3) this.efeitos.faisca(p.x + Phaser.Math.Between(-28, 28), p.y - 6, 1);
        },
      });
      this.efeitos.tremer(0.004, 2600);
    });
    this.time.delayedCall(3500, () => {
      this.mostrar('CONTINUA...', 'A DESCIDA DA CRATERA VEM AÍ', 0);
      this.time.delayedCall(2200, () => this.contarPontos());
    });
  }
}
