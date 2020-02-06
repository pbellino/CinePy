#!/bin/bash

rm -f outp ptrac runtpe

echo 'Comienza simulación de MCNP'
mcnp6 i=Cf252_H2O.i
echo 'Ffializó simulación de MCNP'

echo 'Comienza generación de tiempos en modo lista'
python3 arossi_from_PTRAC_Listmode.py
echo 'Finaliza generación de tiempos en modo lista'

echo 'Comienza procesamiento para obtener la RAD'
python3 arossi_procesamiento_main.py
echo 'Finaliza procesamiento para obtener la RAD'
