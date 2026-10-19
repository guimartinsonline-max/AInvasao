import { som } from '../som.js';
// Tiros dos inimigos, em pool. 'volante' é bala rápida; 'raio' é o tiro verde lento do xeremita.
// mira: ângulo máximo (rad) que o tiro pode apontar para o Lampião; 0 = sai reto.
const TIPOS = {
  volante: { textura: 'tracer', velocidade: 200, mira: 0 },
  raio: { textura: 'raio', velocidade: 110, mira: 0 },
  // Metralhadora do blindado: bala grossa com rastro de fogo, animada.
  pesada: { textura: 'bala_pesada', velocidade: 230, mira: 0, quadros: 2 },
};

export class BalasInimigas {
  constructor(cena, solidos, jogador) {
    this.cena = cena;
    this.jogador = jogador;
    this.dinamites = cena.physics.add.group({ defaultKey: 'dinamite', maxSize: 8 });
    // Dinamite, rojão, obus, carvão e bomba atravessam plataforma de um lado só
    // (girau, telhado, toldo): quem está em cima não fica protegido embaixo dela.
    cena.physics.add.collider(this.dinamites, solidos, (d) => this.explodirDinamite(d),
      (d, s) => !(s.body && s.body.checkCollision.down === false));
    cena.physics.add.overlap(this.dinamites, jogador.corpo, (a, b) => this.explodirDinamite(a === jogador.corpo ? b : a));
    this.dinamites.maxSize = 10;
    this.grupo = cena.physics.add.group({ defaultKey: 'raio', maxSize: 24, allowGravity: false });
    cena.physics.add.overlap(this.grupo, solidos, (bala) => {
      if (!bala.active) return;
      cena.efeitos.impacto(bala.x, bala.y, bala.texture.key === 'raio' ? 'verde' : 'comum');
      this.recolher(bala);
    }, (bala, s) => !(s.body && s.body.checkCollision.down === false) || bala.body.velocity.y > 0);
    cena.physics.add.overlap(this.grupo, jogador.corpo, (a, b) => {
      const bala = a === jogador.corpo ? b : a;
      if (!bala.active || jogador.morto || jogador.invulneravel) return;
      this.recolher(bala);
      jogador.morrer(bala.body.velocity.x);
    });
  }

  // Dinamite do granadeiro: voa em arco girando e explode ao tocar o chão ou o Lampião.
  lancarDinamite(x, y, direcao, distancia) {
    som('arremesso');
    const d = this.dinamites.get(x, y, 'dinamite');
    if (!d) return;
    d.setActive(true).setVisible(true).setDepth(14);
    d.body.reset(x, y);
    d.body.setSize(6, 6);
    const vx = Phaser.Math.Clamp(distancia * 1.05, 50, 190);
    d.body.setVelocity(direcao * vx, -230);
    d.body.setAngularVelocity(direcao * 720);
  }

  // Vômito do soldado contaminado: golfada em arco que espirra no chão.
  lancarVomito(x, y, direcao, distancia) {
    som('arremesso');
    const d = this.dinamites.get(x, y, 'vomito');
    if (!d) return;
    d.setTexture('vomito', 0).setActive(true).setVisible(true).setDepth(14).setFlipX(direcao < 0);
    d.body.reset(x, y);
    d.body.setSize(7, 6);
    d.body.setAngularVelocity(0);
    d.vomito = true;
    d.proximaFumaca = 0;
    const vx = Phaser.Math.Clamp(distancia * 1.1, 60, 200);
    d.body.setVelocity(direcao * vx, -170);
  }

  // Rojão do soldado: sai inclinado para cima, cai em arco e explode no chão.
  lancarRojao(x, y, direcao, distancia) {
    som('rojao');
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

  // Obus do canhão do blindado: arco mais alto, gira a cinta, rastro de fumaça e explosão maior.
  lancarObus(x, y, direcao, distancia) {
    som('canhao');
    const d = this.dinamites.get(x, y, 'obus');
    if (!d) return;
    d.setTexture('obus', 0).setActive(true).setVisible(true).setDepth(14).setFlipX(false);
    d.body.reset(x, y);
    d.body.setSize(12, 8);
    d.body.setAngularVelocity(0);
    d.rojao = true;
    d.obus = true;
    const vx = Phaser.Math.Clamp(distancia * 0.75, 90, 240);
    d.body.setVelocity(direcao * vx, -220);
    d.proximaFumaca = 0;
  }

  // Bomba do biplano: cai do avião com a velocidade dele, aponta para onde vai e explode grande.
  soltarBomba(x, y, vx) {
    som('mergulho');
    const d = this.dinamites.get(x, y, 'bomba_av');
    if (!d) return;
    d.setTexture('bomba_av', 0).setActive(true).setVisible(true).setDepth(14).setFlipX(false);
    d.body.reset(x, y);
    d.body.setSize(10, 6);
    d.body.setAngularVelocity(0);
    d.rojao = true;
    d.obus = true;
    d.bomba = true;
    d.body.setVelocity(vx, 20);
    d.proximaFumaca = 0;
  }

  // Tiro num ângulo qualquer (metralhadora do artilheiro do biplano).
  dispararAngulo(x, y, ang, tipo = 'volante') {
    const cfg = TIPOS[tipo];
    const bala = this.grupo.get(x, y, cfg.textura);
    if (!bala) return;
    bala.setTexture(cfg.textura, 0).setActive(true).setVisible(true).setFlipX(false).setDepth(15);
    bala.body.reset(x, y);
    bala.body.setSize(bala.width, bala.height);
    bala.quadros = cfg.quadros || 1;
    som('tiro_inimigo');
    bala.setRotation(ang);
    bala.body.setVelocity(Math.cos(ang) * cfg.velocidade, Math.sin(ang) * cfg.velocidade);
  }

  // Carvão em brasa da chaminé do trem: arco que cai perto de alvoX e estoura pequeno.
  lancarCarvao(x, y, alvoX) {
    som('chamine');
    const d = this.dinamites.get(x, y, 'carvao');
    if (!d) return;
    d.setTexture('carvao', 0).setActive(true).setVisible(true).setDepth(14).setFlipX(false);
    d.body.reset(x, y);
    d.body.setSize(6, 6);
    const vy = -Phaser.Math.Between(200, 260);
    const queda = Math.max(0, 192 - y);
    const tempo = (-vy + Math.sqrt(vy * vy + 2 * 900 * queda)) / 900;
    d.body.setVelocity((alvoX - x) / tempo, vy);
    d.body.setAngularVelocity(400);
    d.carvao = true;
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
    if (d.vomito) {
      // Espirra gosma no chão (ou no Lampião) sem explodir.
      d.vomito = false;
      cena.efeitos.gosma(x, y - 2, 18);
      const j = this.jogador;
      if (!j.morto && !j.invulneravel && Math.abs(j.x - x) < 14 && Math.abs(j.pe - 14 - y) < 24) {
        if (j.zumbificar) j.zumbificar();
        else j.morrer(j.x - x);
      }
      return;
    }
    const forte = d.rojao;
    const obus = d.obus;
    const carvao = d.carvao;
    d.rojao = false;
    d.obus = false;
    d.bomba = false;
    d.carvao = false;
    cena.efeitos.explosao(x, y - 4, obus ? 1.4 : forte ? 0.9 : carvao ? 0.45 : 0.6);
    if (carvao) cena.efeitos.chama(x, y - 4);
    const j = this.jogador;
    const raio = obus ? 36 : forte ? 28 : carvao ? 16 : 20;
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
    bala.quadros = cfg.quadros || 1;
    som(tipo === 'pesada' ? 'tiro_pesado' : tipo === 'raio' ? 'raio_et' : 'tiro_inimigo');
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
      if (d.active && d.carvao && agora > d.proximaFumaca) {
        // Brasa soltando faísca no ar.
        d.proximaFumaca = agora + 60;
        d.setFrame(Math.floor(agora / 80) % 2);
        this.cena.efeitos.faisca(d.x, d.y, 1);
      }
      if (d.active && d.vomito) {
        // Pinga gosma pelo caminho e tomba para onde vai.
        d.setRotation(Math.atan2(d.body.velocity.y, Math.abs(d.body.velocity.x)) * (d.flipX ? -1 : 1));
        if (agora > d.proximaFumaca) {
          d.proximaFumaca = agora + 70;
          this.cena.efeitos.gosma(d.x, d.y, 1);
        }
        continue;
      }
      if (!d.active || !d.rojao) continue;
      // O rojão aponta para onde vai e solta fumaça.
      d.setRotation(Math.atan2(d.body.velocity.y, d.body.velocity.x));
      if (d.obus) d.setFrame(Math.floor(agora / 60) % (d.bomba ? 2 : 3));
      if (agora > d.proximaFumaca && !d.bomba) {
        d.proximaFumaca = agora + 50;
        this.cena.efeitos.fumaca(d.x - Math.cos(d.rotation) * 10, d.y - Math.sin(d.rotation) * 10);
      }
    }
    for (const bala of this.grupo.getChildren()) {
      if (!bala.active) continue;
      if (bala.quadros > 1) bala.setFrame(Math.floor(agora / 70) % bala.quadros);
      if (bala.x < v.x - 16 || bala.x > v.right + 16 || bala.y < v.y - 30 || bala.y > 260) this.recolher(bala);
    }
  }
}
