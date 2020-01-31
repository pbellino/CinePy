#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TODO
"""

import os.path
import numpy as np


if __name__ == '__main__':

    archivo = 'test_F8_RAD.out'

    with open(archivo, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('1tally fluctuation charts'):
            print(line)
