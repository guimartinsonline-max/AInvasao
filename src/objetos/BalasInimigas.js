// Tiros dos inimigos, em pool. 'volante' é bala rápida; 'raio' é o tiro verde lento do xeremita.
// mira: ângulo máximo (rad) que o tiro pode apontar para o Lampião; 0 = sai reto.
const TIPOS = {
  volante: { textura: 'tracer', velocidade: 200, mira: 0.2 },
  raio: { textura: 'raio', velocidade: 110, mira: 0 },
};

export class BalasInimigas {
  constructor(cena, solidos, jogador) {
    this.cena = cena;
    this.jogador = jogador;
    this.dinamites = cena.physics.add.group({ defaultKey: 'dinamite', maxSize: 8 });
    cena.physics.add.collider(this.dinamites, solidos, (d) => this.explodirDinamite(d));
    cena.physics.add.overlap(this.dinamites, jogador.corpo, (a, b) => this.explodirDinamite(a === jogador.corpo ? b : a));
    this.dinamites.maxSize = 10;
    this.grupo = cena.physics.add.group({ defaultKey: 'raio', maxSize: 24, allowGravity: false });
    cena.physics.add.overlap(this.grupo, solidos, (bala) => {
      if (!bala.active) return;
      cena.efeitos.impacto(bala.x, bala.y, bala.texture.key === 'raio' ? 'verde' : 'comum');
      this.recolher(bala);
    });
    cena.physics.add.overlap(this.grupo, jogador.corpo, (a, b) => {
      const bala = a === jogador.corpo ? b : a;
      if (!bala.active || jogador.morto || jogador.invulneravel) return;
      this.recolher(bala);
      jogador.morrer(bala.body.velocity.x);
    });
  }

  // Dinamite do granadeiro: voa em arco girando e explode ao tocar o chão ou o Lampião.
  lancarDinamite(x, y, direcao, distancia) {
    const d = this.dinamites.get(x, y, 'dinamite');
    if (!d) return;
    d.setActive(true).setVisible(true).setDepth(14);
    d.body.reset(x, y);
    d.body.setSize(6, 6);
    const vx = Phaser.Math.Clamp(distancia * 1.05, 50, 190);
    d.body.setVelocity(direcao * vx, -230);
    d.body.setAngularVelocity(direcao * 720);
  }

  // Rojão do soldado: sai inclinado para cima, cai em arco e explode no chão.
  lancarRojao(x, y, direcao, distancia) {
    const d = this.dinamites.get(x, y, 'foguete');
    if (!d) return;
    d.setTexture('foguete', 0).setActive(true).setVisible(true).setDepth(14).setFlipX(false);
    d.body.reset(x, y);
    d.body.setSize(8, 5);
    d.body.setAngularVelocity(0);
    d.rojao = true;
    const vx = Phaser.Math.Clamp(distancia * 0.9, 90, 230);
    d.body.setVelocity(direcao * vx, -150);
    d.proximaFumaca = 0;
  }

  explodirDinamite(d) {
    if (!d.active) return;
    const cena = this.cena;
    const x = d.x;
    const y = d.y;
    d.setActive(false).setVisible(false);
    d.body.stop();
    d.body.reset(-100, -100);
    const forte = d.rojao;
    d.rojao = false;
    cena.efeitos.explosao(x, y - 4, forte ? 0.9 : 0.6);
    const j = this.jogador;
    const raio = forte ? 28 : 20;
    if (!j.morto && !j.invulneravel && Math.abs(j.x - x) < raio && Math.abs(j.pe - 14 - y) < 26) j.morrer(j.x - x);
  }

  // Mira no peito do alvo, com ângulo limitado pelo tipo (o raio do xeremita sai reto).
  disparar(x, y, direcao, tipo, alvoX = null, alvoY = null) {
    const cfg = TIPOS[tipo];
    const bala = this.grupo.get(x, y, cfg.textura);
    if (!bala) return;
    bala.setTexture(cfg.textura, 0).setActive(true).setVisible(true).setFlipX(direcao < 0).setDepth(15);
    bala.body.reset(x, y);
    bala.body.setSize(bala.width, bala.height);
    let ang = direcao > 0 ? 0 : Math.PI;
    if (alvoX !== null && cfg.mira) {
      const bruto = Math.atan2(alvoY - y, (alvoX - x) * direcao);
      ang = Phaser.Math.Clamp(bruto, -cfg.mira, cfg.mira);
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
    const agora = this.cena.time.now;
    for (const d of this.dinamites.getChildren()) {
      if (!d.active || !d.rojao) continue;
      // O rojão aponta para onde vai e solta fumaça.
      d.setRotation(Math.atan2(d.body.velocity.y, d.body.velocity.x));
      if (agora > d.proximaFumaca) {
        d.proximaFumaca = agora + 50;
        this.cena.efeitos.fumaca(d.x - Math.cos(d.rotation) * 10, d.y - Math.sin(d.rotation) * 10);
      }
    }
    for (const bala of this.grupo.getChildren()) {
      if (bala.active && (bala.x < v.x - 16 || bala.x > v.right + 16)) this.recolher(bala);
    }
  }
}
