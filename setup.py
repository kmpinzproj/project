from setuptools import setup, find_packages

setup(
    name="KreatorBram",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "PySide6",
        "reportlab",
        "trimesh",
        "matplotlib",
        "reportlab",
        "opencv-python",
        "PyOpenGL",
        "pywavefront"
    ],
    entry_points={
        'console_scripts': [
            'kreator-bram=application.main:main',  # Funkcja `main` w `application/main.py`
        ]
    },
)
