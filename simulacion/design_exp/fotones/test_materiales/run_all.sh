#!/bin/bash

NAME=test_M7

rm -f $NAME.*

echo 'Comienza simulación de MCNP'
echo 'Corriendo el archivo: ' $NAME
mcnp6 tasks 4 i=$NAME n=$NAME.
echo 'Ffializó simulación de MCNP'

