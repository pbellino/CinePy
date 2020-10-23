#!/usr/bin/env python3

import sys
sys.path.append('/home/pablo/CinePy/')
from modules.io_modules import read_kcode_out
from modules.simulacion_modules import calcula_param_cin


if __name__ == "__main__":

    filename = "in_kcode.o"

    dic = read_kcode_out(filename)

    out_dic = calcula_param_cin(dic, verbose=True)
