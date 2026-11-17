from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.analysis-deps'))
import numpy as np
import pandas as pd
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager

OUT=ROOT/'outputs'/'study_framework'; OUT.mkdir(exist_ok=True)
font_manager.fontManager.addfont('C:/Windows/Fonts/msyh.ttc')
plt.rcParams.update({'font.family':'Microsoft YaHei','font.size':10,'axes.unicode_minus':False,'pdf.fonttype':42,'svg.fonttype':'none','mathtext.fontset':'dejavusans'})
df=pd.read_csv(ROOT/'data/heart-disease-hypothesis.csv')
valid=df.dropna(subset=['thalach','disease'])
assert len(df)==920 and len(valid)==865
BLUE='#2878A0'; RED='#C75B45'; INK='#22272B'; GREY='#657078'; LIGHT='#E0E5E8'
fig=plt.figure(figsize=(13.2,6.6),facecolor='white')
axes=[fig.add_axes([.035,.12,.33,.77]),fig.add_axes([.395,.12,.25,.77]),fig.add_axes([.685,.12,.285,.77])]
for ax in axes: ax.set(xlim=(0,1),ylim=(0,1)); ax.axis('off')
def text(ax,x,y,s,size=10,color=INK,weight='normal',ha='center',va='center',**kw):
    return ax.text(x,y,s,fontsize=size,color=color,fontweight=weight,ha=ha,va=va,linespacing=1.6,**kw)
def box(ax,x,y,w,h,s,edge=LIGHT,fill='white',size=10,color=INK,weight='normal'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.004,rounding_size=0.008',linewidth=.9,edgecolor=edge,facecolor=fill))
    text(ax,x+w/2,y+h/2,s,size,color,weight)
def arrow(ax,x1,y1,x2,y2):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',color=GREY,lw=1,mutation_scale=10,shrinkA=1,shrinkB=1))
for ax,letter,title in zip(axes,'abc',['研究对象与观察性分组','主要终点与效应定义','统计假设与双侧检验']):
    text(ax,0,1.05,letter,16,weight='bold',ha='left'); text(ax,.08,1.05,title,12,weight='bold',ha='left')
a,b,c=axes
text(a,.5,.965,'四中心横断面资料',10.5,color=GREY)
sites=[('Cleveland',303),('Hungary',294),('Switzerland',123),('VA Long Beach',200)]
for i,(name,n) in enumerate(sites):
    box(a,.02+(i%2)*.5,.79-(i//2)*.125,.46,.105,f'{name}\nn = {n}',size=9.5,fill='#F6F8F9')
for x in [.25,.75]:
    a.plot([x,x],[.66,.625],color=GREY,lw=.9)
a.plot([.25,.75],[.625,.625],color=GREY,lw=.9)
arrow(a,.5,.625,.5,.59)
box(a,.24,.49,.52,.10,'原始样本  n = 920',size=11,weight='bold')
arrow(a,.5,.49,.5,.33)
a.plot([.5,.70],[.415,.415],color=GREY,lw=.9)
arrow(a,.70,.415,.75,.415)
box(a,.755,.367,.235,.096,'心率缺失\nn = 55',size=9,fill='#F3F4F5')
box(a,.19,.225,.62,.105,'主要分析样本  n = 865',size=11,weight='bold')
a.plot([.5,.5],[.225,.19],color=GREY,lw=.9)
a.plot([.25,.75],[.19,.19],color=GREY,lw=.9)
arrow(a,.25,.19,.25,.155); arrow(a,.75,.19,.75,.155)
box(a,.02,.035,.46,.12,'无疾病证据\ndisease = 0  |  n = 391',edge=BLUE,fill='#F0F7FA',size=9.5,color=BLUE)
box(a,.52,.035,.46,.12,'有疾病证据\ndisease = 1  |  n = 474',edge=RED,fill='#FCF3F0',size=9.5,color=RED)
text(a,.5,-.025,'按已有疾病证据分组，非随机分配',9,color=GREY)

text(b,.5,.945,'预先指定的主要终点',10.5,color=GREY)
box(b,.035,.73,.93,.155,'最大运动心率\nthalach  ·  bpm',edge=INK,size=14,weight='bold')
text(b,.5,.665,'分析单位：每名受试者',10.5)
text(b,.5,.615,'每人一条记录，无前后配对测量',9,color=GREY)
text(b,.5,.505,'总体均值差',11,weight='bold')
text(b,.5,.421,r'$\Delta = \mu_{1} - \mu_{0}$',23)
text(b,.5,.335,r'$\mu_1$：有疾病证据组的总体均值',9.5,color=RED)
text(b,.5,.28,r'$\mu_0$：无疾病证据组的总体均值',9.5,color=BLUE)
b.plot([.1,.9],[.21,.21],color=LIGHT,lw=.9)
text(b,.5,.155,'Δ < 0：疾病组平均心率更低',10)
text(b,.5,.095,'Δ > 0：疾病组平均心率更高',10)
text(b,.5,-.025,'目标：估计组间差异及其不确定性',9,color=GREY)

box(c,.02,.77,.96,.155,'$H_0$：Δ = 0\n$H_1$：Δ ≠ 0',size=15,weight='bold',fill='#F6F8F9')
text(c,.5,.70,'双侧 Welch t 检验  ·  α = 0.05',10.5)
curve=fig.add_axes([.712,.365,.235,.235])
nu=837.1762389406794; critical=t.ppf(.975,nu); xx=np.linspace(-4,4,1000); yy=t.pdf(xx,nu)
curve.plot(xx,yy,color=INK,lw=1.4)
for select in [xx<=-critical,xx>=critical]: curve.fill_between(xx,0,yy,where=select,color=RED,alpha=.65)
curve.axhline(0,color=GREY,lw=.7)
for v in [-critical,critical]: curve.plot([v,v],[0,t.pdf(v,nu)],color=RED,lw=.8,ls='--')
curve.set_xlim(-4,4); curve.set_ylim(-.012,.48)
curve.set_xticks([-critical,0,critical],['−t*','0','+t*'],fontsize=9)
curve.set_yticks([])
for spine in curve.spines.values(): spine.set_visible(False)
curve.tick_params(length=0)
curve.text(-2.6,.135,'0.025',color=RED,ha='center',fontsize=9)
curve.text(2.6,.135,'0.025',color=RED,ha='center',fontsize=9)
curve.text(0,.455,'$H_0$ 下检验统计量的分布',ha='center',fontsize=9,color=GREY)
curve.text(0,.15,'不拒绝 $H_0$',ha='center',fontsize=9,color=GREY)
text(c,.5,.245,'两侧阴影：拒绝域，总面积为 0.05',9,color=RED)
text(c,.5,.175,'报告均值差、95% CI 与双侧 p 值',10)
text(c,.5,.095,'p < 0.05：拒绝 $H_0$\np ≥ 0.05：未拒绝 $H_0$',10)
text(c,.5,-.025,'概念示意，不是实际心率分布',9,color=GREY)
fig.text(.5,.025,'研究问题：心脏病证据是否与最大运动心率有关？    |    观察性关联不等于因果关系',ha='center',fontsize=10,color=INK)
for ext in ['png','pdf','svg']:
    fig.savefig(OUT/f'研究设计与假设框架图.{ext}',dpi=450,facecolor='white',bbox_inches='tight',pad_inches=.16)
plt.close(fig)
print(OUT)
