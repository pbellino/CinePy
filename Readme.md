Cinética en Python
==================

Programas para procesar datos de cinética de reactores.


Se comienza tratando de reproducir lo obtenido con octave cuando se procesan los datos con el método de alfa-Feynman.

Contenido de la carpeta
-----------------------

    * `src/` 
        - `alfa_feynman.py` :  Procesa los datos con el método de alfa-Feynman

    * `datos/` 
        Carpeta donde estarán los datos en crudo obtenidos por los programas de adquisición
    
    * `resultados/` 
        Carpeta donde se guardan los archivos con las curvas de a-Feynman

    * `modules/` 
        - `io_modules.py` : Módulo con funciones relacionadas con lectura/escritura de archivos
        - `estadistica.py` : Módulo con funciones estadísticas

    * `tests/`
        - `test_lectura.py` : Script para probar la función de lectura de datos `read_bin_dt` de `modules/io_modules.py`
        - `octave` : Scripts originales cuyos resultados se toman como referencia
