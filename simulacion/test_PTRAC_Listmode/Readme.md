Ejemplo mínimo para usar PTRAC
==============================

De los archivos de salida se tiene:

Se generan 5 fisiones espontáneas y se crean 16 neutrones en total.

Neutrones que escapan : 5
Neutrones capturados en detector : 11
	- Capturados en 10B : 9
 	- Capturados en 6Li : 2

Trato de ver cómo se refleja esto en los archivos PTRAC


1) Utilizando "event=TER"
-------------------------

Permite distinguier el tipo de evento que finaliza el neutrón (escape o captura)

No puedo hacer que distinga el nucleido que genera la captura. No sería importante si
se modela un detector típico de neutrones (salvo que exista captura parásita).

Se debe escribir en binario para tener tiempos con resolución de los us.

Los tiemops son globales.

2) Utilizando "event=CAP"
------------------------

Cambia el formato de escritura del archivo PTRAC (ver Nota 3 en la pg 400 del manual de MCNP).

MCNPTools no lee el archivo binario.

El archivo ASCII tiene resolución temporal de los ms.

EL tiempo se cuenta desde el evento de fuente, se debe corregir.


Conclusiones (parciales)
------------------------

Usar "event=TER" y tener cuidado en que sólo se escriban eventos que dejen señal en el detector.

Para usar "event=CAP" hay dos opciones:
	1) Modificar el fuente de ptrac.F90 para aumentar la precisión y sumarle el tiempo de fuente (obligaría a recompilar MCNP)
	2) Tratar de leer el archivo binario. Tratar de sacar información sobre el tiempo de la fuente y corregir.


