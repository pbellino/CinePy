Fuente quasi-puntual de Cf252 inmersa en esfera de B10
c
c
c
100 1  -2.0        -1000   imp:n=1    $ Fuente Cf252
102 2  -1.0   1000 -1001   imp:n=1    $ Moderador
103 3  -10.0  1001 -1002   imp:n=1    $ Detector
104 0         1002         imp:n=0    $ Exterior

1000 SO  0.0001       $ Esfera para fuente
1001 SO  15.00         $ Esfera para moderador
1002 SO  15.50        $ Esfera para detector

M1    98252     1     $ Cf252
M2     1001     2     $ H
       8016     1     $ O
M3     5010     1     $ B10
c ***************************************************
c FUENTE
c ***************************************************
c Fuente puntual, debe ubicarse en una celda con un
c nucleido que posea datos de fisiones espontáneas
c Se lo distribuye uniformemente en el tiempo
c
SDEF  par=SF  pos= 0 0 0 $  tme=d1
c SI1  0    100.0e8    $ Durante 100 segundos
c SP1  0    1
c ***************************************************
c PTRAC
c ***************************************************
c Si se escribe en formato ascii (file=asc) el formato
c de tiempo sólo llega a los milisegundos. Es necesario
c escribir en formato binario (file=bin) para tener la
c resolución completa del tiempo.
c
c Se agregan eventos de fuente para comparar los tiempos
c No es necesario, sólo para debuggear (se comenta filtro de celda)
PTRAC buffer=1000 file=bin write=all tally=8 event=cap value=0 type=n max=2e9 $ filter=103,icl
c ***************************************************
MODE n
c Analizar si conviene el tiempo máximo
CUT:n 100.0e10 J 0 0
F8:n 103
FT8 CAP -1 -1 5010
NPS 1e6
PRINT


