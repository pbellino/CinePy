
## Compilar el reactímetro con cython

La función `reactimetro()` dentro del archivo `reactimeter.pyx` está optimizada con cython.

Se debe compilar para ser utilizada (no se hace control de cambios sobre el archivo compilado).

La compilación se hace utilizano el archivo `setup.py`:

```
python3 setup.py build_ext --inplace

```

Se genera una carpeta `modules` dentro de la cual hay un archivo .so

Se debe copiar y renombrar el archivo a esta carpeta como `reactimeter.so`

Luego las carpetas generadas se pueden eliminar. 
