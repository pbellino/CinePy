# Simulación para analiar la validez del método


## Objetivo

Analizar si se obtienen los mismos resultados al aplicar el método de alfa Rossi a la señal de neutrones (térmicos) detectados que a una señal de fotones de 2.22MeV de la reacción H(n,g)D.


## Modelo

    - Una fuente cuasi puntual de $^{252}$Cf
    - Una esfera de agua rodeando la fuente
    - Un cascarón esférico vacío, simulando el detector de fotones
    - Un cascarón esférico con He3, simulando al detector de neutrones


## Procedimiento
    
    - Se simulan neutrones y fotones
    - Se modela la fuente de californio con emisión de fotones y neutrons correlacionados
    - Para medir los fotones, se cuentan los que cruzan la superficie del detector, bineando en energía y seleccionando el bin que contenga a 2.22MeV
    - Para medir los neutrones se utiliza F8 + FT CAP
    - Se debe utilizar PTRAC tanto para neutrones como para los gammas, por lo tanto se debe correr el mismo problema dos veces (sólo una PTRAC se puede utilizar por corrida).


## Observaciones

    - Se exageró la densidad del He3 para obtener mayor eficiencia. Esto podría hacer que muchos neutrones se moderen dentro del detector y la comparación no será válida (TODO: modificarlo)


