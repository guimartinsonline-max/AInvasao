import { CenaJogo, CHAO_Y, LARGURA, ALTURA } from './CenaJogo.js';
import { Refem } from '../objetos/Refem.js';
import { Disco, Bode } from '../objetos/Disco.js';
import { Caixotes } from '../objetos/Caixotes.js';

const LARGURA_MUNDO = LARGURA * 3;

// Campo de treino: todas as armas espalhadas, inimigos, refém, disco e
// objetos destrutíveis. Tudo volta depois de um tempo.
export class CampoScene extends CenaJogo {
  constructor() {
    super('Campo');
  }

  configurar() {
    return { largura: LARGURA_MUNDO, inicio: { x: 60, y: CHAO_Y - 18 } };
  }

  criarFundo() {
    // Camadas em parallax: quanto mais longe, mais devagar acompanham a câmera.
    this.add.image(0, 0, 'ceu').setOrigin(0).setScrollFactor(0);
    const camada = (chave, y, fator) => [this.add.tileSprite(0, y, LARGURA, this.textures.get(chave).source[0].height, chave)
      .setOrigin(0).setScrollFactor(0), fator];
    this.nuvens = camada('nuvens', 6, 0.03);
    this.camadas = [
      this.nuvens,
      camada('serras', 96, 0.08),
      camada('paredoes', 86, 0.2),
      camada('planicie', 168, 0.35),
      camada('caatinga', 122, 0.5),
    ];
    this.ventoNuvens = 0;
  }

  montarCenario() {
    this.add.tileSprite(0, CHAO_Y, LARGURA_MUNDO, ALTURA - CHAO_Y, 'chao').setOrigin(0).setDepth(5);
    this.solido(0, CHAO_Y + 2, LARGURA_MUNDO, ALTURA - CHAO_Y);
    // Capim seco na beira do chão.
    for (let x = 8; x < LARGURA_MUNDO; x += Phaser.Math.Between(30, 70)) {
      this.add.image(x, CHAO_Y + 3, 'touceiras', Phaser.Math.Between(0, 3)).setOrigin(0.5, 1).setDepth(6);
    }
    for (const [x, y, n] of [[560, 150, 4], [740, 162, 2], [980, 146, 3]]) {
      this.add.tileSprite(x, y, 32 * n, 12, 'laje').setOrigin(0).setDepth(6);
      this.solido(x, y, 32 * n, 12);
    }
    const c = CHAO_Y + 2;
    // Caixotes destrutíveis (o de cima, empilhado, cai quando o de baixo quebra) e barris.
    this.caixotes = new Caixotes(this, [[176, c - 18], [412, c - 18], [436, c - 18], [424, c - 36], [860, c - 18],
      [944, c - 24, 'barril'], [963, c - 24, 'barril'], [953, c - 48, 'barril']]);
  }

  povoar() {
    const c = CHAO_Y + 2;
    for (const [x, y, tipo, escudo] of [[320, c, 'xeremita'], [624, 150, 'volante'], [880, c, 'volante', true],
      [1060, c, 'xeremita']]) {
      this.adicionarInimigo(x, y, tipo, { escudo });
    }
    // Refém (as balas do Lampião soltam a corda) e o bode Fubá.
    this.refem = new Refem(this, 340, c);
    this.alvos.add(this.refem);
    this.refem.reiniciar();
    this.bode = new Bode(this, 720, c);
    this.physics.add.collider(this.bode, this.solidos);
    this.disco = new Disco(this, 560, [this.refem, this.bode]);
    this.alvos.add(this.disco);
    this.disco.body.allowGravity = false;
    // Itens de arma espalhados; voltam depois de pegos.
    for (const [x, arma] of [[130, 'candeeiro'], [240, 'madsen'], [300, 'estilingue'], [520, 'bacamarte'],
      [610, 'papo_amarelo'], [700, 'buscape'], [780, 'rojao'], [1010, 'desintegrador']]) {
      this.itens.colocar(x, c - 20, arma, { fixo: true });
    }
  }

  atualizarFundo(cam, dt) {
    this.ventoNuvens += dt * 0.004;
    for (const [camada, fator] of this.camadas) camada.tilePositionX = Math.round(cam.scrollX * fator);
    this.nuvens[0].tilePositionX = Math.round(cam.scrollX * this.nuvens[1] + this.ventoNuvens);
  }
}

export { ALTURA };
