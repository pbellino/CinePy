#!/bin/bash

rm -f input.*

echo 'Comienza simulación de MCNP'
mcnp6 tasks 4 i=input n=input.
echo 'Ffializó simulación de MCNP'

