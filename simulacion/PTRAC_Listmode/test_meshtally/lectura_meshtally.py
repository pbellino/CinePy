#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TODO
"""

import numpy as np
from mcnptools import Meshtal
import matplotlib.pyplot as plt


if __name__ == '__main__':

    # Se abren los archivos (binarios y ascii)
    m = Meshtal("test_fmesh.msht")

    print(m.GetProbid())
    print(m.GetComment())
    print(m.GetNps())
    print(m.GetTallyList())

    t14 = m.GetTally(14)

    x = t14.GetXRBins()
    y = t14.GetYZBins()
    z = t14.GetZTBins()

    # xg, yg, zg = np.meshgrid(x, y, z)

    values = np.empty((len(x), len(y), len(z)))
    for i in range(len(x)):
        for j in range(len(y)):
            for k in range(len(z)):
                values[i, j, k] = t14.GetValue(i, j, k)
    h = plt.contourf(x, y, np.log(values[:, :, 50]))
    plt.show()
