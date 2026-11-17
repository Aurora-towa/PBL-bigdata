from pathlib import Path
import sys, json, hashlib
ROOT = Path(__file__).resolve().parents[1]
if (ROOT / '.analysis-deps').exists(): sys.path.insert(0, str(ROOT / '.analysis-deps'))
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict, LeaveOneGroupOut
from sklearn.metrics import roc_auc_score, roc_curve, brier_score_loss
from sklearn.calibration import calibration_curve
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
d=pd.read_csv(ROOT/'data/heart-disease-hypothesis.csv')
assert d.record_id.is_unique and (d.disease == (d.num>0).astype(int)).all()
cols=['age','sex','trestbps','chol','thalach','oldpeak']
d[cols].isna().sum().rename('missing_n').to_csv(OUT/'missingness.csv',encoding='utf-8-sig')
main=d.dropna(subset=['disease','thalach']).copy()
x=main.loc[main.disease==1,'thalach'].to_numpy(); y=main.loc[main.disease==0,'thalach'].to_numpy()
def welch(a,b):
    va=a.var(ddof=1)/len(a); vb=b.var(ddof=1)/len(b)
    se=np.sqrt(va+vb); df=(va+vb)**2/(va**2/(len(a)-1)+vb**2/(len(b)-1))
    delta=a.mean()-b.mean(); ci=delta+np.array([-1,1])*stats.t.ppf(.975,df)*se
    test=stats.ttest_ind(a,b,equal_var=False)
    return dict(delta=float(delta),lo=float(ci[0]),hi=float(ci[1]),p=float(test.pvalue),t=float(test.statistic),df=float(df))
w=welch(x,y)
sp=np.sqrt(((len(x)-1)*x.var(ddof=1)+(len(y)-1)*y.var(ddof=1))/(len(x)+len(y)-2))
g=(1-3/(4*(len(x)+len(y)-2)-1))*w['delta']/sp
desc=main.groupby('disease').thalach.agg(['count','mean','std','median','min','max'])
desc['q1']=main.groupby('disease').thalach.quantile(.25); desc['q3']=main.groupby('disease').thalach.quantile(.75)
desc.to_csv(OUT/'group_summary.csv',encoding='utf-8-sig')
models=[]
for label,formula in [('Unadjusted','thalach ~ disease'),('Age + sex','thalach ~ disease + age + sex'),('Age + sex + site','thalach ~ disease + age + sex + C(site)'),('Age squared + sex + site','thalach ~ disease + age + I(age**2) + sex + C(site)')]:
    m=smf.ols(formula,main).fit(cov_type='HC3'); ci=m.conf_int().loc['disease']
    models.append(dict(model=label,n=int(m.nobs),beta=float(m.params['disease']),lo=float(ci.iloc[0]),hi=float(ci.iloc[1]),p=float(m.pvalues['disease'])))
pd.DataFrame(models).to_csv(OUT/'adjusted_models.csv',index=False,encoding='utf-8-sig')
sites=[]
for site,s in main.groupby('site'):
    a=s.loc[s.disease==1,'thalach'].to_numpy(); b=s.loc[s.disease==0,'thalach'].to_numpy()
    sites.append(dict(site=site,n1=len(a),n0=len(b),**welch(a,b)))
pd.DataFrame(sites).to_csv(OUT/'site_effects.csv',index=False,encoding='utf-8-sig')
u=stats.mannwhitneyu(x,y,alternative='two-sided'); superiority=u.statistic/(len(x)*len(y))
r=stats.pearsonr(main.age,main.thalach); rho=stats.spearmanr(main.age,main.thalach)
tab=pd.crosstab(d.sex,d.disease); chi,pchi,dof,expected=stats.chi2_contingency(tab,correction=False)
proportions=[]
for sex,s in d.groupby('sex'):
    k=int(s.disease.sum()); n=len(s); lo,hi=proportion_confint(k,n,method='wilson')
    proportions.append(dict(sex='Female' if sex==0 else 'Male',k=k,n=n,rate=k/n,lo=lo,hi=hi))
X=d[['age','sex','thalach']]; target=d.disease.astype(int)
cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=20261013)
pipe=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler(),LogisticRegression(max_iter=2000))
pred=cross_val_predict(pipe,X,target,cv=cv,method='predict_proba')[:,1]
pred_site=cross_val_predict(pipe,X,target,cv=LeaveOneGroupOut(),groups=d.site,method='predict_proba')[:,1]
auc=roc_auc_score(target,pred); brier=brier_score_loss(target,pred); auc_site=roc_auc_score(target,pred_site)
rng=np.random.default_rng(20261013); boots=[]
for i in range(2000):
    idx=rng.integers(0,len(d),len(d))
    if len(np.unique(target.iloc[idx]))==2: boots.append(roc_auc_score(target.iloc[idx],pred[idx]))
auc_ci=np.quantile(boots,[.025,.975])
pd.DataFrame({'record_id':d.record_id,'disease':target,'oof_probability':pred,'leave_site_out_probability':pred_site}).to_csv(OUT/'prediction_oof.csv',index=False)
result=dict(total=len(d),complete=len(main),missing_thalach=int(d.thalach.isna().sum()),welch=w,hedges_g=float(g),mannwhitney_p=float(u.pvalue),probability_disease_greater=float(superiority),pearson_r=float(r.statistic),pearson_p=float(r.pvalue),spearman_r=float(rho.statistic),spearman_p=float(rho.pvalue),chi2=float(chi),chi2_p=float(pchi),chi2_expected_min=float(expected.min()),auc=float(auc),auc_ci=auc_ci.tolist(),brier=float(brier),leave_site_out_auc=float(auc_site),models=models,sites=sites,source_sha256=hashlib.sha256((ROOT/'data/heart-disease-hypothesis.csv').read_bytes()).hexdigest())
(OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')

# Original figures, using distribution, interval and panel conventions from the cited papers.
BLUE='#2878A0'; RED='#C75B45'; GRAY='#626B73'
plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.labelsize':10,'axes.titlesize':10,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.8,'xtick.direction':'out','ytick.direction':'out','pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
def save(fig,name):
    for ext in ['png','pdf','svg']: fig.savefig(OUT/f'{name}.{ext}',dpi=400,bbox_inches='tight')
    plt.close(fig)
def panel(ax,letter,title):
    ax.text(-.14,1.08,letter,transform=ax.transAxes,fontweight='bold',fontsize=13)
    ax.set_title(title,loc='left',pad=12)
fig,axs=plt.subplots(1,2,figsize=(7.2,3.35),gridspec_kw={'width_ratios':[1.25,1]})
for i,(a,c) in enumerate([(y,BLUE),(x,RED)]):
    axs[0].scatter(rng.normal(i,.065,len(a)),a,s=7,color=c,alpha=.22,edgecolors='none',rasterized=True)
bp=axs[0].boxplot([y,x],positions=[0,1],widths=.34,showfliers=False,patch_artist=True,medianprops={'color':'black','linewidth':1.2})
for box,c in zip(bp['boxes'],[BLUE,RED]): box.set(facecolor='white',edgecolor=c,linewidth=1.3)
axs[0].set_xticks([0,1],[f'No disease\nn = {len(y)}',f'Disease\nn = {len(x)}']); axs[0].set_ylabel('Maximum exercise heart rate (bpm)')
panel(axs[0],'a','Distribution by disease status')
axs[1].axvline(0,color='0.6',ls='--',lw=.8)
axs[1].errorbar(w['delta'],0,xerr=[[w['delta']-w['lo']],[w['hi']-w['delta']]],fmt='o',color=RED,capsize=4)
axs[1].set_yticks([]); axs[1].set_ylim(-.7,.7); axs[1].set_xlim(-30,4)
axs[1].set_xlabel('Mean difference (bpm)\nDisease minus no disease')
axs[1].text(.04,.85,f"Difference = {w['delta']:.2f} bpm\n95% CI {w['lo']:.2f} to {w['hi']:.2f}\nWelch P = {w['p']:.2e}",transform=axs[1].transAxes,fontsize=8.5)
panel(axs[1],'b','Primary effect estimate'); fig.tight_layout(w_pad=2); save(fig,'figure1_primary')

fig,axs=plt.subplots(1,2,figsize=(7.2,3.5))
for j,row in enumerate(models):
    axs[0].errorbar(row['beta'],j,xerr=[[row['beta']-row['lo']],[row['hi']-row['beta']]],fmt='o',color=BLUE,capsize=3)
axs[0].set_yticks(range(4),[m['model'].replace(' + ',' +\n') for m in models],fontsize=8); axs[0].invert_yaxis(); axs[0].axvline(0,color='0.6',ls='--',lw=.8); axs[0].set_xlabel('Disease coefficient (bpm), 95% CI'); axs[0].set_xlim(-28,2)
panel(axs[0],'a','Adjustment for confounding')
for j,s in enumerate(sites):
    axs[1].errorbar(s['delta'],j,xerr=[[s['delta']-s['lo']],[s['hi']-s['delta']]],fmt='o',color=RED,capsize=3)
axs[1].set_yticks(range(4),[f"{s['site']}\n{s['n1']} / {s['n0']}" for s in sites],fontsize=8); axs[1].invert_yaxis(); axs[1].axvline(0,color='0.6',ls='--',lw=.8); axs[1].set_xlabel('Within-site mean difference (bpm)'); panel(axs[1],'b','Centre-specific estimates')
fig.tight_layout(w_pad=1.6); save(fig,'figure2_adjustment')

fig,axs=plt.subplots(1,2,figsize=(7.2,3.25))
for disease,color,label in [(0,BLUE,'No disease'),(1,RED,'Disease')]:
    s=main[main.disease==disease]; axs[0].scatter(s.age,s.thalach,s=8,alpha=.22,color=color,edgecolors='none',rasterized=True,label=label)
    m=smf.ols('thalach ~ age',s).fit(cov_type='HC3'); grid=pd.DataFrame({'age':np.linspace(s.age.min(),s.age.max(),100)}); pr=m.get_prediction(grid).summary_frame()
    axs[0].plot(grid.age,pr['mean'],color=color); axs[0].fill_between(grid.age,pr['mean_ci_lower'],pr['mean_ci_upper'],color=color,alpha=.12)
axs[0].set(xlabel='Age (years)',ylabel='Maximum exercise heart rate (bpm)'); axs[0].legend(frameon=False,fontsize=8); panel(axs[0],'a','Age and exercise heart rate')
for j,s in enumerate(proportions):
    axs[1].errorbar(j,s['rate']*100,yerr=[[(s['rate']-s['lo'])*100],[(s['hi']-s['rate'])*100]],fmt='o',color=BLUE if j==0 else RED,capsize=4)
    axs[1].text(j,s['hi']*100+4,f"{s['k']}/{s['n']}",ha='center',fontsize=8)
axs[1].set_xticks([0,1],[s['sex'] for s in proportions]); axs[1].set(xlim=(-.6,1.6),ylim=(0,100),ylabel='Disease proportion (%)'); panel(axs[1],'b','Sex and disease status')
fig.tight_layout(w_pad=2); save(fig,'figure3_associations')

fig,axs=plt.subplots(1,2,figsize=(7.2,3.2))
for pr,color,label in [(pred,BLUE,f'5-fold OOF AUC = {auc:.3f}'),(pred_site,RED,f'Leave-centre-out AUC = {auc_site:.3f}')]:
    fpr,tpr,_=roc_curve(target,pr); axs[0].plot(fpr,tpr,color=color,lw=1.5,label=label)
axs[0].plot([0,1],[0,1],ls='--',color='0.65',lw=.8); axs[0].set(xlabel='False positive rate',ylabel='True positive rate',xlim=(0,1),ylim=(0,1)); axs[0].legend(frameon=False,fontsize=8,loc='lower right'); panel(axs[0],'a','Cross-validated discrimination')
fraction,meanprob=calibration_curve(target,pred,n_bins=8,strategy='quantile')
axs[1].plot([0,1],[0,1],ls='--',color='0.65',lw=.8); axs[1].plot(meanprob,fraction,'o-',color=BLUE,ms=4); axs[1].set(xlabel='Mean predicted probability',ylabel='Observed disease proportion',xlim=(0,1),ylim=(0,1)); axs[1].text(.05,.9,f'OOF Brier score = {brier:.3f}',transform=axs[1].transAxes,fontsize=8); panel(axs[1],'b','Calibration in held-out folds')
fig.tight_layout(w_pad=2); save(fig,'figure4_prediction')

# Completed student report, with explicit page boundaries for readable figures.
doc=Document(); sec=doc.sections[0]; sec.page_height=Cm(29.7); sec.page_width=Cm(21); sec.top_margin=Cm(1.8); sec.bottom_margin=Cm(1.7); sec.left_margin=Cm(1.8); sec.right_margin=Cm(1.8)
for name in ['Normal','Title','Heading 1','Heading 2']:
    st=doc.styles[name]; st.font.name='Calibri'; st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Microsoft YaHei'); st.font.color.rgb=RGBColor(0,0,0)
for st in doc.styles:
    for border in list(st._element.iter(qn('w:pBdr'))): border.getparent().remove(border)
doc.styles['Normal'].font.size=Pt(10.5); doc.styles['Normal'].paragraph_format.line_spacing=1.18; doc.styles['Normal'].paragraph_format.space_after=Pt(6)
doc.styles['Title'].font.size=Pt(22); doc.styles['Heading 1'].font.size=Pt(15); doc.styles['Heading 2'].font.size=Pt(12)
def p(t): doc.add_paragraph(t)
def h(t): doc.add_heading(t,level=1)
def page(t): doc.add_page_break(); h(t)
def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers)); t.autofit=False
    for c,s in zip(t.rows[0].cells,headers): c.text=s
    for row in rows:
        for c,s in zip(t.add_row().cells,row): c.text=str(s)
    for i,row in enumerate(t.rows):
        for j,c in enumerate(row.cells):
            if widths: c.width=Cm(widths[j])
            tcPr=c._tc.get_or_add_tcPr(); borders=OxmlElement('w:tcBorders')
            for side in ['top','left','bottom','right']:
                e=OxmlElement('w:'+side); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'4'); e.set(qn('w:color'),'D9D9D9'); borders.append(e)
            tcPr.append(borders); shade=OxmlElement('w:shd'); shade.set(qn('w:fill'),'E8EDF2' if i==0 else ('F5F7F9' if i%2==0 else 'FFFFFF')); tcPr.append(shade)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(4); par.paragraph_format.space_before=Pt(4)
                for run in par.runs: run.font.size=Pt(9); run.bold=(i==0)
        trPr=row._tr.get_or_add_trPr(); trPr.append(OxmlElement('w:cantSplit'))
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    return t
def image(name): doc.add_picture(str(OUT/(name+'.png')),width=Cm(17.0))
def pv(v): return f'{v:.3g}'
doc.add_heading('心脏病证据与最大运动心率的关联',0)
p('第五章学生工作单完成稿  |  统计检验与假设设计')
p(f"本研究使用四中心观察性横断面资料，检验有、无心脏病证据的受试者最大运动心率是否不同。主要分析包含 {len(main)} 名心率记录完整的受试者。有疾病证据组的平均最大运动心率低于无疾病证据组，均值差为 {w['delta']:.2f} bpm（95% CI {w['lo']:.2f} 至 {w['hi']:.2f}）。控制年龄、性别和来源中心后，负向关联仍然存在；该结果不能解释为疾病导致心率降低。")
h('任务一 把问题变成假设')
table(['要素','回答'],[
('研究对象','数据中来自 Cleveland、Hungary、Switzerland 和 VA Long Beach 的受试者；推断范围限于类似入选人群。'),
('比较对象','disease=1（num>0，有疾病证据）与 disease=0（num=0，无疾病证据）；这是数据标签，不是随机处理组。'),
('主要终点','最大运动心率 thalach，单位 bpm；主要效应量定义为疾病组减无疾病组的总体均值差。'),
('分析单位','每名受试者一条记录；不把不同中心作为四个随机实验组。'),
('H0','μ疾病 − μ无疾病 = 0，两组总体平均最大运动心率相等。'),
('H1','μ疾病 − μ无疾病 ≠ 0，两组总体平均最大运动心率不同。'),
('显著性水平','α=0.05，主要终点进行一次双侧检验。'),
('双侧的理由','研究问题是是否不同；增加和降低都可能有研究意义，不能看完结果再改成单侧。')],[3,14])
p('分析原则：以工作单已指定的 thalach 为主要终点；年龄关联、性别比例、模型调整和疾病预测均作为补充或探索性分析，分别解释，不以其中最小的 p 值替代主要结果。')

page('任务二 错误类型与统计功效')
doc.add_heading('两类错误的具体含义',2)
p('Type I error（假阳性）：两组总体平均最大运动心率实际相等，却拒绝 H0，报告两组均值不同。在检验假设和模型成立、分析策略固定的前提下，α=0.05 控制长期重复检验的此类错误概率；它不是“本次结论有 5% 概率错误”。')
p('Type II error（假阴性）：两组总体均值实际存在差异，但未拒绝 H0。其概率为 β；power=1−β 表示在给定真实效应下检出差异的概率。')
doc.add_heading('什么会影响 power',2)
table(['因素','其他条件相同时的影响'],[
('样本量','有效样本量增加会减小标准误，提高 power；严重组间不平衡、缺失与中心差异可能降低信息量。'),
('真实效应','真实均值差的绝对值越大，相对于个体变异越容易识别，power 通常越高。'),
('测量噪声','测量误差和个体变异越大，标准误通常越大，power 越低。增加同源低质量记录不能消除系统偏差。'),
('检验设定','在其他条件相同时，更严格的 α 或多重校正会降低 power；应预先确定，不能为了显著而更改。')],[3,14])
doc.add_heading('未拒绝 H0 的解释边界',2)
p('未拒绝 H0 只表示当前数据不足以排除零差异，不等于证明两组相同，也不等于没有实际意义。应查看 95% CI 是否仍包含较大的差异。如果要证明差异足够小，需事先规定实际等效界值，并使用等效性检验。')
p('本次不报告用观察到的效应反推的“事后 power”；主要结果以效应量和置信区间说明估计精度。未来样本量设计需要先给出最小有意义差异、预期标准差、α 与目标 power。')

page('任务三 选择统计方法')
table(['问题','首选方法','关键假设','备选方法'],[
('两独立疾病组的 thalach','双侧 Welch 独立样本 t 检验','受试者相互独立；均值有意义；无支配结果的极端异常值。无需等方差。','严重偏态或异常值时考虑稳健均值或 bootstrap；Mann–Whitney U 比较分布，不自动等于中位数检验。'),
('同一患者前后测量','配对 t 检验','同一人的记录正确配对；不同人独立；小样本时差值近似正态。','差值对称时用 Wilcoxon 符号秩检验；不对称可考虑符号检验；多时点可用混合模型。'),
('sex 与 disease 比例','Pearson χ² 独立性检验','分类计数来自独立受试者；期望频数足够。','稀疏 2×2 表用 Fisher 精确检验；控制混杂时用 logistic 回归。'),
('age 与 thalach 关联','Pearson 相关及线性回归','独立记录、关系近似线性；检查离群值。经典推断需误差假设，回归可用稳健标准误。','单调但非线性时用 Spearman；明显非线性时考虑样条；调整性别、中心和疾病状态。'),
('预测 disease','Logistic 回归加交叉验证','二元结局；特征不能含标签泄露；连续特征的 logit 形式合理；训练测试分离。','非线性模型可探索，但要同一验证方案；同时评估判别、校准及跨中心泛化。')],[2.6,3.8,5.5,5.1])
p('独立样本与配对样本不能互换：当前文件没有前后时间变量与同一人的重复测量，因此配对题只给方法，不计算配对结果。')
p('中心差异会影响合并比较：主检验报告未调整差异，同时用年龄、性别和中心固定效应的线性模型进行敏感性分析。只有四个中心，简单使用中心聚类稳健标准误的渐近可靠性有限；本报告使用个体层面的 HC3 标准误并明确独立性限制。')

page('任务四 报告一个主要结果')
p(f"原始数据 {len(d)} 人，疾病组 {int(d.disease.sum())} 人、无疾病组 {int((d.disease==0).sum())} 人。thalach 缺失 {int(d.thalach.isna().sum())} 人；主分析保留 {len(main)} 人，不对主要终点插补。疾病组缺失 35/509（6.9%），无疾病组缺失 20/411（4.9%）；VA Long Beach 缺失 53/200（26.5%），提示缺失具有中心差异。以下为有效样本的描述统计。")
table(['疾病状态','n','均值 ± SD','中位数 [Q1, Q3]'],[(('无疾病证据' if idx==0 else '有疾病证据'),int(s['count']),f"{s['mean']:.2f} ± {s['std']:.2f}",f"{s['median']:.1f} [{s['q1']:.1f}, {s['q3']:.1f}]") for idx,s in desc.iterrows()],[4,2,5,6])
image('figure1_primary')
p('图 1 疾病状态与最大运动心率。a，每个散点为一名受试者，横向抖动只用于减少遮挡；箱体为 Q1 至 Q3，横线为中位数，须线至 1.5×IQR 内最远观测值。超出须线的数据仍显示为散点并纳入分析。b，点为疾病组减无疾病组的均值差，误差线为 Welch 95% CI；虚线表示零差异。')
p(f"双侧 Welch 检验得到 t={w['t']:.3f}，自由度={w['df']:.2f}，p={pv(w['p'])}；均值差={w['delta']:.2f} bpm（95% CI {w['lo']:.2f} 至 {w['hi']:.2f}），标准化效应量 Hedges g={g:.3f}（负值表示疾病组较低）。在 α=0.05 下拒绝 H0。")
p(f"组间平均差约 {abs(w['delta']):.1f} bpm，具有可描述的量级，但尚未规定临床最小有意义差异，因此不能仅凭 p 值认定临床获益或诊断价值。组间分布有重叠，不能据此用单个人的心率确定疾病状态。")

page('任务五 混杂控制与敏感性分析')
p('年龄、性别和来源中心是本次优先考虑的混杂来源：年龄结构可能同时影响疾病证据与运动心率；性别与两者可能相关；中心在入选人群、检查流程及记录完整性上可能不同。分析以 disease 为解释变量、thalach 为结局，逐步加入年龄、性别和中心固定效应，并以 HC3 稳健标准误计算区间。')
image('figure2_adjustment')
p('图 2 调整模型与中心内比较。a，点为 disease 的回归系数，误差线为 HC3 95% CI；线性年龄之外另加入年龄平方项作为函数形式敏感性分析。b，各中心的疾病组减无疾病组均值差及 Welch 95% CI；中心名下的数字依次为疾病组和无疾病组有效 n。所有区间均为名义 95%，未作多重校正。')
table(['模型','n','差异 bpm [95% CI]','p'],[(m['model'],m['n'],f"{m['beta']:.2f} [{m['lo']:.2f}, {m['hi']:.2f}]",pv(m['p'])) for m in models],[6,1,7,3])
p(f"加入年龄、性别和中心后，差异为 {models[2]['beta']:.2f} bpm（95% CI {models[2]['lo']:.2f} 至 {models[2]['hi']:.2f}），负向关联保留。Mann–Whitney U 敏感性检验 p={pv(u.pvalue)}；随机抽取疾病组与无疾病组各一人，前者心率更高的概率（并列计半）约为 {superiority:.3f}，该统计量不直接检验均值差。")
p('各中心结果需结合区间宽度理解；某中心区间跨零不代表其与其他中心显著不同。未来可进行疾病×中心交互分析，但应考虑小亚组与多重检验。本次完整病例结果还依赖缺失机制，无法排除非随机缺失偏倚。')

page('补充分析 年龄 性别与疾病预测')
image('figure3_associations')
p(f"图 3 探索性关联。a，{len(main)} 人的年龄与最大运动心率，按疾病状态着色；线为各组线性拟合，阴影为 HC3 95% 均值置信带。总体 Pearson r={r.statistic:.3f}，p={pv(r.pvalue)}；Spearman ρ={rho.statistic:.3f}，p={pv(rho.pvalue)}。总体相关可能混合组间与组内效应。b，各性别疾病证据比例，误差线为 Wilson 95% CI，点上方为疾病人数/该性别总人数。")
p('；'.join(f"{s['sex']}：{s['k']}/{s['n']}={s['rate']*100:.1f}%（95% CI {s['lo']*100:.1f}% 至 {s['hi']*100:.1f}%）" for s in proportions)+f"。Pearson χ²={chi:.3f}，df=1，p={pv(pchi)}；最小期望频数={expected.min():.2f}。这是未调整的样本比例关联，不是性别的因果效应或一般人群患病率。")
image('figure4_prediction')
p(f"图 4 探索性疾病分类。使用 age、sex、thalach 的 L2 正则 logistic 模型。a，蓝线为分层五折交叉验证的折外 ROC；红线为每次留出一个中心的折外 ROC。b，五折折外预测按概率分为 8 个近等人数区间的校准图；虚线为理想校准。五折 AUC={auc:.3f}，固定折外预测 bootstrap 95% CI {auc_ci[0]:.3f} 至 {auc_ci[1]:.3f}；Brier={brier:.3f}；留中心 AUC={auc_site:.3f}。")

page('风险说明 退出卡与参考文献')
doc.add_heading('数据与预测的边界',2)
p('四中心资料没有随机分组或时间先后信息。β 阻滞剂使用、运动能力、吸烟及检查方案等未测量因素可能影响关联，现有字段无法充分控制。静息血压、胆固醇等变量可用于后续有理论依据的扩展模型，但不应机械加入全部变量，以免调整中介或碰撞变量。')
missing_rows=[f"{c} {int(d[c].isna().sum())}" for c in cols]
p('各字段缺失人数：'+ '；'.join(missing_rows)+'。主分析使用完整心率记录；预测模型在每个训练折内进行中位数插补并加入缺失指示，再标准化，避免从测试折获取预处理信息。预测的 num 与 disease_label、sex_label、record_id 均不作为特征，避免标签泄露或冗余编码。')
p('预测模型使用全部 920 人的折外预测；五折按疾病状态分层，随机种子 20261013。AUC 区间通过 2000 次受试者 bootstrap 获得，固定已生成的折外概率，不包含重新训练和折划分的不确定性，不能当作外部验证区间。留中心验证反映来源迁移风险，仍不能替代新临床人群验证。当前任务是已记录疾病状态分类，不能声称预测未来发病风险。')
doc.add_heading('只挑显著指标的风险',2)
p('若反复检验年龄、胆固醇、血压等指标，再只报告显著者，会增加假阳性并夸大效应。应固定主要终点，公开全部探索分析，对同一探索检验族按目的使用 Holm 或 FDR 校正，并在独立数据中验证。本报告补充 p 值均为未校正的探索性结果，不作为新的确证性发现。')
doc.add_heading('退出卡 主张 证据 推理 边界',2)
p('主张：在本次四中心样本中，有心脏病证据与较低的最大运动心率存在统计关联。')
p(f"证据：疾病组减无疾病组的均值差为 {w['delta']:.2f} bpm，95% CI 为 {w['lo']:.2f} 至 {w['hi']:.2f}，双侧 Welch p={pv(w['p'])}。")
p('推理：置信区间排除零差异，控制年龄、性别及来源中心后方向保持一致，支持该样本中的关联判断。')
p('边界：观察性横断面设计、选择偏倚、缺失及未测量混杂使本分析无法证明因果，也无法单凭心率诊断疾病或推广到一般人群。')
doc.add_heading('作图参考文献',2)
refs=[
'[1] Liao S et al. Passive heart-rate monitoring during smartphone use in everyday life. Nature 655, 728–736 (2026). https://doi.org/10.1038/s41586-026-10507-6 参考 Fig. 4b 的分组分布与图注规范；其静息心率不等同于本研究的运动最大心率。',
'[2] Takaoka M et al. Early intermittent hyperlipidaemia alters tissue macrophages to fuel atherosclerosis. Nature 634, 457–465 (2024). https://doi.org/10.1038/s41586-024-07993-x 参考分组定量与相关分析的表达。',
'[3] Proteomic analysis of cardiorespiratory fitness for prediction of mortality and multisystem disease risks. Nature Medicine 30, 1711–1721 (2024). https://doi.org/10.1038/s41591-024-03039-x 参考 Fig. 3a 森林图；本报告使用线性模型，不使用 Cox 模型。',
'[4] Integrative proteomic analyses across common cardiac diseases yield mechanistic insights and enhanced prediction. Nature Cardiovascular Research 3, 1516–1530 (2024). https://doi.org/10.1038/s44161-024-00567-0 参考 Fig. 5 的预测性能表达。']
for ref in refs:
    par=doc.add_paragraph(ref)
    for run in par.runs: run.font.size=Pt(8)
p('图均由本次数据原创绘制，借鉴分面、统一配色、原始点及置信区间表达；未复制原文图像。原始数据与字段定义来自课程所给 CSV 和 data/README.md。')
last_section=False
for par in doc.paragraphs:
    if par.text=='风险说明 退出卡与参考文献': last_section=True
    if last_section and par.style.name=='Normal':
        par.paragraph_format.line_spacing=1.05
        par.paragraph_format.space_after=Pt(4)
        for run in par.runs:
            if not par.text.startswith('['): run.font.size=Pt(10)
for par in doc.paragraphs:
    for border in list(par._element.iter(qn('w:pBdr'))): border.getparent().remove(border)
doc.save(OUT/'心脏病与最大运动心率_作业完成稿.docx')
print(json.dumps(result,ensure_ascii=False,indent=2))
