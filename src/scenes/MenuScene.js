import { LARGURA, ALTURA } from '../config.js';
import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { pedirTelaCheia } from '../escala.js';

export class MenuScene extends Phaser.Scene {
  constructor() {
    super('Menu');
  }

  create() {
    this.cameras.main.setBackgroundColor(P.ceu);

    // Sol e chão provisórios só para dar o clima do sertão.
    this.add.circle(LARGURA / 2, 150, 36, P.sol);
    this.add.rectangle(0, 150, LARGURA, ALTURA - 150, P.terra).setOrigin(0);
    this.add.rectangle(0, 150, LARGURA, 4, P.terra_escura).setOrigin(0);

    this.add.text(LARGURA / 2, 48, 'A INVASÃO', estiloTexto(hex('vermelho_esc'), 24))
      .setOrigin(0.5);
    this.add.text(LARGURA / 2, 76, 'SERTÃO, 1936', estiloTexto(hex('couro_escuro')))
      .setOrigin(0.5);

    const toque = this.sys.game.device.input.touch && !this.sys.game.device.os.desktop;
    const aviso = this.add.text(LARGURA / 2, 184, toque ? 'TOQUE PARA COMEÇAR' : 'APERTE ENTER',
      estiloTexto(hex('branco'))).setOrigin(0.5);
    this.time.addEvent({ delay: 500, loop: true, callback: () => aviso.setVisible(!aviso.visible) });

    const comecar = () => {
      pedirTelaCheia(this.game);
      this.scene.start('Teste');
    };
    this.input.once('pointerdown', comecar);
    this.input.keyboard.once('keydown-ENTER', comecar);
    this.input.keyboard.once('keydown-SPACE', comecar);
    if (this.input.gamepad) this.input.gamepad.once('down', comecar);
  }
}
