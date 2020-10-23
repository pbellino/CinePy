# Pruebas para analizar sólo neutrones correlacionados (sin coincidencias accidentales)


Para comprobar la línea de cálculo utilizada, se puede utilizar los datos del archivo PTRAC para hacer un análisis de ruido neutrónico sólo considerando las capturas de cada cadena de fisión por separado.


## Procedimiento

Sólo se aplica el méotdo de $alpha$-Rossi en este análisis. Para aprovechar las funciones que ya están escritas se procesó de una forma particular al archivo PTRAC.

Se consideró una historia a todas las capturas provenientes del mismo evento de fuente (siempre y cuando haya más de dos capturas). Es decir, del archivo PTRAC se agrupan las capturas con el mismo nps. Como sólo se quiere analizar el valor del $\alpha$, no se tiene en cuenta la normalización de la distribución de alfa-Rossi, de lo contrario habría que contar las historias con una sóla captura (que suman cero a la distribución, pero al promediar influyen en la normalización).

Tanto el preprocesamiento como el procesamiento se hace en un sólo script. Esto no es del todo aconsejable porque se tarda bastante en leer el archivo binario. Si fuera necesario habría que guradar un archivo intermedio.

## Contenido

Para analizar alfa-Rossi sin accidentales:

* `procesamiento_sin_accidentales.py` : lee el archivo PTRAC, separa por historias, calcula la distribución de alfa-Rossi y guarda el archivo con el promedio.
* `arossi_analisis_main.py`

Para analizar alfa-Rossi estandar (con coincidencias accidentales):

Se usa la misma línea de procesamiento que se tenía:

* `lectura_salidas_mcnp.py`
* `arossi_procesamiento_main.py`
* `arossi_analisis_main.py`
