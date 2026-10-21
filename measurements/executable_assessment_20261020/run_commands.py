"""Local command exercises; no model generation or network calls requested."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tomllib
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
entries = tomllib.loads((ROOT/'pyproject.toml').read_text())['project']['scripts']
entries['at'] = 'ars_therapeutica.cli:main'
rna = ''.join(('AUG','GCU','CGU','AAU','GAU','UGU','GAA','GGU','CAC','AUU','CUU','AAA','UAU','CCU','CAA','UCU','ACU','GUU','UGG','UUU','UAA'))
commands = {
'rebis': ['--version'],
'rebis.chain': ['--seq', rna, '--target','CC(=O)O','--depth','1','--pdb',str(OUT/'chain.pdb')],
'rebis.gene-pipeline': ['--seq',rna,'--pdb',str(OUT/'gene.pdb')],
'rebis.ch3mpiler': ['fg','CCO'],
'rebis.serpentrod': ['foldv2',rna,'--pdb',str(OUT/'gen2.pdb')],
'rebis.ligand': ['--pdb-file',str(ROOT/'measurements/native_protein_glut_20261020/gen2.pdb'),'--active','Met1,Ala2','--json'],
'rebis.sidechain': ['--batch','--json'],
'rebis.therapeutics': ['sim','--time','1','--noise','0'],
'rebis.materials': ['metamaterial','--size','5','--cycles','1','--heal-steps','1'],
'rebis.biology': ['morphogenesis','--steps','1','--grid-size','8','--n-types','2'],
'rebis.pipeline': ['list'],
'rebis.gene': ['analyze',rna,'--translate'],
'rebis.alchemy': ['operations'],
'rebis.clink': ['layers'],
'rebis.p4ra': ['belnap'],
'rebis.demo': ['list'],
'rebis.status': [],
'rebis.verify': [],
'rebis.vox': ['peptide','AGPSTVLR'],
'at': ['spectrum'],
}
results=[]
for name,args in commands.items():
 module,fn=entries[name].split(':')
 argv=[sys.executable,'-c',f'from {module} import {fn}; import sys; sys.exit({fn}())',*args]
 t=time.monotonic()
 try:
  p=subprocess.run(argv,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT)+os.pathsep+str(ROOT/'Ars_Therapeutica')},capture_output=True,text=True,timeout=30)
  (OUT/(name+'.run.log')).write_text(p.stdout+p.stderr)
  results.append({'command':name,'args':args,'returncode':p.returncode,'seconds':time.monotonic()-t,'log':name+'.run.log'})
 except subprocess.TimeoutExpired as e:
  (OUT/(name+'.run.log')).write_bytes((e.stdout or b'')+(e.stderr or b''))
  results.append({'command':name,'args':args,'timeout_seconds':30})
(OUT/'command_runs.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([{k:v for k,v in r.items() if k not in ('args','log')} for r in results],indent=2))
