import { LARGURA, ALTURA } from '../config.js';
import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { pedirTelaCheia } from '../escala.js';

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
    this.cameras.main.setBackgroundColor(P.ceu);

    this.add.rectangle(0, 0, LARGURA, 40, P.ceu_escuro).setOrigin(0);
    this.add.rectangle(0, 110, LARGURA, 40, P.ceu_claro).setOrigin(0);
    this.add.image(70, 120, 'nuvem');
    this.add.image(320, 100, 'nuvem');
    this.add.tileSprite(0, 112, LARGURA, 60, 'serras').setOrigin(0);
    this.add.rectangle(0, 150, LARGURA, ALTURA - 150, P.areia).setOrigin(0);
    this.add.rectangle(0, 150, LARGURA, 2, P.barro).setOrigin(0);

    this.add.text(LARGURA / 2 + 2, 50, 'A INVASÃO', estiloTexto(hex('azul_sombra'), 24)).setOrigin(0.5);
    this.add.text(LARGURA / 2, 48, 'A INVASÃO', estiloTexto(hex('amarelo_fogo'), 24)).setOrigin(0.5);
    this.add.text(LARGURA / 2, 76, 'SERTÃO, 1936', estiloTexto(hex('branco'))).setOrigin(0.5);

    this.aviso = this.add.text(LARGURA / 2, 180, '', estiloTexto(hex('couro_escuro'))).setOrigin(0.5);
    this.time.addEvent({ delay: 500, loop: true, callback: () => this.aviso.setVisible(!this.aviso.visible) });
    this.mostrarAviso(this.controles.fonte);
    const desligar = this.controles.aoMudarFonte((f) => this.mostrarAviso(f));
    this.events.once('shutdown', desligar);

    this.botaoPaleta = this.add.text(LARGURA - 4, ALTURA - 4, 'PALETA', estiloTexto(hex('couro')))
      .setOrigin(1).setInteractive();
    this.botaoPaleta.on('pointerdown', (p, x, y, e) => {
      e.stopPropagation();
      this.scene.start('Paleta');
    });
    this.input.on('pointerdown', () => this.comecar());
    this.input.keyboard.on('keydown-P', () => this.scene.start('Paleta'));
  }

  mostrarAviso(fonte) {
    this.aviso.setText(AVISOS[fonte]);
  }

  comecar() {
    if (this.saindo) return;
    this.saindo = true;
    pedirTelaCheia(this.game);
    this.scene.start('Campo');
  }

  update() {
    const c = this.controles;
    c.atualizar();
    if (c.apertou('confirmar')) this.comecar();
  }
}
