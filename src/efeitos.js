import { P } from './paleta.js';

// Efeitos de impacto (game feel). Tudo é criado uma vez e reaproveitado.
export class Efeitos {
  constructor(cena, solidos) {
    this.cena = cena;
    this.congeladoAte = 0;

    const add = (textura, config) => cena.add.particles(0, 0, textura, { emitting: false, ...config });

    this.poeiraEm = add('px2', {
      lifespan: { min: 200, max: 400 }, speed: { min: 10, max: 40 }, angle: { min: 200, max: 340 },
      gravityY: 60, alpha: { start: 1, end: 0 }, tint: P.areia_clara,
    });
    this.faiscaEm = add('px', {
      lifespan: { min: 120, max: 260 }, speed: { min: 40, max: 120 },
      gravityY: 200, tint: [P.amarelo_fogo, P.branco, P.laranja_fogo],
    });
    this.fumacaEm = add('bola', {
      lifespan: { min: 600, max: 1100 }, speed: { min: 8, max: 30 }, angle: { min: 240, max: 300 },
      scale: { start: 1, end: 2.5 }, alpha: { start: 0.9, end: 0 },
      color: [P.cinza_claro, P.cinza, P.cinza_escuro],
    });
    this.fogoEm = add('disco', {
      lifespan: { min: 250, max: 550 }, speed: { min: 30, max: 150 },
      scale: { start: 0.9, end: 0 }, gravityY: -80,
      color: [P.branco, P.amarelo_fogo, P.laranja_fogo, P.vermelho, P.azul_sombra],
    });
    this.detritoEm = add('px2', {
      lifespan: 900, speed: { min: 80, max: 200 }, angle: { min: 200, max: 340 },
      gravityY: 600, tint: [P.terra, P.terra_escura, P.barro],
    });
    this.gosmaEm = add('px2', {
      lifespan: { min: 400, max: 800 }, speed: { min: 60, max: 180 }, angle: { min: 190, max: 350 },
      gravityY: 500, tint: [P.alien, P.alien_brilho, P.alien_esc],
    });

    this.clarao = cena.add.image(0, 0, 'clarao').setOrigin(0.1, 0.5).setVisible(false).setDepth(20);
    this.flashes = this.pool(4, () => cena.add.image(0, 0, 'disco').setVisible(false).setDepth(19));

    this.capsulas = cena.physics.add.group({ defaultKey: 'capsula', maxSize: 24 });
    cena.physics.add.collider(this.capsulas, solidos, (c) => {
      if (c.body.velocity.y === 0 || Math.abs(c.body.velocity.y) < 30) c.body.setAngularVelocity(0);
    });
    this.proximaCapsula = 0;
  }

  pool(n, criar) {
    const lista = [];
    for (let i = 0; i < n; i++) lista.push(criar());
    return lista;
  }

  // Pequena pausa no impacto forte: congela a física e os efeitos por alguns ms.
  parar(ms) {
    const agora = this.cena.time.now;
    this.congeladoAte = Math.max(this.congeladoAte, agora + ms);
    this.cena.physics.world.pause();
    this.cena.time.delayedCall(ms, () => {
      if (this.cena.time.now >= this.congeladoAte - 1) this.cena.physics.world.resume();
    });
  }

  get congelado() {
    return this.cena.time.now < this.congeladoAte;
  }

  tremer(forca = 0.006, ms = 120) {
    this.cena.cameras.main.shake(ms, forca);
  }

  poeira(x, y, n = 5) {
    this.poeiraEm.explode(n, x, y);
  }

  faisca(x, y, n = 5) {
    this.faiscaEm.explode(n, x, y);
  }

  gosma(x, y, n = 24) {
    this.gosmaEm.explode(n, x, y);
  }

  disparo(x, y, angulo) {
    this.clarao.setPosition(x, y).setRotation(angulo).setVisible(true).setScale(Phaser.Math.FloatBetween(0.8, 1.2));
    this.cena.time.delayedCall(40, () => this.clarao.setVisible(false));
  }

  capsula(x, y, direcao) {
    // Pool cheio: recicla a mais antiga.
    const c = this.capsulas.get(x, y) || this.capsulas.getChildren()[this.proximaCapsula++ % this.capsulas.maxSize];
    c.body.reset(x, y);
    c.setActive(true).setVisible(true).setAlpha(1);
    c.body.setBounce(0.45).setDrag(60, 0).setAngularVelocity(Phaser.Math.Between(-900, 900));
    c.body.setVelocity(-direcao * Phaser.Math.Between(30, 70), Phaser.Math.Between(-140, -90));
    c.body.setSize(2, 1);
    c.vence = this.cena.time.now + 1500;
  }

  atualizar() {
    const agora = this.cena.time.now;
    for (const c of this.capsulas.getChildren()) {
      if (!c.active) continue;
      if (agora > c.vence) c.setActive(false).setVisible(false).body.reset(-50, -50);
      else if (agora > c.vence - 300) c.setAlpha((c.vence - agora) / 300);
    }
  }

  explosao(x, y, tamanho = 1) {
    const flash = this.flashes.find((f) => !f.visible) || this.flashes[0];
    flash.setPosition(x, y).setVisible(true).setScale(0.3).setAlpha(1).setTint(P.branco);
    this.cena.tweens.killTweensOf(flash);
    this.cena.tweens.add({
      targets: flash, scale: 3 * tamanho, alpha: 0, duration: 180, ease: 'Quad.easeOut',
      onUpdate: (tw) => flash.setTint(tw.progress < 0.4 ? P.branco : P.amarelo_fogo),
      onComplete: () => flash.setVisible(false),
    });
    this.fogoEm.explode(Math.round(28 * tamanho), x, y);
    this.fumacaEm.explode(Math.round(14 * tamanho), x, y - 4);
    this.detritoEm.explode(Math.round(12 * tamanho), x, y);
    this.faiscaEm.explode(Math.round(10 * tamanho), x, y);
    this.tremer(0.012 * tamanho, 260);
    this.parar(70);
  }
}
