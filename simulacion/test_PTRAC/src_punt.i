Fuente quasi-puntual de Cf252 inmersa en esfera de B10
c
c
c
100 1  -2.0        -1000   imp:n=1    $ Fuente Cf252
102 2  -10.0  1000 -1001   imp:n=1    $ Detector
103 0         1001         imp:n=0    $ Exterior

1000 SO  0.0001       $ Esfera para fuente
1001 SO  50.00        $ Esfera para detector

M1    98252    1    $ Cf252
M2    5010     1    $ B10
c ***************************************************
c FUENTE
c ***************************************************
c Fuente puntual, debe ubicarse en una celda con un
c nucleido que posea datos de fisiones espontáneas
c Se lo distribuye uniformemente en el tiempo
c
SDEF  par=SF  pos= 0 0 0  tme=d1
SI1  0    100.0e8    $ Durante 100 segundos
SP1  0    1
c ***************************************************
c PTRAC
c ***************************************************
c Si se escribe en formato ascii (file=asc) el formato
c de tiempo sólo llega a los milisegundos. Es necesario
c escribir en formato binario (file=bin) para tener la
c resolución completa del tiempo.
c
PTRAC buffer=1000 file=bin write=all event=src,bnk,ter type=n max=2e9
c ***************************************************
c ***************************************************
MODE n
CUT:n 1e100 0.0 0 0
NPS 5
PRINT


