from pathlib import Path
import sys,json
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Rectangle
from docx import Document
from docx.shared import Cm
R=Path(__file__).resolve().parents[1];G=R/'outputs/figures';r=json.loads((R/'outputs/分析结果.json').read_text(encoding='utf-8'))
B='#387DA0';O='#C9714D';K='#29343B';BG='#F7F0E6';EDGE='#CBB7A2'
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':11,'text.color':K,'axes.unicode_minus':False,'svg.fonttype':'none'})
f=plt.figure(figsize=(13,6.1),facecolor=BG);ax=f.add_axes([0,0,1,1]);ax.set(xlim=(0,13),ylim=(0,6.1));ax.axis('off')
def box(x,y,w,h,color=BG):ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.025,rounding_size=.07',facecolor=color,edgecolor=EDGE,lw=.8))
def txt(x,y,t,size=11,ha='left',color=K,weight='normal'):ax.text(x,y,t,fontsize=size,ha=ha,va='center',color=color,fontweight=weight,linespacing=1.5)
def arrow(points,color=K,dashed=False):
 for a,b in zip(points[:-2],points[1:-1]):ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=1,ls='--' if dashed else '-')
 ax.annotate('',xy=points[-1],xytext=points[-2],arrowprops=dict(arrowstyle='-|>',lw=1,color=color,linestyle='--' if dashed else '-'))
def panel(x,y,w,h,letter,title):
 box(x,y,w,h);txt(x+.15,y+h-.25,letter,16,weight='bold');txt(x+.5,y+h-.25,title,12,weight='bold')
# The full-width first panel separates development from the held-out data.
panel(.18,4.55,12.64,1.35,'a','研究问题与数据准备')
txt(.55,5.12,'13 项混合类型输入 → 心脏病标签',12)
txt(.55,4.82,'270 条记录：120 阳性 / 150 阴性',10)
arrow([(4.05,5.05),(4.45,5.05)])
box(4.5,4.75,2.6,.68,'#EEDDCB');txt(5.8,5.17,'缺失审计与固定划分',11,ha='center');txt(5.8,4.91,'分层 80 / 20；seed = 2026',10,ha='center')
arrow([(7.15,5.05),(7.55,5.05)])
txt(7.65,5.16,'开发集 216 条',12,color=B,weight='bold');txt(7.65,4.88,'训练、比较与阈值选择',10)
box(10.25,4.75,2.25,.68,'#EEE9E2');txt(11.375,5.17,'留出测试 54 条',11,ha='center');txt(11.375,4.91,'方案固定后使用',10,ha='center')
# Middle: preprocessing, parallel model explanations, and validation evidence.
panel(.18,2.05,3.42,2.18,'b','无泄漏预处理')
txt(.48,3.52,'仅在每个训练折内拟合',11,color=B)
txt(.48,3.17,'连续变量：中位数填补 → 标准化',10)
txt(.48,2.84,'分类变量：众数填补 → 参照编码',10)
for i in range(5):
 for j in range(5):ax.add_patch(Rectangle((.52+j*.24,2.24+i*.065),.205,.045,facecolor=O if j==i else '#A9C4D2',edgecolor='none'))
txt(1.94,2.43,'5 折 × 5 次重复',10);txt(1.94,2.19,'验证折只做转换',9)
panel(3.86,2.05,5.04,2.18,'c','两条概率建模路径')
txt(4.1,3.52,'Logistic 回归',12,color=B,weight='bold');txt(6.65,3.52,'LDA',12,color=O,weight='bold')
txt(4.1,3.20,'线性评分 → sigmoid → P(Y | X)',10)
txt(6.65,3.20,'类条件密度 × 先验 → 后验',10)
txt(4.1,2.90,'交叉熵 + L2 惩罚',10);txt(6.65,2.90,'类内正态；共享协方差',10)
ax.plot([6.4,6.4],[2.28,3.65],color=EDGE,lw=.6)
z=np.linspace(-4,4,100);ax.plot(4.15+(z+4)/5,2.22+.43/(1+np.exp(-z)),color=B,lw=1.7)
xx=np.linspace(-3,4,120)
for mu,col in [(0,B),(1.6,O)]:ax.plot(6.7+(xx+3)*.23,2.22+.43*np.exp(-.5*(xx-mu)**2),color=col,lw=1.5)
txt(5.95,2.31,'示意',8,ha='right');txt(8.57,2.31,'示意',8,ha='right')
panel(9.15,2.05,3.67,2.18,'d','开发集评价')
txt(9.45,3.52,'区分：ROC-AUC / AP',11)
txt(9.45,3.17,'概率：Brier / 交叉熵 / 校准',10)
txt(9.45,2.83,'解释：OR、参数量与稳定性',10)
txt(9.45,2.45,'对照：先验基线、Gaussian NB',10,color='#75695F')
arrow([(8.4,4.55),(8.4,4.39),(1.9,4.39),(1.9,4.23)],B)
arrow([(3.6,3.0),(3.86,3.0)])
arrow([(8.9,3.0),(9.15,3.0)])
# Bottom: all development decisions precede the test evaluation.
panel(.18,.18,7.55,1.55,'e','任务代价与方案固定')
txt(.48,.99,'阈值网格 0.10–0.90',11)
txt(.48,.59,'最小化平均 5×FN + FP',10)
arrow([(3.18,.84),(3.60,.84)])
txt(3.8,.99,'L2 Logistic：C = 1；阈值 = 0.20',11,color=B,weight='bold')
txt(3.8,.59,'固定预处理与指标 → 全开发集拟合',10)
panel(8.0,.18,4.82,1.55,'f','固定测试与结论边界')
txt(8.3,.99,'54 条记录：TP 23 / FN 1 / TN 14 / FP 16',10)
txt(8.3,.59,'指标与 bootstrap 区间；限定内部评价',10)
arrow([(10.9,2.05),(10.9,1.90),(1.9,1.90),(1.9,1.73)])
arrow([(7.73,.82),(8.0,.82)],B)
# Reserved test data bypasses all development-stage choices.
arrow([(12.58,4.75),(12.94,4.75),(12.94,.99),(12.82,.99)],'#8C8176',True)
png=G/'图1_线性分类模型整体流程.png';svg=G/'图1_线性分类模型整体流程.svg'
f.savefig(png,dpi=300,facecolor=BG);f.savefig(svg,facecolor=BG);plt.close(f)
src=R/'线性模型课程作业_完成稿.docx';doc=Document(src)
pic=doc.inline_shapes[0];rid=pic._inline.graphic.graphicData.pic.blipFill.blip.embed
doc.part.related_parts[rid]._blob=png.read_bytes();pic.width=Cm(17.4);pic.height=Cm(17.4*6.1/13)
for p in doc.paragraphs:
 if p.text.startswith('图1 '):
  p.clear();p.add_run('图1 线性分类模型的整体研究与评价流程。').bold=True
  p.add_run('a，审计数据并划分开发与留出测试集。b–d，在训练折内预处理，对照两条概率建模路径并评价折外预测。e，仅依据开发证据选择阈值并固定方案。f，最终测试与结论边界。蓝色突出Logistic路径，橙色表示LDA与验证折；实线为分析流程，灰虚线为预留测试数据通路。曲线为概念示意。')
out=R/'线性模型课程作业_完成稿_流程图更新版.docx';doc.save(out);print(out)
