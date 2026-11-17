from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.analysis-deps'))
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
ROOT=Path('C:/Users/340/Desktop/6. multiple-test');OUT=ROOT/'outputs/2026-10-14';FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
R=json.loads((OUT/'results.json').read_text(encoding='utf-8'));res=pd.read_csv(OUT/'discovery_all_7129.csv');c=pd.read_csv(OUT/'candidate_validation.csv');sim=pd.read_csv(OUT/'simulation_summary.csv');bias=pd.read_csv(OUT/'selection_bias_example.csv');data=pd.read_csv(ROOT/'data/leukemia.csv')
B='#387DA0';O='#C9714D';G='#626C73';PALE='#FBF7F0';PUR='#78658E'
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':9,'axes.labelsize':10,'axes.titlesize':10,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,'figure.facecolor':PALE,'axes.facecolor':PALE,'savefig.facecolor':PALE,'pdf.fonttype':42,'svg.fonttype':'none','mathtext.fontset':'stix'})
def save(f,name):
 for ext in ['png','svg','pdf']:f.savefig(FIG/(name+'.'+ext),dpi=400,bbox_inches='tight',pad_inches=.12)
 plt.close(f)
def panel(ax,letter,title):
 ax.set_title(title,loc='left',pad=12);ax.text(-.12,1.08,letter,transform=ax.transAxes,weight='bold',fontsize=13)
# Study schematic with precise counts and locked validation.
f=plt.figure(figsize=(9,4.0));ax=f.add_axes([0,0,1,1]);ax.set(xlim=(0,100),ylim=(0,45));ax.axis('off')
def box(x,y,w,h,title,body,fill):
 ax.add_patch(Rectangle((x,y),w,h,facecolor=fill,edgecolor='#C9B8A5',lw=.8));ax.text(x+w/2,y+h-3,title,ha='center',va='center',weight='bold',fontsize=11);ax.text(x+w/2,y+h/2-1,body,ha='center',va='center',fontsize=10,linespacing=1.5)
def arrow(x,y,xx,yy):ax.add_patch(FancyArrowPatch((x,y),(xx,yy),arrowstyle='-|>',mutation_scale=12,color=G,lw=1.2))
box(2,26,27,16,'a  原始表达样本','72 份样本 × 7,129 个探针\nALL 47；AML 25','#F6E6D8')
box(36,26,28,16,'b  发现部分 train','38 份：ALL 27；AML 11\n逐探针双侧 Welch t 检验','#EAF1F3')
box(71,26,27,16,'c  完整家族校正','Raw 1,694；Bonferroni 26\nBH 535（阈值 0.05）','#F8E7DC')
arrow(29,34,36,34);arrow(64,34,71,34)
box(71,3,27,16,'d  锁定 10 个候选','发现集 BH 显著者\n按原始 p 值排序取前 10','#F6E6D8')
box(36,3,28,16,'e  留出部分 test','34 份：ALL 20；AML 14\n候选家族 Bonferroni 校正','#EAF1F3')
box(2,3,27,16,'f  评价重复性','10 / 10 方向一致\n7 / 10 满足验证判据','#F8E7DC')
arrow(84.5,26,84.5,19);arrow(71,11,64,11);arrow(36,11,29,11)
save(f,'figure1_design')
# Long-run simulation errors and power.
f,axs=plt.subplots(1,3,figsize=(9,3.25))
for ax,metric,letter,title in zip(axs,['FWER','FDR','power'],'abc',['至少一次假发现的概率','错误发现比例的期望','真实信号检出比例']):
 ds=[0,.5,1] if metric!='power' else [.5,1]
 for j,(method,col) in enumerate([('Raw',G),('Bonferroni',B),('BH',O)]):
  vals=[float(sim[(sim.delta==d)&(sim.method==method)][metric].iloc[0]) for d in ds];xx=np.arange(len(ds))+(j-1)*.23;ax.bar(xx,vals,width=.21,color=col,label=method)
 ax.set_xticks(range(len(ds)),[f'δ = {v:g}' for v in ds]);ax.set_ylim(0,1.08);ax.set_ylabel(metric if metric!='power' else 'Power');panel(ax,letter,title)
 if metric!='power':ax.axhline(.05,color=PUR,ls='--',lw=1)
handles,labels=axs[0].get_legend_handles_labels();f.legend(handles,labels,frameon=False,fontsize=9,loc='lower center',ncol=3);f.tight_layout(w_pad=1.6,rect=[0,.10,1,1]);save(f,'figure2_simulation')
# Raw p histogram, counts, standardized effect evidence, BH decision rule.
f,axs=plt.subplots(2,2,figsize=(9,6.2));ax=axs[0,0];ax.hist(res.p,bins=np.linspace(0,1,31),color=B,edgecolor=PALE);ax.set(xlabel='Raw p',ylabel='Number of probes');panel(ax,'a','发现部分的原始 p 值分布')
ax=axs[0,1];names=['Raw','Bonferroni','BH'];ns=[R['counts'][x] for x in names];ax.bar(names,ns,color=[G,B,O],width=.55);ax.set(ylabel='Number of discoveries',ylim=(0,1900));[ax.text(j,n+35,str(n),ha='center') for j,n in enumerate(ns)];panel(ax,'b','相同阈值下的发现数量')
ax=axs[1,0];cat=np.where(res.bonf<=.05,2,np.where(res.bh<=.05,1,0))
for k,col,label in [(0,'#BBB7B0','BH > 0.05'),(1,O,'BH ≤ 0.05 only'),(2,B,'Bonferroni ≤ 0.05')]:
 ix=cat==k;ax.scatter(res.d[ix],-np.log10(res.p[ix]),s=7,c=col,alpha=.65,edgecolor='none',label=label)
ax.axhline(-np.log10(R['bonf_threshold']),ls='--',color=B,lw=.7);ax.set(xlabel='Cohen d (AML − ALL)',ylabel='−log₁₀(raw p)');ax.legend(frameon=False,fontsize=7,loc='upper left');panel(ax,'c','效应大小与统计证据')
ax=axs[1,1];ps=np.sort(res.p);rk=np.arange(1,len(ps)+1);ax.loglog(rk,ps,color=G,lw=1,label='Ordered raw p');ax.loglog(rk,.05*rk/len(ps),color=O,lw=1.2,label='BH: 0.05 × rank / m');ax.axhline(R['bonf_threshold'],color=B,ls='--',lw=.8,label='Bonferroni');ax.scatter([535],[ps[534]],color=O,s=22,zorder=5);ax.annotate('k = 535',xy=(535,ps[534]),xytext=(75,.05),arrowprops={'arrowstyle':'-','color':G},fontsize=8);ax.set(xlabel='Rank',ylabel='Raw p threshold');ax.legend(frameon=False,fontsize=7,loc='lower right');panel(ax,'d','BH 阶梯法与固定阈值')
f.tight_layout(w_pad=2,h_pad=2.2);save(f,'figure3_discovery')
# Selection correction comparison.
f,ax=plt.subplots(figsize=(8.7,2.6));ix=np.arange(1,21);ax.plot(ix,bias.bh,'o-',ms=4,color=B,label='Full family: m = 7,129');ax.plot(ix,bias.wrong_bh,'s-',ms=3,color=O,label='Selected top 20 only (invalid)');ax.set(yscale='log',xlabel='Rank among selected 20 probes',ylabel='BH adjusted p',xticks=[1,5,10,15,20]);ax.legend(frameon=False,loc='lower right',fontsize=8);panel(ax,'a','事后缩小检验家族会使校正值过小');f.tight_layout();save(f,'figure4_selection')
# Fixed candidates, ordered groups; training moments define all z scores.
groups=[('train','ALL'),('train','AML'),('test','ALL'),('test','AML')];ordered=pd.concat([data[(data.original_split==split)&(data.diagnosis==diag)] for split,diag in groups]);tr=data[data.original_split=='train'];mu=tr[c.probe].mean();sd=tr[c.probe].std();z=((ordered[c.probe]-mu)/sd).to_numpy().T
f,ax=plt.subplots(figsize=(9,3.35));cmap=LinearSegmentedColormap.from_list('blue_cream_orange',[B,PALE,O]);im=ax.imshow(z,aspect='auto',cmap=cmap,vmin=-2.5,vmax=2.5,interpolation='nearest');ax.set_yticks(range(10),c.probe,fontsize=8);ax.set_xticks([13,32,47.5,64.5],['发现 ALL\nn = 27','发现 AML\nn = 11','验证 ALL\nn = 20','验证 AML\nn = 14']);ax.tick_params(length=0);[ax.axvline(x,color=PALE,lw=2.5) for x in [26.5,37.5,57.5]];cb=f.colorbar(im,ax=ax,pad=.025,fraction=.03);cb.set_label('Discovery-standardized expression (z)');panel(ax,'b','锁定候选在发现与留出样本中的表达');f.tight_layout();save(f,'figure5_heatmap')
# Validation family intervals at 99.5%, alongside discovery nominal 95%.
va=data[(data.original_split=='test')&(data.diagnosis=='AML')][c.probe].to_numpy();vb=data[(data.original_split=='test')&(data.diagnosis=='ALL')][c.probe].to_numpy();v1=va.var(0,ddof=1)/len(va);v0=vb.var(0,ddof=1)/len(vb);se=np.sqrt(v1+v0);df=(v1+v0)**2/(v1*v1/(len(va)-1)+v0*v0/(len(vb)-1));crit=stats.t.ppf(1-.05/(2*len(c)),df);c['lo_bonf_validation']=c.delta_validation-crit*se;c['hi_bonf_validation']=c.delta_validation+crit*se;c.to_csv(OUT/'candidate_validation.csv',index=False,encoding='utf-8-sig')
f,axs=plt.subplots(1,2,figsize=(9,4.7),sharey=True)
for ax,split,lo,hi,col,letter,title in [(axs[0],'discovery','lo_discovery','hi_discovery',B,'a','发现部分：逐项 95% CI'),(axs[1],'validation','lo_bonf_validation','hi_bonf_validation',O,'b','验证部分：Bonferroni 同时区间')]:
 vals=c['delta_'+split];err=[vals-c[lo],c[hi]-vals];ax.errorbar(vals,np.arange(10),xerr=err,fmt='o',ms=4,capsize=3,color=col);ax.axvline(0,ls='--',lw=.8,c=G);ax.set(xlabel='Mean difference (AML − ALL)',yticks=range(10));panel(ax,letter,title)
axs[0].set_yticklabels(c.probe,fontsize=8);axs[0].invert_yaxis();axs[1].set_yticks(range(10));axs[0].set_xlim(-7500,2500);axs[1].set_xlim(-7500,2500)
for i,row in c.iterrows():axs[1].text(2550,i,'通过' if row.replicated else '未通过',va='center',fontsize=8,color=O if row.replicated else G,clip_on=False)
f.tight_layout(w_pad=2.5,rect=[0,0,.96,1]);save(f,'figure6_validation')
# Leading candidate sample distributions, not a new selection.
probe=c.probe.iloc[0];f,axs=plt.subplots(1,2,figsize=(8.8,3.1),sharey=True);rng=np.random.default_rng(20261014)
for ax,split,letter,title in [(axs[0],'train','a','发现部分'),(axs[1],'test','b','留出验证部分')]:
 sub=data[data.original_split==split]
 for j,(diag,col) in enumerate([('ALL',B),('AML',O)]):
  vals=sub.loc[sub.diagnosis==diag,probe].to_numpy();ax.scatter(rng.normal(j,.06,len(vals)),vals,s=17,color=col,alpha=.75,edgecolor='none');ax.plot([j-.2,j+.2],[vals.mean()]*2,color='black',lw=1.3)
 ax.set_xticks([0,1],[f'ALL (n = {(sub.diagnosis=="ALL").sum()})',f'AML (n = {(sub.diagnosis=="AML").sum()})']);ax.set_xlim(-.5,1.5);panel(ax,letter,title)
axs[0].set_ylabel('Expression (original scale)');f.suptitle(probe,fontsize=11,y=1.02);f.tight_layout();save(f,'figure7_candidate')
print('Saved 7 figures, PNG/SVG/PDF')
