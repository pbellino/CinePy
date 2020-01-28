F8 CAP con GATE infinito
========================

Archivos para entender cómo funciona la opción CAP + GATE utilizando un tally F8.

Para comparar, también se calcula el modo lista con PTRAC.

Valores de referencia
---------------------

En la simulación del ejemplo, se crean 5 eventos de fisiones espontáneas en la fuente.

Los datos que me interesan de salida del archivo `test_F8_RAD.out` son:

```
 source                  16        escape                   2    
 nucl. interaction        0        energy cutoff            0    
 particle decay           0        time cutoff              0    
 weight window            0        weight window            0    
 cell importance          0        cell importance          0    
 weight cutoff            0        weight cutoff            0    
 e or t importance        0        e or t importance        0    
 dxtran                   0        dxtran                   0    
 forced collisions        0        forced collisions        0    
 exp. transform           0        exp. transform           0    
 upscattering             0        downscattering           0    
 photonuclear             0        capture                 14    
 (n,xn)                   0        loss to (n,xn)           0    
 prompt fission           0        loss to fission          0    
 delayed fission          0        nucl. interaction        0    
 prompt photofis          0        particle decay           0    
 tabular boundary         0        tabular boundary         0    
 tabular sampling         0        elastic scatter          0    
     total               16            total               16    

```

Y las 14 capturas se producen en:

```
      cell     cell   nuclides     atom       total    wgt. lost   wgt. gain  
     index     name            fraction  collisions   to capture  by fission  

         1      100  98252.80c 1.00E+00           0   0.0000E+00  0.0000E+00  

         2      102   5010.80c 5.00E-01          34   6.8750E-01  0.0000E+00  
                      3006.80c 5.00E-01          19   1.8750E-01  0.0000E+00  

              total                              53   8.7500E-01  0.0000E+00  

```

Normalizando con lo 16 neutrones de fuente, se obtienen que 11 fueron capturados en 10B y 3 en 6Li.


Para saber los tiempos de esas capturas leo la salida de PTRAC:

```
         1    1.61257E-02     102       5   98252
         1    3.28054E-02     102       4   98252
         1    1.17922E-02     102       3   98252
         1    1.91867E-01     102       2   98252
         1    2.73396E-01     102       1   98252
         2    2.63435E-02     102       2   98252
         2    1.65109E-01     102       1   98252
         3    4.23965E-02     102       4   98252
         3    3.73567E-01     102       3   98252
         3    1.12488E-01     102       2   98252
         3    1.31614E-01     102       1   98252
         4    0.00000E+00       0       3
         4    3.34260E-01     102       2   98252
         4    2.85168E-02     102       1   98252
         5    0.00000E+00       0       2
         5    1.26235E-01     102       1   98252

```

La primer file el el número de historia, la seguna el tiempo (en shakes) y la tercera la celda. Un cero en la celda indica que esa partícula escapó.

De esa tabla se ve que en la primer historia (fisión espontánea) se crearon 5 neutrones y todos ellos fueron capturados en el detector. En la historia 5 se crearon dos neutrones, uno se escapó y otro fue capturado. Esto es importante para luego entender cómo calcula el tally F8 con GATE.


Tally F8 con GATE infinito
--------------------------

El resultado de utilizar F8 con la opción CAP y un GATE infinito es:

```
 neutron captures on   5010   3006

 time gate:  predelay =  0.0000E+00     gate width =  1.0000E+30

        pulses           occurrences      occurrences   
       in gate  histogram  by number        by weight   

 captures =  0          5          0      0.00000E+00   
 captures =  1          4          4      2.50000E-01   
 captures =  2          2          4      2.50000E-01   
 captures =  3          2          6      3.75000E-01   
 captures =  4          1          4      2.50000E-01   

    total              14         18      1.12500E+00   


```

1) Con este tally sólo se obtienen las coincidencias reales (la parte correlacionada de la distribución de alfa-Rossi). Esto es así porque los aportes al tally se hacen por evento de fuente. Es decir, en el gate sólo se cuentan las capturas producidos por neutrones de la misma historia de la captura que produce el trigger. No se mezclan historias, por lo tanto no hay coincidencias accidentales.

2) La forma de contar es la siguiente:

    a) Antes se vio que la historia # 1 produjo 5 capturas en el detector. Cada una de esas capturas sirvió como trigger de un GATE infinito. Entonces:

	- 1er trigger: 4 capturas
	- 2do trigger: 3 capturas
	- 3er trigger: 2 capturas
	- 4to trigger: 1 captura
	- 5to trigger: 0 captura

       Por lo tanto, cada trigger sumó 1 a cada captura en el histograma

    b) Se repite lo mismo para las cuatro historias restante. La historia #2 tiene dos capturas, por lo tanto el análisis sería:
	
	- 1er trigger: 1 captura
	- 2do trigger: 0 captura

      Juntando todo:

	|historia	|captura=0	|captura=1	|captura=2	|captura=3	|captura=4|
	| :-----------: | :-----------: | :-----------: | :-----------: | :-----------: | :-----: |
	|1		|1		|1		|1		|1		|1        |
	|2		|1		|1		|0		|0		|0        |
	|3              |1		|1		|1		|1		|0        |
	|4		|1		|1		|0		|0		|0        |
	|5		|1		|0		|0		|0		|0        |

     Sumando todas las historias se obtiene la columna "histogram" que muestra la salia del tally.

   c) Por la forma de contar, la suma de capturas=0 debe coincidir con la cantidad de historias (eventos de fuente) que tuvieron al menos una captura en el detector (en el ejemplo fueron todas)

   d) Como toda captura en el detector abre un GATE y aporta algo a algún bin (cantidad de capturas en el GATE), entonces la suma de todos los valores obtenidos en el histograma debe coincidir con la cantidad total de neutrones capturados en el detector. En el ejemplo es 5 + 4 + 2 + 2 + 1 = 14.

   e) En todo esto los tiempos no intervienen porque se utilizó un GATE infinito, cada vez que se abría un GATE se sabía de antemano que el resto de los neutrones de dicha historia iban a caer dentro del GATE y contribuir al tally.				
