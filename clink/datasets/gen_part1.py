#!/usr/bin/env python3
"""Build the complete generators.py with all 9 layers."""
import os, json, textwrap

PY = "/home/mrnob0dy666/red-hot_rebis/clink/datasets/generators.py"

def write(s):
    with open(PY, 'a') as f:
        f.write(s + '\n')

# Reset
open(PY, 'w').write('"""\ngenerators.py — Physically actionable datasets\nAuthor: Lando (R) (O)perator\n"""\n')

write('''from __future__ import annotations
import json, os, sys, math, random, hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

@dataclass
class DatasetFile:
    filename: str; extension: str; content: str
    description: str; format_name: str; frobenius_hash: str = ""

@dataclass
class DatasetOutput:
    layer_idx: int; layer_name: str; layer_tier: str
    files: List[DatasetFile] = field(default_factory=list)
    structural_tuple: Dict[str,str] = field(default_factory=dict)
    frobenius_verified: bool = False
    generation_time: str = field(default_factory=lambda: datetime.now().isoformat())
    tool_bridges_used: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

class DatasetGenerator:
    layer_idx: int = -1
    def __init__(self):
        from clink.chain import clink_layer_tuple
        self.tup = clink_layer_tuple(self.layer_idx)
        name = getattr(self, "layer_name", str(self.layer_idx))
        self.output_dir = Path(__file__).parent / "output" / name.replace(" ","_")
    def generate(self, design_data=None) -> DatasetOutput:
        raise NotImplementedError
''')
