from pathlib import Path
import sys,json,hashlib,platform
from datetime import datetime,timezone
sys.path.insert(0,'D:\\课程\\大数据实践课\\第五课\\hypothesis\\.analysis-deps')
import numpy as np
import pandas as pd
import scipy
from scipy import stats
from statsmodels.stats.multitest import multipletests
ROOT=Path('C:/Users/340/Desktop/6. multiple-test')
OUT=ROOT/'outputs/2026-10-14';OUT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'data/leukemia.csv'
def bh(p):
 p=np.asarray(p); ix=np.argsort(p,kind='stable'); adj=np.minimum.accumulate((p[ix]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1]; out=np.empty(len(p));out[ix]=np.minimum(adj,1);return out
def test(d,probes):
 a=d.loc[d.diagnosis=='AML',probes].to_numpy(float);b=d.loc[d.diagnosis=='ALL',probes].to_numpy(float)
 va=a.var(0,ddof=1)/len(a);vb=b.var(0,ddof=1)/len(b);se=np.sqrt(va+vb);df=(va+vb)**2/(va**2/(len(a)-1)+vb**2/(len(b)-1));delta=a.mean(0)-b.mean(0);crit=stats.t.ppf(.975,df);p=stats.ttest_ind(a,b,axis=0,equal_var=False).pvalue
 sd=np.sqrt(((len(a)-1)*a.var(0,ddof=1)+(len(b)-1)*b.var(0,ddof=1))/(len(a)+len(b)-2))
 return pd.DataFrame(dict(probe=probes,n_AML=len(a),n_ALL=len(b),mean_AML=a.mean(0),mean_ALL=b.mean(0),delta=delta,lo=delta-crit*se,hi=delta+crit*se,d=delta/sd,pooled_sd=sd,p=p,bonf=np.minimum(p*len(p),1),bh=bh(p)))
# Read only discovery rows before storing the locked list and validation rule.
train=pd.read_csv(SRC,nrows=38);assert (train.original_split=='train').all()
probes=train.columns[3:].tolist();assert len(probes)==7129
res=test(train,probes);assert np.isfinite(res.p).all()
np.testing.assert_allclose(res.bh,multipletests(res.p,method='fdr_bh')[1],rtol=1e-12)
rank=res.sort_values(['p','probe']);lock=rank[rank.bh<=.05].head(10).copy()
lockpath=OUT/'locked_candidates.json'
payload=dict(locked_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),discovery_rule='BH<=0.05 among 7129 probes, sort raw p then probe, first 10',validation_rule='Two-sided Welch; candidate-family Bonferroni<=0.05 and same delta sign',candidates=lock[['probe','delta','p','bh']].to_dict('records'))
if lockpath.exists():
 prior=json.loads(lockpath.read_text(encoding='utf-8'));assert prior['candidates']==payload['candidates'];payload=prior
else:
 with lockpath.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
print('Candidates locked before holdout access',flush=True)
all_data=pd.read_csv(SRC);valid=all_data[all_data.original_split=='test'];assert len(valid)==34
vr=test(valid,lock.probe.tolist());joined=lock.merge(vr,on='probe',suffixes=('_discovery','_validation'));joined['same_direction']=np.sign(joined.delta_discovery)==np.sign(joined.delta_validation);joined['replicated']=joined.same_direction&(joined.bonf_validation<=.05)
res.to_csv(OUT/'discovery_all_7129.csv',index=False,encoding='utf-8-sig');joined.to_csv(OUT/'candidate_validation.csv',index=False,encoding='utf-8-sig')
top20=rank.head(20).copy();top20['wrong_bh']=bh(top20.p);top20.to_csv(OUT/'selection_bias_example.csv',index=False,encoding='utf-8-sig')
assert all_data.sample_id.is_unique and len(all_data.columns)==len(set(all_data.columns))
v=all_data[probes].to_numpy(float);assert np.isfinite(v).all()
qc=dict(n=len(all_data),m=len(probes),missing=int(np.isnan(v).sum()),negative=int((v<0).sum()),zero=int((v==0).sum()),minimum=float(v.min()),maximum=float(v.max()),constant=int((np.ptp(v,axis=0)==0).sum()),duplicate_rows=int(all_data[probes].duplicated().sum()),controls=sum(x.startswith('AFFX') for x in probes))
# Known-truth simulation: same normal noise for all three signal settings.
rng=np.random.default_rng(42);records=[]
for rep in range(1000):
 a=rng.normal(size=(11,1000));b=rng.normal(size=(27,1000));base=a.mean(0)-b.mean(0);sp=((10*a.var(0,ddof=1)+26*b.var(0,ddof=1))/36)**.5;se=sp*np.sqrt(1/11+1/27)
 for delta in [0.,.5,1.]:
  dif=base.copy();dif[:100]+=delta;p=2*stats.t.sf(abs(dif/se),36)
  for method,adj in [('Raw',p),('Bonferroni',np.minimum(p*1000,1)),('BH',bh(p))]:
   reject=adj<=.05;R=int(reject.sum());S=int(reject[:100].sum()) if delta else 0;V=R-S
   records.append(dict(rep=rep,delta=delta,method=method,R=R,V=V,S=S,FDP=V/max(R,1),FWER=int(V>0),power=S/100 if delta else np.nan))
sim=pd.DataFrame(records);sim.to_csv(OUT/'simulation_runs.csv',index=False)
summary=[]
for (delta,method),g in sim.groupby(['delta','method'],sort=False):
 summary.append(dict(delta=delta,method=method,first_R=int(g.iloc[0].R),mean_R=float(g.R.mean()),sd_R=float(g.R.std()),q05=float(g.R.quantile(.05)),q95=float(g.R.quantile(.95)),mean_V=float(g.V.mean()),FWER=float(g.FWER.mean()),FDR=float(g.FDP.mean()),power=float(g.power.mean()) if delta else None,FDR_mcse=float(g.FDP.std()/np.sqrt(len(g)))))
pd.DataFrame(summary).to_csv(OUT/'simulation_summary.csv',index=False,encoding='utf-8-sig')
ans=dict(qc=qc,counts={'Raw':int((res.p<=.05).sum()),'Bonferroni':int((res.bonf<=.05).sum()),'BH':int((res.bh<=.05).sum())},bonf_threshold=.05/len(probes),bh_raw_threshold=float(res.loc[res.bh<=.05,'p'].max()),replicated=int(joined.replicated.sum()),direction_consistent=int(joined.same_direction.sum()),candidate_n=len(joined),candidate_control_n=int(joined.probe.str.startswith('AFFX').sum()),simulation=summary,lock=payload,versions={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__})
(OUT/'results.json').write_text(json.dumps(ans,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:ans[k] for k in ['qc','counts','bonf_threshold','replicated','direction_consistent']},indent=2),flush=True)
print(joined[['probe','delta_discovery','bh_discovery','delta_validation','bonf_validation','replicated']].to_string(index=False),flush=True)
print(pd.DataFrame(summary)[['delta','method','mean_R','FDR','FWER','power']].to_string(index=False))
