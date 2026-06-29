"""
iupac_resolver.py — Deterministic IUPAC → SMILES conversion via OPSIN.

OPSIN (Open Parser for Systematic IUPAC Nomenclature) is a Java library
that parses IUPAC chemical names to SMILES deterministically — no web
service needed. It handles systematic IUPAC names, not trivial names.

Usage:
    from iupac_resolver import iupac_to_smiles
    smiles = iupac_to_smiles("2-acetyloxybenzoic acid")
    # returns "CC(=O)Oc1ccccc1C(=O)O"

Author: Lando⊗⊙perator
"""
import subprocess
import os
import tempfile
import re
from typing import Optional
from shared.rich_output import *


OPSIN_JAR = os.path.join(os.path.dirname(__file__), "ext", "opsin-cli.jar")

# Fallback lookup for common trivial names OPSIN won't parse
# These are names where the IUPAC systematic name differs from common usage
TRIVIAL_NAME_MAP = {
    "aspirin": "2-acetyloxybenzoic acid",
    "acetone": "propan-2-one",
    "benzene": "cyclohexa-1,3,5-triene",
    "toluene": "methylbenzene",
    "xylene": "dimethylbenzene",
    "phenol": "hydroxybenzene",
    "aniline": "aminobenzene",
    "styrene": "ethenylbenzene",
    "naphthalene": "bicyclo[4.4.0]deca-1,3,5,7,9-pentaene",
    "pyridine": "azabenzene",
    "furan": "oxacyclopenta-2,4-diene",
    "thiophene": "thiacyclopenta-2,4-diene",
    "pyrrole": "1H-pyrrole",
    "imidazole": "1H-imidazole",
    "pyrimidine": "1,3-diazabenzene",
    "purine": "7H-purine",
    "indole": "1H-indole",
    "quinoline": "1-benzazabenzene",
    "isoquinoline": "2-benzazabenzene",
    "chloroform": "trichloromethane",
    "formaldehyde": "methanal",
    "acetaldehyde": "ethanal",
    "acetic acid": "ethanoic acid",
    "ethanol": "ethyl alcohol",
    "methanol": "methyl alcohol",
    "glycerol": "1,2,3-trihydroxypropane",
    "urea": "carbamide",
    "glucose": "2,3,4,5,6-pentahydroxyhexanal",
    "fructose": "1,3,4,5,6-pentahydroxyhexan-2-one",
    "sucrose": "2,3,4,5,6-pentahydroxy-6-(hydroxymethyl)oxan-2-yl]oxane-3,4,5-triol",
    "ethylene glycol": "ethane-1,2-diol",
}

def normalize_name(name: str) -> str:
    """Normalize a chemical name for OPSIN parsing.
    
    - Strips leading/trailing whitespace
    - Removes extra whitespace
    - Handles common abbreviations
    """
    name = name.strip()
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name)
    # Check trivial name map
    key = name.lower()
    if key in TRIVIAL_NAME_MAP:
        return TRIVIAL_NAME_MAP[key]
    return name


def iupac_to_smiles(name: str, timeout: int = 30) -> Optional[str]:
    """Convert an IUPAC name to SMILES using OPSIN (deterministic, no web).
    
    Args:
        name: IUPAC chemical name (systematic preferred; trivial names
              may fail and are resolved via TRIVIAL_NAME_MAP fallback)
        timeout: seconds to wait for OPSIN
    
    Returns:
        SMILES string, or None if parsing failed
    """
    if not os.path.isfile(OPSIN_JAR):
        raise FileNotFoundError(
            f"OPSIN JAR not found at {OPSIN_JAR}. "
            "Download from https://github.com/dan2097/opsin/releases"
        )
    
    normalized = normalize_name(name)
    
    try:
        proc = subprocess.run(
            ["java", "-jar", OPSIN_JAR],
            input=normalized.encode("utf-8"),
            capture_output=True,
            timeout=timeout,
        )
        stdout = proc.stdout.decode("utf-8").strip()
        stderr = proc.stderr.decode("utf-8").strip()
        
        # OPSIN outputs SMILES on the first line if successful
        # If it fails, it prints an error message
        if stdout and not stdout.startswith("Run the jar"):
            # Take first non-empty, non-help line
            for line in stdout.split("\n"):
                line = line.strip()
                if line and not line.startswith("Run the jar") and not line.startswith("Enter"):
                    return line
        
        # If name contains trivial name markers, try resolving via PubChem
        # as fallback for names OPSIN genuinely can't handle
        return None
        
    except subprocess.TimeoutExpired:
        return None
    except subprocess.CalledProcessError:
        return None


def batch_iupac_to_smiles(names: list[str], timeout_per: int = 15) -> dict[str, Optional[str]]:
    """Convert multiple IUPAC names to SMILES.
    
    Args:
        names: list of IUPAC names
        timeout_per: seconds per name
    
    Returns:
        dict mapping each name to its SMILES or None
    """
    results = {}
    for name in names:
        results[name] = iupac_to_smiles(name, timeout=timeout_per)
    return results


if __name__ == "__main__":
    # Quick test
    tests = [
        "aspirin",
        "2-acetyloxybenzoic acid",
        "acetic acid",
        "ethanol",
        "propan-2-one",
        "3-(2,3,4,5-tetrahydropyridin-6-yl)pyridine",
    ]
    for t in tests:
        s = iupac_to_smiles(t)
        info_line(f"  {t:45s} → {s or 'FAILED'}")
