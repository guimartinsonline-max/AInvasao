import { LARGURA, ALTURA, DY } from '../config.js';
import { hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { pedirTelaCheia } from '../escala.js';
import { LAMPIAO, INIMIGOS } from '../quadros.js';

const AVISOS = {
  toque: 'TOQUE PARA COMEÇAR',
  teclado: 'APERTE ENTER',
  controle: 'APERTE A OU START',
};

export class MenuScene extends Phaser.Scene {
  constructor() {
    super('Menu');
  }

  create() {
    this.controles = this.game.controles;
    this.add.image(0, 0, 'ceu').setOrigin(0);
    // O cenário fica embaixo, no mesmo lugar da fase (DY a mais de céu em cima).
    const faixa = (chave, y, x = 0) => this.add.tileSprite(x, y, LARGURA - x, this.textures.get(chave).source[0].height, chave).setOrigin(0);
    faixa('nuvens', 6);
    faixa('serras', DY - 32);
    faixa('paredoes', 46 + DY).tilePositionX = 40;
    faixa('planicie', 168 + DY);
    faixa('caatinga', 122 + DY).tilePositionX = 60;
    this.add.tileSprite(0, 192 + DY, LARGURA, 24, 'chao').setOrigin(0);
        this.add.image(LARGURA / 2, 194 + DY, 'lampiao', LAMPIAO.parado).setOrigin(LAMPIAO.peX / LAMPIAO.largura, LAMPIAO.peY / LAMPIAO.altura);
    for (const [x, tipo] of [[LARGURA / 2 + 74, 'xeremita'], [LARGURA / 2 + 124, 'volante']]) {
      const q = INIMIGOS[tipo];
      this.add.image(x, 194 + DY, tipo, q.parado).setFlipX(true).setOrigin((q.largura - q.peX) / q.largura, q.peY / q.altura);
    }

    this.add.text(LARGURA / 2 + 2, 50 + DY / 2, 'A INVASÃO', estiloTexto(hex('azul_sombra'), 24)).setOrigin(0.5);
    this.add.text(LARGURA / 2, 48 + DY / 2, 'A INVASÃO', estiloTexto(hex('amarelo_fogo'), 24)).setOrigin(0.5);
    this.add.text(LARGURA / 2, 76 + DY / 2, 'SERTÃO, 1936', estiloTexto(hex('branco'))).setOrigin(0.5);

    // Opções: a fase 1 e o campo de treino (todas as armas, tudo volta).
    this.opcoes = [
      { cena: 'Fase1', texto: 'MISSÃO 1' },
      { cena: 'Campo', texto: 'CAMPO DE TREINO' },
    ].map((o, k) => {
      const t = this.add.text(LARGURA / 2, 122 + DY / 2 + k * 16, o.texto, estiloTexto(hex('branco'))).setOrigin(0.5)
        .setInteractive({ useHandCursor: true });
      t.on('pointerdown', (p, x, y, e) => {
        e.stopPropagation();
        this.escolha = k;
        this.comecar();
      });
      return { ...o, t };
    });
    this.escolha = 0;
    this.marcar();
    this.aviso = this.add.text(LARGURA / 2, 100 + DY / 2, '', estiloTexto(hex('branco'))).setOrigin(0.5);
    this.time.addEvent({ delay: 500, loop: true, callback: () => this.aviso.setVisible(!this.aviso.visible) });
    this.mostrarAviso(this.controles.fonte);
    const desligar = this.controles.aoMudarFonte((f) => this.mostrarAviso(f));
    this.events.once('shutdown', desligar);

    this.botaoPaleta = this.add.text(LARGURA - 4, ALTURA - 4, 'PALETA', estiloTexto(hex('areia_clara')))
      .setOrigin(1).setInteractive();
    this.botaoPaleta.on('pointerdown', (p, x, y, e) => {
      e.stopPropagation();
      this.scene.start('Paleta');
    });
    this.input.on('pointerdown', () => this.comecar());
    this.input.keyboard.on('keydown-P', () => this.scene.start('Paleta'));
  }

  marcar() {
    this.opcoes.forEach((o, k) => {
      const sel = k === this.escolha;
      o.t.setText(sel ? `> ${o.texto} <` : o.texto).setColor(sel ? hex('amarelo_fogo') : hex('branco'));
    });
  }

  mostrarAviso(fonte) {
    this.aviso.setText(AVISOS[fonte]);
  }

  comecar() {
    if (this.saindo) return;
    this.saindo = true;
    pedirTelaCheia(this.game);
    this.scene.start(this.opcoes[this.escolha].cena);
  }

  update() {
    const c = this.controles;
    c.atualizar();
    if (c.apertou('baixo') || c.apertou('cima')) {
      this.escolha = (this.escolha + 1) % this.opcoes.length;
      this.marcar();
    }
    if (c.apertou('confirmar')) this.comecar();
  }
}
