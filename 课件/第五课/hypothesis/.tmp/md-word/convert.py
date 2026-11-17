from pathlib import Path
import re
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
src=Path('C:/Users/340/Desktop/6. multiple-test/student-worksheet.md')
doc=Document()
s=doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7); s.top_margin=Cm(1.8); s.bottom_margin=Cm(1.8); s.left_margin=Cm(1.7); s.right_margin=Cm(1.7)
for name in ['Normal','Title','Heading 1','Heading 2','List Bullet','List Number']:
 st=doc.styles[name]; st.font.name='Calibri'; st.font.color.rgb=RGBColor(0,0,0); st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
 st.font.size=Pt(10.5 if name in ['Normal','List Bullet','List Number'] else 20 if name=='Title' else 14 if name=='Heading 1' else 12)
 st.paragraph_format.space_after=Pt(6); st.paragraph_format.line_spacing=1.15

def inline(p,text):
 for x in re.split(r'(\*\*.*?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))',text):
  if not x: continue
  if x.startswith('**'): r=p.add_run(x[2:-2]); r.bold=True
  elif x.startswith('`'): r=p.add_run(x[1:-1]); r.font.name='Consolas'; r.font.size=Pt(9.5)
  elif x.startswith('['):
   m=re.match(r'\[([^\]]+)\]\(([^)]+)\)',x); r=p.add_run(m[1]+' ('+m[2]+')')
  else: r=p.add_run(x)
lines=src.read_text(encoding='utf-8-sig').splitlines(); i=0
while i<len(lines):
 line=lines[i].strip(); i+=1
 if not line: continue
 if line.startswith('|'):
  group=[line]
  while i<len(lines) and lines[i].strip().startswith('|'): group.append(lines[i].strip()); i+=1
  rows=[[c.strip() for c in z.strip('|').split('|')] for z in group]
  rows=[z for z in rows if not all(re.fullmatch(r':?-+:?',c) for c in z)]
  t=doc.add_table(rows=0, cols=len(rows[0])); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
  n=len(rows[0]); widths=([3.3,1.7,1.7,10.9] if n==4 and rows[0][0]=='分析部分' else [5.2,6.2,6.2] if n==3 else [17.6/n]*n)
  for j,w in enumerate(widths): t.columns[j].width=Cm(w)
  for k,rr in enumerate(rows):
   cells=t.add_row().cells
   trpr=cells[0]._tc.getparent().get_or_add_trPr(); ns=OxmlElement('w:cantSplit'); trpr.append(ns)
   if k==0: rep=OxmlElement('w:tblHeader'); trpr.append(rep)
   for j,txt in enumerate(rr):
    c=cells[j]; c.width=Cm(widths[j]); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p=c.paragraphs[0]; p.paragraph_format.space_after=Pt(4); p.paragraph_format.space_before=Pt(4); p.paragraph_format.line_spacing=1.05; inline(p,txt)
    for r in p.runs: r.font.size=Pt(9); r.bold=k==0
    pr=c._tc.get_or_add_tcPr(); borders=OxmlElement('w:tcBorders')
    for edge in ['top','left','bottom','right']:
     el=OxmlElement('w:'+edge); el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'4'); el.set(qn('w:color'),'D9D9D9'); borders.append(el)
    pr.append(borders)
    if k==0: sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'E7EDF2'); pr.append(sh)
  doc.add_paragraph().paragraph_format.space_after=Pt(0)
 elif line.startswith('# '): inline(doc.add_paragraph(style='Title'),line[2:])
 elif line.startswith('## '): inline(doc.add_paragraph(style='Heading 1'),line[3:])
 elif line.startswith('- '): inline(doc.add_paragraph(style='List Bullet'),line[2:])
 else:
  p=doc.add_paragraph(); inline(p,line)
out=src.with_suffix('.docx'); doc.save(out); print(out)
