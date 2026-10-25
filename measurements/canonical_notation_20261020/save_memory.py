"""Save the notation correction and verified continuation handles."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
receipt=json.loads((OUT/'notation_receipt.json').read_text())
assert receipt['status']=='passed' and receipt['native_vox_to_rebis_ligand']=='passed'
MEMORY=Path('/home/mrnob0dy666/.codex/memories/imsgct')
name='canonical_protein_notation_20261020.md'
text='''# Canonical protein notation, 2026-10-20

Lando requires SNS_PRIME.md as the notation authority, with only the canonical primitive symbols in axis positions: ⊢ ⊣ ≻ ≺ ⋈ ⊤ ∈ ∋ ⊙ ⊥ ⊞ ⊡. Apply this to code schemas, returned tuples, comments, documentation and rendered glyphs. Biological one-letter alphabets and truth values retain their own meanings.

The active protein, gene and ligand producers/consumers now carry canonical tuple keys directly. Removed the short-key conversions and the obsolete stoichiometry alias normalizer. Canonicalized the winding symbol through connected Rebis runtime modules. Full source-bound residue/form records remain retained.

Verification: red-hot_rebis/measurements/canonical_notation_20261020/run.py and result.json pass all20/22forms, legacy/Gen2/gene processing, 80sidechain compositions, both ligand paths, shared catalytic chain and six installed CLI paths. notation_receipt.json audits 557 emitted tuple dictionaries and checks actual native Vox PDB/carrier to Rebis ligand. Rebuilt Vox is byte-identical to the three installed binaries. Historical receipts retain their original source bindings.

README and guides document the canonical alphabet. The Markdown renderer dropped canonical glyphs; render_guide.py protects them through conversion and binds primitive glyphs to Everson Mono and Shavian to Trabajo. Canonical generated TeX is ig-docs/red-hot-rebis-user-guide.tex. Regenerate with render_guide.py then ltx on that TeX, not raw Markdown, and visually review glyphs.

The earlier 30protein geometry findings remain open; this notation change does not establish folding accuracy. The audit scope is active protein/gene/ligand code and current README/guide, not an assertion that all unrelated historical workspace material has been migrated.
'''
(MEMORY/name).write_text(text)
p=MEMORY/'CURRENT.md';s=p.read_text();header='CANONICAL PROTEIN NOTATION 2026-10-20: SNS_PRIME.md governs all primitive-axis labels and tuple keys. Active protein/gene/ligand schemas now use ⊢⊣≻≺⋈⊤∈∋⊙⊥⊞⊡ directly; integrated all20/22forms and 557emitted tuple dictionaries pass. Rebuilt Vox matches installed binaries. Guide renderer required explicit glyph preservation. See [[canonical_protein_notation_20261020]].\n\n'
if header not in s:p.write_text(header+s)
p=MEMORY/'MEMORY.md';s=p.read_text();entry='\n- [[canonical_protein_notation_20261020]]: canonical SNS Prime axis schemas, integrated verification and PDF glyph rendering.\n'
if entry not in s:p.write_text(s.rstrip()+'\n'+entry)
print('Saved canonical notation memory and index')
