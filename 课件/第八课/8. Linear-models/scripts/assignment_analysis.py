from pathlib import Path
import sys,json,warnings
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
import numpy as np,pandas as pd
from sklearn.model_selection import train_test_split,StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss,confusion_matrix
from sklearn.base import clone
R=Path(__file__).resolve().parents[1];O=R/'outputs';O.mkdir(exist_ok=True)
d=pd.read_csv(R/'data/heart.csv');N=['age','trestbps','chol','thalach','oldpeak'];C=['sex','cp','fbs','restecg','exang','slope','ca','thal'];F=N+C;Y='heart_disease_present'
levels=[[0,1],[1,2,3,4],[0,1],[0,1,2],[0,1],[1,2,3],[0,1,2,3],[3,6,7]]
X=d[F].copy();zero=int(X.chol.eq(0).sum());X.loc[X.chol.eq(0),'chol']=np.nan
dev,test=train_test_split(np.arange(len(d)),test_size=.2,stratify=d[Y],random_state=2026)
x=X.iloc[dev];y=d[Y].iloc[dev].to_numpy()
def pre(extra=False):return ColumnTransformer([('num',Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler())]),N+(['age_copy'] if extra else [])),('cat',Pipeline([('imp',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(categories=levels,drop='first',handle_unknown='ignore',sparse_output=False))]),C)])
def pipe(model,extra=False):return Pipeline([('pre',pre(extra)),('model',model)])
def metric(y,p,t=.5):
 tn,fp,fn,tp=map(int,confusion_matrix(y,p>=t,labels=[0,1]).ravel());return dict(auc=roc_auc_score(y,p),ap=average_precision_score(y,p),brier=brier_score_loss(y,p),loss=log_loss(y,p),tn=tn,fp=fp,fn=fn,tp=tp,cost=5*fn+fp,sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),precision=tp/(tp+fp) if tp+fp else None,accuracy=(tn+tp)/len(y))
models={'Logistic':pipe(LogisticRegression(C=1,max_iter=3000)),'LDA':pipe(LinearDiscriminantAnalysis(solver='svd')),'Gaussian NB':pipe(GaussianNB())}
pred={k:np.zeros((5,len(y))) for k in [*models,'先验基线']};folds=[]
for rep in range(5):
 cv=StratifiedKFold(5,shuffle=True,random_state=2026+rep)
 for a,b in cv.split(x,y):
  for name,m in models.items():pred[name][rep,b]=clone(m).fit(x.iloc[a],y[a]).predict_proba(x.iloc[b])[:,1]
  pred['先验基线'][rep,b]=y[a].mean()
for k,v in pred.items():np.save(O/(k.replace(' ','_')+'_oof.npy'),v)
summary={k:{z:float(np.mean([metric(y,p)[z] for p in ps])) for z in ['auc','ap','brier','loss','cost','fn','fp']} for k,ps in pred.items()}
thresholds=[dict(t=float(t),cost=float(np.mean([metric(y,p,t)['cost'] for p in pred['Logistic']])),fn=float(np.mean([metric(y,p,t)['fn'] for p in pred['Logistic']])),fp=float(np.mean([metric(y,p,t)['fp'] for p in pred['Logistic']]))) for t in np.arange(1,10)/10]
best=min(thresholds,key=lambda z:(z['cost'],z['t']))['t']
protocol=dict(model='L2 Logistic C=1',features=F,numeric=N,categorical=C,levels=levels,drop='first',threshold=best,cost='5*FN+FP',cv='5 folds x 5 repetitions; seed 2026..2030',chol_zero='missing',dev_ids=d.iloc[dev].sample_id.tolist(),test_ids=d.iloc[test].sample_id.tolist(),selection='Logistic predesignated for mixed inputs and conditional probability; threshold minimum mean repeat OOF cost; tie lower threshold')
(O/'固定分析方案.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
print('Frozen threshold',best,flush=True)
final=clone(models['Logistic']).fit(x,y);pt=final.predict_proba(X.iloc[test])[:,1];yt=d[Y].iloc[test].to_numpy();tm=metric(yt,pt,best)
rng=np.random.default_rng(2026);boot=[]
for b in range(2000):
 ix=rng.integers(0,len(yt),len(yt))
 if len(np.unique(yt[ix]))<2:continue
 boot.append(metric(yt[ix],pt[ix],best))
ci={k:np.quantile([b[k] for b in boot if b[k] is not None],[.025,.975]).tolist() for k in ['auc','ap','brier','loss','accuracy','sensitivity','specificity','precision','cost']}
features=final['pre'].get_feature_names_out();co=pd.DataFrame(dict(feature=features,beta=final['model'].coef_[0],OR=np.exp(final['model'].coef_[0])));co.to_csv(O/'系数与OR.csv',index=False)
xx=x.copy();xx['age_copy']=xx.age.to_numpy()+np.random.default_rng(8).normal(0,.5,len(x));dup=pipe(LogisticRegression(C=1,max_iter=3000),True);dp=np.zeros(len(y))
for a,b in StratifiedKFold(5,shuffle=True,random_state=2026).split(x,y):dp[b]=clone(dup).fit(xx.iloc[a],y[a]).predict_proba(xx.iloc[b])[:,1]
bb=[]
for b in range(200):
 ix=rng.integers(0,len(y),len(y));m=clone(models['Logistic']).fit(x.iloc[ix],y[ix]);n=clone(dup).fit(xx.iloc[ix],y[ix]);bb.append([m['model'].coef_[0,0],n['model'].coef_[0,0],n['model'].coef_[0,5]])
bb=np.array(bb);np.save(O/'年龄系数bootstrap.npy',bb)
# Deliberate feature-warp experiment, development only, never a tuned candidate.
stress=x.copy();sd=x.age.std();stress['age']=np.exp((x.age-50)/10);sp=np.zeros(len(y))
for a,b in StratifiedKFold(5,shuffle=True,random_state=2026).split(x,y):sp[b]=clone(models['LDA']).fit(stress.iloc[a],y[a]).predict_proba(stress.iloc[b])[:,1]
z=final['pre'].transform(x)[:,:5];cov=[np.cov(z[y==c].T) for c in [0,1]];ratio=np.diag(cov[1])/np.diag(cov[0])
missing=d[F].isna().sum().sort_values(ascending=False)
bins=[];pv=pred['Logistic'][0]
for lo,hi in zip(np.arange(0,1,.2),np.arange(.2,1.01,.2)):
 idx=(pv>=lo)&(pv<hi if hi<.99 else pv<=1)
 if idx.sum():bins.append(dict(mean=float(pv[idx].mean()),obs=float(y[idx].mean()),n=int(idx.sum())))
res=dict(audit=dict(n=len(d),positive=int(d[Y].sum()),missing=missing.to_dict(),chol_zero=zero,dev_n=len(dev),dev_pos=int(y.sum()),test_n=len(test),test_pos=int(yt.sum()),sites=d.site.value_counts().to_dict(),duplicates=int(d.record_id.duplicated().sum())),summary=summary,thresholds=thresholds,threshold=best,test=tm,ci=ci,first_repeat={k:metric(y,v[0]) for k,v in pred.items()},chosen_oof=metric(y,pv,best),duplicate=metric(y,dp),bootstrap_coef=np.quantile(bb,[.025,.5,.975],axis=0).tolist(),stress=metric(y,sp),cov_ratio=ratio.tolist(),bins=bins,p=len(features),age_sd=float(final['pre'].named_transformers_['num']['scale'].scale_[0]))
(O/'分析结果.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8');pd.DataFrame(dict(sample_id=d.iloc[dev].sample_id,y=y,p=pv)).to_csv(O/'开发集折外预测.csv',index=False);pd.DataFrame(dict(sample_id=d.iloc[test].sample_id,y=yt,p=pt)).to_csv(O/'测试预测.csv',index=False)
print(json.dumps(res,ensure_ascii=False,indent=2))
