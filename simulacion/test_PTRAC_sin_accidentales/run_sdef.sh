#!/bin/bash

# Script para ejecutar al sistema utilizando SDEF
# Como por cada corrida de puede poner sólo una tarjeta PTRAC,
# se generan dos inputs temporales para cada corrida (una para
# usar PTRAC con fotones, y la otra con neutrones).

# Archivo principal
INPUT=in_sdef
echo
echo "***********************************************************************"
echo "* Recordar que el input ${INPUT} debe tener los dos PTRAC sin comentar *"
echo "***********************************************************************"
echo

# Nombre de los archivos temporales que correrán n y p
INPUT_N=${INPUT}_n

# Quito tallies de fotones para correr PTRAC de neutrones
sed '/@BEGIN_TALLY_P/,/@END_TALLY_P/d' ${INPUT} > ${INPUT_N}

# Corro los inputs temporales
rm -f ${INPUT_N}.*
mcnp6 i=${INPUT_N} n=${INPUT_N}. 
P1=$!

# Espera a que terminen
wait ${P1}

# Borro input temporales
rm ${INPUT_N}
