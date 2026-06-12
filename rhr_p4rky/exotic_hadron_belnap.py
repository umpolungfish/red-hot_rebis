# p4ramill_py/exotic_hadron_belnap.py
# Python mirror of Imscribing/Paraconsistent/ExoticHadronBelnap.lean
# Author: Lando ⊗ ⊙perator

from dataclasses import dataclass
from typing import Optional, Set, Tuple, List, Union
from quark_belnap import ColorState, QuarkState, anti_color, color_join
from orbital_belnap import OrbitalState
from hadron_belnap import Meson, Baryon

# === §1 GLUEBALL ===
class GluonColor:
    RG = "rg"
    RB = "rb"
    GR = "gr"
    GB = "gb"
    BR = "br"
    BG = "bg"
    RRDD = "rrdd"
    BBRD = "bbrd"

    ALL = {RG, RB, GR, GB, BR, BG, RRDD, BBRD}

@dataclass
class Glueball:
    gluons: Set[str]
    
    def __post_init__(self):
        assert len(self.gluons) >= 2, "Glueball must have >= 2 gluons"
    
    def depair(self):
        return (self, self)
    
    @staticmethod
    def pair(g1, g2):
        merged = g1.gluons | g2.gluons
        if len(merged) >= 2:
            return Glueball(gluons=merged)
        return None

def test_glueball():
    g = Glueball(gluons={GluonColor.RG, GluonColor.GR})
    d1, d2 = g.depair()
    result = Glueball.pair(d1, d2)
    assert result == g, f"Frobenius failed: {result} != {g}"
    print("  Glueball Frobenius: OK")

# === §2 TETRAQUARK ===
@dataclass
class Tetraquark:
    q1: QuarkState
    q2: QuarkState
    aq1: QuarkState
    aq2: QuarkState
    
    def __post_init__(self):
        assert self.aq1.color == anti_color(self.q1.color), "aq1 must be anti-color of q1"
        assert self.aq2.color == anti_color(self.q2.color), "aq2 must be anti-color of q2"
        total = color_join(
            color_join(self.q1.color, self.q2.color),
            color_join(self.aq1.color, self.aq2.color)
        )
        assert total == ColorState.White, f"Tetraquark not white: total={total}"
    
    def depair(self):
        return ((self.q1, self.aq1), (self.q2, self.aq2))
    
    @staticmethod
    def pair(p1, p2):
        q1, aq1 = p1
        q2, aq2 = p2
        if aq1.color != anti_color(q1.color):
            return None
        if aq2.color != anti_color(q2.color):
            return None
        total = color_join(
            color_join(q1.color, q2.color),
            color_join(aq1.color, aq2.color)
        )
        if total != ColorState.White:
            return None
        return Tetraquark(q1=q1, q2=q2, aq1=aq1, aq2=aq2)

def test_tetraquark():
    q1 = QuarkState(color=ColorState.Red, spin=OrbitalState.spinUp)
    q2 = QuarkState(color=ColorState.Green, spin=OrbitalState.spinDown)
    aq1 = QuarkState(color=anti_color(ColorState.Red), spin=OrbitalState.empty)
    aq2 = QuarkState(color=anti_color(ColorState.Green), spin=OrbitalState.empty)
    t = Tetraquark(q1=q1, q2=q2, aq1=aq1, aq2=aq2)
    d1, d2 = t.depair()
    result = Tetraquark.pair(d1, d2)
    assert result == t, f"Frobenius failed: {result} != {t}"
    print("  Tetraquark Frobenius: OK")

# === §3 PENTAQUARK ===
@dataclass
class Pentaquark:
    q1: QuarkState
    q2: QuarkState
    q3: QuarkState
    q4: QuarkState
    aq1: QuarkState
    
    def __post_init__(self):
        total = color_join(
            color_join(color_join(color_join(self.q1.color, self.q2.color), 
                                   self.q3.color), self.q4.color),
            self.aq1.color
        )
        assert total == ColorState.White, f"Pentaquark not white: total={total}"

# === RUN TESTS ===
if __name__ == "__main__":
    print("ExoticHadronBelnap tests:")
    test_glueball()
    test_tetraquark()
    print("All exotic hadron tests passed!")
