"""Utilidades comunes: ejecutar ngspice en modo batch y leer la salida de wrdata."""
import os, subprocess, tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
SPICE = os.path.join(AQUI, '..', 'spice')
GRAF = os.path.join(AQUI, '..', 'graficas')
TMP = os.environ.get('SIM_TMP', os.path.join(tempfile.gettempdir(), 'sim_lhdt'))
os.makedirs(TMP, exist_ok=True)
os.makedirs(GRAF, exist_ok=True)

# Paleta y estilo comunes (legibles en claro, con colores distinguibles)
COL = ['#2a6fdb', '#e4572e', '#29a36a', '#8e5bd6', '#d4a017', '#555555']
plt.rcParams.update({'figure.dpi': 110, 'savefig.dpi': 150, 'axes.grid': True, 'grid.alpha': 0.3,
                     'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 9,
                     'axes.prop_cycle': matplotlib.cycler(color=COL)})


def run(nombre, cuerpo, vectores, tran):
    """Escribe <nombre>.cir en TMP (incluye los .inc de spice/), lo simula y devuelve dict de arrays."""
    out = os.path.join(TMP, nombre + '.txt')
    cir = os.path.join(TMP, nombre + '.cir')
    with open(cir, 'w') as f:
        f.write(f'* {nombre}\n{cuerpo}\n.options method=gear reltol=1e-3 abstol=1e-6 vntol=1e-5 itl4=50\n'
                f'{tran}\n.control\nrun\nset wr_singlescale\nwrdata {out} {" ".join(vectores)}\n.endc\n.end\n')
    r = subprocess.run(['ngspice', '-b', cir], cwd=SPICE, capture_output=True, text=True)
    if not os.path.exists(out) or 'Error' in r.stdout + r.stderr and 'rror on line' in r.stdout + r.stderr:
        raise RuntimeError(r.stdout[-3000:] + r.stderr[-3000:])
    d = np.loadtxt(out)
    res = {'t': d[:, 0]}
    for i, v in enumerate(vectores):
        res[v] = d[:, i + 1]
    os.remove(out)
    return res


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(os.path.join(GRAF, nombre))
    plt.close(fig)
