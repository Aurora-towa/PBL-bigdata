from pathlib import Path
import sys,json,itertools
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
import numpy as np,pandas as pd
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import confusion_matrix,log_loss,roc_auc_score,average_precision_score,brier_score_loss
R=Path(__file__).resolve().parents[1];O=R/'outputs/课程作业';O.mkdir(parents=True,exist_ok=True)
F=['fever_ge_38','nausea','lumbar_pain','urine_pushing','micturition_pain','burning_urethra'];Y='bladder_inflammation'
tr=pd.read_csv(R/'data/student/train.csv');va=pd.read_csv(R/'data/student/validation.csv')
m=BernoulliNB(alpha=1,binarize=None).fit(tr[F],tr[Y])
def score(y,p,t=.5):
 tn,fp,fn,tp=map(int,confusion_matrix(y,p>=t,labels=[0,1]).ravel())
 return dict(tn=tn,fp=fp,fn=fn,tp=tp,accuracy=(tn+tp)/len(y),sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),precision=tp/(tp+fp) if tp+fp else None,f1=2*tp/(2*tp+fp+fn),logloss=log_loss(y,p),auc=roc_auc_score(y,p),ap=average_precision_score(y,p),brier=brier_score_loss(y,p))
vp=m.predict_proba(va[F])[:,1];theta=np.exp(m.feature_log_prob_);x=np.array([0,0,0,1,1,1]);factors=np.where(x,theta,1-theta);weights=np.exp(m.class_log_prior_)*factors.prod(axis=1)
# Fix the main analysis before loading the supplied held-out labels.
(O/'固定分析方案.json').write_text(json.dumps(dict(features=F,alpha=1,threshold=.5,training_ids=tr.sample_id.tolist(),refit=False,note='采用工作单原始配置；工作单已包含部分测试汇总，本分析属于复算，不声称前瞻盲测。'),ensure_ascii=False,indent=2),encoding='utf-8')
te=pd.read_csv(R/'data/student/locked-test-features.csv').merge(pd.read_csv(R/'data/teacher/locked-test-labels.csv'),on='sample_id',validate='one_to_one')
tp=m.predict_proba(te[F])[:,1]
comb=np.array(list(itertools.product([0,1],repeat=6)))
dup=np.column_stack([tr[F],tr.nausea]);dm=BernoulliNB(alpha=1,binarize=None).fit(dup,tr[Y]);p0=m.predict_proba(pd.DataFrame(comb,columns=F))[:,1];p1=dm.predict_proba(np.column_stack([comb,comb[:,1]]))[:,1];ix=np.argsort(-abs(p1-p0))[:3]
two=BernoulliNB(alpha=1,binarize=None).fit(tr[F[3:5]],tr[Y]);twop=two.predict_proba(va[F[3:5]])[:,1]
joint=[]
for c in [0,1]:
 z=tr[tr[Y]==c];a=int(z[F[3]].sum());b=int(z[F[4]].sum());ab=int((z[F[3]]*z[F[4]]).sum());joint.append(dict(c=c,n=len(z),a=a,b=b,ab=ab,joint=ab/len(z),product=a*b/len(z)**2))
bins=[]
for lo,hi in zip([0,.2,.4,.6,.8],[.2,.4,.6,.8,1]):
 keep=(vp>=lo)&((vp<hi) if hi<1 else (vp<=hi))
 if keep.sum():bins.append(dict(lo=lo,hi=hi,n=int(keep.sum()),positive=int(va[Y][keep].sum()),mean=float(vp[keep].mean()),observed=float(va[Y][keep].mean())))
allx=pd.concat([tr,va,te],ignore_index=True);seen=set(map(tuple,tr[F].values))
res=dict(train=score(tr[Y],m.predict_proba(tr[F])[:,1]),val=score(va[Y],vp),test=score(te[Y],tp),baseline=score(va[Y],np.full(len(va),tr[Y].mean())),two=score(va[Y],twop),transformed=score(va[Y],.25+.5*vp),thresholds={str(t):score(va[Y],vp,t) for t in [.1,.5,.9]},theta=theta.tolist(),counts=[tr[tr[Y]==c][F].sum().tolist() for c in [0,1]],factors=factors.tolist(),weights=weights.tolist(),manual_p=float(weights[1]/weights.sum()),joint=joint,bins=bins,duplicate=[dict(x=comb[i].tolist(),before=float(p0[i]),after=float(p1[i])) for i in ix],audit=dict(missing=int(allx.isna().sum().sum()),profiles=len(allx[F].drop_duplicates()),val_seen=sum(tuple(x) in seen for x in va[F].values),test_seen=sum(tuple(x) in seen for x in te[F].values),id_unique=int(allx.sample_id.nunique()),duplicate_rows=int(allx.drop(columns='sample_id').duplicated().sum())))
(O/'计算结果.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
for name,d,p in [('train',tr,m.predict_proba(tr[F])[:,1]),('validation',va,vp),('test',te,tp)]:pd.DataFrame(dict(sample_id=d.sample_id,y=d[Y],probability=p,prediction=(p>=.5).astype(int))).to_csv(O/(name+'_predictions.csv'),index=False)
print(json.dumps(res,ensure_ascii=False,indent=2))
