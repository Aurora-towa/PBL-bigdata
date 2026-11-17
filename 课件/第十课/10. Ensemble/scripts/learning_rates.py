from pathlib import Path
src=Path(__file__).with_name('assignment.py').read_text(encoding='utf-8-sig');exec(src[:src.index('rows=[];pred={}')])
from sklearn.metrics import accuracy_score
from matplotlib.colors import LinearSegmentedColormap
O=R/'outputs/learning_rates';O.mkdir(exist_ok=True)
rates=[.5,.3,.2,.1,.01,.001,.0001];allrows=[];summ=[];raw=[]
for lr in rates:
 m=GradientBoostingClassifier(n_estimators=500,learning_rate=lr,max_depth=2,random_state=1010).fit(X,y);seq=[]
 for n,(pt,pv) in enumerate(zip(m.staged_predict_proba(X),m.staged_predict_proba(V)),1):
  pp=pv[:,1];cm=confusion_matrix(z,pp>=.5).ravel();row=[lr,n,log_loss(y,pt),log_loss(z,pv),roc_auc_score(z,pp),balanced_accuracy_score(z,pp>=.5),*cm];seq.append(row)
  if n in [200,500]:raw.extend(zip([lr]*len(z),[n]*len(z),v.sample_id,z,pp,(pp>=.5).astype(int)))
 allrows.extend(seq);best=min(seq,key=lambda r:r[3]);end=seq[-1];summ.append([str(lr),seq[199][3],end[2],end[3],end[4],end[5],best[1],best[3],*end[6:]])
a=pd.DataFrame(allrows,columns=['学习率','轮数','训练损失','验证损失','验证AUC','验证BA','TN','FP','FN','TP']);a.to_csv(O/'逐轮实验结果.csv',index=False,encoding='utf-8-sig')
s=pd.DataFrame(summ,columns=['学习率','200轮验证损失','500轮训练损失','500轮验证损失','500轮AUC','500轮BA','最优轮数','最小验证损失','TN','FP','FN','TP']);s.to_csv(O/'学习率实验汇总.csv',index=False,encoding='utf-8-sig');pd.DataFrame(raw,columns=['学习率','轮数','ID','真实','概率','预测']).to_csv(O/'逐条验证预测.csv',index=False,encoding='utf-8-sig')
colors=[C,'#D9BD76','#B990A6',B,'#67A497','#8295AD','#999999']
f,axs=plt.subplots(1,2,figsize=(10,3.6))
for lr,col in zip(rates,colors):
 q=a[a.学习率==lr]
 for ax,key in zip(axs,['训练损失','验证损失']):ax.plot(q.轮数,q[key],color=col,alpha=.5,label=str(lr));ax.set(xlabel='提升轮数',ylabel='Log-loss',title=key,ylim=(0,.8))
axs[1].legend(title='学习率',fontsize=8,ncol=2);save(f,1)
f,axs=plt.subplots(1,2,figsize=(10,3.6));rounds=[10,50,100,200,300,500]
for ax,key in zip(axs,['验证损失','验证BA']):
 h=a[a.轮数.isin(rounds)].pivot(index='学习率',columns='轮数',values=key).reindex(rates);ax.imshow(h,aspect='auto',cmap=LinearSegmentedColormap.from_list('palette',['#FFF8ED',C if key=='验证损失' else B]),alpha=.5,vmin=0,vmax=.8 if key=='验证损失' else 1);ax.set(xticks=range(6),xticklabels=rounds,yticks=range(7),yticklabels=[str(x) for x in rates],xlabel='提升轮数',ylabel='学习率',title=key)
 for i in range(7):
  for j in range(6):ax.text(j,i,f'{h.iloc[i,j]:.3f}',ha='center',va='center',fontsize=8)
save(f,2)
exec(src[src.index('def para(s):'):src.index("d.add_heading('集成学习")])
d=Document(R/'集成学习课程作业_实验扩展完成稿.docx');start=next(p._p for p in d.paragraphs if p.text.startswith('问题四'));end=next(p._p for p in d.paragraphs if p.text.startswith('问题五'));el=start.getnext()
while el is not end:
 nxt=el.getnext();el.getparent().remove(el);el=nxt
old=set(d._element.body)
para('实验将学习率设为0.5、0.3、0.2、0.1、0.01、0.001和0.0001。每个模型均使用深度2的树，最多运行500轮，随机种子1010；训练集341条、验证集114条，阈值固定为0.5。固定200轮和500轮用于公平比较计算预算；同时记录500轮内验证损失最低的轮数，作为探索性的早停候选。测试标签未读取。')
fig(1,'七种学习率下的逐轮Log-loss。左为训练、右为验证，横轴统一为1—500轮；曲线为真实实验结果。学习率影响每轮更新幅度，小学习率需要更多轮数才能充分拟合。')
table(s[['学习率','200轮验证损失','500轮训练损失','500轮验证损失','500轮AUC','500轮BA']],'表  固定轮数下的原始结果')
para('同时报告AUC、BA和Log-loss，是因为三者评价不同方面：AUC反映概率排序；BA反映阈值0.5下两类召回的平均；Log-loss还对预测概率的置信程度敏感。即使AUC较高，极小学习率的预测也可能尚未越过分类阈值，导致BA接近0.5。')
fig(2,'学习率与轮数的联合热力图。左为验证Log-loss，越低越好；右为验证BA，越高越好。数字为实际指标，所有配置使用相同验证记录。')
table(s[['学习率','最优轮数','最小验证损失','TN','FP','FN','TP']],'表  早停候选与500轮原始混淆计数')
best=s.loc[s['500轮验证损失'].idxmin()];small=s.iloc[-1];early=s.loc[s['最小验证损失'].idxmin()]
para(f'在统一500轮预算下，学习率{best["学习率"]}的验证损失最低，为{best["500轮验证损失"]:.4f}，AUC为{best["500轮AUC"]:.4f}，BA为{best["500轮BA"]:.4f}。学习率0.0001在500轮时验证损失为{small["500轮验证损失"]:.4f}、BA为{small["500轮BA"]:.4f}，应解释为当前轮数预算下学习不足，而不是该学习率在所有条件下都不可用。')
para(f'在全部7×500个逐轮结果中，最低验证损失出现在学习率{early["学习率"]}、第{int(early["最优轮数"])}轮，为{early["最小验证损失"]:.4f}。这是同一验证集上筛选得到的最小值，可能偏乐观，不能充当独立泛化结果。最优轮数若等于500，只说明当前搜索边界处仍有改善空间，不能断言已找到全局最优轮数。')
para('较大学习率可能更快降低训练误差，但当训练损失继续下降、验证损失反而增加时，应考虑早停。下一步可在训练集内部交叉验证选择学习率与轮数，再锁定配置进行一次留出测试。此次扫描保持其余问题中的基线配置不变，目的在于解释学习率与轮数的配合。')
table(pd.DataFrame({'方面':['训练方式','主要机制','常用基学习器','关键参数'],'Bagging与RF':['可并行','降低方差与相关性','深树','树数、特征数、叶节点规模'],'Boosting':['顺序依赖','逐步修正当前误差','浅树','学习率、轮数、深度']}),'表  两类集成方法比较')
for el in [e for e in d._element.body if e not in old and e.tag!=qn('w:sectPr')]:end.addprevious(el)
# Sequential captions and fully explicit mixed-script fonts.
fi=ti=0
for p in d.paragraphs:
 if p.text.startswith('图') and '  ' in p.text[:8]:fi+=1;p.runs[0].text=__import__('re').sub(r'^图\d+',f'图{fi}',p.runs[0].text)
 if p.text.startswith('表'):
  ti+=1;p.runs[0].text=__import__('re').sub(r'^表\d*',f'表{ti}',p.runs[0].text);p.paragraph_format.keep_with_next=True
 if p._p.xpath('.//w:drawing'):p.paragraph_format.keep_with_next=True
for tb in d.tables:
 for row in tb.rows[:-1]:
  for c in row.cells:
   for p in c.paragraphs:p.paragraph_format.keep_with_next=True
for p in list(d.paragraphs)+[p for tb in d.tables for row in tb.rows for c in row.cells for p in c.paragraphs]:
 for run in p.runs:
  run.font.name='Times New Roman';rf=run._element.get_or_add_rPr().rFonts
  for k,val in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('cs','Times New Roman'),('eastAsia','宋体')]:rf.set(qn('w:'+k),val)
  for k in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:rf.attrib.pop(qn('w:'+k),None)
d.save(R/'集成学习课程作业_七组学习率实验完成稿.docx');print(s.to_string(index=False))
