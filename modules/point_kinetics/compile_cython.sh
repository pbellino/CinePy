#!/bin/bash

# Auxiliary script used for compiling .pyx files with cython
# Also: copy .so files and delete temporal folders


FILES=(reactimeter direct_kinetic_solver)

for file in "${FILES[@]}"; do
    cat > setup.py << EOF
from distutils.core import setup
from Cython.Build import cythonize


setup(
    ext_modules = cythonize("${file}.pyx")
)
EOF

    python3 setup.py build_ext --inplace
    cp CinePy/modules/point_kinetics/${file}*.so ./${file}.so
    rm ${file}.c
done

rm -fr build CinePy setup.py

