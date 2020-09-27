#!/bin/bash

PTRAC=$1".p"
OUT=$1".o"

echo "Cantidad de capturas:"
grep " 5000 " $PTRAC | wc -l

echo "Cantidad de sup. cruzadas:"
grep " 3000 " $PTRAC | wc -l

echo "Cantidad de historias:"
grep " 9000 " $PTRAC | wc -l

echo "De acuerdo a " $OUT
grep -A 1 "ascii" $OUT

