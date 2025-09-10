#!/bin/bash


FILES=(reactimeter direct_kinetic_solver)

for file in "${FILES[@]}"; do
    cat > setup.py << EOF
from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "$file",  # Name of the compiled module
        ["$file.pyx"], # Nombre del archivo .pyx
        # include_dirs=[numpy.get_include()],  # NumPy headers
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        extra_compile_args=["-O3", "-ffast-math"],  # Optimization flags
        extra_link_args=['-lm'],
    )
]

setup(
    #name="reactimetro",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'language_level': 3,
        }
    ),
    zip_safe=False,
)

EOF

    python3 setup.py build_ext --inplace
    rm ${file}.c
done

rm -fr build setup.py

