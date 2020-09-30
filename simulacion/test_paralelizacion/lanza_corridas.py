#!/usr/bin/env python3

"""
Script que lanza en paralelo corridas de mcnp con distintas semillas
"""

import sys
sys.path.append('/home/pablo/CinePy')
from modules.corridas_paralelizadas import run_paralelo


if __name__ == '__main__':

    # Para correr en una PC
    run_paralelo(4, 'in_sdef', machine='PC', run_script='run_sdef.sh')
