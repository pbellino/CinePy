
# Simulación de la distribución de alfa-Rossi (RAD) con tally F8 + GATES

Se simula la distribución de alfa-Rossi sin las coincidencias accidentales. MCNP hace el analisis de coincidencias por evento de fuente (fisión espontánea). Se utilizan muchas tallies F8 con GATES consecutivos, cada una de ellas es un bin de la distribucción.

La entrada de tallies de MCNP se escribe por separado y luego se llaman desde el archivo de entrada de MCNP.

## Contenidos

  * `genera_tallies_GATE.py` : Escribe las tallies consecutivas (alrededor de 100) con el mismo gate-width (GW) y distintos pre-delay (PD). Las tallies generadas se escriben en el archivo `solo_tallies`.

  * `test_F8_RAD.i` : Archivo de entrada de MCNP

  * `lee_F8_tally_RAD.py` : Script para leer la tally fluctuation charts del archivo de salida de MCNP.

  * `RAD_from_PTRAC_Listmode.py` : Con el objetivo de comprobar la forma en que MCNP calcula la RAD, también se obtienen los tiempos de captura en el detector (Listmode) utilizando la opción PTRAC. Este script lee el archivo binario generado por la PTRAC, y calcula la distribución de alfa-Rossi por historias (es decir, implícitamente eliminando las coincidencias accidentales para poder comparar con los resultados de la F8+GATES). 

## Comparación

  Al ejecutar el script `RAD_from_PTRAC_Listmode.py` se obtiene la comparación entre utilizar la PTRAc y las tallies F8.

  La comparación debe hacerse teniendo en cuenta que:

    1) La PTRAC tiene como salida el tiempo de captura desde el evento de fuente, no del tiempo global. En este caso, esto no es un problema porque la comparación se hace por historias (debido a que el tally F8 así lo hace). 

    2) El método que utiizo para generar la RAD a partir de los datos en modo lista no es exactamente igual a la forma en que MCNP calcula la RAD con las tallies F8. Yo sólo utilizo todos los triggers que abran una ventana temporal de hasta `dtmax_s`, es decir, si hay un pulo por el final de la medición, éste no será tomado como trigger porque la medición se cortará antes de alcanzar el `dtmax_s`. Esto lo hago para que cada bin de la RAD tenga la misma cantidad de triggers (de lo contrario habría que normalizar cada bin por separado). Ver el ejemplo en Resultados para que se entienda mejor.

    Por otro lado, cuando MCNP calcula la RAD, no tiene en cuenta eso y utiliza todos los pulsos como triggers. Habría que analizar esto con más detalle para despueś poner la normalización correcta en la RAD.


### Resultados

  Cuando se ejecuta `RAD_from_PTRAC_Listmode.py` se obtiene:

```
--------------------------------------------------
RAD con PTRAC sin accidentales: 
         [1 2 1 0 0 0 0 1 1 0]
--------------------------------------------------
RAD con F8 + GATES: 
         [1 2 1 0 0 0 0 1 2 0]
--------------------------------------------------

```

La diferencia en el bin #9 se debe a lo mencionado antes. En particular, si se miran los tiempos de la primer historia:

```
[  0.00000000e+00   4.33349609e-11   2.10132599e-10   1.80074692e-09  2.61603355e-09]

```

Cuando se analiza al pulso #4, vemos que el pulso siguiente está separado en un instante de 0.8159e-9 s. Como el dtmax_s que yo elegí es 1e-9 segundos. En mi algoritmo yo no tomo este pulso como trigger pues la medición se corta antes. En cambio, MCNP sí lo cuenta, y como dt_s=0.1e-9 s, el pulso siguiente caerá en el bin #9. Por esta razón se encuentra la discrepancia.

En general, la discrepancia tiene que ser despreciable si se toman muchas historias. 

