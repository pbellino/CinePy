Cinética en Python
==================

Programas para procesar datos de cinética de reactores.


Se comienza tratando de reproducir lo obtenido con octave cuando se procesan los datos con el método de alfa-Feynman y alfa-Rossi.

Contenido de la carpeta
-----------------------

    * `src/` 
        - `alfa_feynman_procesamiento.py` :  Procesa los datos con el método de alfa-Feynman
        - `alfa_feynman_grafica_adquisicion.py` :  Grafica los datos guardados por los programas de adquisición
        - `alfa_feynman_analisis.py` : Graficación y ajuste no lineal para las curvas de alfa-Feynman
        - `arossi_procesamiento.py` : Lee el archivo de timestamping, aplica el método de alfa-Rossi y escribe los resultados.
        _ `arossi_analisis.py` : Lee los archivos escritos por `arossi_procesamiento.py`, grafica los resultados y hace los ajustes de las curvas.
        - `inter_arrival_analysis.py` : Grafica histograma de tiempo entre pulsos
        - `dead_time_analysis.py` : Analiza y simula tiempos muertos en las mediciones con timestamping.
        - `inter_arrival_analysis_ipynb` : Notebook de prueba para los análisis que se hacen en `dead_time_analysis.py`

    * `datos/` 
        Carpeta donde estarán los datos en crudo obtenidos por los programas de adquisición
 
    * `constantes/` 
        Carpeta donde estarán los archivos con las constantes necesarias
    
    * `src/resultados/` 
        Carpeta donde se guardan los archivos con los datos ya procesados

    * `modules/`
        - `io_modules.py` : Módulo con funciones relacionadas con lectura/escritura de archivos
        - `estadistica.py` : Módulo con funciones estadísticas
 
        - `alfa_rossi_preprocesamiento.py` : Lee archivo de tiempo entre pulsos y devuelve las historias por separado.
        - `alfa_rossi_procesamiento.py` : Procesa todas las historias en el método de alfa-Rossi.
        - `alfa_rossi_escritura.py` : Escribe los resultados del procesamiento en archivos.
        - `alfa_rossi_lectura.py` : Lee los datos escritos del procesamiento.
        - `alfa_rossi_analisis.py` : Grafica los datos escritos por el procesamiento. Hace ajustes teóricos a las curvas medidas.
        - `funciones.py` : Módulo con las funciones teóricas que se utilizan en los ajustes.
        - `flag_np_deadtime.pyx` : Función en cython en la cual se basa la simulación del tiempo muerto no-paralizable. Se debe compilar para generar el .so que debe ubicarse en esta misma carpeta.


    * `tests/`
        - `test_read_bin_dt.py` : Script para probar la función de lectura de datos `read_bin_dt` de `modules/io_modules.py`
        - `test_read_timestamp.py`: Script para probal la función de lectura de datos `read_timestamp` de `modules/io_modules.py`
        - `test_ajuste_afey.py` : Se prueba el ajuste no lineal con señales simuladas
        - `test_arossi_una_historia_I.py` : Se prueba el procesamiento de una historia con el método de alfa-Rossi
        - `octave` : Scripts originales cuyos resultados se toman como referencia


TODO: 
----
      - Análisis espectral a partir de los datos de time-stamping y de ventanas temporales.

      - Análisis de alfa-Feynman a partir de los datos de timestamping.

      - Análisis de muchos archivos.

      - Propagación de errores y obtención de parámetros cineticos.
