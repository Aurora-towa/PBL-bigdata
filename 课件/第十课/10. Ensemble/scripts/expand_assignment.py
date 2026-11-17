from pathlib import Path
src=Path(__file__).with_name('assignment.py').read_text(encoding='utf-8-sig')
exec(src[:src.index('rows=[];pred={}')])
from sklearn.metrics import accuracy_score,recall_score,f1_score
from matplotlib.font_manager import FontProperties
from docx.enum.text import WD_BREAK
O=R/'outputs/expanded';O.mkdir(exist_ok=True)
base_save=save
def save(f,n):
 from matplotlib.text import Text
 for tx in f.findobj(Text):
  tx.set_fontfamily(['Times New Roman','SimSun']);tx.set_fontweight('normal')
 base_save(f,n)
rows=[];raw=[];f,axs=plt.subplots(2,2,figsize=(10,5))
for i,name in enumerate(['Tree','RF']):
 m=models[name].fit(X,y)
 for j,(xx,yy,ids,part) in enumerate([(X,y,t.sample_id,'训练'),(V,z,v.sample_id,'验证')]):
  pr=m.predict_proba(xx)[:,1];cl=(pr>=.5).astype(int);cm=confusion_matrix(yy,cl).ravel();rows.append([name,part,*cm,roc_auc_score(yy,pr),balanced_accuracy_score(yy,cl)])
  order=np.lexsort((ids,yy));a=axs[i,j]
  for label,col in [(0,B),(1,C)]:
   mask=yy.to_numpy()[order]==label;a.scatter(np.arange(len(yy))[mask],pr[order][mask],s=9,color=col,alpha=.5,label=f'真实 {label}')
  err=cl[order]!=yy.to_numpy()[order];a.scatter(np.arange(len(yy))[err],pr[order][err],s=28,facecolors='none',edgecolors='#333A40',lw=.6,label='误分类');a.axhline(.5,color='gray',ls='--',lw=.6);a.set(title=f'{name} · {part}',xlabel='记录序号（真实类别与ID排序）',ylabel='恶性预测概率',ylim=(-.04,1.04));a.legend(fontsize=7)
  raw.extend(zip([name]*len(yy),[part]*len(yy),ids,yy,pr,cl))
save(f,7);counts=pd.DataFrame(rows,columns=['模型','数据','TN','FP','FN','TP','AUC','BA']);counts.to_csv(O/'训练验证计数.csv',index=False,encoding='utf-8-sig');raw=pd.DataFrame(raw,columns=['模型','数据','ID','真实','概率','预测']);raw.to_csv(O/'逐条原始预测.csv',index=False,encoding='utf-8-sig')
f,axs=plt.subplots(2,2,figsize=(7,5))
for a,row in zip(axs.flat,rows):
 cm=np.array(row[2:6]).reshape(2,2);a.imshow(cm,cmap='Blues',alpha=.5,vmin=0,vmax=214);a.set(title=f'{row[0]} · {row[1]}',xticks=[0,1],yticks=[0,1],xlabel='预测类别',ylabel='真实类别')
 for i in range(2):
  for j in range(2):a.text(j,i,f'{cm[i,j]}\n{cm[i,j]/cm[i].sum():.1%}',ha='center',va='center',fontsize=9)
save(f,8)
g=[]
for trees in [10,50,100,300]:
 for feat in ['sqrt',.5,1.0]:
  m=RandomForestClassifier(n_estimators=trees,max_features=feat,random_state=1010,n_jobs=1).fit(X,y);pr=m.predict_proba(V)[:,1];pp=pr>=.5;tn,fp,fn,tp=confusion_matrix(z,pp).ravel();g.append([trees,str(feat),roc_auc_score(y,m.predict_proba(X)[:,1]),roc_auc_score(z,pr),accuracy_score(z,pp),balanced_accuracy_score(z,pp),recall_score(z,pp),tn/(tn+fp),f1_score(z,pp),tn,fp,fn,tp])
g=pd.DataFrame(g,columns=['树数','特征数','训练AUC','验证AUC','准确率','BA','敏感度','特异度','F1','TN','FP','FN','TP']);g.to_csv(O/'随机森林参数原始结果.csv',index=False,encoding='utf-8-sig')
f,axs=plt.subplots(1,3,figsize=(10,3));g['差值']=g.训练AUC-g.验证AUC
for a,key in zip(axs,['训练AUC','验证AUC','差值']):
 h=g.pivot(index='树数',columns='特征数',values=key).reindex(columns=['sqrt','0.5','1.0']);a.imshow(h,aspect='auto',cmap='Oranges',alpha=.5,vmin=0 if key=='差值' else .95,vmax=.05 if key=='差值' else 1);a.set(title=key,xticks=range(3),xticklabels=h.columns,yticks=range(4),yticklabels=h.index,xlabel='每次分裂候选特征',ylabel='树数')
 for i in range(4):
  for j in range(3):a.text(j,i,f'{h.iloc[i,j]:.3f}',ha='center',va='center',fontsize=9)
save(f,9)
sel=g[((g.树数.isin([10,100,300]))&(g.特征数=='sqrt'))|((g.树数==100)&(g.特征数=='1.0'))];keys=['验证AUC','准确率','BA','敏感度','特异度','F1'];ang=np.linspace(0,2*np.pi,6,endpoint=False);f=plt.figure(figsize=(8,4));a=f.add_subplot(111,projection='polar')
for (_,r),col in zip(sel.iterrows(),[B,C,'#D9BD76','#8B91A8']):
 vals=r[keys].astype(float).to_numpy();a.plot(np.r_[ang,ang[0]],np.r_[vals,vals[0]],color=col,alpha=.5,label=f'B={r.树数}, features={r.特征数}')
a.set_xticks(ang,keys);a.set_ylim(0,1);a.set_yticks([.25,.5,.75,1]);a.legend(loc='center left',bbox_to_anchor=(1.15,.5),fontsize=9);save(f,10)
# Reuse authoring helpers, then place new content inside the matching question.
exec(src[src.index('def para(s):'):src.index("d.add_heading('集成学习")])
d=Document(R/'集成学习课程作业_完成稿.docx')
def insert_before(prefix,build):
 anchor=next(p._p for p in d.paragraphs if p.text.startswith(prefix));old=set(d._element.body);build();new=[el for el in d._element.body if el not in old and el.tag!=qn('w:sectPr')]
 for el in new:anchor.addprevious(el)
def predict_section():
 d.add_heading('训练拟合与逐条预测',2);fig(7,'单树与随机森林的逐条预测。蓝点为良性，橙点为恶性，空心圈标出误分类；虚线为0.5阈值。各面板使用各自的数据集排序。')
 table(raw[(raw.模型=='RF')&(raw.数据=='验证')].sort_values('ID').head(8)[['ID','真实','概率','预测']],'原始结果表 随机森林验证集按ID排列的前8条记录')
 para('单树在训练数据上的概率集中在0和1，反映叶节点对训练记录的拟合；森林通过多树平均产生连续概率。训练表现不能用来替代验证表现。图中的错误圈帮助定位阈值两侧的错分，而不是通过重新排列记录制造类别分离。')
 fig(8,'训练与验证混淆矩阵。第一行为计数，第二行为同一真实类别内的占比；颜色使用统一计数范围，样本量不同的面板应结合行百分比比较。',13)
 table(counts,'原始结果表 训练与验证混淆计数和评价指标')
 rf=counts[(counts.模型=='RF')&(counts.数据=='验证')].iloc[0];para(f'随机森林在验证集中误判{rf.FP}条良性记录、漏判{rf.FN}条恶性记录，BA为{rf.BA:.3f}。错误数仍然很少，新增或减少一条错分即可改变模型排名，因此应保留原始计数并结合独立验证判断。')
def param_section():
 d.add_heading('树数与特征随机化的联合实验',2);fig(9,'12组随机森林参数实验。行是树数，列是每次分裂的候选特征数：sqrt约为5项，0.5为15项，1.0为全部30项。前两图统一AUC范围0.95—1；第三图为训练减验证AUC，范围0—0.05。')
 table(g[['树数','特征数','训练AUC','验证AUC','BA','FN','FP']],'原始结果表 随机森林参数扫描')
 q=g[g.特征数=='sqrt'];para(f'sqrt设置下，10棵树的验证AUC为{q.iloc[0].验证AUC:.4f}，300棵树为{q.iloc[-1].验证AUC:.4f}。树数增加后的变化应看实际数值，不能预设单调提升。训练与验证AUC的差值只是当前划分上的拟合差距，不能单独作为过拟合检验。所有配置共用相同随机种子和数据，参数扫描结果属于探索性证据。')
 fig(10,'四组参数配置的验证指标雷达图。六个轴均为0—1、数值越大越好；折线用于比较指标形态，不计算或比较多边形面积。')
 table(sel[['树数','特征数']+keys],'原始结果表 雷达图的六项指标')
 para('这些配置的指标集中在较高水平，雷达图差别较小，因此同时给出三线表，避免通过缩短坐标范围夸大差距。敏感度体现恶性召回，特异度体现良性召回；AUC反映概率排序，不等于在固定阈值下零错分。扫描没有改变原报告的固定配置，也没有读取封存测试标签。')
insert_before('问题四',param_section);insert_before('问题六',predict_section)
# Explicit fonts for every run and style; remove inherited decorative title rules.
for style in d.styles:
 if hasattr(style,'font'):
  style.font.name='Times New Roman';rp=style.element.get_or_add_rPr();rf=rp.find(qn('w:rFonts'))
  if rf is None:rf=OxmlElement('w:rFonts');rp.insert(0,rf)
  for k,val in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('cs','Times New Roman'),('eastAsia','宋体')]:rf.set(qn('w:'+k),val)
  for k in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:rf.attrib.pop(qn('w:'+k),None)
for el in d._element.iter(qn('w:pBdr')):el.getparent().remove(el)
for st in d.styles:
 for el in st.element.iter(qn('w:pBdr')):el.getparent().remove(el)
paras=list(d.paragraphs)+[p for tb in d.tables for row in tb.rows for c in row.cells for p in c.paragraphs]
for p in paras:
 for run in p.runs:
  run.font.name='Times New Roman';rf=run._element.get_or_add_rPr().rFonts
  for k,val in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('cs','Times New Roman'),('eastAsia','宋体')]:rf.set(qn('w:'+k),val)
  for k in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:rf.attrib.pop(qn('w:'+k),None)
# Renumber figure and table captions by document order.
fi=ti=0
for p in d.paragraphs:
 if p.text.startswith('图') and '  ' in p.text[:8]:
  fi+=1;p.runs[0].text=__import__('re').sub(r'^图\d+',f'图{fi}',p.runs[0].text)
 if p.text.startswith('表') or p.text.startswith('原始结果表'):
  ti+=1
  if p.runs:p.runs[0].text=__import__('re').sub(r'^(表\d+|原始结果表)',f'表{ti}',p.runs[0].text)
d.save(R/'集成学习课程作业_实验扩展完成稿.docx');print('DONE',len(d.inline_shapes),len(d.tables))
