from pathlib import Path
import sys,warnings
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
warnings.filterwarnings('ignore',category=FutureWarning)
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.colors import to_rgba,LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.shared import Cm,Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'outputs/清新暖橙版';DEST.mkdir(exist_ok=True)
ORANGE=to_rgba('#FFBC78',.5);GREEN='#739C89';TERRA='#D88B68';INK='#37433D'
widths={n:(13.0 if n==8 else 15.5 if n==6 else 17.4) for n in range(1,12)}
def uniform_save(fig,n):
 if n==1:plt.close(fig);return
 ratio=(widths[n]/2.54)/fig.get_figwidth()
 for tx in fig.findobj(Text):
  tx.set_fontsize(7.5/ratio);tx.set_color(INK)
  tx.set_text(tx.get_text().replace('记录顺序（按真实类别、ID排列）','记录序号（按类别与ID排序）'))
 for ax in fig.axes:
  ax.set_facecolor('none')
  for title in [ax.title,ax._left_title,ax._right_title]:
   title.set_fontsize(8.5/ratio)
   if n==8:title.set_text(title.get_text().replace('Linear C=1','Linear').replace('RBF C=10 γ=10','RBF'))
  ax.xaxis.label.set_fontsize(7.5/ratio);ax.yaxis.label.set_fontsize(7.5/ratio)
  ax.tick_params(labelsize=7/ratio)
  if n==10 and ax.name=='polar':ax.tick_params(labelsize=7/ratio)
 fig.patch.set_facecolor(ORANGE)
 fig.tight_layout(pad=1.0,w_pad=1.4,h_pad=1.5)
 fig.savefig(DEST/f'图{n}.png',dpi=300,facecolor=ORANGE)
 fig.savefig(DEST/f'图{n}.svg',facecolor=ORANGE)
 plt.close(fig)
def recolor(s):
 return s.replace('#387DA0',GREEN).replace('#C9714D',TERRA).replace('#F7F0E6','#FFF5E9').replace('#8C8176','#A59B85').replace('#E8E8DF','#EAF0DF').replace('#F1DAC8','#F8E3CF').replace('#B9A27D','#D5B773')
# Redraw from plotting sources rather than editing raster pixels.
s=recolor((ROOT/'scripts/assignment_report.py').read_text(encoding='utf-8'));pre=s[:s.index('def save(')];body=s[s.index('f=plt.figure',s.index('def save(')):s.index('d=Document();')]
exec(pre,globals());save=uniform_save;exec(body,globals())
s=recolor((ROOT/'scripts/expanded_report.py').read_text(encoding='utf-8'));pre=s[:s.index('def save(')];body=s[s.index("names=['Linear",s.index('def save(')):s.index('# Use the same document')]
exec(pre,globals());save=uniform_save;exec(body,globals())
# Visual workflow: actual geometry, parameter evidence, and test counts.
from lab_utils import load_development,geometry_experiment
train,validation=load_development();geo=geometry_experiment(train)
fig=plt.figure(figsize=(12,5.0),facecolor=ORANGE);canvas=fig.add_axes([0,0,1,1]);canvas.set(xlim=(0,12),ylim=(0,5));canvas.axis('off')
def text(x,y,t,size=13,color=INK):canvas.text(x,y,t,fontsize=size,color=color,va='center')
def panel(x,y,w,h,num,title):
 canvas.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.02,rounding_size=.07',facecolor='#FFF9F1',edgecolor='#DBB590',lw=.8));text(x+.14,y+h-.25,num,15,GREEN);text(x+.65,y+h-.25,title,14)
def arrow(a,b):canvas.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='-|>',color='#879184',lw=1.3))
panel(.15,3.75,11.7,1.08,'01','数据准备与固定划分')
text(.4,4.15,'310 条记录 · 两项输入 → NO / AB',13);text(5.0,4.15,'训练 186',13,GREEN);text(7.1,4.15,'验证 62',13,TERRA);text(9.2,4.15,'测试 62',13)
panel(.15,1.05,3.7,2.4,'02','间隔几何')
panel(4.15,1.05,3.7,2.4,'03','参数实验')
panel(8.15,1.05,3.7,2.4,'04','预测评价')
arrow((2,3.75),(2,3.45));arrow((3.85,2.2),(4.15,2.2));arrow((7.85,2.2),(8.15,2.2))
ax=fig.add_axes([.06,.35,.23,.23]);ax.set_facecolor('none');z=geo['z'];y=geo['subset'].abnormal.to_numpy()
for cls,col,mark in [(0,GREEN,'o'),(1,TERRA,'^')]:ax.scatter(z[y==cls,0],z[y==cls,1],c=col,marker=mark,s=24)
w=geo['model'].coef_[0];b=geo['model'].intercept_[0];xx=np.linspace(-2,1.7,100)
for lev,ls in [(-1,'--'),(0,'-'),(1,'--')]:ax.plot(xx,(lev-w[0]*xx-b)/w[1],color=INK,ls=ls,lw=.8)
sv=geo['model'].support_;ax.scatter(z[sv,0],z[sv,1],s=70,facecolors='none',edgecolors=INK);ax.set(xlim=(-2,1.7),ylim=(-1.1,2.1));ax.tick_params(labelsize=10);text(.5,1.29,'八点教学子集 · 支持向量',12)
ax=fig.add_axes([.39,.35,.23,.23]);heat=pd.read_csv(ROOT/'outputs/参数网格.csv');heat=heat[heat.kernel=='rbf'].pivot(index='C',columns='gamma',values='val_balanced_accuracy');ax.imshow(heat,cmap=LinearSegmentedColormap.from_list('warmgrid',['#FFF7EB',TERRA]),vmin=.5,vmax=.85,aspect='auto');ax.set_xticks(range(4),['.01','.1','1','10']);ax.set_yticks(range(4),['.1','1','10','100']);ax.tick_params(labelsize=10)
for i in range(4):
 for j in range(4):ax.text(j,i,f'{heat.iloc[i,j]:.2f}',ha='center',va='center',fontsize=10,color=INK)
text(4.48,1.29,'RBF：行 C，列 gamma；验证 BA',11.5)
ax=fig.add_axes([.73,.35,.20,.23]);mat=np.array([[19,1],[11,31]]);ax.imshow(mat,cmap=LinearSegmentedColormap.from_list('warmcm',['#FFF7EB',TERRA]),vmin=0,vmax=42);ax.set_xticks([0,1],['预测 NO','预测 AB']);ax.set_yticks([0,1],['真实 NO','真实 AB']);ax.tick_params(labelsize=10)
for i in range(2):
 for j in range(2):ax.text(j,i,str(mat[i,j]),ha='center',va='center',fontsize=13,color=INK)
text(8.49,1.29,'配置固定后 · RBF 测试计数',12)
canvas.add_patch(FancyBboxPatch((.15,.15),11.7,.6,boxstyle='round,pad=.02,rounding_size=.06',facecolor='#FFF9F1',edgecolor='#DBB590',lw=.8));text(.4,.45,'训练标准化 → 验证选参 → 固定配置 → 留出测试；补充实验仅使用训练 / 验证集',13)
fig.savefig(DEST/'图1.png',dpi=300,facecolor=ORANGE);fig.savefig(DEST/'图1.svg',facecolor=ORANGE);plt.close(fig)
d=Document(ROOT/'SVM课程作业_单栏实验扩展版.docx')
from PIL import Image
for n,pic in enumerate(d.inline_shapes,1):
 imagepath=DEST/f'图{n}.png';rid=pic._inline.graphic.graphicData.pic.blipFill.blip.embed;d.part.related_parts[rid]._blob=imagepath.read_bytes();im=Image.open(imagepath);pic.width=Cm(widths[n]);pic.height=Cm(widths[n]*im.height/im.width)
for p in d.paragraphs:
 if p.text.startswith('图1 '):
  p.clear();p.add_run('图1 SVM研究与评价流程。').bold=True;p.add_run('流程图中嵌入实际八点几何结果、RBF验证参数热力图和固定RBF测试混淆矩阵。绿圆为NO，陶土色三角为AB，空心圈为支持向量；实线为边界，虚线为参考带。热力图表示验证平衡准确率；混淆矩阵数字为记录数。测试结果不用于再次选参。')
 else:
  for run in p.runs:
   if not run.text: continue
   run.text=run.text.replace('蓝色','鼠尾草绿色').replace('蓝圆','绿圆').replace('蓝点','绿点').replace('蓝线','绿线').replace('蓝柱','绿柱').replace('橙色','陶土色').replace('橙三角','陶土色三角').replace('橙线','陶土色线').replace('橙柱','陶土色柱')
for t in d.tables:
 t.alignment=WD_TABLE_ALIGNMENT.CENTER
 pr=t._tbl.tblPr
 for old in list(pr.findall(qn('w:tblBorders'))):pr.remove(old)
 borders=OxmlElement('w:tblBorders')
 for edge in ['top','bottom','left','right','insideH','insideV']:
  e=OxmlElement('w:'+edge);e.set(qn('w:val'),'nil');borders.append(e)
 pr.append(borders)
 for i,row in enumerate(t.rows):
  for c in row.cells:
   cp=c._tc.get_or_add_tcPr()
   for old in list(cp.findall(qn('w:tcBorders'))):cp.remove(old)
   bd=OxmlElement('w:tcBorders')
   for edge in ['top','bottom','left','right','insideH','insideV']:
    e=OxmlElement('w:'+edge);on=(edge=='top' and i==0) or (edge=='bottom' and i in [0,len(t.rows)-1]);e.set(qn('w:val'),'single' if on else 'nil');e.set(qn('w:sz'),'6' if edge=='bottom' and i==0 else '10');e.set(qn('w:color'),'000000');bd.append(e)
   cp.append(bd)
   for p in c.paragraphs:p.alignment=1
out=ROOT/'SVM课程作业_单栏实验扩展版_清新暖橙.docx';d.save(out);print(out)


