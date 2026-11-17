from pathlib import Path
from copy import deepcopy
import sys
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.shared import Cm,Pt
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];G=R/'outputs/figures';BG='#F7F0E6';B='#387DA0';C='#C9714D';K='#29343B'
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'svg.fonttype':'none','text.color':K})
f=plt.figure(figsize=(12,4.1),facecolor=BG);ax=f.add_axes([0,0,1,1]);ax.axis('off');ax.set(xlim=(0,12),ylim=(0,4.1))
def card(x,y,num,title,lines,accent):
 ax.add_patch(FancyBboxPatch((x,y),3.65,1.55,boxstyle='round,pad=.02,rounding_size=.08',facecolor='#FFFCF7',edgecolor='#D7C7B6',lw=.8))
 ax.plot([x+.17,x+.17],[y+.22,y+1.33],lw=3,color=accent)
 ax.text(x+.35,y+1.23,num,fontsize=15,fontweight='bold',color=accent,va='center');ax.text(x+.83,y+1.23,title,fontsize=13,va='center')
 ax.text(x+.35,y+.77,lines,fontsize=11.5,va='top',linespacing=1.55)
def arr(a,b):ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',lw=1.2,color='#6C7476'))
card(.2,2.32,'01','任务与数据','310 条记录；两个预设输入\n训练 186 / 验证 62 / 测试 62',B)
card(4.18,2.32,'02','几何与容错','边界 → 距离 → 支持向量\n八点示例；hinge 与 soft margin',B)
card(8.16,2.32,'03','完整训练实验','训练集标准化；受控改变 C\n核函数、gamma 与尺度比较',B)
card(.2,.22,'04','验证与稳定性','平衡准确率选参；阈值为 0\n人工扰动检验局部敏感性',C)
card(4.18,.22,'05','固定配置','Linear：C = 1\nRBF：C = 10，gamma = 10',C)
card(8.16,.22,'06','留出测试与解释','62 条记录；不合并验证集重训\n两类召回率、AUC及适用边界',C)
arr((3.85,3.1),(4.18,3.1));arr((7.83,3.1),(8.16,3.1));arr((3.85,1),(4.18,1));arr((7.83,1),(8.16,1))
ax.plot([10,10,2],[2.32,2.05,2.05],color='#6C7476',lw=1.1);arr((2,2.05),(2,1.77))
f.savefig(G/'图1_期刊流程图.png',dpi=300,facecolor=BG);f.savefig(G/'图1_期刊流程图.svg',facecolor=BG);plt.close(f)
d=Document(R/'SVM课程作业_完成稿.docx');pic=d.inline_shapes[0];rid=pic._inline.graphic.graphicData.pic.blipFill.blip.embed;d.part.related_parts[rid]._blob=(G/'图1_期刊流程图.png').read_bytes();pic.width=Cm(17.4);pic.height=Cm(17.4*4.1/12)
groups=[];current=None
for el in list(d.element.body):
 if el.tag==qn('w:sectPr'):continue
 txt=''.join(el.itertext()) if False else ''.join(el.xpath('.//w:t')) if False else ''.join(n.text or '' for n in el.iter(qn('w:t')))
 style=el.find('./'+qn('w:pPr')+'/'+qn('w:pStyle')) if el.tag==qn('w:p') else None
 if style is not None and style.get(qn('w:val'))=='Heading1':
  current={'heading':deepcopy(el),'body':[],'media':[]};groups.append(current);continue
 if current is None:continue
 if el.tag==qn('w:tbl') or el.findall('.//'+qn('w:drawing')) or txt.startswith(('图','表')):current['media'].append(deepcopy(el))
 else:current['body'].append(deepcopy(el))
for el in list(d.element.body):
 if el.tag!=qn('w:sectPr'):d.element.body.remove(el)
def setup(sec,cols=1):
 sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(1.6);sec.bottom_margin=Cm(1.6);sec.left_margin=Cm(1.8);sec.right_margin=Cm(1.8)
 c=sec._sectPr.find(qn('w:cols'));c.set(qn('w:num'),str(cols));c.set(qn('w:space'),'454');c.set(qn('w:equalWidth'),'1')
def append(el):d.element.body.insert(len(d.element.body)-1,el)
setup(d.sections[0]);d.styles['Normal'].paragraph_format.line_spacing=1.12;d.styles['Normal'].paragraph_format.space_after=Pt(5)
d.styles['Heading 1'].font.size=Pt(12);d.styles['Title'].font.size=Pt(18)
names=['1 研究任务与数据','2 间隔原则与支持向量','3 软间隔与惩罚参数','4 核函数与局部相似度','5 尺度与扰动敏感性','6 固定测试与讨论']
for i,g in enumerate(groups):
 if i:setup(d.add_section(WD_SECTION_START.NEW_PAGE),1)
 if i==0:
  q=d.add_paragraph('脊柱测量数据中的支持向量机分析','Title');q.alignment=1
  abstract=g['body'].pop(0);append(abstract)
  q=d.paragraphs[-1];q.text='摘要：'+q.text
  q=d.add_paragraph('关键词：支持向量机；软间隔；核函数；标准化；模型验证');q.paragraph_format.space_after=Pt(6)
 q=d.add_heading(names[i],1);q.paragraph_format.page_break_before=False
 for el in g['media']:
  if el.tag==qn('w:p'):
   pp=el.find(qn('w:pPr'))
   if pp is not None:
    br=pp.find(qn('w:pageBreakBefore'))
    if br is not None:pp.remove(br)
   txt=''.join(n.text or '' for n in el.iter(qn('w:t')))
   if txt.startswith('图1 '):
    ts=list(el.iter(qn('w:t')))
    if ts:
     ts[0].text='图1 SVM研究与评价流程。'
     for t in ts[1:]:t.text=''
     if len(ts)>1:ts[1].text='蓝色表示数据准备与训练实验，橙色表示验证、配置固定及留出评价。八点子集只用于几何解释，正式参数实验使用全部186条训练记录；测试结果不用于再次选参。'
  append(el)
 setup(d.add_section(WD_SECTION_START.CONTINUOUS),2)
 lengths=[len(''.join(t.text or '' for t in el.iter(qn('w:t')))) for el in g['body']]
 total=sum(lengths);split=min(range(1,len(lengths)),key=lambda k:abs(sum(lengths[:k])-total/2)) if len(lengths)>1 else -1
 for bi,el in enumerate(g['body']):
  if bi==split:
   q=d.add_paragraph();q.paragraph_format.space_after=Pt(0);q.paragraph_format.space_before=Pt(0);q.paragraph_format.line_spacing=Pt(1);q.add_run().add_break(WD_BREAK.COLUMN)
  pp=el.find(qn('w:pPr'))
  if pp is not None:
   br=pp.find(qn('w:pageBreakBefore'))
   if br is not None:pp.remove(br)
  append(el)
# Keep exactly three rules in each centered table; remove all vertical/interior rules.
for table in d.tables:
 table.alignment=1
 for i,row in enumerate(table.rows):
  for cell in row.cells:
   tc=cell._tc.get_or_add_tcPr()
   for old in list(tc.findall(qn('w:tcBorders'))):tc.remove(old)
   bd=OxmlElement('w:tcBorders')
   for edge in ['top','bottom','left','right','insideH','insideV']:
    e=OxmlElement('w:'+edge);on=(edge=='top' and i==0) or (edge=='bottom' and i in [0,len(table.rows)-1]);e.set(qn('w:val'),'single' if on else 'nil');e.set(qn('w:sz'),'6' if edge=='bottom' and i==0 else '10');e.set(qn('w:color'),'000000');bd.append(e)
   tc.append(bd)
   for q in cell.paragraphs:q.alignment=1
out=R/'SVM课程作业_中文期刊双栏版.docx';d.save(out);print(out)
