import { BALAS } from '../armas.js';

// Balas do jogador, reaproveitadas de um pool fixo. O tipo (src/armas.js)
// define textura, velocidade, dano, alcance, explosão e se atravessa inimigos.
export class Balas {
  constructor(cena, solidos, alvos, aoAcertar, aoAcertarCaixote) {
    this.cena = cena;
    this.grupo = cena.physics.add.group({ defaultKey: 'bala', maxSize: 48, allowGravity: false });

    cena.physics.add.overlap(this.grupo, solidos, (bala, solido) => {
      if (!bala.active) return;
      if (solido.caixote && !bala.tipo.explode) aoAcertarCaixote(solido.caixote, bala);
      if (bala.tipo.explode) this.explodir(bala);
      else cena.efeitos.faisca(bala.x, bala.y, 3);
      this.recolher(bala);
    });
    cena.physics.add.overlap(this.grupo, alvos, (bala, alvo) => {
      if (!bala.active || !alvo.vivo) return;
      if (bala.tipo.atravessa) {
        // Atinge cada inimigo uma vez só.
        if (bala.atingidos.includes(alvo)) return;
        bala.atingidos.push(alvo);
      }
      if (bala.tipo.explode) {
        this.explodir(bala);
        this.recolher(bala);
        return;
      }
      aoAcertar(alvo, bala);
      if (!bala.tipo.atravessa) this.recolher(bala);
    });
  }

  disparar(x, y, ang, tipo = 'comum') {
    const cfg = BALAS[tipo];
    const bala = this.grupo.get(x, y, cfg.textura);
    if (!bala) return;
    bala.tipo = cfg;
    bala.nasceu = this.cena.time.now;
    bala.atingidos = [];
    bala.setTexture(cfg.textura).setActive(true).setVisible(true).setRotation(ang).setDepth(14);
    bala.body.reset(x, y);
    const vertical = Math.abs(Math.sin(ang)) > 0.7;
    const w = bala.width;
    const h = bala.height;
    bala.body.setSize(vertical ? h : w, vertical ? w : h);
    bala.angulo = ang;
    bala.body.setVelocity(Math.cos(ang) * cfg.velocidade, Math.sin(ang) * cfg.velocidade);
  }

  explodir(bala) {
    const e = bala.tipo.explode;
    this.cena.explodir(bala.x, bala.y, e.raio, e.dano, 0.7);
  }

  recolher(bala) {
    bala.setActive(false).setVisible(false);
    bala.body.stop();
    bala.body.reset(-100, -100);
  }

  atualizar(dt) {
    const v = this.cena.cameras.main.worldView;
    const agora = this.cena.time.now;
    for (const bala of this.grupo.getChildren()) {
      if (!bala.active) continue;
      const cfg = bala.tipo;
      if (cfg.acelera) {
        // Rojão: sai devagar, acelera e solta faíscas.
        const vel = Math.min(cfg.maxima, Math.hypot(bala.body.velocity.x, bala.body.velocity.y) + cfg.acelera * dt / 1000);
        bala.body.setVelocity(Math.cos(bala.angulo) * vel, Math.sin(bala.angulo) * vel);
        if (Math.random() < 0.6) this.cena.efeitos.faisca(bala.x - Math.cos(bala.angulo) * 5, bala.y, 1);
      }
      if (cfg.vida && agora - bala.nasceu > cfg.vida) {
        this.recolher(bala);
        continue;
      }
      if (bala.x < v.x - 8 || bala.x > v.right + 8 || bala.y < v.y - 8 || bala.y > v.bottom + 8) {
        this.recolher(bala);
      }
    }
  }
}
