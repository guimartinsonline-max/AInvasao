import { BALAS } from '../armas.js';
import { EFEITOS } from '../quadros.js';

// Balas do jogador, reaproveitadas de um pool fixo. O tipo (src/armas.js)
// define folha animada, velocidade, dano, alcance, explosão, gravidade,
// quique, perseguição e se atravessa inimigos.
export class Balas {
  constructor(cena, solidos, alvos, aoAcertar, aoAcertarCaixote) {
    this.cena = cena;
    this.alvos = alvos;
    this.grupo = cena.physics.add.group({ defaultKey: 'tracer', maxSize: 64, allowGravity: false });

    cena.physics.add.overlap(this.grupo, solidos, (bala, solido) => {
      if (!bala.active) return;
      const tipo = bala.tipo;
      // Pedra da Baladeira: quica no chão algumas vezes.
      if (tipo.quica && bala.quiques < tipo.quica && bala.body.velocity.y > 0) {
        bala.quiques++;
        bala.y -= 2;
        bala.body.setVelocityY(-Math.abs(bala.body.velocity.y) * 0.6);
        bala.body.setVelocityX(bala.body.velocity.x * 0.8);
        cena.efeitos.poeira(bala.x, bala.y + 2, 3);
        return;
      }
      if (solido.caixote && !tipo.explode) aoAcertarCaixote(solido.caixote, bala);
      if (tipo.explode) this.explodir(bala);
      else if (tipo.textura === 'chama') cena.efeitos.fumaca(bala.x, bala.y);
      else cena.efeitos.impacto(bala.x, bala.y, tipo.impacto);
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
    bala.quiques = 0;
    bala.fase = Math.random() * Math.PI * 2;
    bala.setTexture(cfg.textura, 0).setActive(true).setVisible(true).setDepth(14).setScale(1);
    bala.body.reset(x, y);
    bala.body.allowGravity = !!cfg.gravidade;
    bala.body.setGravityY(cfg.gravidade ? cfg.gravidade - this.cena.physics.world.gravity.y : 0);
    // A pedra e a chama não giram com a direção; as outras apontam para onde vão.
    const gira = !cfg.gravidade && cfg.textura !== 'chama' && cfg.textura !== 'chumbo';
    bala.setRotation(gira ? ang : 0);
    bala.setFlipX(!gira && Math.cos(ang) < -0.1);
    const vertical = gira && Math.abs(Math.sin(ang)) > 0.7;
    const w = cfg.corpo || bala.width;
    const h = cfg.corpo || Math.max(bala.height, 3);
    bala.body.setSize(vertical ? h : w, vertical ? w : h);
    bala.angulo = ang;
    let vy = Math.sin(ang) * cfg.velocidade;
    if (cfg.levanta && Math.abs(Math.sin(ang)) < 0.7) vy -= cfg.levanta;
    bala.body.setVelocity(Math.cos(ang) * cfg.velocidade, vy);
    bala.proximoRastro = 0;
    return bala;
  }

  explodir(bala) {
    const e = bala.tipo.explode;
    this.cena.explodir(bala.x, bala.y, e.raio, e.dano, e.tamanho);
  }

  recolher(bala) {
    bala.setActive(false).setVisible(false);
    bala.body.stop();
    bala.body.reset(-100, -100);
  }

  // Inimigo vivo mais perto, para o Buscapé perseguir.
  maisPerto(bala) {
    let melhor = null;
    let dist = 220;
    for (const alvo of this.alvos.getChildren()) {
      if (!alvo.vivo || alvo.persegue === false) continue;
      const d = Phaser.Math.Distance.Between(bala.x, bala.y, alvo.x, alvo.y - 18);
      if (d < dist) {
        dist = d;
        melhor = alvo;
      }
    }
    return melhor;
  }

  atualizar(dt) {
    const v = this.cena.cameras.main.worldView;
    const agora = this.cena.time.now;
    const ef = this.cena.efeitos;
    for (const bala of this.grupo.getChildren()) {
      if (!bala.active) continue;
      const cfg = bala.tipo;
      const idade = agora - bala.nasceu;
      const quadros = EFEITOS[cfg.textura].quadros;
      if (cfg.textura === 'chama') {
        // A chama nasce branca, cresce, escurece e vira fumaça ao longo da vida.
        bala.setFrame(Math.min(quadros - 1, Math.floor((idade / cfg.vida) * quadros)));
        const k = Math.pow(cfg.freio, dt / 16.7);
        bala.body.setVelocity(bala.body.velocity.x * k, bala.body.velocity.y * k - cfg.sobe * dt / 1000);
      } else if (quadros > 1) {
        bala.setFrame(Math.floor(idade / 60) % quadros);
      }
      if (cfg.acelera) {
        // Rojão: sai devagar e acelera.
        const vel = Math.min(cfg.maxima, Math.hypot(bala.body.velocity.x, bala.body.velocity.y) + cfg.acelera * dt / 1000);
        bala.body.setVelocity(Math.cos(bala.angulo) * vel, Math.sin(bala.angulo) * vel);
      }
      if (cfg.busca) {
        // Buscapé: serpenteia e vira aos poucos na direção do inimigo mais perto.
        const alvo = this.maisPerto(bala);
        let ang = Math.atan2(bala.body.velocity.y, bala.body.velocity.x);
        if (alvo) {
          const quer = Math.atan2(alvo.y - 18 - bala.y, alvo.x - bala.x);
          ang += Phaser.Math.Clamp(Phaser.Math.Angle.Wrap(quer - ang), -cfg.busca * dt / 1000, cfg.busca * dt / 1000);
        }
        const zig = Math.sin(idade / 70 + bala.fase) * cfg.ziguezague * dt / 1000;
        ang += zig;
        bala.body.setVelocity(Math.cos(ang) * cfg.velocidade, Math.sin(ang) * cfg.velocidade);
        bala.setRotation(ang);
      }
      if (cfg.rastro && agora > bala.proximoRastro) {
        const tras = bala.rotation + Math.PI;
        const rx = bala.x + Math.cos(tras) * 8;
        const ry = bala.y + Math.sin(tras) * 8;
        if (cfg.rastro === 'fumaca') {
          ef.fumaca(rx, ry);
          bala.proximoRastro = agora + 45;
        } else {
          ef.faisca(rx, ry, 1);
          bala.proximoRastro = agora + 25;
        }
      }
      if (cfg.vida && idade > cfg.vida) {
        if (cfg.explode) this.explodir(bala);
        this.recolher(bala);
        continue;
      }
      if (bala.x < v.x - 8 || bala.x > v.right + 8 || bala.y < v.y - 30 || bala.y > v.bottom + 8) {
        this.recolher(bala);
      }
    }
  }
}
