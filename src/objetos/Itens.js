import { P } from '../paleta.js';
import { CAIXA_ITEM } from '../sprites.js';

// Itens de arma no chão, como os do Metal Slug: caixa quadrada com a letra da
// arma, que quica ao cair e pisca. Reaproveitados de um pool fixo.
const QUANTOS = 16;
const PISCA = 900; // ms entre um brilho e outro

export class Itens {
  constructor(cena, solidos, jogador, aoPegar) {
    this.cena = cena;
    this.grupo = cena.physics.add.group({ maxSize: QUANTOS });
    for (let k = 0; k < QUANTOS; k++) {
      const item = this.grupo.create(-100, -100, 'item_M').setOrigin(0.5, 1).setDepth(7);
      item.body.setSize(CAIXA_ITEM.largura - 2, CAIXA_ITEM.altura - 2).setOffset(1, 1);
      item.body.setBounce(0.35).setDrag(120, 0).setMaxVelocityY(400);
      item.disableBody(true, true);
    }
    cena.physics.add.collider(this.grupo, solidos);
    cena.physics.add.overlap(jogador.corpo, this.grupo, (corpo, item) => {
      if (!item.active || jogador.morto || cena.time.now < item.pegavelEm) return;
      this.recolher(item);
      aoPegar(item.arma, item);
    });
  }

  // Põe um item no mundo. pulo: sai saltando (de caixote ou refém).
  // fixo: volta ao mesmo lugar depois de pego (campo de treino).
  colocar(x, y, arma, { pulo = false, fixo = false } = {}) {
    const item = this.grupo.getFirstDead(false) || this.grupo.getChildren()[0];
    item.enableBody(true, x, y, true, true);
    // Comida usa o próprio desenho; arma e granada usam a caixa com a letra.
    item.setTexture(arma.startsWith('comida_') ? arma : `item_${arma}`).clearTint();
    item.body.setSize(item.width - 2, item.height - 2).setOffset(1, 1);
    item.arma = arma;
    item.fixo = fixo ? { x, y } : null;
    item.fase = Math.random() * PISCA;
    item.pegavelEm = this.cena.time.now + (pulo ? 250 : 0);
    item.body.setVelocity(pulo ? Phaser.Math.Between(-30, 30) : 0, pulo ? -170 : 0);
    return item;
  }

  recolher(item) {
    item.disableBody(true, true);
    if (item.fixo) {
      const { x, y } = item.fixo;
      const arma = item.arma;
      this.cena.time.delayedCall(8000, () => this.colocar(x, y - 40, arma, { fixo: true }));
    }
  }

  atualizar(t) {
    for (const item of this.grupo.getChildren()) {
      if (!item.active) continue;
      // Brilho branco de tempos em tempos, para chamar atenção.
      const ciclo = (t + item.fase) % PISCA;
      if (ciclo < 60) item.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
      else item.clearTint();
    }
  }
}
