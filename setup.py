"""setup.py — Red-Hot Rebis Integrated Imscribing Grammar Toolchain"""
from setuptools import setup, find_packages

setup(
    name="red-hot-rebis",
    version="1.0.0",
    description="Integrated Imscribing Grammar toolchain: serpentrod ⊗ ch3mpiler ⊗ pipeline ⊗ gene_imscriber",
    author="Lando ⊗ ⊙perator",
    author_email="mrnob0dy666@devilsdevice",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "shared": ["IG_catalog.json"],
    },
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "rebis=rebis:main",
        ],
    },
    install_requires=[
        "numpy>=1.24",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
