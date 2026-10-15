// Tiros dos inimigos, em pool. 'volante' é bala rápida; 'raio' é o tiro verde lento do xeremita.
const TIPOS = {
  volante: { textura: 'bala', velocidade: 200 },
  raio: { textura: 'raio', velocidade: 120 },
};

export class BalasInimigas {
  constructor(cena, solidos, jogador) {
    this.cena = cena;
    this.grupo = cena.physics.add.group({ defaultKey: 'raio', maxSize: 24, allowGravity: false });
    cena.physics.add.overlap(this.grupo, solidos, (bala) => {
      if (!bala.active) return;
      cena.efeitos.faisca(bala.x, bala.y, 3);
      this.recolher(bala);
    });
    cena.physics.add.overlap(this.grupo, jogador.corpo, (a, b) => {
      const bala = a === jogador.corpo ? b : a;
      if (!bala.active || jogador.morto || jogador.invulneravel) return;
      this.recolher(bala);
      jogador.morrer(bala.body.velocity.x);
    });
  }

  // Mira no peito do alvo, com ângulo limitado (no máximo ~30 graus).
  disparar(x, y, direcao, tipo, alvoX = null, alvoY = null) {
    const cfg = TIPOS[tipo];
    const bala = this.grupo.get(x, y, cfg.textura);
    if (!bala) return;
    bala.setTexture(cfg.textura).setActive(true).setVisible(true).setFlipX(direcao < 0).setDepth(15);
    bala.body.reset(x, y);
    bala.body.setSize(bala.width, bala.height);
    let ang = direcao > 0 ? 0 : Math.PI;
    if (alvoX !== null) {
      const bruto = Math.atan2(alvoY - y, (alvoX - x) * direcao);
      ang = Phaser.Math.Clamp(bruto, -0.5, 0.5);
      if (direcao < 0) ang = Math.PI - ang;
    }
    bala.setFlipX(false).setRotation(ang);
    bala.body.setVelocity(Math.cos(ang) * cfg.velocidade, Math.sin(ang) * cfg.velocidade);
  }

  recolher(bala) {
    bala.setActive(false).setVisible(false);
    bala.body.stop();
    bala.body.reset(-100, -100);
  }

  atualizar() {
    const v = this.cena.cameras.main.worldView;
    for (const bala of this.grupo.getChildren()) {
      if (bala.active && (bala.x < v.x - 16 || bala.x > v.right + 16)) this.recolher(bala);
    }
  }
}
