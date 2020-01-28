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
