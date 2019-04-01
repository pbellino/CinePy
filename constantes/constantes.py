#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Archivo con las constantes relativas a cin+etica de reactores
y a distintos reactores nucleares
"""


class Constantes_Nucleares:
    """ Constantes comunes """

    ENERGIA_FISION = 3.2e-11  # [J]
    FACTOR_DIVEN = 0.7962
    EFECTIVIDAD_FOTONEUTRONES = 0
    FACTOR_BENNETT = 1

# Constantes propias para cada reactor
# Son una subclase de Constantes_Nucleares


class RA0(Constantes_Nucleares):
    LAMBDA_REDUCIDO = 0.016700  # [s]
    FACTOR_FORMA_L = 1.18
    BETA_EFECTIVO = 0.00792


class RA1(Constantes_Nucleares):
    LAMBDA_REDUCIDO = 0.011900  # [s]
    FACTOR_FORMA_L = 1.18
    BETA_EFECTIVO = 0.00751
    SIGMA_BETA_EFECTIVO = 0.00003


class RA3(Constantes_Nucleares):
    LAMBDA_REDUCIDO = 0.008340  # [s]
    FACTOR_FORMA_L = 1.19
    BETA_EFECTIVO = 0.007682
    EFECTIVIDAD_FOTONEUTRONES = 1.12e-4


class RA4(Constantes_Nucleares):
    LAMBDA_REDUCIDO = 0.0065  # [s]
    FACTOR_FORMA_L = 1.18
    BETA_EFECTIVO = 0.0073


class RA6(Constantes_Nucleares):
    LAMBDA_REDUCIDO = 0.010000  # [s]
    FACTOR_FORMA_L = 1.19
    BETA_EFECTIVO = 0.007642


class RA8(Constantes_Nucleares):
    LAMBDA_REDUCIDO = 0.006184  # [s]
    FACTOR_FORMA_L = 1.18
    BETA_EFECTIVO = 0.0076


class CNAII(Constantes_Nucleares):
    LAMBDA_REDUCIDO = 0.069439  # [s]
    FACTOR_FORMA_L = 1.00
    BETA_EFECTIVO = 0.00758
    EFECTIVIDAD_FOTONEUTRONES = 0.62


if __name__ == '__main__':

    a = RA0
    b = RA0.FACTOR_DIVEN

    print(vars(a))
    print(b)
