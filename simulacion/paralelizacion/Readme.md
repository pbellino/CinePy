
# Lanza corridas en Neurus

En esta carpeta están los archivos mínimos requeridos para lanzar distintas
instancias de MCNP6 en el cluster Neurus.

El objetivo es poder paralelizar un problema en el caso que no sea posible
ejecutar la versión paralelizada de MCNP. Ya sea porque debido a las
características del archivo de entrada no admita una paralelización (por
ejemplo, con la opción PTRAC) o porque no se disponga del ejecutable para MPI
de MCNP6.

Las dos opciones que se pueden hacer son:

### 1) Ejecutar instancias de MCNP en serie de a un core

    Esto sirve cuando se utiliza la opción PTRAC

### 2) Ejecutar instancias de MCNP y paralelizar con OPENMP

    Esto sirve cuando no se utiliza la opción PTRAC

## Contenido

    - ``input``: Input de MCNP
    - ``lanza_corridas.py``: Script para lanzar los jobs
    - ``mcnp6.slurm``: Script de slurm para ejecutaar mcnp6 en una sola
      instancia
    - ``mcnp6_gcc6.3_openmp.slurm``: Script de slurm para ejecutar mcnp6 con
      OPENMP


## Procedimiento

Al ejecutar el script ``lanza_corridas.py`` se realiza lo siguiente:

Dentro de la carpeta raíz (donde están todos estos archivos) se generan
carpetas (una por cada corrida que se lanzó) con el nombre ``case_001``,
``case_002``, etc.

Dentro de cada carpeta se copian el archivo de slurm que correspondan (de acuerdo a lo
elegido en el script de python) y el input de mcnp.

Al ser copiados se realizan las siguientes modificaciones:

    - Al input de mcnp6 se le cambia la semilla del generador de números
      aleatorios. El input se escribe como ``case_xxx`` (el mismo nombre de la
      carpeta donde se encuentra)

    - Al archivos de slurm se le modifica el nombre del job y el nombre del
      input de MCNP



