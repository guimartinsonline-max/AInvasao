const VELOCIDADE = 380;

// Balas do jogador, reaproveitadas de um pool fixo.
export class Balas {
  constructor(cena, solidos, alvos, aoAcertar) {
    this.cena = cena;
    this.grupo = cena.physics.add.group({ defaultKey: 'bala', maxSize: 32, allowGravity: false });

    cena.physics.add.overlap(this.grupo, solidos, (bala) => {
      if (!bala.active) return;
      cena.efeitos.faisca(bala.x, bala.y, 3);
      this.recolher(bala);
    });
    cena.physics.add.overlap(this.grupo, alvos, (bala, alvo) => {
      if (!bala.active || !alvo.vivo) return;
      aoAcertar(alvo, bala);
      this.recolher(bala);
    });
  }

  disparar(x, y, angulo) {
    const bala = this.grupo.get(x, y);
    if (!bala) return;
    bala.setActive(true).setVisible(true).setRotation(angulo);
    bala.body.reset(x, y);
    const vertical = Math.abs(Math.sin(angulo)) > 0.7;
    bala.body.setSize(vertical ? 2 : 5, vertical ? 5 : 2);
    bala.body.setVelocity(Math.cos(angulo) * VELOCIDADE, Math.sin(angulo) * VELOCIDADE);
  }

  recolher(bala) {
    bala.setActive(false).setVisible(false);
    bala.body.stop();
    bala.body.reset(-100, -100);
  }

  atualizar() {
    const v = this.cena.cameras.main.worldView;
    for (const bala of this.grupo.getChildren()) {
      if (!bala.active) continue;
      if (bala.x < v.x - 8 || bala.x > v.right + 8 || bala.y < v.y - 8 || bala.y > v.bottom + 8) {
        this.recolher(bala);
      }
    }
  }
}
