"""Gera os efeitos de tiro, explosão e a bateria da trilha em mp3 (assets/sons/).

Cada tiro é montado em camadas, como um tiro gravado: estalo supersônico (ruído
curtíssimo), estrondo grave do cano, corpo de médios, mecânica da arma (ferrolho,
alavanca, pente) e a cauda de eco do sertão aberto. Tudo passa por saturação e
compressão para soar gordo e na cara, no espírito do Metal Slug.

Uso: python3 tools/som/gerar_sons.py   (precisa de numpy, scipy e ffmpeg)
"""
import os
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAIDA = os.path.join(RAIZ, 'assets', 'sons')
rng = np.random.default_rng(1936)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def ruido(dur):
    return rng.uniform(-1, 1, int(dur * SR))


def filtro(x, tipo, f, ordem=2):
    if isinstance(f, (list, tuple)):
        f = [min(max(v, 20), SR / 2 - 100) for v in f]
    else:
        f = min(max(f, 20), SR / 2 - 100)
    return sosfilt(butter(ordem, f, btype=tipo, fs=SR, output='sos'), x)


def env(dur, ataque=0.0005, queda=0.05, forma=1.0):
    t = t_(dur)
    e = np.exp(-t / queda) ** forma
    a = int(ataque * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def mix(*partes, dur=None):
    n = max(len(p) + int(o * SR) for o, p in partes) if dur is None else int(dur * SR)
    y = np.zeros(n)
    for o, p in partes:
        i = int(o * SR)
        m = min(len(p), n - i)
        if m > 0:
            y[i:i + m] += p[:m]
    return y


def seno_desliza(dur, f0, f1, queda):
    t = t_(dur)
    f = f1 + (f0 - f1) * np.exp(-t / (queda * 0.6))
    fase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(fase) * env(dur, 0.001, queda)


def reverb(x, dur=0.8, brilho=3500, mistura=0.35, eco=0.12):
    """Cauda de ambiente aberto: ruído decaindo (difuso) + um eco de barranco."""
    ir = ruido(dur) * np.exp(-t_(dur) / (dur / 5))
    ir = filtro(ir, 'lowpass', brilho)
    ir[:int(0.004 * SR)] *= 0.2
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    molhado = fftconvolve(x, ir)[:len(x) + len(ir)]
    seco = np.concatenate([x, np.zeros(len(molhado) - len(x))])
    if eco:
        d = int(eco * SR)
        ec = np.zeros_like(seco)
        ec[d:] = filtro(seco, 'lowpass', 1800)[:-d] * 0.28
        seco = seco + ec
    return seco + molhado * mistura


def saturar(x, ganho=2.5):
    return np.tanh(x * ganho) / np.tanh(ganho)


def clique_metal(dur=0.05, freqs=(2900, 4300, 6100), queda=0.012):
    t = t_(dur)
    y = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in freqs) / len(freqs)
    y = y * np.exp(-t / queda) + filtro(ruido(dur), 'highpass', 3000) * np.exp(-t / (queda * 0.5)) * 0.6
    return y


def tiro(crack=1.0, boom=1.0, f_boom=(140, 45), corpo=1.0, f_corpo=(700, 2600),
         queda_corpo=0.05, cauda=0.7, brilho=4000, mistura=0.4, eco=0.13, drive=2.4, dur=0.5):
    estalo = filtro(ruido(0.012), 'highpass', 1500) * env(0.012, 0.0002, 0.0025) * crack
    estrondo = seno_desliza(0.35, f_boom[0], f_boom[1], 0.07) * boom
    estrondo += filtro(ruido(0.35), 'lowpass', 220) * env(0.35, 0.001, 0.06) * boom * 1.2
    meio = filtro(ruido(0.3), 'bandpass', list(f_corpo)) * env(0.3, 0.0005, queda_corpo) * corpo * 1.6
    seco = mix((0, estalo * 1.4), (0, estrondo), (0.0005, meio), dur=dur)
    seco = saturar(seco, drive)
    return reverb(seco, cauda, brilho, mistura, eco)


def normalizar(x, pico=0.95):
    # Corta o silêncio do fim e normaliza.
    x = x / (np.max(np.abs(x)) + 1e-9) * pico
    a = np.abs(x)
    fim = len(x) - np.argmax(a[::-1] > 0.003)
    x = x[:max(fim, int(0.02 * SR))]
    caida = min(int(0.02 * SR), len(x))
    x[-caida:] *= np.linspace(1, 0, caida)
    return x


# ---------------------------------------------------------------- armas do Lampião
def pistola():
    y = tiro(crack=1.1, boom=0.7, f_boom=(170, 60), corpo=0.9, f_corpo=(900, 3200), queda_corpo=0.04,
             cauda=0.55, mistura=0.35, dur=0.35)
    return mix((0, y), (0.07, clique_metal(0.05, (3100, 4700, 6900)) * 0.25))  # ferrolho voltando


def madsen():
    return tiro(crack=1.2, boom=1.0, f_boom=(150, 50), corpo=1.0, f_corpo=(600, 2400), queda_corpo=0.035,
                cauda=0.35, mistura=0.25, eco=0.09, drive=3.0, dur=0.22)


def bacamarte():
    y = tiro(crack=0.8, boom=1.6, f_boom=(110, 35), corpo=1.3, f_corpo=(300, 1800), queda_corpo=0.09,
             cauda=1.1, brilho=2600, mistura=0.5, eco=0.18, drive=3.2, dur=0.6)
    # Chumbo espalhando: chiado grosso logo depois do estouro.
    chumbo = filtro(ruido(0.25), 'bandpass', [1500, 6000]) * env(0.25, 0.002, 0.05) * 0.3
    return mix((0, y), (0.01, chumbo))


def papo_amarelo():
    y = tiro(crack=1.5, boom=0.9, f_boom=(160, 55), corpo=0.9, f_corpo=(1200, 4500), queda_corpo=0.04,
             cauda=1.0, brilho=5000, mistura=0.45, eco=0.2, drive=2.6, dur=0.5)
    # Alavanca do Winchester: clec-clac.
    return mix((0, y), (0.32, clique_metal(0.05, (2200, 3600, 5200)) * 0.35),
               (0.42, clique_metal(0.06, (1800, 2900, 4400), 0.015) * 0.4))


def rojao():
    d = 0.6
    t = t_(d)
    sopro = filtro(ruido(d), 'bandpass', [500, 4000]) * np.minimum(1, t / 0.03) * np.exp(-t / 0.25)
    assobio = np.sin(2 * np.pi * np.cumsum(900 + 1800 * t / d) / SR) * np.exp(-t / 0.3) * 0.12
    estouro = tiro(crack=0.5, boom=1.2, f_boom=(90, 40), corpo=0.6, f_corpo=(300, 1200), cauda=0.6,
                   mistura=0.3, dur=0.25) * 0.6
    return reverb(saturar(mix((0, estouro), (0, sopro * 0.9), (0.02, assobio)), 1.8), 0.6, 3000, 0.3, 0.12)


def desintegrador():
    d = 0.45
    t = t_(d)
    f = 1800 * np.exp(-t / 0.08) + 180
    mod = np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR) * 3
    y = np.sin(2 * np.pi * np.cumsum(f) / SR + mod) * np.exp(-t / 0.12)
    y += filtro(ruido(d), 'bandpass', [2000, 7000]) * np.exp(-t / 0.03) * 0.5
    return reverb(saturar(y, 1.8), 0.5, 6000, 0.35, 0)


def candeeiro():
    d = 0.32
    t = t_(d)
    ronco = filtro(ruido(d), 'lowpass', 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
    chiado = filtro(ruido(d), 'bandpass', [1500, 5000]) * 0.35
    estalos = np.zeros(len(t))
    for _ in range(9):
        i = rng.integers(0, len(t) - 400)
        estalos[i:i + 300] += filtro(ruido(300 / SR), 'highpass', 2000) * np.exp(-np.arange(300) / 50) * rng.uniform(0.3, 0.8)
    y = (ronco + chiado + estalos) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.05)
    return saturar(y, 1.6)


def estilingue():
    d = 0.22
    t = t_(d)
    estalo = filtro(ruido(0.02), 'bandpass', [800, 3000]) * env(0.02, 0.0005, 0.004)
    borracha = np.sin(2 * np.pi * np.cumsum(260 - 140 * t / d) / SR) * np.exp(-t / 0.03) * 0.6
    vento = filtro(ruido(d), 'bandpass', [600, 2400]) * np.sin(np.pi * t / d) * 0.35
    return mix((0, estalo), (0, borracha), (0.01, vento))


def buscape():
    d = 0.5
    t = t_(d)
    assobio = np.sin(2 * np.pi * np.cumsum(1400 + 2600 * (t / d) ** 0.7 + 60 * np.sin(2 * np.pi * 30 * t)) / SR)
    assobio *= np.minimum(1, t / 0.02) * np.exp(-t / 0.35) * 0.5
    fagulha = filtro(ruido(d), 'highpass', 3000) * np.exp(-t / 0.2) * 0.4
    pipoco = tiro(crack=1, boom=0.3, f_corpo=(1500, 5000), cauda=0.3, mistura=0.2, dur=0.1) * 0.5
    return mix((0, pipoco), (0.01, assobio), (0, fagulha))


def metralha_jumento():
    return tiro(crack=1.1, boom=1.4, f_boom=(120, 40), corpo=1.1, f_corpo=(400, 2000), queda_corpo=0.04,
                cauda=0.4, brilho=3000, mistura=0.3, eco=0.1, drive=3.4, dur=0.22)


# ---------------------------------------------------------------- inimigos e veículos
def tiro_inimigo():
    # Fuzil da Volante: mais seco e um pouco distante (menos grave, mais eco).
    y = tiro(crack=1.0, boom=0.5, f_boom=(200, 80), corpo=0.8, f_corpo=(900, 3500), queda_corpo=0.03,
             cauda=0.7, brilho=3200, mistura=0.55, eco=0.16, drive=2.0, dur=0.25)
    return filtro(y, 'highpass', 150)


def tiro_pesado():
    return tiro(crack=1.0, boom=1.3, f_boom=(110, 40), corpo=1.0, f_corpo=(350, 1800), queda_corpo=0.04,
                cauda=0.5, brilho=2800, mistura=0.35, eco=0.12, drive=3.2, dur=0.25)


def canhao():
    y = tiro(crack=0.6, boom=2.2, f_boom=(80, 28), corpo=1.0, f_corpo=(150, 900), queda_corpo=0.15,
             cauda=1.6, brilho=1800, mistura=0.6, eco=0.25, drive=3.0, dur=0.9)
    return mix((0, y), (0.12, clique_metal(0.08, (900, 1500, 2300), 0.03) * 0.2))


def explosao(tam):
    d = 0.6 + 0.6 * tam
    t = t_(d)
    estouro = filtro(ruido(d), 'lowpass', 1200 + 1800 * tam) * np.exp(-t / (0.08 + 0.12 * tam))
    ronco = filtro(ruido(d), 'lowpass', 160) * np.exp(-t / (0.25 + 0.35 * tam)) * 2.2
    grave = seno_desliza(d, 90, 30, 0.2 + 0.2 * tam) * 1.4
    detritos = np.zeros(len(t))
    for _ in range(int(10 + 20 * tam)):
        i = rng.integers(int(0.05 * SR), len(t) - 800)
        k = filtro(ruido(800 / SR), 'bandpass', [1500, 5000]) * np.exp(-np.arange(800) / 120)
        detritos[i:i + 800] += k * rng.uniform(0.05, 0.25) * np.exp(-t[i] / 0.5)
    crack = filtro(ruido(0.02), 'highpass', 1000) * env(0.02, 0.0003, 0.004) * 1.5
    y = saturar(mix((0, crack), (0, estouro), (0, ronco), (0, grave), (0, detritos)), 2.8)
    return reverb(y, 1.2 + tam * 0.6, 1800, 0.45, 0.22)


def impacto():
    d = 0.08
    t = t_(d)
    y = filtro(ruido(d), 'bandpass', [900, 4500]) * np.exp(-t / 0.012)
    y += np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.02) * 0.5
    return saturar(y, 2)


def ricochete():
    d = 0.35
    t = t_(d)
    f = 3800 - 2200 * t / d
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12) * 0.5
    return mix((0, impacto() * 0.8), (0.005, y))


def faca():
    d = 0.22
    t = t_(d)
    vento = filtro(ruido(d), 'bandpass', [1500, 7000]) * np.sin(np.pi * np.minimum(1, t / 0.12)) * np.exp(-t / 0.08)
    lamina = np.sin(2 * np.pi * np.cumsum(5200 + 900 * t) / SR) * np.exp(-t / 0.06) * 0.15
    golpe = filtro(ruido(0.06), 'lowpass', 700) * env(0.06, 0.001, 0.015)
    return mix((0, vento), (0, lamina), (0.07, golpe * 1.4))


def recarga():
    return mix((0, clique_metal(0.05, (1900, 3100, 4700), 0.014) * 0.6),
               (0.12, clique_metal(0.06, (2500, 3900, 5600), 0.012) * 0.8))


# ---------------------------------------------------------------- bateria da trilha
def bumbo():
    d = 0.35
    y = mix((0, seno_desliza(d, 160, 48, 0.09) * 1.3),
            (0, filtro(ruido(0.01), 'highpass', 2000) * env(0.01, 0.0001, 0.002) * 0.4))
    return saturar(y, 2.2)


def caixa():
    d = 0.3
    t = t_(d)
    corpo = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.7
    esteira = filtro(ruido(d), 'bandpass', [1800, 9000]) * np.exp(-t / 0.08)
    y = saturar(corpo + esteira * 1.1, 2.0)
    return reverb(y, 0.4, 6000, 0.25, 0)


def chimbal():
    d = 0.06
    return filtro(ruido(d), 'highpass', 7000) * env(d, 0.0002, 0.012)


def chimbal_aberto():
    d = 0.3
    return filtro(ruido(d), 'highpass', 6500) * env(d, 0.0003, 0.09)


def prato():
    d = 1.4
    t = t_(d)
    y = filtro(ruido(d), 'highpass', 4500) * np.exp(-t / 0.45)
    y += sum(np.sin(2 * np.pi * f * t) for f in (3170, 4460, 5530, 6890)) * np.exp(-t / 0.3) * 0.04
    return y


def surdo():
    return saturar(seno_desliza(0.4, 130, 75, 0.12) * 1.2 + filtro(ruido(0.4), 'lowpass', 400) * env(0.4, 0.001, 0.04) * 0.3, 1.8)


def zabumba():
    # Pancada grave de zabumba (a base de baião misturada na bateria de rock).
    return saturar(seno_desliza(0.4, 110, 62, 0.1) * 1.3 + filtro(ruido(0.4), 'bandpass', [80, 600]) * env(0.4, 0.001, 0.03) * 0.5, 1.6)


SONS = {
    'pistola': pistola, 'madsen': madsen, 'bacamarte': bacamarte, 'papo_amarelo': papo_amarelo,
    'rojao': rojao, 'desintegrador': desintegrador, 'candeeiro': candeeiro, 'estilingue': estilingue,
    'buscape': buscape, 'metralha_jumento': metralha_jumento, 'tiro_inimigo': tiro_inimigo,
    'tiro_pesado': tiro_pesado, 'canhao': canhao,
    'explosao_p': lambda: explosao(0.3), 'explosao_m': lambda: explosao(1.0), 'explosao_g': lambda: explosao(1.8),
    'impacto': impacto, 'ricochete': ricochete, 'faca': faca, 'recarga': recarga,
    'bumbo': bumbo, 'caixa': caixa, 'chimbal': chimbal, 'chimbal_aberto': chimbal_aberto,
    'prato': prato, 'surdo': surdo, 'zabumba': zabumba,
}


def main():
    os.makedirs(SAIDA, exist_ok=True)
    total = 0
    with tempfile.TemporaryDirectory() as tmp:
        for nome, f in SONS.items():
            x = normalizar(f())
            w = os.path.join(tmp, nome + '.wav')
            wavfile.write(w, SR, (x * 32767).astype(np.int16))
            mp3 = os.path.join(SAIDA, nome + '.mp3')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-ac', '1', '-ar', '44100',
                            '-codec:a', 'libmp3lame', '-b:a', '64k', mp3], check=True)
            total += os.path.getsize(mp3)
    print(f'{len(SONS)} sons em assets/sons ({total // 1024} KB)')


if __name__ == '__main__':
    main()
