#! /bin/bash

# Script para ejecutar el sisitema con KCODE

# INPUT=alfas
INPUT=in_kcode

rm ${INPUT}.*
cnp6 tasks 8 i=${INPUT} n=${INPUT}.

