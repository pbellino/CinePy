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
INPUT_P=${INPUT}_p

# Quito tallies de neutrones para correr PTRAC de fotones
sed '/@BEGIN_TALLY_N/,/@END_TALLY_N/d' ${INPUT} > ${INPUT_P}
# Quito tallies de fotones para correr PTRAC de neutrones
sed '/@BEGIN_TALLY_P/,/@END_TALLY_P/d' ${INPUT} > ${INPUT_N}

# Corro el sistema para cada PTRAC
for name in ${INPUT_N} ${INPUT_P}; do
    rm -f ${name}.*
    mcnp6 i=${name} n=${name}.
    # Borro input temporal
    rm ${name}
done
