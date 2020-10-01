#!/bin/bash

# Script para ejecutar al sistema utilizando SDEF
# Corre sólo neutrones pero conserva la notación que se 
# utilizaría al correr neutrones y fotones por separado

# Archivo principal
if [ -z "$1" ]
then
    INPUT=in_sdef
else
    INPUT="$1"
fi

echo
echo "***********************************************************************"
echo "* Recordar que el input ${INPUT} debe tener los dos PTRAC sin comentar *"
echo "***********************************************************************"
echo

# Quito tallies de fotones para correr PTRAC de neutrones
sed '/@BEGIN_TALLY_P/,/@END_TALLY_P/d' ${INPUT} > ${INPUT}_n 

mcnp6 i=${INPUT}_n n=${INPUT}. 

