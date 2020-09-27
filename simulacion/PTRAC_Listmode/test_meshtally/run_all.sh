#!/bin/bash

rm -f test_fmesh.*

echo "Ejecutando MCNP...."
mcnp6 i=test_fmesh n=test_fmesh.
echo "Fin de ejecución de MCNP"

