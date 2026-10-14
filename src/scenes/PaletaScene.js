import { LARGURA, ALTURA } from '../config.js';
import { P, hex } from '../paleta.js';
import { estiloTexto } from '../texto.js';

// Mostra a paleta (toque numa cor para ver o nome) e confere escala, física e fps.
export class PaletaScene extends Phaser.Scene {
  constructor() {
    super('Paleta');
  }

  create() {
    this.cameras.main.setBackgroundColor(P.sombra);

    const nomes = Object.keys(P);
    const lado = 16;
    const x0 = (LARGURA - 8 * (lado + 2)) / 2;
    nomes.forEach((nome, i) => {
      const x = x0 + (i % 8) * (lado + 2);
      const y = 20 + Math.floor(i / 8) * (lado + 2);
      this.add.rectangle(x, y, lado, lado, P[nome]).setOrigin(0)
        .setInteractive()
        .on('pointerdown', () => this.nomeCor.setText(nome.toUpperCase()));
    });
    this.add.text(4, 4, 'PALETA', estiloTexto(hex('cinza_claro')));
    this.nomeCor = this.add.text(LARGURA - 4, 4, '', estiloTexto(hex('amarelo_fogo'))).setOrigin(1, 0);

    // Chão e caixas caindo: confere a física Arcade e o reaproveitamento de objetos.
    const chao = this.add.rectangle(0, ALTURA - 16, LARGURA, 16, P.terra).setOrigin(0);
    this.physics.add.existing(chao, true);

    this.caixas = this.physics.add.group({ defaultKey: 'px', maxSize: 12 });
    this.physics.add.collider(this.caixas, chao);
    this.time.addEvent({ delay: 400, loop: true, callback: () => this.soltarCaixa() });

    this.info = this.add.text(4, ALTURA - 13, '', estiloTexto(hex('branco')));

    this.add.text(LARGURA - 4, ALTURA - 13, 'VOLTAR', estiloTexto(hex('branco'))).setOrigin(1, 0)
      .setInteractive().on('pointerdown', () => this.scene.start('Menu'));
    this.input.keyboard.once('keydown-ESC', () => this.scene.start('Menu'));
  }

  soltarCaixa() {
    let caixa = this.caixas.get(Phaser.Math.Between(20, LARGURA - 20), 100);
    if (!caixa) {
      // Pool cheio: recicla a caixa mais antiga em vez de criar outra.
      caixa = this.caixas.getFirstAlive();
      caixa.body.reset(Phaser.Math.Between(20, LARGURA - 20), 100);
    }
    const cores = [P.barro, P.mandacaru, P.alien, P.vermelho, P.areia];
    caixa.setActive(true).setVisible(true)
      .setDisplaySize(8, 8)
      .setTint(Phaser.Utils.Array.GetRandom(cores));
    caixa.body.setSize(1, 1).setBounce(0.3).setVelocity(Phaser.Math.Between(-60, 60), 0);
    this.caixas.remove(caixa);
    this.caixas.add(caixa);
  }

  update() {
    const c = this.game.canvas;
    const escala = (c.getBoundingClientRect().width / LARGURA) * (window.devicePixelRatio || 1);
    this.info.setText(`${LARGURA}x${ALTURA}  x${escala.toFixed(2)}  ${Math.round(this.game.loop.actualFps)} FPS`);
  }
}
