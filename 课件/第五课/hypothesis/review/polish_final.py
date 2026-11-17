from pathlib import Path
from docx import Document
from docx.shared import Pt
root=Path(__file__).resolve().parents[1]
d=Document(root/'完成稿.docx')
for p in d.paragraphs:
 if p.text.startswith('['):
  p.paragraph_format.line_spacing=1.1
  p.paragraph_format.space_after=Pt(7)
  for r in p.runs:r.font.size=Pt(9)
 if p.text.startswith('图 1 和图 2 为研究设计'):
  d._element.body.insert(len(d._element.body)-1,p._p)
  for r in p.runs:r.bold=False;r.font.size=Pt(9)
for t in d.tables:
 nxt=t._tbl.getnext()
 if nxt is not None and nxt.tag.endswith('}p'):
  from docx.text.paragraph import Paragraph
  Paragraph(nxt,t._parent).paragraph_format.space_before=Pt(7)
d.save(root/'完成稿.docx')
