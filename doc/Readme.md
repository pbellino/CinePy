$\alpha$-Rossi
==============

Procesamiento de datos
----------------------

![Diagrama de flujo para el procesamiento de $\alpha$-Rossi](flujo_procesamiento.png)


Cython
------

Para generar el tiempo muerto no paralizable se utilizó una función optimizada con cython:

`flag_np_deadtime.pyx`

que se debe compilar utilizando el script `setup.py`:

```
python3 setup.py build_ext --inplace

```

Todos estos scripts están en la carpeta `modules`. 

Luego de compilar se copia el *.so a `modules` (originalmente lo guarda en una subcarpeta).
