import { LARGURA, ALTURA } from '../config.js';
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
    this.add.image(0, 6, 'nuvens').setOrigin(0);
    this.add.image(0, 96, 'serras').setOrigin(0);
    this.add.image(-40, 86, 'paredoes').setOrigin(0);
    this.add.image(344, 86, 'paredoes').setOrigin(0);
    this.add.image(0, 168, 'planicie').setOrigin(0);
    this.add.image(-60, 122, 'caatinga').setOrigin(0);
    this.add.image(324, 122, 'caatinga').setOrigin(0);
    this.add.tileSprite(0, 192, LARGURA, 24, 'chao').setOrigin(0);
        this.add.image(196, 194, 'lampiao', LAMPIAO.parado).setOrigin(LAMPIAO.peX / LAMPIAO.largura, LAMPIAO.peY / LAMPIAO.altura);
    for (const [x, tipo] of [[270, 'xeremita'], [320, 'volante']]) {
      const q = INIMIGOS[tipo];
      this.add.image(x, 194, tipo, q.parado).setFlipX(true).setOrigin((q.largura - q.peX) / q.largura, q.peY / q.altura);
    }

    this.add.text(LARGURA / 2 + 2, 50, 'A INVASÃO', estiloTexto(hex('azul_sombra'), 24)).setOrigin(0.5);
    this.add.text(LARGURA / 2, 48, 'A INVASÃO', estiloTexto(hex('amarelo_fogo'), 24)).setOrigin(0.5);
    this.add.text(LARGURA / 2, 76, 'SERTÃO, 1936', estiloTexto(hex('branco'))).setOrigin(0.5);

    this.aviso = this.add.text(LARGURA / 2, 100, '', estiloTexto(hex('branco'))).setOrigin(0.5);
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
