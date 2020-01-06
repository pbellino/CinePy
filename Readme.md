Cinética en Python
==================

Programas para procesar datos de cinética de reactores.


Se comienza tratando de reproducir lo obtenido con octave cuando se procesan los datos con el método de alfa-Feynman.

Contenido de la carpeta
-----------------------

    * `src/` 
        - `alfa_feynman.py` :  Procesa los datos con el método de alfa-Feynman
        - `grafica_adquisicion.py` :  Grafica los datos guardados por los programas de adquisición
        - `analisis_alfa_feynman.py` : Graficación y ajuste no lineal para las curvas de alfa-Feynman
        - `inter_arrival_analysis.py` : Grafica histograma de tiempo entre pulsos

    * `datos/` 
        Carpeta donde estarán los datos en crudo obtenidos por los programas de adquisición
 
    * `constantes/` 
        Carpeta donde estarán los archivos con las constantes necesarias
    
    * `src/resultados/` 
        Carpeta donde se guardan los archivos con los datos ya procesados

    * `modules/`
        - `io_modules.py` : Módulo con funciones relacionadas con lectura/escritura de archivos
        - `estadistica.py` : Módulo con funciones estadísticas

    * `tests/`
        - `test_read_bin_dt.py` : Script para probar la función de lectura de datos `read_bin_dt` de `modules/io_modules.py`
        - `test_read_timestamp.py`: Script para probal la función de lectura de datos `read_timestamp` de `modules/io_modules.py`
        - `test_ajuste_afey.py` : Se prueba el ajuste no lineal con señales simuladas
        - `octave` : Scripts originales cuyos resultados se toman como referencia

