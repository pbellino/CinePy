from distutils.core import setup
from Cython.Build import cythonize

""" Script para compilar con cython """

setup(
    ext_modules = cythonize(["reactimeter.pyx", "direct_kinetic_solver.pyx"])
)
