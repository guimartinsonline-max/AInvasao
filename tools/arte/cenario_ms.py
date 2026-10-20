"""Acabamento dos cenários no padrão novo (ESTILO.md, 20/10).

Os cenários foram pintados com as cores antigas da paleta, acinzentadas. Esta passada
troca cada cor antiga do cenário por uma irmã saturada `cen_<nome>` (registrada na
paleta), seguindo a regra das rampas novas: a sombra puxa para o azul/roxo, a luz puxa
para o amarelo e o meio-tom ganha cor. Depois dá a luz de um lado só (cima-esquerda) na
silhueta das peças das camadas de perto: beirada de cima-esquerda um degrau mais clara,
beirada de baixo-direita um degrau mais escura (nada de borda clara em volta toda).

Roda no fim do exportar.py e pode rodar sozinha sobre os PNGs prontos:
    python3 tools/arte/cenario_ms.py            # aplica em assets/sprites
    python3 tools/arte/cenario_ms.py --paleta   # só recalcula as cores cen_* na paleta
Aplicar duas vezes não muda nada (as cores cen_* não são trocadas de novo e a luz só\nentra nos pixels trocados agora).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = Path(__file__).resolve().parents[2]
PALETA = RAIZ / "assets/paleta.json"
SPRITES = RAIZ / "assets/sprites"

# Cores que não mudam: verde-alien (reservado), fogo e brilho puro já são saturados.
FIXAS = {"alien_esc", "alien", "alien_brilho", "alien_profundo", "alien_medio", "alien_luz",
         "laranja_fogo", "amarelo_fogo", "ouro_escuro", "amarelo_claro", "laranja_escuro",
         "preto", "branco"}

# Peças de cenário (camadas e objetos de fundo). Personagens, itens e efeitos ficam de fora.
PREFIXOS = ("f1_", "f2_", "f2b_", "ceu", "casa_vila_", "segredo_")
AVULSOS = {"nuvens", "chao", "caatinga", "serras", "paredoes", "planicie", "touceiras", "pedra",
           "laje", "ponte_seg", "varal", "roupa", "gerador", "holofote", "jaula", "lampada",
           "mesa_truco", "biruta", "bandeira", "pedaco_disco", "plataforma_elevador", "panela"}
# Camadas que levam a luz de um lado na silhueta (as de perto; longe fica chapado pela névoa).
COM_LUZ = ("f1_jogo", "f1_perto", "f1_frente", "f2_jogo", "f2_perto", "f2_frente",
           "f2b_jogo", "f2b_perto", "f2b_frente")
EXCLUIR = ("_fumaca", "_fogo")


# ---------- cor (Oklab) ----------
def _lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _srgb(c):
    c = np.clip(c, 0, 1)
    return np.round(255 * np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055))


def _oklab(rgb):
    r, g, b = _lin(np.asarray(rgb, float))
    lm = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    lm, m, s = np.cbrt(lm), np.cbrt(m), np.cbrt(s)
    return np.array([0.2104542553 * lm + 0.7936177850 * m - 0.0040720468 * s,
                     1.9779984951 * lm - 2.4285922050 * m + 0.4505937099 * s,
                     0.0259040371 * lm + 0.7827717662 * m - 0.8086757660 * s])


def _rgb(lab):
    L, a, b = lab
    lm = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return _srgb(np.array([4.0767416621 * lm - 3.3077115913 * m + 0.2309699292 * s,
                           -1.2684380046 * lm + 2.6097574011 * m - 0.3413193965 * s,
                           -0.0041960833 * lm - 0.7034186147 * m + 1.7076147010 * s])).astype(int)


CEU = {"ceu_escuro", "ceu", "ceu_claro", "horizonte", "ceu_medio", "ceu_luz", "azul_medio",
       "vermelho_esc", "vermelho_medio", "vermelho"}  # telha vermelha já é viva


def saturar(hexcor, ceu=False):
    """Irmã saturada de uma cor antiga: mais croma, sombra fria, luz quente, mais contraste.
    O céu e a telha só ganham um pouco (azul e vermelho berrantes brigam com a terra)."""
    rgb = [int(hexcor[i:i + 2], 16) for i in (1, 3, 5)]
    L, a, b = _oklab(rgb)
    C, h = np.hypot(a, b), np.arctan2(b, a)
    # Contraste: afasta do meio-tom (escuro mais fundo, claro mais aceso).
    if ceu:
        L2, C2 = L, C * 1.08
        lab = np.array([L2, C2 * np.cos(h), C2 * np.sin(h)])
        return "#%02x%02x%02x" % tuple(np.clip(_rgb(lab), 0, 255))
    L2 = 0.62 + (L - 0.62) * 1.12
    # Croma: cores de terra ganham bem mais; cinzas ganham um pouco (puxando para o azul-roxo).
    C2 = C * 1.4 + (0.012 if C > 0.03 else 0.006)
    # Matiz: no escuro gira para o azul-roxo (~285°), no claro para o amarelo (~85°).
    frio, quente = np.radians(285), np.radians(85)
    def girar(h, alvo, t):
        d = (alvo - h + np.pi) % (2 * np.pi) - np.pi
        return h + d * t
    if L < 0.62:
        h = girar(h, frio, min(1, (0.62 - L) / 0.4) * (0.12 if C > 0.03 else 0.5))
    else:
        h = girar(h, quente, min(1, (L - 0.62) / 0.3) * 0.3)
    C2 = min(C2, 0.04 + 0.32 * min(L2, 1 - L2 + 0.25))  # não estourar fora do sRGB
    for _ in range(12):  # traz para dentro da gama
        lab = np.array([L2, C2 * np.cos(h), C2 * np.sin(h)])
        r = _rgb(lab)
        if (r >= 0).all() and (r <= 255).all():
            break
        C2 *= 0.9
    r = np.clip(_rgb(np.array([L2, C2 * np.cos(h), C2 * np.sin(h)])), 0, 255)
    return "#%02x%02x%02x" % tuple(r)


def atualizar_paleta(usadas):
    p = json.loads(PALETA.read_text())
    cores = p["cores"]
    for n in sorted(usadas):
        if n in FIXAS or n.startswith("cen_"):
            continue
        cores[f"cen_{n}"] = saturar(cores[n], n in CEU)
    p["nome"] = f"Sertão {len(cores)} (rampas saturadas; cen_* = cenário no padrão novo)"
    PALETA.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n")
    return cores


def _arquivos():
    for f in sorted(SPRITES.glob("*.png")):
        n = f.stem
        if any(e in n for e in EXCLUIR):
            continue
        if n.startswith(PREFIXOS) or n in AVULSOS:
            yield f


def _hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def luz_de_lado(a, rampa_mais, rampa_menos, novos):
    """Beirada de cima-esquerda um degrau mais clara e de baixo-direita mais escura.
    Só mexe nos pixels que acabaram de trocar de cor (`novos`), para não dar a luz duas vezes."""
    m = a[..., 3] == 255
    if not m.any():
        return a
    # Só peças com corpo (pelo menos 3 px de grossura): capim e fio ficam como estão.
    corpo = ndimage.binary_opening(m, np.ones((3, 3)))
    # A linha logo dentro do contorno escuro (o contorno é o 1º px; a luz vai no 2º).
    dentro = ndimage.binary_erosion(m)
    borda_cl = corpo & dentro & ~ndimage.binary_erosion(m, iterations=2)
    # direção: a beirada tem vazio em cima/esquerda (a 2 px)
    vazio = ~m
    vz2_cima = np.zeros_like(m); vz2_cima[2:] = vazio[:-2]
    vz2_esq = np.zeros_like(m); vz2_esq[:, 2:] = vazio[:, :-2]
    vz2_baixo = np.zeros_like(m); vz2_baixo[:-2] = vazio[2:]
    vz2_dir = np.zeros_like(m); vz2_dir[:, :-2] = vazio[:, 2:]
    acende = borda_cl & novos & (vz2_cima | vz2_esq) & ~(vz2_baixo | vz2_dir)
    apaga = borda_cl & novos & (vz2_baixo | vz2_dir) & ~(vz2_cima | vz2_esq)
    rgb = a[..., :3]
    chave = (rgb[..., 0].astype(np.int32) << 16) | (rgb[..., 1].astype(np.int32) << 8) | rgb[..., 2]
    out = a.copy()
    for alvo, tabela in ((acende, rampa_mais), (apaga, rampa_menos)):
        for k, novo in tabela.items():
            sel = alvo & (chave == k)
            out[sel, :3] = novo
    return out


def _rampas(cores):
    """Para cada cor cen_*, o vizinho mais claro e mais escuro do mesmo material."""
    import motor  # noqa: E402  (rampas antigas por material)
    sys.path.insert(0, str(Path(__file__).parent))
    seqs = list(motor.RAMPAS.values())
    for pre in ("mad_n", "lona_n", "lona_q", "oliva_n", "chao_n", "corda_n"):
        seqs.append(sorted((n for n in cores if n.startswith(pre) and n[len(pre):].isdigit()),
                           key=lambda n: int(n[len(pre):])))
    seqs += [["terra_escura", "terra", "terra_media", "barro", "areia_media", "areia", "areia_luz", "areia_clara"],
             ["sombra", "sombra_media", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"],
             ["caatinga_esc", "caatinga_media", "caatinga", "mandacaru", "mandacaru_luz"],
             ["couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz", "couro_claro"]]
    mais, menos = {}, {}
    for s in seqs:
        s = [n for n in s if n in cores and n not in FIXAS and f"cen_{n}" in cores]
        for k, n in enumerate(s):
            c = _hexrgb(cores[f"cen_{n}"])
            k_ = (c[0] << 16) | (c[1] << 8) | c[2]
            if k + 1 < len(s) and k_ not in mais:
                mais[k_] = _hexrgb(cores[f"cen_{s[k + 1]}"])
            if k > 0 and k_ not in menos:
                menos[k_] = _hexrgb(cores[f"cen_{s[k - 1]}"])
    return mais, menos


def aplicar(arquivos=None, so_paleta=False):
    sys.path.insert(0, str(Path(__file__).parent))
    cores = json.loads(PALETA.read_text())["cores"]
    inv = {_hexrgb(h): n for n, h in cores.items()}
    arquivos = list(arquivos or _arquivos())
    usadas = set()
    imgs = {}
    for f in arquivos:
        a = np.array(Image.open(f).convert("RGBA"))
        imgs[f] = a
        u = np.unique(a[a[..., 3] > 0][:, :3], axis=0)
        usadas |= {inv[tuple(c)] for c in u if tuple(c) in inv}
    cores = atualizar_paleta(usadas | {n[4:] for n in cores if n.startswith("cen_")})
    if so_paleta:
        return
    troca = {}
    for n in usadas:
        if n in FIXAS or n.startswith("cen_"):
            continue
        c = _hexrgb(cores[n])
        troca[(c[0] << 16) | (c[1] << 8) | c[2]] = _hexrgb(cores[f"cen_{n}"])
    mais, menos = _rampas(cores)
    for f, a in imgs.items():
        rgb = a[..., :3]
        chave = (rgb[..., 0].astype(np.int32) << 16) | (rgb[..., 1].astype(np.int32) << 8) | rgb[..., 2]
        out = a.copy()
        vis = a[..., 3] > 0
        novos = np.zeros(vis.shape, bool)
        for k, novo in troca.items():
            sel = vis & (chave == k)
            out[sel, :3] = novo
            novos |= sel
        if not novos.any():
            continue
        if f.stem.startswith(COM_LUZ):
            out = luz_de_lado(out, mais, menos, novos)
        Image.fromarray(out).save(f)
    return [f.name for f in imgs]


if __name__ == "__main__":
    r = aplicar(so_paleta="--paleta" in sys.argv)
    print("cenário no padrão novo:", len(r or []), "arquivos")
