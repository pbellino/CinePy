#! /usr/bin/env python3

import sys
sys.path.append('../../')
from modules.io_modules import read_kcode_out


if __name__ == "__main__":

    filename = "in_kcode.o"

    dic = read_kcode_out(filename)
    for key, val in dic.items():
        print(key, val)
