from pathlib import Path
import sys,re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.analysis-deps'))
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from PIL import Image
OUT=ROOT/'review/final-assets';OUT.mkdir(parents=True,exist_ok=True)
# Re-render statistical evidence from the original analysis, preserving calculations.
src=(ROOT/'outputs/analysis.py').read_text(encoding='utf-8').split('# Completed student report')[0]
src=src.replace("OUT=ROOT/'outputs'", "OUT=ROOT/'review/final-assets'")
src=src.replace("'font.family':'Arial'", "'font.family':'Times New Roman'")
src=src.replace("'savefig.facecolor':'white'", "'savefig.facecolor':'#FBF7F0','figure.facecolor':'#FBF7F0','axes.facecolor':'#FBF7F0'")
src=src.replace("BLUE='#2878A0'; RED='#C75B45'", "BLUE='#387DA0'; RED='#C9714D'")
exec(compile(src,str(ROOT/'outputs/analysis.py'),'exec'),{'__file__':str(ROOT/'outputs/analysis.py')})
d=Document(ROOT/'心脏病与最大运动心率_作业完成稿.docx')
pars=d.paragraphs
# Replace the four result figures, keeping their original anchoring.
for pi,name in zip([20,27,33,36],['figure1_primary','figure2_adjustment','figure3_associations','figure4_prediction']):
 p=pars[pi];p.clear();p.add_run().add_picture(str(OUT/(name+'.png')),width=Cm(17));p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.paragraph_format.keep_with_next=True
# Remove old framework and its bundled break, then insert exact supplied images
# with nondestructive Word crop regions. Source image pixels remain unchanged.
pars[4].clear()
def before(anchor):
 el=OxmlElement('w:p');anchor._p.addprevious(el);return Paragraph(el,anchor._parent)
def figure_page(anchor,file,top,bottom,caption):
 first=before(anchor);first.paragraph_format.page_break_before=True
 pic=first.add_run().add_picture(str(file),width=Cm(17.4))
 im=Image.open(file);ratio=im.height/im.width*(1-top-bottom)
 pic.height=int(Cm(17.4)*ratio)
 fill=pic._inline.xpath('.//pic:blipFill')[0];crop=OxmlElement('a:srcRect');crop.set('t',str(round(top*100000)));crop.set('b',str(round(bottom*100000)));fill.insert(1,crop)
 first.alignment=WD_ALIGN_PARAGRAPH.CENTER;first.paragraph_format.keep_with_next=True
 cap=before(anchor);cap.add_run(caption);cap.paragraph_format.space_before=Pt(8)
 anchor.paragraph_format.page_break_before=True
figure_page(pars[5],Path('C:/Users/340/AppData/Local/Temp/codex-clipboard-2529940d-3f44-4be0-9528-a3f1c4f8a613.png'),0,0.059,
 '图 1 研究对象 主要终点与统计假设。a，四中心原始样本共 920 人，剔除最大运动心率缺失的 55 人后，纳入 865 人，其中无疾病证据组 391 人，有疾病证据组 474 人。b，主要终点为最大运动心率 thalach（bpm），总体均值差定义为有疾病证据组减无疾病证据组。蓝色表示无疾病证据组，橙红色表示有疾病证据组；箱线图及效应量图形为示意，标注数值来自实际分析。c，双侧 Welch t 检验，α=0.05；曲线两端阴影为概念性拒绝域。观察性关联不等于因果关系。')
# Remove preexisting page break before task 4 so added figure gets one break only.
pars[17].clear()
figure_page(pars[18],Path('C:/Users/340/AppData/Local/Temp/codex-clipboard-443ea1cd-5571-4691-b582-68306898baf2.png'),128/1120,105/1120,
 '图 2 数据结构与统计方法选择。a，独立两组连续结局采用 Welch t 检验。b，同一受试者前后测量采用配对 t 检验。c，两个分类变量的关联采用 Pearson χ² 检验，稀疏 2×2 表可采用 Fisher 精确检验。d，连续变量的线性关联采用 Pearson 相关，单调关联可用 Spearman 秩相关。e，二分类预测采用 Logistic 回归并评价判别与校准。散点、配对连线、区间和概率曲线均为概念示意，不代表本数据的检验结果；本数据没有前后配对测量。交叉验证用于预测评价，本身不是假设检验。图形组织参考 Nature Methods 的 Points of Significance 系列。')
for p in d.paragraphs:
 if re.match(r'图 [1-4] ',p.text) and p not in []:
  # Only original result captions, distinguished by content.
  for old,title in [(1,'疾病状态与最大运动心率'),(2,'调整模型与中心内比较'),(3,'探索性关联'),(4,'探索性疾病分类')]:
   if p.text.startswith(f'图 {old} {title}'):
    p.text=p.text.replace(f'图 {old} ',f'图 {old+2} ',1).replace('红线','橙红线')
 if p.text.startswith('图均由本次数据原创绘制'):
  p.text='图 1 和图 2 为研究设计与统计方法示意，图 3 至图 6 由课程数据计算绘制。原始数据与字段定义来自课程所给 CSV 和 data/README.md。'
# Place references on their own page to keep the risk discussion readable.
for p in d.paragraphs:
 if p.text=='作图参考文献':p.paragraph_format.page_break_before=True
for t in ['[5] Krzywinski M, Altman N. Comparing samples—part I. Nature Methods. 2014;11:215–216. doi:10.1038/nmeth.2858.', '[6] Krzywinski M, Altman N. Designing comparative experiments. Nature Methods. 2014;11:597–598. doi:10.1038/nmeth.2974.', '[7] Altman N, Krzywinski M. Association, correlation and causation. Nature Methods. 2015;12:899–900. doi:10.1038/nmeth.3587.', '[8] Lever J, Krzywinski M, Altman N. Logistic regression. Nature Methods. 2016;13:541–542. doi:10.1038/nmeth.3904.']:
 d.add_paragraph(t)
titles=['表 1 研究问题与假设定义','表 2 统计功效的影响因素','表 3 统计方法及适用条件','表 4 最大运动心率的分组描述统计','表 5 调整模型的效应估计']
for ti,t in enumerate(d.tables):
 el=OxmlElement('w:p');t._tbl.addprevious(el);cap=Paragraph(el,t._parent);cap.text=titles[ti];cap.alignment=WD_ALIGN_PARAGRAPH.CENTER;cap.paragraph_format.keep_with_next=True
 t.alignment=WD_TABLE_ALIGNMENT.CENTER
 pr=t._tbl.tblPr
 for old in list(pr.findall(qn('w:tblBorders'))):pr.remove(old)
 borders=OxmlElement('w:tblBorders')
 for edge in ['top','bottom','left','right','insideH','insideV']:
  e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single' if edge in ['top','bottom'] else 'nil');e.set(qn('w:sz'),'12');e.set(qn('w:color'),'000000');borders.append(e)
 pr.append(borders)
 for ri,row in enumerate(t.rows):
  for c in row.cells:
   cp=c._tc.get_or_add_tcPr()
   for name in ['tcBorders','shd']:
    for old in list(cp.findall(qn('w:'+name))):cp.remove(old)
   bd=OxmlElement('w:tcBorders')
   for edge in ['top','bottom','left','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single' if ri==0 and edge=='bottom' else 'nil');e.set(qn('w:sz'),'6');e.set(qn('w:color'),'000000');bd.append(e)
   # Table outer rules are set on cells too for reliable Word rendering.
   for edge,yes in [('top',ri==0),('bottom',ri==len(t.rows)-1)]:
    if yes:
     e=bd.find(qn('w:'+edge));e.set(qn('w:val'),'single');e.set(qn('w:sz'),'12')
   cp.append(bd);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   for p in c.paragraphs:
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(4);p.paragraph_format.space_after=Pt(4)
def font_run(r,size=None):
 r.font.name='Times New Roman';r.font.color.rgb=RGBColor(0,0,0)
 rf=r._element.get_or_add_rPr().rFonts
 for attr,val in [('eastAsia','宋体'),('ascii','Times New Roman'),('hAnsi','Times New Roman'),('cs','Times New Roman')]:rf.set(qn('w:'+attr),val)
 for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
  rf.attrib.pop(qn('w:'+attr),None)
 if size:r.font.size=Pt(size)
for st in d.styles:
 if hasattr(st,'font'):
  st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
  st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体')
for p in d.paragraphs:
 iscap=p.text.startswith('图 ');istable=p.text.startswith('表 ')
 if iscap:p.paragraph_format.line_spacing=1.1;p.paragraph_format.space_after=Pt(6)
 for r in p.runs:font_run(r,9 if iscap else (10 if istable else None))
 if iscap:
  # Bold the figure name through the first full stop.
  txt=p.text;name,sep,rest=txt.partition('。');p.clear();a=p.add_run(name+sep);a.bold=True;font_run(a,9);font_run(p.add_run(rest),9)
for t in d.tables:
 for row in t.rows:
  for c in row.cells:
   for p in c.paragraphs:
    for r in p.runs:font_run(r,9)
for sec in d.sections:
 for area in [sec.header,sec.footer]:
  for p in area.paragraphs:
   for r in p.runs:font_run(r)
d.save(ROOT/'完成稿.docx')
print('Saved',ROOT/'完成稿.docx')
