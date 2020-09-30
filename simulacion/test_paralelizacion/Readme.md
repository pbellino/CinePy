# Pruebas para paralelizar y combinar resutlados

Carpeta para probar la paralelización y posterior lectura y compaginar los resultados.

Se quiere generar un archivo similar al que se hubiera obtenido de haberse corrido en serie. De esta manera se puede aplicar las mismas funciones que ya están implementadas.

Algunos pasos que se deben seguir:

* El archivo PTRAC de cada corrida tendrá su propio número de historia, se debe cambiar al juntar los resultados. Esto se usa para asignar los tiempos de cada evento de fuente.

* Entonces es necesario saber cuántos eventos de fuente se generaron en cada corrida (se asume que cada corrida tiene el mismo nps).


