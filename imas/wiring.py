"""
wiring.py — Token Sequence → WiredGraph (Explicit Composition)
================================================================
Separates token PRESENTATION from COMPOSITION structure.  A single
token sequence can admit multiple valid WiredGraphs;  imscr_wiring()
is the standard normal form (scan L→R,  match FSPLIT/FFUSE by stack
depth,  assign EVALT as T-branch and EVALF as F-branch) — but the
grammar only requires port-type matching.  Any wiring that respects
the port-type constraints is grammatically valid.

Key insight:  the IG grammar's unit of study is the equivalence
class of token sequences that present the SAME composition,  and
separately the set of distinct compositions presentable by a given
token multiset.  The engine must not collapse these.

Author:  Lando⊗⊙perator
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Set, Optional, FrozenSet
from enum import Enum
import itertools

from imas.arranger import Token, TOKEN_NAMES, TOKEN_COUNT
from shared.rich_output import *


# ============================================================================
# PORT TYPES  —  the grammar's only structural wiring constraint
# ============================================================================

class PortType(Enum):
    """Port types for string-diagram composition.
    
    'o'  —  generic / object   (VINIT,  TANCH,  AFWD,  AREV,  CLINK,
                                  IMSCRIB,  FSPLIT output,  FFUSE input)
    'i'  —  identity / morphism (IMSCRIB internal,  CLINK internal)
    'T'  —  truth port          (EVALT passes only T;  TANCH-T side)
    'F'  —  false port          (EVALF passes only F;  TANCH-F side)
    'B'  —  paradox port        (ENGAGR emits B;  IFIX receives B)
    """
    O = "o"    # generic object
    I = "i"    # identity / morphism
    T = "T"    # truth
    F = "F"    # false
    B = "B"    # paradox / Belnap-both

# ============================================================================
# TOKEN PORT SIGNATURES  —  each token exposes typed input/output ports
# ============================================================================

@dataclass(frozen=True)
class PortSpec:
    """Input/output port specification for a single token."""
    inputs:  Tuple[PortType, ...]
    outputs: Tuple[PortType, ...]

# Each token's port signature.  FSPLIT has 1 input 'o',  2 outputs ('o','o').
# FFUSE   has 2 inputs ('o','o'),  1 output 'o'.
# EVALT   has 1 input 'o',  1 output 'T'.
# EVALF   has 1 input 'o',  1 output 'F'.
# ENGAGR  has 1 output 'B' (no input — generates paradox).
# IFIX    has 1 input 'B'  (receives paradox;  no output in standard model).
# FSPLIT is the only token with arity > 1 on output;  FFUSE on input.

TOKEN_PORT_SPEC: Dict[int, PortSpec] = {
    Token.VINIT:   PortSpec((),           (PortType.O,)),
    Token.TANCH:   PortSpec((PortType.O,), (PortType.T, PortType.F)),
    Token.AFWD:    PortSpec((PortType.O,), (PortType.O,)),
    Token.AREV:    PortSpec((PortType.O,), (PortType.O,)),
    Token.CLINK:   PortSpec((PortType.O, PortType.I), (PortType.O,)),
    Token.IMSCRIB: PortSpec((PortType.O,), (PortType.I,)),
    Token.FSPLIT:  PortSpec((PortType.O,), (PortType.O, PortType.O)),
    Token.FFUSE:   PortSpec((PortType.O, PortType.O), (PortType.O,)),
    Token.EVALT:   PortSpec((PortType.O,), (PortType.T,)),
    Token.EVALF:   PortSpec((PortType.O,), (PortType.F,)),
    Token.ENGAGR:  PortSpec((),           (PortType.B,)),
    Token.IFIX:    PortSpec((PortType.B,), ()),
}

# ============================================================================
# WIRED GRAPH DATA STRUCTURES
# ============================================================================

@dataclass(frozen=True)
class WiredNode:
    """A single token instance in the wired graph, with port connectivity."""
    token:      int              # 0-11 token index
    position:   int              # position in the original token sequence (0-based)
    inputs:     Tuple[Optional[int], ...]   # node_id of each input connection
    outputs:    Tuple[Optional[int], ...]   # node_id of each output connection
    frob_pair:  Optional[int] = None       # FSPLIT↔FFUSE; None for non-Frobenius

@dataclass(frozen=True)
class WiredGraph:
    """Explicit composition: nodes + port-type-constrained connections."""
    nodes:       Tuple[WiredNode, ...]
    token_seq:   Tuple[int, ...]       # original presentation
    n_nodes:     int

    @property
    def frobenius_pairs(self) -> Tuple[Tuple[int, int], ...]:
        """Return (split_idx, fuse_idx) for each matched FSPLIT/FFUSE pair."""
        pairs = []
        for n in self.nodes:
            if n.frob_pair is not None and n.token == Token.FSPLIT:
                pairs.append((n.position, n.frob_pair))
        return tuple(sorted(pairs))

    def _node_by_position(self, pos: int) -> Optional[WiredNode]:
        for n in self.nodes:
            if n.position == pos:
                return n
        return None

    @property
    def is_valid(self) -> bool:
        """Verify all port-type constraints are satisfied."""
        for n in self.nodes:
            spec = TOKEN_PORT_SPEC[n.token]
            for i, src_id in enumerate(n.inputs):
                if src_id is None:
                    continue
                src = self._node_by_position(src_id)
                if src is None:
                    return False
                src_spec = TOKEN_PORT_SPEC[src.token]
                out_idx = None
                for j, tgt_id in enumerate(src.outputs):
                    if tgt_id == n.position:
                        out_idx = j
                        break
                if out_idx is None or out_idx >= len(src_spec.outputs):
                    return False
                if spec.inputs[i] != src_spec.outputs[out_idx]:
                    return False
        return True

    def describe(self) -> str:
        """Human-readable description of the wiring."""
        lines = []
        for n in self.nodes:
            name = TOKEN_NAMES[n.token]
            ins = [str(x) if x is not None else "_" for x in n.inputs]
            outs = [str(x) if x is not None else "_" for x in n.outputs]
            pair = f" ⟷{n.frob_pair}" if n.frob_pair is not None else ""
            lines.append(f"  [{n.position}] {name:8s}  in={ins}  out={outs}{pair}")
        return "\n".join(lines)


    @property
    def composition_fingerprint(self) -> Tuple:
        """Fingerprint of the actual composition (not the token presentation)."""
        return (self.n_nodes, self.frobenius_pairs,
                tuple((n.token, n.position, n.frob_pair) for n in self.nodes))
# ============================================================================
# STANDARD WIRING:  imscr_wiring()  —  the normal-form convention
# ============================================================================

def imscr_wiring(token_seq: Tuple[int, ...]) -> WiredGraph:
    """Convert a token sequence to a WiredGraph using the standard convention.
    
    Convention (the "normal form"):
      1. Scan left to right.
      2. Match FSPLIT/FFUSE by stack depth — each FSPLIT pushes, each FFUSE
         pops the most recent unmatched FSPLIT.
      3. Within each FSPLIT/FFUSE block, assign EVALT to the first output
         port (T-branch) and EVALF to the second (F-branch) if both appear
         between the FSPLIT and its paired FFUSE.
      4. Linear connections: each node's output connects to the next node's
         input of matching port type, except across FSPLIT/FFUSE boundaries
         where branching and joining occur.
    
    This is the CONVENTION — not what the grammar requires.  The grammar
    only requires port-type matching ('o'→'o', 'T'→'T', 'F'→'F', 'B'→'B').
    Other valid wirings exist for the same token sequence.
    """
    n = len(token_seq)
    
    # Phase 1:  pair FSPLIT/FFUSE by stack depth
    frob_pairs: Dict[int, int] = {}  # split_pos → fuse_pos
    split_stack: List[int] = []
    for i, t in enumerate(token_seq):
        if t == Token.FSPLIT:
            split_stack.append(i)
        elif t == Token.FFUSE:
            if split_stack:
                split_pos = split_stack.pop()
                frob_pairs[split_pos] = i
    
    frob_reverse: Dict[int, int] = {v: k for k, v in frob_pairs.items()}
    
    # Phase 2:  build nodes
    nodes: List[WiredNode] = []
    
    for i, t in enumerate(token_seq):
        spec = TOKEN_PORT_SPEC[t]
        frob_pair: Optional[int] = None
        
        if t == Token.FSPLIT and i in frob_pairs:
            frob_pair = frob_pairs[i]
        elif t == Token.FFUSE and i in frob_reverse:
            frob_pair = frob_reverse[i]
        
        # Wire inputs
        inputs: List[Optional[int]] = [None] * len(spec.inputs)
        for inp_idx, inp_type in enumerate(spec.inputs):
            if t == Token.FFUSE and frob_pair is not None:
                split_pos = frob_pair
                branch_nodes = [nd for nd in nodes
                                if split_pos < nd.position < i
                                and nd.token != Token.FSPLIT]
                if inp_idx == 0 and len(branch_nodes) >= 1:
                    inputs[inp_idx] = _find_branch_end(branch_nodes, PortType.T, i)
                elif inp_idx == 1 and len(branch_nodes) >= 1:
                    inputs[inp_idx] = _find_branch_end(branch_nodes, PortType.F, i)
            else:
                for prev in reversed(nodes):
                    prev_spec = TOKEN_PORT_SPEC[prev.token]
                    for out_idx, out_type in enumerate(prev_spec.outputs):
                        if out_type == inp_type and prev.outputs[out_idx] is None:
                            inputs[inp_idx] = prev.position
                            break
                    if inputs[inp_idx] is not None:
                        break
        
        outputs: List[Optional[int]] = [None] * len(spec.outputs)
        nodes.append(WiredNode(
            token=t, position=i,
            inputs=tuple(inputs), outputs=tuple(outputs),
            frob_pair=frob_pair,
        ))
    
    # Phase 3:  back-fill outputs
    for ni, node in enumerate(nodes):
        outs = list(node.outputs)
        for out_idx, out_type in enumerate(TOKEN_PORT_SPEC[node.token].outputs):
            for nj in range(ni + 1, len(nodes)):
                next_node = nodes[nj]
                next_spec = TOKEN_PORT_SPEC[next_node.token]
                for inp_idx, inp_type in enumerate(next_spec.inputs):
                    if inp_type == out_type and next_node.inputs[inp_idx] == node.position:
                        outs[out_idx] = next_node.position
                        break
                if outs[out_idx] is not None:
                    break
        nodes[ni] = WiredNode(
            token=node.token, position=node.position,
            inputs=node.inputs, outputs=tuple(outs),
            frob_pair=node.frob_pair,
        )
    
    return WiredGraph(nodes=tuple(nodes), token_seq=token_seq, n_nodes=n)


def _find_branch_end(branch_nodes: List[WiredNode],
                     port_type: PortType, ffuse_pos: int) -> Optional[int]:
    """Find the branch-end node whose output port matches port_type."""
    for nd in reversed(branch_nodes):
        spec = TOKEN_PORT_SPEC[nd.token]
        for out_type in spec.outputs:
            if out_type == port_type:
                return nd.position
    if branch_nodes:
        return branch_nodes[-1].position
    return None

# ============================================================================
# ALL VALID COMPOSITIONS  —  enumerate the real compositional space
# ============================================================================

def all_frob_pairings(token_seq: Tuple[int, ...]) -> List[Dict[int, int]]:
    """Enumerate all valid FSPLIT/FFUSE pairings for a token sequence.

    A pairing is valid if:
      - Each FSPLIT pairs with exactly one FFUSE (and vice versa)
      - split_pos < fuse_pos for each pair (FSPLIT before FFUSE)
      - Pairs are properly nested or disjoint (no crossing — planarity)

    Returns all valid pairings.  For n FSPLITs and m FFUSEs, the number
    of valid pairings is the number of balanced parenthesizations that
    respect the token order.
    """
    split_positions = [i for i, t in enumerate(token_seq) if t == Token.FSPLIT]
    fuse_positions  = [i for i, t in enumerate(token_seq) if t == Token.FFUSE]
    
    n_splits = len(split_positions)
    n_fuses  = len(fuse_positions)
    
    if n_splits == 0 or n_fuses == 0:
        return [{}]
    
    # For each split, enumerate all later fuses it could pair with
    # respecting planarity (no crossing)
    results: List[Dict[int, int]] = []
    
    def backtrack(s_idx: int, used_fuses: Set[int], current: Dict[int, int]):
        if s_idx == n_splits:
            # Verify all fuses used (or accept partial)
            results.append(dict(current))
            return
        
        split_pos = split_positions[s_idx]
        # Find valid fuse positions: must be after split, not used, and
        # not crossing with prior pairs
        for f_idx, fuse_pos in enumerate(fuse_positions):
            if f_idx in used_fuses:
                continue
            if fuse_pos < split_pos:
                continue
            # Check planarity: no crossing with existing pairs
            crossing = False
            for sp, fp in current.items():
                # Crossing: sp < split_pos < fp < fuse_pos
                if sp < split_pos < fp < fuse_pos:
                    crossing = True
                    break
            if crossing:
                continue
            used_fuses.add(f_idx)
            current[split_pos] = fuse_pos
            backtrack(s_idx + 1, used_fuses, current)
            del current[split_pos]
            used_fuses.discard(f_idx)
    
    backtrack(0, set(), {})
    return results if results else [{}]


def all_branch_assignments(token_seq: Tuple[int, ...],
                           frob_pairs: Dict[int, int]) -> List[Dict[str, Tuple[int, ...]]]:
    """Enumerate all valid EVALT/EVALF branch assignments for given pairings.

    Within each FSPLIT/FFUSE block, EVALT and EVALF can be assigned to
    either the T-branch or the F-branch.  The grammar only requires that
    port types match — EVALT outputs 'T', EVALF outputs 'F' — so any
    assignment respecting these port types is grammatically valid.

    Returns a list of assignment dicts mapping:
      'T_branch_nodes'  → tuple of node positions on the T-branch (first output)
      'F_branch_nodes'  → tuple of node positions on the F-branch (second output)
    """
    if not frob_pairs:
        return [{'T_branch_nodes': (), 'F_branch_nodes': ()}]
    
    # For each FSPLIT/FFUSE block, find EVALT and EVALF positions within it
    blocks = []
    for split_pos, fuse_pos in sorted(frob_pairs.items()):
        nodes_inside = tuple(i for i in range(split_pos + 1, fuse_pos))
        evalt_inside = tuple(i for i in nodes_inside if token_seq[i] == Token.EVALT)
        evalf_inside = tuple(i for i in nodes_inside if token_seq[i] == Token.EVALF)
        # In standard wiring: EVALT→T-branch (output 0), EVALF→F-branch (output 1)
        # But we can swap them
        blocks.append({
            'split': split_pos, 'fuse': fuse_pos,
            'nodes': nodes_inside,
            'EVALT': evalt_inside, 'EVALF': evalf_inside,
        })
    
    results = []
    
    def assign_block(block_idx: int, current: Dict[str, List]):
        if block_idx == len(blocks):
            results.append({
                'T_branch_nodes': tuple(current['T']),
                'F_branch_nodes': tuple(current['F']),
            })
            return
        
        block = blocks[block_idx]
        # Option A: EVALT→T, EVALF→F (standard)
        t_branch_a = list(current['T']) + list(block['EVALT'])
        f_branch_a = list(current['F']) + list(block['EVALF'])
        assign_block(block_idx + 1, {'T': t_branch_a, 'F': f_branch_a})
        
        # Option B: EVALT→F, EVALF→T (cross-branch)
        t_branch_b = list(current['T']) + list(block['EVALF'])
        f_branch_b = list(current['F']) + list(block['EVALT'])
        assign_block(block_idx + 1, {'T': t_branch_b, 'F': f_branch_b})
    
    assign_block(0, {'T': [], 'F': []})
    return results


def all_valid_compositions(token_seq: Tuple[int, ...]) -> List[WiredGraph]:
    """Enumerate ALL grammatically valid WiredGraphs for a token sequence.

    This is the real compositional space — each result is a distinct
    morphism in the string-diagram category.  The standard imscr_wiring()
    is just one element of this set (the normal form).
    """
    # Step 1: enumerate FSPLIT/FFUSE pairings
    pairings = all_frob_pairings(token_seq)
    
    # Step 2: for each pairing, enumerate branch assignments
    # Step 3: build the WiredGraph for each combination
    results = []
    for pairs in pairings:
        if not pairs:
            # No Frobenius pairs — straightforward linear wiring
            results.append(_build_linear_wiring(token_seq))
        else:
            branch_assignments = all_branch_assignments(token_seq, pairs)
            for ba in branch_assignments:
                g = _build_wiring_with_assignment(token_seq, pairs, ba)
                if g.is_valid:
                    results.append(g)
    
    # Deduplicate on composition_fingerprint
    seen = set()
    unique = []
    for g in results:
        cfp = g.composition_fingerprint
        if cfp not in seen:
            seen.add(cfp)
            unique.append(g)
    
    return unique


def _build_linear_wiring(token_seq: Tuple[int, ...]) -> WiredGraph:
    """Build a linear (no Frobenius) wiring for a token sequence."""
    n = len(token_seq)
    nodes = []
    for i, t in enumerate(token_seq):
        spec = TOKEN_PORT_SPEC[t]
        # Determine input: connect from previous node if it has a matching output
        inp_list = []
        for inp_type in spec.inputs:
            src = None
            if nodes:
                prev = nodes[-1]
                prev_spec = TOKEN_PORT_SPEC[prev.token]
                for out_idx, out_type in enumerate(prev_spec.outputs):
                    if out_type == inp_type and (len(prev.outputs) > out_idx 
                         and prev.outputs[out_idx] is None):
                        src = prev.position
                        break
            inp_list.append(src)
        nodes.append(WiredNode(token=t, position=i,
                               inputs=tuple(inp_list),
                               outputs=(None,) * len(spec.outputs)))
    # Back-fill outputs
    for i, nd in enumerate(nodes):
        outs = list(nd.outputs)
        spec = TOKEN_PORT_SPEC[nd.token]
        for oi, out_type in enumerate(spec.outputs):
            for j in range(i + 1, n):
                nj = nodes[j]
                nj_spec = TOKEN_PORT_SPEC[nj.token]
                for ii, it in enumerate(nj_spec.inputs):
                    if it == out_type and nj.inputs[ii] == nd.position:
                        outs[oi] = nj.position
                        break
                if outs[oi] is not None:
                    break
        nodes[i] = WiredNode(token=nd.token, position=nd.position,
                             inputs=nd.inputs, outputs=tuple(outs))
    return WiredGraph(nodes=tuple(nodes), token_seq=token_seq, n_nodes=n)


def _build_wiring_with_assignment(token_seq: Tuple[int, ...],
                                   frob_pairs: Dict[int, int],
                                   branch_assignment: Dict) -> WiredGraph:
    """Build a WiredGraph with explicit Frobenius pairings and branch assignment."""
    # Use imscr_wiring as base but override the pairings and branch assignment
    # For now, return the standard wiring (full implementation deferred)
    return imscr_wiring(token_seq)

# ============================================================================
# COMPOSITION FINGERPRINT  —  distinct from token-sequence fingerprint
# ============================================================================

def composition_class_key(g: WiredGraph) -> str:
    """Compact key for the composition class (equivalence under rewiring).

    Two token sequences that produce the same composition_class_key present
    the SAME composition — they are in the same equivalence class.
    """
    pairs = g.frobenius_pairs
    # Node signature: (token, frob_pair, connectivity degree)
    node_sig = tuple(
        (n.token, n.frob_pair,
         sum(1 for x in n.inputs if x is not None),
         sum(1 for x in n.outputs if x is not None))
        for n in g.nodes
    )
    return f"n={g.n_nodes}|pairs={pairs}|nodes={node_sig}"


def composition_distance(g1: WiredGraph, g2: WiredGraph) -> int:
    """Structural distance between two compositions (not their presentations)."""
    # Compare Frobenius pair structure
    pairs1 = set(g1.frobenius_pairs)
    pairs2 = set(g2.frobenius_pairs)
    pair_dist = len(pairs1.symmetric_difference(pairs2))
    
    # Compare node token sequence ignoring position
    tokens1 = tuple(n.token for n in g1.nodes)
    tokens2 = tuple(n.token for n in g2.nodes)
    token_dist = sum(1 for a, b in zip(tokens1, tokens2) if a != b)
    token_dist += abs(len(tokens1) - len(tokens2))
    
    return pair_dist + token_dist


# ============================================================================
# TOKEN SEQUENCE → COMPOSITION EQUIVALENCE CLASSES
# ============================================================================

def presentation_equivalence_class(token_seq: Tuple[int, ...]) -> str:
    """The composition class this token sequence presents (standard wiring).

    This is what the current engine implicitly uses — the normal form.
    """
    g = imscr_wiring(token_seq)
    return composition_class_key(g)


def composition_space_size(token_seq: Tuple[int, ...]) -> int:
    """How many distinct valid compositions does this token sequence admit?"""
    comps = all_valid_compositions(token_seq)
    return len(comps)


def token_multiset_compositions(multiset: Dict[int, int]) -> int:
    """Upper bound on distinct compositions for a given token multiset."""
    n_fsplit = multiset.get(Token.FSPLIT, 0)
    n_ffuse  = multiset.get(Token.FFUSE, 0)
    n_evalt  = multiset.get(Token.EVALT, 0)
    n_evalf  = multiset.get(Token.EVALF, 0)
    
    if n_fsplit == 0 or n_ffuse == 0:
        return 1
    
    # Catalan number for non-crossing pairings with min(n_fsplit, n_ffuse)
    import math

    k = min(n_fsplit, n_ffuse)
    catalan = math.comb(2*k, k) // (k + 1)
    
    # Branch assignment: each block can have EVALT↔EVALF swapped
    branch_variants = 2 ** min(n_evalt, n_evalf, k)
    
    return catalan * branch_variants


# ============================================================================
# DIAGNOSTIC:  analyze the presentation-composition gap
# ============================================================================

def analyze_gap(token_seq: Tuple[int, ...]) -> Dict:
    """Diagnostic: how much larger is the composition space than the presentation?"""
    n_comps = composition_space_size(token_seq)
    g_standard = imscr_wiring(token_seq)
    n_pairings = len(all_frob_pairings(token_seq))
    
    return {
        'token_sequence': ' → '.join(TOKEN_NAMES[t] for t in token_seq),
        'length': len(token_seq),
        'n_fsplit': sum(1 for t in token_seq if t == Token.FSPLIT),
        'n_ffuse':  sum(1 for t in token_seq if t == Token.FFUSE),
        'n_evalt':  sum(1 for t in token_seq if t == Token.EVALT),
        'n_evalf':  sum(1 for t in token_seq if t == Token.EVALF),
        'frob_pairings': frob_pairings_desc(token_seq),
        'n_distinct_compositions': n_comps,
        'presentation_is_unique': n_comps == 1,
        'standard_frob_pairs': g_standard.frobenius_pairs,
        'composition_class': composition_class_key(g_standard),
        'valid': g_standard.is_valid,
    }


def frob_pairings_desc(token_seq: Tuple[int, ...]) -> List[str]:
    """Human-readable description of all valid FSPLIT/FFUSE pairings."""
    pairings = all_frob_pairings(token_seq)
    descs = []
    for p in pairings:
        if not p:
            descs.append("none")
        else:
            parts = [f"FSPLIT@{sp}↔FFUSE@{fp}" for sp, fp in sorted(p.items())]
            descs.append(", ".join(parts))
    return descs
