from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "reactimeter",  # Name of the compiled module
        ["reactimeter.pyx"],   # Your .pyx file
        include_dirs=[numpy.get_include()],  # NumPy headers
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        extra_compile_args=["-O3", "-ffast-math"],  # Optimization flags
    )
]

setup(
    name="reactimetro",
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
