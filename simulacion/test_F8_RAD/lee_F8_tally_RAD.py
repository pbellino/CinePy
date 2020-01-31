#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TODO
"""

import numpy as np
import sys

sys.path.append('../../')
from modules.io_modules import lee_tally_F8_RAD


if __name__ == '__main__':

    archivo = 'test_F8_RAD.out'

    data, cap_NG, nps = lee_tally_F8_RAD(archivo)
    RAD = data[:, 0] * nps
    tot_cap = cap_NG[0] * nps
    print('Capturas totales: {}'.format(tot_cap))
    print(RAD)
