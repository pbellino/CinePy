from distutils.core import setup
from Cython.Build import cythonize

""" Script para compilar con cython """

setup(
    ext_modules = cythonize("flag_np_deadtime.pyx")
)
