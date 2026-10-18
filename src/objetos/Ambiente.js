import { P } from '../paleta.js';
import { som } from '../som.js';

// Cenário vivo: urubus que levantam voo, galinhas (assam no fogo), varal que a
// explosão arrebenta, casas que perdem o telhado e a ponte que a granada quebra.
// As explosões do Lampião avisam pelo evento 'explosao' da cena (x, y, raio).

export const AMBIENTE = {
  urubu: { largura: 26, altura: 18 },
  galinha: { largura: 16, altura: 15 },
  roupa: { largura: 12, altura: 12 },
  varal: { largura: 70, altura: 40 },
  ponte_seg: { largura: 139, altura: 60 },
};

// ---------------------------------------------------------------- urubus
// Pousados (no chão ou num galho seco); quando o Lampião chega perto, voam para longe.
export class Urubus {
  constructor(cena, lista) {
    this.cena = cena;
    this.bandos = lista.map(([x, pe]) => ({
      s: cena.add.sprite(x, pe, 'urubu', 0).setOrigin(0.5, 1).setDepth(6).setFlipX(Math.random() < 0.5),
      voando: false, vx: 0, vy: 0,
    }));
  }

  atualizar(t, dt) {
    const j = this.cena.jogador;
    const s_ = dt / 1000;
    for (const u of this.bandos) {
      const s = u.s;
      if (!s.visible) continue;
      if (!u.voando) {
        // Pousado: de vez em quando abre a asa.
        s.setFrame(Math.floor((t + s.x * 7) / 1800) % 5 === 0 ? 1 : 0);
        if (Math.abs(j.x - s.x) < 80 && !j.morto) {
          u.voando = true;
          const lado = s.x > j.x ? 1 : -1;
          u.vx = lado * Phaser.Math.Between(50, 80);
          u.vy = -Phaser.Math.Between(50, 80);
          s.setFlipX(lado < 0);
          this.cena.efeitos.poeira(s.x, s.y, 3);
        }
        continue;
      }
      s.setFrame(1 + (Math.floor(t / 110) % 2));
      u.vy = Math.max(u.vy - 20 * s_, -90);
      s.x += u.vx * s_;
      s.y += u.vy * s_;
      if (s.y < -this.cena.cameras.main.height) s.setVisible(false);
    }
  }
}

// ---------------------------------------------------------------- galinhas
// Ciscam e bicam o chão; com o Lampião perto ou levando tiro, correm batendo asa.
// Fogo ou explosão: vira galinha assada (comida que vale 800).
export class Galinha extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, pe) {
    super(cena, x, pe, 'galinha', 0);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.setOrigin(0.5, 1).setDepth(8);
    this.body.setSize(10, 10).setOffset(3, 5);
    this.vivo = true;
    this.persegue = false; // o buscapé não vai atrás de galinha
    this.direcao = Math.random() < 0.5 ? -1 : 1;
    this.fugindoAte = 0;
    this.proximaVolta = 0;
  }

  levarDano(dano, origemX, forte = false, morte = null, queima = false) {
    if (!this.vivo) return;
    const cena = this.scene;
    if (queima || morte === 'fogo' || forte) {
      // Assada: some numa nuvem de penas e cai a galinha assada.
      this.vivo = false;
      cena.efeitos.penasEm.explode(16, this.x, this.y - 6);
      if (queima || morte === 'fogo') cena.efeitos.chama(this.x, this.y - 6);
      cena.soltarItem(this.x, this.y - 10, 'comida_galinha');
      this.setVisible(false);
      this.body.enable = false;
      return;
    }
    // Tiro: penas voando e ela dispara a correr.
    som('galinha');
    cena.efeitos.penasEm.explode(8, this.x, this.y - 6);
    this.fugir(origemX);
    this.body.setVelocityY(-120);
  }

  fugir(deX) {
    this.direcao = this.x > deX ? 1 : -1;
    this.fugindoAte = this.scene.time.now + 1800;
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (!this.vivo) return;
    const j = this.scene.jogador;
    if (!j.morto && Math.abs(j.x - this.x) < 46 && t > this.fugindoAte) this.fugir(j.x);
    if (t < this.fugindoAte) {
      this.body.setVelocityX(this.direcao * 95);
      this.setFrame(2 + (Math.floor(t / 90) % 2));
      if (this.body.blocked.down && (this.body.blocked.left || this.body.blocked.right || Math.random() < 0.01)) {
        this.body.setVelocityY(-170); // pulinho de galinha assustada
      }
    } else {
      if (t > this.proximaVolta) {
        this.proximaVolta = t + Phaser.Math.Between(900, 2200);
        this.direcao = Math.random() < 0.5 ? -1 : 1;
        this.anda = Math.random() < 0.5;
      }
      this.body.setVelocityX(this.anda ? this.direcao * 18 : 0);
      this.setFrame(this.anda ? 0 : (Math.floor(t / 260) % 3 === 0 ? 1 : 0));
    }
    this.setFlipX(this.direcao < 0);
  }
}

// ---------------------------------------------------------------- varal
export class Varal {
  constructor(cena, x, pe) {
    this.cena = cena;
    this.img = cena.add.image(x, pe, 'varal', 0).setOrigin(0, 1).setDepth(5);
    this.inteiro = true;
    this.roupas = [0, 1, 2].map((k) => cena.add.image(0, 0, 'roupa', k).setDepth(12).setVisible(false));
    cena.events.on('explosao', (ex, ey, raio) => {
      const cx = this.img.x + AMBIENTE.varal.largura / 2;
      if (this.inteiro && Math.abs(ex - cx) < raio + 40 && Math.abs(ey - (pe - 30)) < raio + 40) this.arrebentar(ex);
    });
  }

  // A corda arrebenta e a roupa sai voando, girando, e cai devagar.
  arrebentar(ex) {
    const cena = this.cena;
    this.inteiro = false;
    this.img.setFrame(1);
    cena.pontuar(50, this.img.x + 35, this.img.y - 40);
    this.roupas.forEach((r, k) => {
      const x0 = this.img.x + 14 + k * 20;
      const y0 = this.img.y - 30;
      const lado = x0 >= ex ? 1 : -1;
      r.setPosition(x0, y0).setVisible(true).setRotation(0).setAlpha(1);
      cena.tweens.add({ targets: r, x: x0 + lado * Phaser.Math.Between(30, 70), duration: 1600, ease: 'Sine.easeOut' });
      cena.tweens.add({ targets: r, y: y0 - Phaser.Math.Between(30, 60), duration: 400, ease: 'Quad.easeOut',
        onComplete: () => cena.tweens.add({ targets: r, y: this.img.y - 2, duration: 1200, ease: 'Sine.easeIn' }) });
      cena.tweens.add({ targets: r, rotation: lado * Phaser.Math.FloatBetween(3, 7), duration: 1600 });
    });
  }
}

// ---------------------------------------------------------------- casas da vila
export class CasaVila {
  constructor(cena, chave, x, pe, w, h) {
    this.cena = cena;
    this.img = cena.add.image(x, pe, chave, 0).setOrigin(0, 1).setDepth(5);
    this.w = w;
    this.h = h;
    this.inteira = true;
    cena.events.on('explosao', (ex, ey, raio) => {
      if (!this.inteira) return;
      const topo = pe - h;
      if (ex > x - raio && ex < x + w + raio && ey > topo - raio && ey < pe) this.destelhar(ex);
    });
  }

  // As telhas voam e caem quebrando; sobram os caibros.
  destelhar(ex) {
    const cena = this.cena;
    this.inteira = false;
    this.img.setFrame(1);
    cena.pontuar(100, this.img.x + this.w / 2, this.img.y - this.h - 6);
    const topo = this.img.y - this.h + 8;
    for (let k = 0; k < 6; k++) {
      const x = this.img.x + this.w * (0.15 + k * 0.14);
      cena.efeitos.telhasEm.explode(4, x, topo + Phaser.Math.Between(0, 8));
      cena.efeitos.poeira(x, topo + 10, 3);
    }
    cena.efeitos.tremer(0.006, 160);
  }
}

// ---------------------------------------------------------------- ponte
// Pedaços da ponte de tábuas: cada um é uma plataforma; explosão em cima quebra o pedaço.
export class Ponte {
  constructor(cena, [x0, y, n, w]) {
    this.cena = cena;
    this.pedacos = [];
    for (let k = 0; k < n; k++) {
      const x = x0 + k * w;
      const img = cena.add.image(x, y - 12, 'ponte_seg', 0).setOrigin(0).setDepth(5);
      const solido = cena.solido(x, y, w, 6, true);
      this.pedacos.push({ x, w, y, img, solido, inteiro: true });
    }
    cena.events.on('explosao', (ex, ey, raio) => {
      for (const p of this.pedacos) {
        if (p.inteiro && ex > p.x - raio / 2 && ex < p.x + p.w + raio / 2 && Math.abs(ey - p.y) < raio + 10) this.quebrar(p);
      }
    });
  }

  quebrar(p) {
    const cena = this.cena;
    p.inteiro = false;
    p.img.setFrame(1);
    p.solido.body.enable = false;
    cena.pontuar(100, p.x + p.w / 2, p.y - 20);
    for (let k = 0; k < 6; k++) {
      cena.efeitos.lascasEm.explode(5, p.x + 10 + k * (p.w - 20) / 5, p.y + 2);
    }
    cena.efeitos.poeira(p.x + p.w / 2, p.y + 4, 10);
    cena.efeitos.tremer(0.008, 200);
  }
}

export { P };
