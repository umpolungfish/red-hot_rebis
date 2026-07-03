"""setup.py — Red-Hot Rebis (delegates to pyproject.toml)

Callable from anywhere via:  pip install -e .  then  rebis.<x> <command>

Usage:
  pip install -e .                    # Install from anywhere
  rebis status                        # Package status
  rebis.materials list                # Materials design tools
  rebis.ch3mpiler forward <SMILES>    # Forward synthesis
  rebis.p4ra genetics                 # Genetic code B4 lattice
  rebis.verify                        # Frobenius closure check
  python3 -c 'import rebis; rebis.p4ra.Belnap.T'
"""
from setuptools import setup, find_packages

setup(
    name="red-hot-rebis",
    version="3.0.0",
    description="Red-Hot Rebis — Integrated Imscribing Grammar toolchain",
    author="Lando ⊗ ⊙perator",
    author_email="mrnob0dy666@devilsdevice",
    packages=find_packages(include=[
        "rebis", "rebis.*",
        "rhr_p4rky", "rhr_p4rky.*",
        "shared", "shared.*",
        "ch3mpiler", "ch3mpiler.*",
        "clink", "clink.*",
        "materials", "materials.*",
        "biology", "biology.*",
        "serpentrod", "serpentrod.*",
        "imas", "imas.*",
        "pipeline", "pipeline.*",
        "cdxml", "cdxml.*",
        "scripts", "scripts.*",
        "therapeutics", "therapeutics.*",
        "unified_demo", "unified_demo.*",
        "gene_imscriber", "gene_imscriber.*",
        "imasm_iterator", "imasm_iterator.*",
        "alchemical_bridge", "alchemical_bridge.*",
        "Ars_Therapeutica", "Ars_Therapeutica.*",
    ]),
    include_package_data=True,
    package_data={
        "shared": ["*.json"],
        "*": ["*.json", "*.txt", "*.csv", "*.fasta", "*.pdb"],
    },
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "rebis=rebis.cli:main",
            "rebis.materials=rebis.materials:main",
            "rebis.ch3mpiler=rebis.ch3mpiler:main",
            "rebis.sidechain=rebis.sidechain:main",
            "rebis.clink=rebis.clink:main",
            "rebis.p4ra=rebis.p4ra:main",
            "rebis.biology=rebis.biology:main",
            "rebis.therapeutics=rebis.therapeutics:main",
            "rebis.serpentrod=rebis.serpentrod:main",
            "rebis.pipeline=rebis.pipeline:main",
            "rebis.gene=rebis.gene:main",
            "rebis.alchemy=rebis.alchemy:main",
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