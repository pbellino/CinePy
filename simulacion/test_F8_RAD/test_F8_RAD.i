Fuente quasi-puntual de Cf252 inmersa en esfera de B10
c
c
c
100 1  -2.0        -1000   imp:n=1    $ Fuente Cf252
102 2  -10.0  1000 -1001   imp:n=1    $ Detector
103 0         1001         imp:n=0    $ Exterior

1000 SO  0.0001       $ Esfera para fuente
1001 SO  2.50         $ Esfera para detector

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
c PTRAC para debuggear 
c ***************************************************
c Recordar asociar el tally con capturas totales sin GATE
c
PTRAC buffer=1000 file=asc write=all tally=0008 event=cap value=0 type=n max=2e9 filter=102,icl
c
c ----------------------------------------
c Definición de las tallies con GATE
c ----------------------------------------
FC0008 Capturas en He3 - Sin GATE
F0008:n 102
FT0008 CAP 5010 3006 
c
FC0018 Capturas en He3 - PD=0.00e+00s GW=1.0e-10s
F0018:n 102
FT0018 CAP 5010 3006 GATE 0.0 0.01
c
FC0028 Capturas en He3 - PD=1.00e-10s GW=1.0e-10s
F0028:n 102
FT0028 CAP 5010 3006 GATE 0.01 0.01
c
FC0038 Capturas en He3 - PD=2.00e-10s GW=1.0e-10s
F0038:n 102
FT0038 CAP 5010 3006 GATE 0.02 0.01
c
FC0048 Capturas en He3 - PD=3.00e-10s GW=1.0e-10s
F0048:n 102
FT0048 CAP 5010 3006 GATE 0.03 0.01
c
FC0058 Capturas en He3 - PD=4.00e-10s GW=1.0e-10s
F0058:n 102
FT0058 CAP 5010 3006 GATE 0.04 0.01
c
FC0068 Capturas en He3 - PD=5.00e-10s GW=1.0e-10s
F0068:n 102
FT0068 CAP 5010 3006 GATE 0.05 0.01
c
FC0078 Capturas en He3 - PD=6.00e-10s GW=1.0e-10s
F0078:n 102
FT0078 CAP 5010 3006 GATE 0.06 0.01
c
FC0088 Capturas en He3 - PD=7.00e-10s GW=1.0e-10s
F0088:n 102
FT0088 CAP 5010 3006 GATE 0.07 0.01
c
FC0098 Capturas en He3 - PD=8.00e-10s GW=1.0e-10s
F0098:n 102
FT0098 CAP 5010 3006 GATE 0.08 0.01
c
FC0108 Capturas en He3 - PD=9.00e-10s GW=1.0e-10s
F0108:n 102
FT0108 CAP 5010 3006 GATE 0.09 0.01
c
c Fin de las tallies con gate
c ----------------------------------------
