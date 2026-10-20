"""Sombreado no nível novo para quem ainda usava o Tela.volume (com pontilhado) ou o
Tela.cel de 3 tons: veículos, biplano, jumento e trem. Cada rampa ganha um degrau mais
escuro embaixo e um mais claro em cima (beirada acesa, miolo de sombra), sem pontilhado.
"""
from motor import IDX, NOMES

_EXT = {}


def estender(rampa):
    """Rampa com um tom mais escuro antes e um mais claro depois (da paleta antiga)."""
    from blindagem import ESC, CLA
    k = tuple(rampa)
    if k not in _EXT:
        r = list(rampa)
        esc = NOMES[ESC[IDX[r[0]]]]
        cla = NOMES[CLA[IDX[r[-1]]]]
        if esc not in r:
            r = [esc] + r
        if cla not in r:
            r = r + [cla]
        _EXT[k] = r
    return _EXT[k]


def vol(t, m, rampa, achatado=2.4, linha=True, **kw):
    """Substitui t.volume(...)."""
    from caricatos import sombrear, RAMPAS_MOTOR
    rampa = RAMPAS_MOTOR.get(rampa, rampa) if isinstance(rampa, str) else rampa
    return sombrear(t, m, estender(rampa), achatado=min(4.0, max(1.2, achatado)), linha=linha)


def cel(t, m, rampa, sombra=2, luz=1, linha=True, deslocar=0, rebaixo=False):
    """Substitui t.cel(...)."""
    from caricatos import sombrear, RAMPAS_MOTOR
    rampa = RAMPAS_MOTOR.get(rampa, rampa) if isinstance(rampa, str) else rampa
    return sombrear(t, m, estender(rampa), deslocar=deslocar, linha=linha, brilho=sombra > 0)
