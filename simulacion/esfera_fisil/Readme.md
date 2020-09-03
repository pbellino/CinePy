# Validación de los métodos de multiplicidad gamma/neutrones

Objetivo: Utilizar una medio físil subcrítico y mediante los cálculos de ruido neutrónico obtener parámetros cinéticos que luego serán contrastados con los valores obtenidos de una simulación con kcode.

## Descripción del problema

* Esfera con material físil y moderados homogeneos
* Fuente de neutrones puntual y sin correlación
* Detector ficticio de gamma rodeando la esfera físil
* Detector de He3 rodenado al detector de gammas

## Contenido de la carpeta

* `in_sdef` : input para realizar la simulación con fuente fija (lee a `sistema`). No se puede correr por sí solo, se lo llama con `run_sdef.h`. Para correrlo, se debe comentar alguna de las PTRAC.
* `in_kcode` : input para realizar la simulación con kcode (lee a `sistema`)
* `sistema` : parte del input que describe al sistema (celdas, superficies y materiales)
* `run_sdef.sh` : script para correr el problema con fuente fija. Como se necesitan hacer dos corridas por separado (una para usar el PTRAC de neutrones y otra para el de fotones), el script crea dos inputs temporales y los corre. Finalmente borra los inputs temporales. La salida generada son archivos `in_sdef_n` e `in_sdef_p` correspondientes a las corridas para el PTRAC de neutrones y de fotones respectivamente.
