from pathlib import Path
import sys,json,warnings
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
warnings.filterwarnings('ignore',category=FutureWarning)
import numpy as np,pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import precision_score,f1_score
from lab_utils import load_development,make_model,metrics,FEATURES
R=Path(__file__).resolve().parents[1];O=R/'outputs/补充实验';O.mkdir(exist_ok=True)
tr,va=load_development();settings=[('Linear C=0.1','linear',.1,.1),('Linear C=1','linear',1,.1),('RBF C=1 γ=1','rbf',1,1),('RBF C=10 γ=10','rbf',10,10)]
rows=[];preds=[];models={}
for name,k,c,g in settings:
 m=make_model(k,c,g).fit(tr[FEATURES],tr.abnormal);models[name]=m
 for part,df in [('train',tr),('validation',va)]:
  s=m.decision_function(df[FEATURES]);p=(s>=0).astype(int);z=metrics(df.abnormal,s);z.update(model=name,part=part,precision=float(precision_score(df.abnormal,p,zero_division=0)),f1=float(f1_score(df.abnormal,p)),n_sv=len(m['svc'].support_));rows.append(z)
  a=df.copy();a['model']=name;a['part']=part;a['score']=s;a['prediction']=p;a['error']=(p!=df.abnormal).astype(int);preds.append(a)
pd.DataFrame(rows).to_csv(O/'训练验证指标.csv',index=False,encoding='utf-8-sig');pd.concat(preds).to_csv(O/'逐条原始预测.csv',index=False,encoding='utf-8-sig')
weights=[]
for name,k,c,g in [settings[1],settings[3]]:
 for weight in [None,'balanced']:
  m=make_model(k,c,g);m.set_params(svc__class_weight=weight);m.fit(tr[FEATURES],tr.abnormal);z=metrics(va.abnormal,m.decision_function(va[FEATURES]));z.update(model=name,weight=str(weight));weights.append(z)
pd.DataFrame(weights).to_csv(O/'类别权重实验.csv',index=False,encoding='utf-8-sig')
learning=[]
for n in [40,80,120,160,186]:
 splits=[np.arange(len(tr))] if n==186 else [a for a,b in StratifiedShuffleSplit(n_splits=20,train_size=n,random_state=2026+n).split(tr,tr.abnormal)]
 for rep,ix in enumerate(splits):
  for name,k,c,g in [settings[1],settings[3]]:
   m=make_model(k,c,g).fit(tr.iloc[ix][FEATURES],tr.iloc[ix].abnormal);a=metrics(tr.iloc[ix].abnormal,m.decision_function(tr.iloc[ix][FEATURES]));b=metrics(va.abnormal,m.decision_function(va[FEATURES]));learning.append(dict(model=name,n=n,rep=rep,train_ba=a['balanced_accuracy'],val_ba=b['balanced_accuracy']))
pd.DataFrame(learning).to_csv(O/'学习曲线重复结果.csv',index=False,encoding='utf-8-sig')
print(pd.DataFrame(rows).to_string(index=False));print(pd.DataFrame(weights).to_string(index=False));print(pd.DataFrame(learning).groupby(['model','n'])[['train_ba','val_ba']].mean().to_string())
