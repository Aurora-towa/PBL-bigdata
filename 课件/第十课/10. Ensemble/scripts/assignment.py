import sys
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
from pathlib import Path
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,BaggingClassifier,GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score,balanced_accuracy_score,confusion_matrix,log_loss,roc_curve
from sklearn.model_selection import StratifiedKFold,cross_val_score
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from docx import Document
from docx.shared import Cm,Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];O=R/'outputs/assignment';O.mkdir(parents=True,exist_ok=True)
t=pd.read_csv(R/'data/student/train.csv');v=pd.read_csv(R/'data/student/validation.csv');cols=t.columns.drop(['sample_id','malignant']);X=t[cols];y=t.malignant;V=v[cols];z=v.malignant
B='#4389A2';C='#E49A64';BG=(1,248/255,237/255,.2)
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
def save(f,n):
 f.patch.set_facecolor(BG)
 for a in f.axes:a.set_facecolor('none')
 f.tight_layout();f.savefig(O/f'图{n}.png',dpi=240,facecolor=BG);f.savefig(O/f'图{n}.svg',facecolor=BG);plt.close(f)
models={'Tree':DecisionTreeClassifier(random_state=1010),'Bagging':BaggingClassifier(n_estimators=100,random_state=1010,n_jobs=1),'RF':RandomForestClassifier(n_estimators=100,max_features='sqrt',random_state=1010,n_jobs=1),'GB':GradientBoostingClassifier(n_estimators=100,learning_rate=.1,max_depth=2,random_state=1010),'LR':make_pipeline(StandardScaler(),LogisticRegression(max_iter=3000)),'SVM':make_pipeline(StandardScaler(),SVC(C=1,probability=True,random_state=1010))}
rows=[];pred={}
for name,m in models.items():
 m.fit(X,y);pr=m.predict_proba(V)[:,1];pred[name]=pr;cv=cross_val_score(clone(m),X,y,cv=StratifiedKFold(5,shuffle=True,random_state=1010),scoring='roc_auc');cm=confusion_matrix(z,pr>=.5).ravel();rows.append([name,roc_auc_score(z,pr),balanced_accuracy_score(z,pr>=.5),cv.mean(),cv.std(ddof=1),*cm])
res=pd.DataFrame(rows,columns=['模型','验证AUC','验证BA','训练CV均值','折间SD','TN','FP','FN','TP']);res.to_csv(O/'模型原始指标.csv',index=False,encoding='utf-8-sig');pd.DataFrame(pred).assign(sample_id=v.sample_id,truth=z).to_csv(O/'逐条验证概率.csv',index=False,encoding='utf-8-sig')
dep=[]
for depth in [1,2,3,4,None]:
 m=DecisionTreeClassifier(max_depth=depth,random_state=1010).fit(X,y);dep.append([str(depth),balanced_accuracy_score(y,m.predict(X)),balanced_accuracy_score(z,m.predict(V))])
dep=pd.DataFrame(dep,columns=['深度','训练BA','验证BA']);dep.to_csv(O/'树深度.csv',index=False)
rng=np.random.default_rng(1010);unique=np.array([len(np.unique(rng.integers(0,len(t),len(t))))/len(t) for _ in range(1000)])
stab=[]
for name in ['Tree','Bagging','RF']:
 ps=[]
 for rep in range(20):
  idx=np.random.default_rng(1010+rep).integers(0,len(t),len(t));m=clone(models[name]).fit(X.iloc[idx],y.iloc[idx]);ps.append(m.predict_proba(V)[:,1])
 ps=np.array(ps);np.save(O/f'{name}_bootstrap_probs.npy',ps);stab.append([name,ps.std(axis=0,ddof=1).mean(),((ps>=.5)!=(pred[name]>=.5)).mean()])
stab=pd.DataFrame(stab,columns=['模型','平均概率SD','相对原模型翻转率']);stab.to_csv(O/'稳定性.csv',index=False)
grid=[]
for lr in [.03,.1,.3]:
 m=GradientBoostingClassifier(n_estimators=200,learning_rate=lr,max_depth=2,random_state=1010).fit(X,y)
 for i,(pt,pv) in enumerate(zip(m.staged_predict_proba(X),m.staged_predict_proba(V)),1):grid.append([lr,i,log_loss(y,pt),log_loss(z,pv)])
grid=pd.DataFrame(grid,columns=['学习率','轮数','训练损失','验证损失']);grid.to_csv(O/'Boosting逐轮结果.csv',index=False)
f,ax=plt.subplots(1,3,figsize=(10,3));ax[0].bar(['训练','验证','封存测试'],[341,114,114],color=[B,C,'#D9BD76'],alpha=.5);ax[0].set_title('a  数据与固定划分');ax[1].plot(dep.深度,dep.训练BA,'o-',color=B,alpha=.5,label='训练');ax[1].plot(dep.深度,dep.验证BA,'o-',color=C,alpha=.5,label='验证');ax[1].set_title('b  单树到多模型比较');ax[1].legend();ax[2].bar(res.模型,res.验证AUC,color=B,alpha=.5);ax[2].set(ylim=(.5,1),title='c  验证与稳定性评价');save(f,1)
f,ax=plt.subplots(1,2,figsize=(10,3));ax[0].plot(dep.深度,dep.训练BA,'o-',color=B,alpha=.5,label='训练');ax[0].plot(dep.深度,dep.验证BA,'o-',color=C,alpha=.5,label='验证');ax[0].legend();ax[0].set(xlabel='最大深度（None为不限）',ylabel='平衡准确率');ax[1].hist(unique,bins=20,color=B,alpha=.5);ax[1].axvline(unique.mean(),color=C);ax[1].set(xlabel='Bootstrap不同记录占比',ylabel='模拟次数');save(f,2)
f,ax=plt.subplots(1,2,figsize=(10,3));ax[0].bar(stab.模型,stab.平均概率SD,color=B,alpha=.5);ax[0].set_ylabel('平均预测概率标准差');ax[1].bar(stab.模型,stab.相对原模型翻转率,color=C,alpha=.5);ax[1].set_ylabel('类别翻转率');save(f,3)
f,ax=plt.subplots(1,2,figsize=(10,3));
for lr,col in zip([.03,.1,.3],[B,C,'#D9BD76']):
 q=grid[grid.学习率==lr];ax[0].plot(q.轮数,q.训练损失,color=col,alpha=.5,label=str(lr));ax[1].plot(q.轮数,q.验证损失,color=col,alpha=.5,label=str(lr))
for a,title in zip(ax,['训练集','验证集']):a.set(xlabel='提升轮数',ylabel='Log-loss',title=title);a.legend(title='学习率')
save(f,4)
f,ax=plt.subplots(2,3,figsize=(9,5));
for a,(name,pr) in zip(ax.flat,pred.items()):
 cm=confusion_matrix(z,pr>=.5);a.imshow(cm,cmap='Blues',alpha=.5);a.set(title=name,xticks=[0,1],yticks=[0,1],xlabel='预测类别',ylabel='真实类别')
 for i in range(2):
  for j in range(2):a.text(j,i,str(cm[i,j]),ha='center',va='center')
save(f,5)
imp=permutation_importance(models['RF'],V,z,n_repeats=20,scoring='roc_auc',random_state=1010,n_jobs=1);ix=np.argsort(imp.importances_mean)[-8:];it=pd.DataFrame({'特征':cols[ix],'置换AUC下降':imp.importances_mean[ix],'重复SD':imp.importances_std[ix]});it.to_csv(O/'置换重要性.csv',index=False)
f,ax=plt.subplots(1,2,figsize=(10,3.6));ax[0].barh(cols[ix],imp.importances_mean[ix],xerr=imp.importances_std[ix],color=B,alpha=.5);ax[0].set_xlabel('验证AUC下降');
for name,col in zip(['Tree','RF','LR','GB'],[B,C,'#D9BD76','#888888']):
 fp,tp,_=roc_curve(z,pred[name]);ax[1].plot(fp,tp,label=name,color=col,alpha=.5)
ax[1].plot([0,1],[0,1],'k:',lw=.5);ax[1].set(xlabel='假阳性率',ylabel='真阳性率');ax[1].legend();save(f,6)
d=Document();sec=d.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=sec.bottom_margin=Cm(1.8);sec.left_margin=sec.right_margin=Cm(1.8)
for sty in ['Normal','Title','Heading 1','Heading 2']:
 s=d.styles[sty];s.font.name='Times New Roman';s._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体');s.font.size=Pt(10.5 if sty=='Normal' else 14);s.font.color.rgb=__import__('docx').shared.RGBColor(0,0,0)
d.styles['Normal'].paragraph_format.first_line_indent=Cm(.74)
def para(s):d.add_paragraph(s)
def table(df,title):
 p=d.add_paragraph(title);p.alignment=1;p.paragraph_format.first_line_indent=0
 tb=d.add_table(rows=1,cols=len(df.columns));tb.alignment=1
 for c,s in zip(tb.rows[0].cells,df.columns):c.text=str(s)
 for row in df.itertuples(index=False):
  for c,s in zip(tb.add_row().cells,row):c.text=f'{s:.3f}' if isinstance(s,(float,np.floating)) else str(s)
 for i,row in enumerate(tb.rows):
  for c in row.cells:
   bd=OxmlElement('w:tcBorders')
   for edge in ['top','bottom','left','right']:
    e=OxmlElement('w:'+edge);on=(edge=='top' and i==0) or (edge=='bottom' and i in [0,len(tb.rows)-1]);e.set(qn('w:val'),'single' if on else 'nil');e.set(qn('w:sz'),'8');bd.append(e)
   c._tc.get_or_add_tcPr().append(bd)
   for p in c.paragraphs:
    p.alignment=1;p.paragraph_format.first_line_indent=0
    for run in p.runs:run.font.size=Pt(9)
def fig(n,cap,w=17):
 p=d.add_paragraph();p.alignment=1;p.paragraph_format.first_line_indent=0;p.add_run().add_picture(str(O/f'图{n}.png'),width=Cm(w));p=d.add_paragraph(f'图{n}  '+cap);p.paragraph_format.first_line_indent=0
 for run in p.runs:run.font.size=Pt(9)
def page(title):d.add_page_break();d.add_heading(title,1)
d.add_heading('集成学习的性能与稳定性实验',0);d.add_heading('问题一 多个模型如何公平比较',1)
para('本作业选用课程方案A，研究在相同数据划分下，集成学习能否改善识别表现和训练扰动下的稳定性。每条记录为乳腺肿块细胞核图像的30项测量特征，恶性编码为1，良性为0；sample_id只用于追踪。标签表示记录的诊断类别，不能解释为未来发病风险。')
para('训练集341条、验证集114条、封存测试集114条。全部实验只使用前两部分，测试标签未读取。固定随机种子1010；逻辑回归和SVM在管道内标准化，五折交叉验证只在训练集内进行，折内拟合标准化参数。阈值固定为0.5，不根据验证结果调阈值。')
fig(1,'实验框架与实际结果概览。按数据划分、模型实验、验证评价顺序展开；柱高和曲线均来自本次计算。BA为平衡准确率，AUC为ROC曲线下面积。')
table(pd.DataFrame({'数据':['训练','验证'],'记录数':[len(t),len(v)],'恶性':[int(y.sum()),int(z.sum())],'良性':[int((1-y).sum()),int((1-z).sum())]}),'表1 样本构成')
para('比较配置为不限深度单树、100棵全特征Bagging、100棵sqrt随机森林、100轮深度2且学习率0.1的梯度提升，以及默认C=1的逻辑回归和RBF-SVM。所有配置在比较前固定，额外参数扫描仅用于解释机制。')
page('问题二 树越深越好吗 重抽样改变了什么');fig(2,'树深度与Bootstrap覆盖率。左图蓝线为训练BA、橙线为验证BA；右图为1000次有放回抽样，每次抽取341条。');table(dep,'表2 单树深度实验')
para(f'训练误差可以随树加深而下降，但验证表现未必同步改善。深树可能把训练集局部差异拟合为分裂规则。Gini不纯度衡量节点类别混杂程度，分裂选择使加权不纯度下降最大的特征与阈值。叶节点概率来自其中类别的经验比例，不等于校准后的临床风险。')
para(f'1000次Bootstrap中不同记录平均占比为{unique.mean():.3f}，平均袋外占比为{1-unique.mean():.3f}，接近大样本下的0.632和0.368。袋外比例因抽样而变；OOB可估计训练流程内部预测误差，但不能替代独立人群验证。树依据特征排序分裂，通常无需标准化；LR和SVM对特征尺度更敏感。')
page('问题三 Bagging和随机森林能否稳定预测');fig(3,'相同20组Bootstrap训练样本下的稳定性。左图为114条验证记录的概率SD均值；右图为相对各自原训练模型的类别翻转率。');table(stab,'表3 重抽样稳定性结果')
para('各模型使用同一组重抽样索引，验证记录保持不动。概率SD反映训练样本变化带来的波动；翻转率以原训练集拟合模型为参照，二者不能当作泛化误差或置信区间。Bagging平均多棵深树的预测，随机森林进一步随机选择候选特征，可能降低树间相关性。')
para('等方差、等相关条件下，B个模型平均后的方差为ρσ²+(1−ρ)σ²/B。当B增大时，方差趋向ρσ²；模型总犯相同错误时，继续增加树数收益有限。平均通常主要降低方差，不能保证消除系统性偏差。')
page('问题四 Boosting为什么需要控制学习率和轮数');fig(4,'三种学习率下的逐轮损失。左为训练损失，右为验证损失；所有模型均使用深度2的树并运行200轮。');best=grid.loc[grid.groupby('学习率').验证损失.idxmin()];table(best,'表4 各学习率在本次扫描中的最小验证损失')
para('梯度提升依次拟合当前模型尚未解释的部分。对二分类log-loss，在加性得分尺度上，负梯度可写为y−p。AdaBoost通过增加错分记录权重调整下一轮关注对象；两者都具有顺序依赖。较大学习率可能更快降低训练损失，也可能使验证损失提前恶化。表4由验证集选择，存在选择乐观偏差，不作为独立测试结果。')
table(pd.DataFrame({'方面':['训练方式','主要机制','常用基学习器','关键参数'],'Bagging与RF':['可并行','降低方差与相关性','深树','树数、特征数、叶节点规模'],'Boosting':['顺序依赖','逐步修正当前误差','浅树','学习率、轮数、深度']}),'表5 两类集成方法比较')
page('问题五 集成模型是否超过简单基线');fig(5,'固定阈值0.5下的验证混淆矩阵。行是真实类别，列是预测类别，0为良性、1为恶性；数字为实际记录数。',14);table(res[['模型','验证AUC','验证BA','训练CV均值','折间SD']],'表6 固定配置比较')
para('五折结果报告均值与折间标准差，标准差不是均值置信区间。AUC比较排序能力，BA平均两类召回率，混淆矩阵显示漏判与误判的实际数量。验证集仅114条，小幅差异不能单凭排名认定优劣。训练交叉验证与验证集并非同一评价样本，不能直接用折间SD检验模型差异。')
page('问题六 如何解释结果并作出有限的选择');fig(6,'随机森林置换重要性与验证ROC。左图显示验证AUC下降最大的8项特征，误差棒为20次置换的SD；右图比较单树、RF、LR和GB。');table(it.sort_values('置换AUC下降',ascending=False).head(5),'表7 随机森林前五项置换重要性')
winner=res.sort_values('验证AUC',ascending=False).iloc[0]
para(f'本次固定配置中，{winner["模型"]}的验证AUC最高，为{winner["验证AUC"]:.3f}，相应BA为{winner["验证BA"]:.3f}。这说明集成方法是否占优需要实际比较，不能从模型复杂度推断。选型时应同时查看错分数量、概率波动及解释成本；单树容易描述但可能不稳定，森林通常更稳健，线性模型则提供较简洁的基线。')
para('置换重要性表示打乱特征后当前模型预测能力的下降，不是因果效应。高度相关的测量可互相替代，单项重要性可能被稀释。当前验证集还承担参数探索与解释任务，因此结果属于课程开发分析。若后续独立数据上简单模型达到相近表现，应优先保留更易解释的方案；若集成模型持续减少恶性漏判且稳定性更好，再考虑采用集成。')
para('本报告未打开教师保留的测试标签，也未合并训练和验证集重新训练。下一步应先锁定模型、阈值和评价指标，再进行一次留出测试。数据缺少可核验的患者分组和时间信息，当前实验不支持跨医院推广或临床决策结论。全部逐条预测、实验指标与绘图源文件随报告保存在outputs/assignment中。')
d.save(R/'集成学习课程作业_完成稿.docx');print(res.to_string(index=False));print('DONE')

