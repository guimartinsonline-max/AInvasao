import { ajustes } from './ajustes.js';
import { P } from './paleta.js';
import { EFEITOS } from './quadros.js';
import { som } from './som.js';

// Velocidade (quadros por segundo) de cada efeito animado.
const FPS = { clarao: 50, clarao_g: 40, impacto: 30, impacto_verde: 30, explosao: 22, explosao_p: 26, poeira_passo: 18, fumaca: 14, chama: 14, rajada: 20, corte_arco: 26, clarao_canhao: 36 };

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

    // Tábuas de caixote quebrado: giram e caem.
    this.tabuasEm = add('tabua', {
      lifespan: 1000, speed: { min: 70, max: 190 }, angle: { min: 200, max: 340 },
      gravityY: 650, alpha: { start: 1, end: 0, ease: 'Expo.easeIn' },
      rotate: { onEmit: () => Phaser.Math.Between(0, 359), onUpdate: (p, k, t, v) => v + (p.velocityX > 0 ? 14 : -14) },
    });
    this.cinzasEm = add('px2', {
      lifespan: { min: 500, max: 1000 }, speed: { min: 15, max: 70 }, angle: { min: 200, max: 340 },
      gravityY: 220, tint: [P.preto, P.sombra, P.cinza_escuro, P.laranja_escuro],
      x: { min: -6, max: 6 }, y: { min: -16, max: 16 },
    });
    // Sangue: respingo que espirra e cai (só nos soldados; o xeremita solta gosma verde).
    this.sangueEm = add('px2', {
      lifespan: { min: 350, max: 800 }, speed: { min: 60, max: 200 }, angle: { min: 185, max: 355 },
      gravityY: 640, scale: { start: 1.6, end: 0.8 }, tint: [P.vermelho, P.vermelho_medio, P.vermelho_esc],
    });
    this.lascasEm = add('px2', {
      lifespan: 600, speed: { min: 40, max: 140 }, angle: { min: 190, max: 350 },
      gravityY: 600, tint: [P.couro_claro, P.couro, P.couro_luz],
    });
    // Telhas do telhado que a explosão arranca: pedaços de barro vermelho girando.
    this.telhasEm = add('px2', {
      lifespan: 900, speed: { min: 60, max: 170 }, angle: { min: 200, max: 340 }, gravityY: 600,
      scale: { min: 1.5, max: 2.5 }, tint: [P.vermelho_esc, P.terra, P.laranja_escuro, P.barro],
    });
    // Penas de galinha: sobem e descem devagar, balançando.
    this.penasEm = add('px2', {
      lifespan: 1400, speed: { min: 20, max: 80 }, angle: { min: 200, max: 340 }, gravityY: 60,
      tint: [P.branco, P.couro_claro, P.barro], accelerationX: { min: -30, max: 30 },
    });

    // Efeitos desenhados quadro a quadro (clarão, impacto, explosão, fumaça), num pool só.
    for (const [chave, fps] of Object.entries(FPS)) {
      if (!cena.anims.exists(chave)) {
        cena.anims.create({ key: chave, frames: cena.anims.generateFrameNumbers(chave, { start: 0, end: EFEITOS[chave].quadros - 1 }), frameRate: fps });
      }
    }
    if (!cena.anims.exists('fumaca_lenta')) {
      cena.anims.create({ key: 'fumaca_lenta', frames: cena.anims.generateFrameNumbers('fumaca', { start: 0, end: 3 }), frameRate: 4 });
    }
    this.animados = this.pool(40, () => {
      const s = cena.add.sprite(-100, -100, 'impacto').setVisible(false).setDepth(19);
      s.on('animationcomplete', () => s.setVisible(false));
      return s;
    });
    this.proximoAnimado = 0;

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
    if (!ajustes.tremida) return; // desligada nas opções
    this.cena.cameras.main.shake(ms, forca);
  }

  poeira(x, y, n = 5) {
    this.poeiraEm.explode(n, x, y);
  }

  faisca(x, y, n = 5) {
    this.faiscaEm.explode(n, x, y);
  }

  lascas(x, y) {
    this.lascasEm.explode(4, x, y);
  }

  tabuas(x, y) {
    som('madeira');
    this.tabuasEm.explode(7, x, y);
    this.lascasEm.explode(10, x, y);
  }

  // Cinza de quem morreu queimado.
  cinzas(x, y) {
    this.cinzasEm.explode(26, x, y);
  }

  sangue(x, y, n = 8) {
    this.sangueEm.explode(n, x, y);
  }

  gosma(x, y, n = 24) {
    this.gosmaEm.explode(n, x, y);
  }

  // Toca um efeito animado. Pool cheio: reaproveita o mais antigo.
  animar(chave, x, y, { rotacao = 0, origemX = 0.5, profundidade = 19, espelhar = false, anim = chave, escala = 1 } = {}) {
    let s = this.animados.find((a) => !a.visible);
    if (!s) s = this.animados[this.proximoAnimado++ % this.animados.length];
    this.cena.tweens.killTweensOf(s);
    s.setTexture(chave, 0).setPosition(Math.round(x), Math.round(y)).setOrigin(origemX, 0.5)
      .setRotation(rotacao).setFlipX(espelhar).setDepth(profundidade).setVisible(true).setAlpha(1).setScale(escala).clearTint();
    s.play(anim);
    return s;
  }

  // Fumaça que sobe devagar e é levada pelo vento (coluna do disco caído).
  fumacaSobe(x, y) {
    const s = this.animar('fumaca', x, y, { profundidade: 6, anim: 'fumaca_lenta' });
    this.cena.tweens.add({ targets: s, y: y - 70, x: x + 18, duration: 1000 });
  }

  // Fumaça que fica pairando (explosões): sobe devagar, cresce e some aos poucos.
  fumacaFica(x, y, escala = 1.6) {
    const s = this.animar('fumaca', x, y, { profundidade: 17, anim: 'fumaca_lenta', escala });
    s.anims.stop();
    s.setFrame(1).setAlpha(0.85);
    this.cena.tweens.add({
      targets: s, y: y - 40, x: x + Phaser.Math.Between(4, 16), scale: escala * 1.6, alpha: 0, duration: 2400,
      ease: 'Sine.easeOut', onComplete: () => s.setVisible(false),
    });
  }

  // Poeirinha do passo e da queda, desenhada (mais encorpada que as partículas).
  poeiraPasso(x, y, espelhar = false) {
    this.animar('poeira_passo', x, y - 4, { profundidade: 14, espelhar });
  }

  // Clarão no cano: estrela de fogo (normal ou grande) ou anel verde.
  disparo(x, y, angulo, tipo = 'normal') {
    if (!tipo) return;
    if (tipo === 'verde') {
      this.animar('impacto_verde', x, y, { profundidade: 20 });
      return;
    }
    const chave = tipo === 'canhao' ? 'clarao_canhao' : tipo === 'grande' ? 'clarao_g' : 'clarao';
    this.animar(chave, x, y, { rotacao: angulo, origemX: 0.05, profundidade: 20 });
  }

  impacto(x, y, tipo = 'comum') {
    som('impacto');
    if (tipo === 'verde') this.animar('impacto_verde', x, y);
    else if (tipo) this.animar('impacto', x, y);
    this.faiscaEm.explode(2, x, y);
  }

  fumaca(x, y) {
    this.animar('fumaca', x, y, { profundidade: 13 });
  }

  chama(x, y) {
    this.animar('chama', x, y, { profundidade: 16 });
  }

  capsula(x, y, direcao) {
    // Pool cheio: recicla a mais antiga.
    const c = this.capsulas.get(x, y) || this.capsulas.getChildren()[this.proximaCapsula++ % this.capsulas.maxSize];
    c.body.reset(x, y);
    c.setActive(true).setVisible(true).setAlpha(1);
    c.body.setBounce(0.55).setDrag(50, 0).setAngularVelocity(Phaser.Math.Between(-900, 900));
    c.body.setVelocity(-direcao * Phaser.Math.Between(30, 70), Phaser.Math.Between(-140, -90));
    c.body.setSize(2, 1);
    c.vence = this.cena.time.now + 2600;
  }

  atualizar() {
    const agora = this.cena.time.now;
    for (const c of this.capsulas.getChildren()) {
      if (!c.active) continue;
      if (agora > c.vence) c.setActive(false).setVisible(false).body.reset(-50, -50);
      else if (agora > c.vence - 500) c.setAlpha((c.vence - agora) / 500);
    }
  }

  // Explosão desenhada em 8 quadros (grande ou pequena), com estilhaços e faíscas.
  explosao(x, y, tamanho = 1) {
    som('explosao', tamanho);
    const grande = tamanho >= 0.9;
    this.animar(grande ? 'explosao' : 'explosao_p', x, y - (grande ? 16 : 10), { profundidade: 18 });
    // Fumaça que fica no ar depois da explosão, subindo devagar e sumindo.
    for (let i = 0; i < (grande ? 3 : 1); i++) {
      this.cena.time.delayedCall(420 + i * 140, () => this.fumacaFica(x + Phaser.Math.Between(-10, 10), y - 18 - i * 6, grande ? 1.8 : 1.2));
    }
    if (tamanho > 1.1) {
      // Explosão maior: mais duas bolas de fogo em volta.
      this.cena.time.delayedCall(60, () => this.animar('explosao_p', x - 14, y - 2, { profundidade: 18 }));
      this.cena.time.delayedCall(110, () => this.animar('explosao_p', x + 13, y - 10, { profundidade: 18 }));
    }
    this.fogoEm.explode(Math.round(10 * tamanho), x, y);
    this.fumacaEm.explode(Math.round(6 * tamanho), x, y - 10);
    this.detritoEm.explode(Math.round(12 * tamanho), x, y);
    this.faiscaEm.explode(Math.round(10 * tamanho), x, y);
    this.tremer(0.012 * tamanho, 260);
    this.parar(70);
  }
}
