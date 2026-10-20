import { hex, P } from '../paleta.js';
import { estiloTexto } from '../texto.js';
import { som } from '../som.js';
// Chão das fases geradas pela arte (o sólido começa em y 194).
const CHAO_Y = 194;

// Peças vivas do acampamento da base (fase 2, trecho 2; dados em base do fase2b.json,
// arte em tools/arte/fase2b.py): holofotes que varrem o chão e tocam o alarme,
// geradores que, arrebentados, apagam a luz daquele pedaço, jaulas com aliens presos,
// o guindaste com o pedaço do disco pendurado, o varal de lâmpadas e a bandeira.

const VE_ALARME = 9000; // ms entre um alarme e outro do mesmo holofote

// Peça que leva tiro como um inimigo (fica no grupo de alvos), mas não anda.
class Peca extends Phaser.Physics.Arcade.Sprite {
  constructor(cena, x, y, chave, vida) {
    super(cena, x, y, chave, 0);
    cena.add.existing(this);
    cena.physics.add.existing(this);
    this.vivo = true;
    this.voa = true;
    this.persegue = false;
    this.segredo = true; // o jumento kamikaze não trata como alvo
    this.vida = vida;
    this.body.allowGravity = false;
    this.body.setImmovable(true);
  }

  piscar() {
    this.setTint(P.branco).setTintMode(Phaser.TintModes.FILL);
    this.scene.time.delayedCall(45, () => this.clearTint());
  }
}

// ------------------------------------------------------------------ holofote
class Holofote extends Peca {
  constructor(base, cfg) {
    const cena = base.cena;
    super(cena, cfg.x, cfg.y, 'holofote', 3);
    this.base = base;
    this.gerador = cfg.gerador;
    this.de = cfg.de;
    this.ate = cfg.ate;
    this.setOrigin(10 / 24, 8 / 18).setDepth(6.5);
    this.body.setSize(18, 14).setOffset(3, 1);
    this.facho = cena.add.graphics().setDepth(6.2).setBlendMode(Phaser.BlendModes.ADD);
    this.aceso = true;
    this.fase = Math.random() * 6;
    this.alarmeEm = -VE_ALARME;
    this.alarmes = 0;
    this.travado = 0;
  }

  // Ângulo da varredura: vai e volta devagar entre de e ate (0 = para a direita).
  angulo(t) {
    if (this.travado > t) return this.mira;
    const k = (Math.sin(t / 1300 + this.fase) + 1) / 2;
    const meio = Math.PI / 2;
    return meio + (k - 0.5) * 2 * (this.ate - this.de);
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    this.facho.clear();
    if (!this.aceso) return;
    const cena = this.scene;
    const ang = this.angulo(t);
    this.setRotation(ang);
    this.setFrame(Math.floor(t / 90) % 7 === 0 ? 1 : 0);
    // Facho: cone até o chão com a mancha de luz embaixo.
    const ox = this.x + Math.cos(ang) * 10;
    const oy = this.y + Math.sin(ang) * 10;
    const dist = (CHAO_Y + 2 - oy) / Math.max(0.2, Math.sin(ang));
    const abre = 0.13;
    const pa = [ox + Math.cos(ang - abre) * dist, oy + Math.sin(ang - abre) * dist];
    const pb = [ox + Math.cos(ang + abre) * dist, oy + Math.sin(ang + abre) * dist];
    const alarme = this.travado > t;
    const cor = alarme ? 0xd04030 : 0xf0d890;
    this.facho.fillStyle(cor, alarme ? 0.22 : 0.13);
    this.facho.fillTriangle(ox, oy, pa[0], pa[1], pb[0], pb[1]);
    this.facho.fillStyle(cor, alarme ? 0.18 : 0.12);
    const cx = (pa[0] + pb[0]) / 2;
    this.facho.fillEllipse(cx, CHAO_Y + 1, Math.abs(pb[0] - pa[0]) + 8, 7);
    // Pegou o Lampião em pé dentro do facho: alarme.
    const j = cena.jogador;
    if (j.morto || j.agachado || this.base.apagado(this.gerador)) return;
    const aj = Math.atan2(j.pe - 20 - oy, j.x - ox);
    if (Math.abs(Phaser.Math.Angle.Wrap(aj - ang)) < abre && j.pe - 20 > oy && t - this.alarmeEm > VE_ALARME) {
      this.alarme(t, aj);
    }
  }

  alarme(t, mira) {
    const cena = this.scene;
    this.alarmeEm = t;
    this.travado = t + 1300;
    this.mira = mira;
    this.alarmes++;
    const txt = cena.add.text(this.x, this.y - 22, 'ALARME!', estiloTexto(hex('vermelho'))).setOrigin(0.5).setDepth(31);
    cena.tweens.add({ targets: txt, alpha: 0.2, yoyo: true, repeat: 4, duration: 140, onComplete: () => txt.destroy() });
    for (let k = 0; k < 5; k++) cena.time.delayedCall(k * 220, () => som('alerta'));
    // Sirene chama reforço: mascarados entram pelas bordas (no máximo três vezes por torre).
    if (this.alarmes > 3) return;
    const v = cena.cameras.main.worldView;
    ['dir', 'esq'].forEach((lado, k) => cena.time.delayedCall(600 + k * 700, () => {
      if (cena.pausado) return;
      const x = lado === 'esq' ? v.x - 18 : v.right + 18;
      const ini = cena.adicionarInimigo(x, cena.chaoAbaixo(x, 60), 'mascarado', {});
      ini.virar(lado === 'esq' ? 1 : -1);
      ini.falar('MMMPH!', 700);
    }));
  }

  levarDano(dano = 1) {
    if (!this.vivo) return;
    this.vida -= Math.max(1, Math.min(dano, 2));
    this.piscar();
    if (this.vida <= 0) this.quebrar();
  }

  quebrar() {
    const cena = this.scene;
    this.vivo = false;
    this.body.enable = false;
    this.apagar();
    this.setFrame(2);
    som('impacto');
    cena.pontuar(300, this.x, this.y - 20);
    cena.efeitos.faisca(this.x + 8, this.y, 14);
    cena.efeitos.estilhacos?.(this.x, this.y, 5, 60, CHAO_Y);
  }

  apagar() {
    this.aceso = false;
    this.facho.clear();
    if (this.vivo) this.setFrame(2);
  }
}

// ------------------------------------------------------------------ gerador
class Gerador extends Peca {
  constructor(base, cfg) {
    const cena = base.cena;
    super(cena, cfg.x, CHAO_Y + 1, 'gerador', 10);
    this.base = base;
    this.id = cfg.id;
    this.setOrigin(0.5, 1).setDepth(6.5);
    this.body.setSize(40, 30).setOffset(3, 3);
    this.proximaFumaca = 0;
    this.som = 0;
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (!this.vivo) return;
    // Roncando: treme, o volante gira e o escapamento solta fumaça preta.
    this.setFrame(Math.floor(t / 70) % 2);
    if (t > this.proximaFumaca) {
      this.proximaFumaca = t + 260;
      this.scene.efeitos.fumacaSobe?.(this.x - 9, this.y - 32);
    }
    const j = this.scene.jogador;
    if (t > this.som && Math.abs(j.x - this.x) < 200) {
      this.som = t + 240;
      som('motor', 0.35);
    }
  }

  levarDano(dano = 1) {
    if (!this.vivo) return;
    this.vida -= Math.max(1, Math.min(dano, 4));
    this.piscar();
    this.scene.efeitos.faisca(this.x + Phaser.Math.Between(-12, 12), this.y - 18, 3);
    if (this.vida <= 0) this.estourar();
  }

  estourar() {
    const cena = this.scene;
    this.vivo = false;
    this.body.enable = false;
    this.setFrame(2);
    cena.explodir(this.x, this.y - 16, 46, 6, 1.4);
    cena.efeitos.tremer(0.01, 300);
    cena.efeitos.fumacaFica?.(this.x, this.y - 24, 1.4);
    cena.pontuar(500, this.x, this.y - 40);
    // Fogo que fica no gerador arrebentado.
    this.chama = cena.add.sprite(this.x - 2, this.y - 10, 'chama', 0).setOrigin(0.5, 1).setDepth(6.6).setScale(0.8)
      .play('chama_viva');
    this.base.apagarLuz(this.id, this.x);
  }
}

// ------------------------------------------------------------------ jaula
class Jaula extends Peca {
  constructor(base, cfg) {
    const cena = base.cena;
    super(cena, cfg.x, CHAO_Y - 1, 'jaula', 6);
    this.base = base;
    this.setOrigin(0.5, 1).setDepth(8.5);
    this.body.setSize(36, 40).setOffset(2, 4);
    // O alien preso fica atrás das grades até a jaula arrebentar.
    this.alien = cena.adicionarInimigo(cfg.x, CHAO_Y - 4, cfg.alien, {});
    this.alien.preso = true;
    this.alien.persegue = false;
    this.alien.setDepth(8);
    this.proximoRugido = cena.time.now + Phaser.Math.Between(1500, 3000);
    cena.events.on('explosao', (ex, ey, raio) => {
      if (this.vivo && Math.abs(ex - this.x) < raio + 26 && Math.abs(ey - (this.y - 20)) < raio + 30) this.abrir();
    });
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    if (!this.vivo) return;
    // O bicho chacoalha as grades e rosna de vez em quando.
    if (t > this.proximoRugido) {
      this.proximoRugido = t + Phaser.Math.Between(2500, 4500);
      this.x += 1;
      this.scene.time.delayedCall(60, () => { this.x -= 2; });
      this.scene.time.delayedCall(120, () => { this.x += 1; });
      this.alien.falar(Phaser.Utils.Array.GetRandom(['GRRR!', 'KRRR!', 'SHHH!']), 600);
    }
  }

  levarDano(dano = 1) {
    if (!this.vivo) return;
    this.vida -= Math.max(1, Math.min(dano, 3));
    this.piscar();
    this.scene.efeitos.faisca(this.x + Phaser.Math.Between(-14, 14), this.y - 22, 2);
    if (this.vida <= 0) this.abrir();
  }

  abrir() {
    const cena = this.scene;
    if (!this.vivo) return;
    this.vivo = false;
    this.body.enable = false;
    this.setFrame(1);
    som('impacto');
    cena.efeitos.faisca(this.x, this.y - 22, 16);
    cena.efeitos.estilhacos?.(this.x, this.y - 20, 6, 80, CHAO_Y);
    // Solto: pula para fora e ataca quem estiver mais perto (Volante ou Lampião).
    const a = this.alien;
    a.preso = false;
    a.cacaTodos = true;
    a.persegue = true;
    a.setDepth(9);
    a.body.setVelocity(Phaser.Math.Between(-60, 60), -220);
    a.caindo = true;
    a.falar('GRAAAH!', 900);
    for (const o of cena.alvos.getChildren()) {
      if (o !== a && o.vivo && o.falar && !o.cfg?.alien && Math.abs(o.x - this.x) < 170) {
        o.falar('ELE SOLTOU!', 900);
      }
    }
  }
}

// ------------------------------------------------------------------ guindaste
// Pedaço do casco do disco pendurado na lança. Atirando no cabo (o alvo é o cabo), ele
// arrebenta e o pedaço despenca esmagando quem estiver embaixo.
class Guindaste extends Peca {
  constructor(base, cfg) {
    const cena = base.cena;
    super(cena, cfg.x, cfg.y + cfg.comprimento / 2, 'lampada', 6);
    this.base = base;
    this.topo = { x: cfg.x, y: cfg.y };
    this.comp = cfg.comprimento;
    this.setVisible(false);
    this.body.setSize(10, cfg.comprimento - 10).setOffset(-2, -cfg.comprimento / 2 + 5);
    this.cabo = cena.add.graphics().setDepth(6.4);
    this.pedaco = cena.add.sprite(cfg.x, cfg.y + cfg.comprimento, 'pedaco_disco', 0).setOrigin(0.5, 16 / 40).setDepth(6.5);
    this.caindo = false;
    this.vy = 0;
    this.proximaFaisca = 0;
  }

  preUpdate(t, dt) {
    super.preUpdate(t, dt);
    const cena = this.scene;
    const p = this.pedaco;
    p.setFrame(Math.floor(t / 400) % 2);
    if (this.caindo) {
      this.vy += 900 * dt / 1000;
      p.y += this.vy * dt / 1000;
      p.rotation += 0.6 * dt / 1000;
      this.cabo.clear();
      this.cabo.lineStyle(1, 0x3a3a48).lineBetween(this.topo.x, this.topo.y, this.topo.x + Math.sin(t / 90) * 3, this.topo.y + 20);
      if (p.y + 20 >= CHAO_Y) this.esmagar();
      return;
    }
    if (this.caiu) return;
    // Balança devagar na corrente, soltando faísca verde de vez em quando.
    const ang = Math.sin(t / 900) * 0.1;
    p.setPosition(this.topo.x + Math.sin(ang) * this.comp, this.topo.y + Math.cos(ang) * this.comp).setRotation(-ang);
    this.cabo.clear();
    this.cabo.lineStyle(2, 0x23233a).lineBetween(this.topo.x, this.topo.y, p.x, p.y - 8);
    this.cabo.lineStyle(1, 0x6b6b7d).lineBetween(this.topo.x, this.topo.y, p.x, p.y - 8);
    if (t > this.proximaFaisca) {
      this.proximaFaisca = t + Phaser.Math.Between(500, 1400);
      cena.efeitos.gosma?.(p.x + Phaser.Math.Between(-20, 20), p.y + 12, 1);
    }
  }

  levarDano(dano = 1) {
    if (!this.vivo) return;
    this.vida -= Math.max(1, Math.min(dano, 3));
    this.scene.efeitos.faisca(this.x, this.y + Phaser.Math.Between(-12, 12), 3);
    if (this.vida <= 0) this.arrebentar();
  }

  arrebentar() {
    const cena = this.scene;
    this.vivo = false;
    this.body.enable = false;
    this.caindo = true;
    this.vy = 30;
    som('impacto');
    cena.efeitos.faisca(this.topo.x, this.topo.y + 10, 12);
    const txt = cena.add.text(this.pedaco.x, this.pedaco.y - 40, 'CUIDADO!', estiloTexto(hex('amarelo_fogo'))).setOrigin(0.5).setDepth(31);
    cena.tweens.add({ targets: txt, alpha: 0, delay: 500, duration: 300, onComplete: () => txt.destroy() });
  }

  esmagar() {
    const cena = this.scene;
    const p = this.pedaco;
    this.caindo = false;
    this.caiu = true;
    p.setPosition(p.x, CHAO_Y - 20).setRotation(0.12);
    cena.tweens.add({ targets: p, y: CHAO_Y - 26, duration: 90, yoyo: true });
    // Esmaga quem estiver embaixo e solta o brilho verde do casco.
    let esmagados = 0;
    for (const o of cena.alvos.getChildren()) {
      if (o.vivo && o.levarDano && !o.segredo && Math.abs(o.x - p.x) < 34 && Math.abs(o.y - CHAO_Y) < 30) {
        o.levarDano(99, p.x, true);
        esmagados++;
      }
    }
    const j = cena.jogador;
    if (!j.morto && Math.abs(j.x - p.x) < 26) j.morrer(0);
    cena.efeitos.explosao(p.x, CHAO_Y - 12, 1.6);
    cena.efeitos.gosma?.(p.x, CHAO_Y - 14, 30);
    cena.efeitos.poeira(p.x, CHAO_Y, 24);
    cena.efeitos.tremer(0.02, 450);
    cena.efeitos.fumacaFica?.(p.x, CHAO_Y - 20, 1.6);
    cena.pontuar(1000 + esmagados * 200, p.x, CHAO_Y - 50);
    if (esmagados) cena.mostrar?.('ESMAGOU!', '', 900);
    this.cabo.clear();
  }
}

// ------------------------------------------------------------------ conjunto
export class Base {
  constructor(cena, dados) {
    this.cena = cena;
    this.apagados = new Set();
    if (!cena.anims.exists('bandeira_tremula')) {
      cena.anims.create({ key: 'bandeira_tremula', frames: cena.anims.generateFrameNumbers('bandeira', { start: 0, end: 3 }),
        frameRate: 8, repeat: -1 });
    }
    this.holofotes = (dados.holofotes || []).map((c) => this.alvo(new Holofote(this, c)));
    this.geradores = (dados.geradores || []).map((c) => this.alvo(new Gerador(this, c)));
    this.jaulas = (dados.jaulas || []).map((c) => this.alvo(new Jaula(this, c)));
    this.guindaste = dados.guindaste ? this.alvo(new Guindaste(this, dados.guindaste)) : null;
    // Varal de lâmpadas entre os postes: fio caído em curva e lâmpadas piscando.
    this.varais = (dados.lampadas || []).map((v) => {
      const fio = cena.add.graphics().setDepth(5.5);
      const n = Math.floor((v.x1 - v.x0) / 26);
      const pts = [];
      for (let k = 0; k <= n * 4; k++) {
        const f = k / (n * 4);
        pts.push(new Phaser.Math.Vector2(v.x0 + (v.x1 - v.x0) * f, v.y + Math.sin(f * Math.PI) * 14));
      }
      fio.lineStyle(1, 0x14141c).strokePoints(pts);
      const lamps = [];
      for (let k = 1; k < n; k++) {
        const f = k / n;
        lamps.push(cena.add.sprite(v.x0 + (v.x1 - v.x0) * f, v.y + Math.sin(f * Math.PI) * 14, 'lampada', 0)
          .setOrigin(0.5, 0).setDepth(5.6));
      }
      return { ...v, lamps };
    });
    this.escuros = [];
  }

  alvo(p) {
    this.cena.alvos.add(p);
    p.body.allowGravity = false;
    return p;
  }

  apagado(id) {
    return this.apagados.has(id);
  }

  // Gerador arrebentado: apaga holofotes e lâmpadas daquele gerador, escurece o pedaço e
  // os soldados por perto ficam perdidos um tempo ("CADÊ A LUZ?!").
  apagarLuz(id, x) {
    const cena = this.cena;
    this.apagados.add(id);
    for (const h of this.holofotes) if (h.gerador === id) h.apagar();
    for (const v of this.varais) if (v.gerador === id) v.lamps.forEach((l) => l.setFrame(2));
    // Escuridão em camadas (mais forte no meio, sem borda reta).
    for (const [larg, alfa] of [[700, 0.1], [560, 0.1], [420, 0.12]]) {
      const escuro = cena.add.rectangle(x - larg / 2, -200, larg, 600, 0x0e0d24, 0).setOrigin(0).setDepth(24);
      cena.tweens.add({ targets: escuro, fillAlpha: alfa, duration: 400 });
      this.escuros.push(escuro);
    }
    const t = cena.time.now;
    for (const o of cena.alvos.getChildren()) {
      if (!o.vivo || !o.falar || o.cfg?.alien || Math.abs(o.x - x) > 330) continue;
      o.falar(Phaser.Utils.Array.GetRandom(['CADÊ A LUZ?!', 'APAGOU TUDO!', 'NÃO VEJO NADA!']), 1300);
      o.proximoTiro = Math.max(o.proximoTiro || 0, t + 2600);
      o.estado = 'panico';
      o.fimEstado = t + 900;
    }
  }

  atualizar(t) {
    // Lâmpadas tremendo de leve (a corrente do gerador oscila).
    for (const v of this.varais) {
      if (this.apagado(v.gerador)) continue;
      v.lamps.forEach((l, k) => l.setFrame((Math.floor(t / 110) + k * 3) % 11 === 0 ? 1 : 0));
    }
  }
}
