"""
generators.py — Dataset generator base classes
Author: Lando
"""
from __future__ import annotations
import json, os, sys, math, random, hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

# Every generator stamps its output with the chain's closure verdict, so the
# check it calls has to be in scope here.
from clink.chain import (
    clink_frobenius_closed,
    compute_c_score_from_tuple,
    compute_tier_from_tuple,
)

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

