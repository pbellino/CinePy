Fuente quasi-puntual de Cf252 inmersa en esfera de B10
c
c
c
100 1  -2.0        -1000   imp:n=1    $ Fuente Cf252
102 2  -10.0  1000 -1001   imp:n=1    $ Detector
103 0         1001         imp:n=0    $ Exterior

1000 SO  0.0001       $ Esfera para fuente
1001 SO  2.00         $ Esfera para detector

M1    98252    1      $ Cf252
M2    5010     0.5    $ B10
      3006     0.5    $ Li6
c ***************************************************
c FUENTE
c ***************************************************
c Fuente puntual, debe ubicarse en una celda con un
c nucleido que posea datos de fisiones espontáneas
c Se lo distribuye uniformemente en el tiempo
c
SDEF  par=SF  pos= 0 0 0 tme=d1
SI1  0    100.0e8    $ Durante 100 segundos
SP1  0    1
c ***************************************************
MODE n
c Conviene poner el t_maximo como el tiempo de la medición
c Debe coincidir con el tiempo máximo en que se muestrea
c la fuente
CUT:n 100.0e8 J 0 0
c CUT:n 100.0e8 
NPS 5
PRINT
c ***************************************************
c
c ----------------------------------------
c Definición de las tallies con GATE
c ----------------------------------------
FC0008 Capturas en He3 - PD=0.00e+00s GW=1.0e-10s
F0008:n 102
c FT0008 CAP 5010 3006 GATE 0 1000000
FT0008 CAP -21 -12  5010 3006 GATE 0 1e31
c
c Fin de las tallies con gate
c ----------------------------------------
