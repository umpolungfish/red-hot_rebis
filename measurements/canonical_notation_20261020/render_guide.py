"""Preserve canonical primitive and Shavian glyphs through Markdown conversion."""
from pathlib import Path
import subprocess,re
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
source=ROOT/'ig-docs/red-hot-rebis-user-guide.md'
glyphs='⊢⊣≻≺⋈⊤∈∋⊙⊥⊞⊡⟨⟩·'+''.join(chr(c) for c in range(0x10450,0x10480))
text=source.read_text()
for c in glyphs:text=text.replace(c,f'CANONICALGLYPH{ord(c)}END')
intermediate=OUT/'guide_input.md';intermediate.write_text(text)
tex=source.with_suffix('.tex')
subprocess.run(['latextiler','convert',str(intermediate),'-F','latex','--force','-o',str(tex),'--font-size','12'],check=True,capture_output=True,text=True)
text=tex.read_text()
for c in glyphs:text=text.replace(f'CANONICALGLYPH{ord(c)}END',c)
# Replace the converter's inherited font block with canonical glyph definitions.
a=text.find('\\AtBeginDocument{')
b=text.index('\\usepackage{textcomp}',a) if a>=0 else text.index('\\begin{document}')
a=b if a<0 else a
block='\\usepackage{fontspec,newunicodechar}\n\\newfontfamily\\shavfont[Scale=1.0]{Trabajo}\n\\newfontface\\igprimfont{Everson Mono}\n\\AtBeginDocument{\n' if a==b else '\\AtBeginDocument{\n'
for c in glyphs:
    font='shavfont' if ord(c)>=0x10450 else 'igprimfont'
    rendered='{\\'+font+' \\char"'+f'{ord(c):X}'+'}'
    block+='\\newunicodechar{'+c+'}{\\ifmmode\\text{'+rendered+'}\\else'+rendered+'\\fi}\n'
block+='}\n'
text=text[:a]+block+text[b:]
text=text.replace('\\newfontfamily\\shavfont[Scale=1.0]{Everson Mono}','\\newfontfamily\\shavfont[Scale=1.0]{Trabajo}')
tex.write_text(text)
print(tex)
