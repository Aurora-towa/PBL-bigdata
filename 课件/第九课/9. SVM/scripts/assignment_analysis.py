from pathlib import Path
import sys,json
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
import numpy as np,pandas as pd
from lab_utils import load_development,geometry_experiment,parameter_experiment,scaling_experiment,select_validation_configs,noise_experiment,evaluate_locked,FEATURES
R=Path(__file__).resolve().parents[1];O=R/'outputs';O.mkdir(exist_ok=True)
tr,va=load_development();geo=geometry_experiment(tr);grid,models=parameter_experiment(tr,va);scale,delta=scaling_experiment(tr,va);configs=select_validation_configs(grid)
# Persist the full development-only choices before accessing any held-out labels.
protocol=dict(features=FEATURES,training_n=186,validation_n=62,scaler='StandardScaler fit on train only',threshold=0,selection='Within each family maximize validation balanced accuracy; tie smaller C then smaller gamma',configs=configs,refit_train_validation=False,test_scope='Course held-out demonstration, already evaluated by course authors; not independent prospective confirmation')
(O/'固定分析方案.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
test=evaluate_locked(configs,freeze_confirmed=True,open_test=True)
for name,data in [('参数网格',grid),('尺度实验',scale),('几何记录',geo['table']),('候选边界',geo['candidates']),('删点实验',geo['changes']),('矛盾标签实验',geo['contradiction']),('固定测试结果',test)]:data.to_csv(O/(name+'.csv'),index=False,encoding='utf-8-sig')
noise=[]
for fam,key in configs.items():
 z=noise_experiment(models[key],tr,va);z['family']=fam;noise.append(z)
pd.concat(noise).to_csv(O/'扰动实验.csv',index=False,encoding='utf-8-sig')
chosen=[]
for fam,key in configs.items():chosen.append(grid[(grid.kernel==key[0])&(grid.C==key[1])&(grid.gamma==key[2])].iloc[0].to_dict())
te=pd.read_csv(R/'data/student/locked-test-features.csv');allx=pd.concat([tr,va,te],ignore_index=True)
assert set(tr.sample_id).isdisjoint(va.sample_id) and set(te.sample_id).isdisjoint(set(tr.sample_id)|set(va.sample_id))
res=dict(audit=dict(n=len(allx),missing=int(allx[FEATURES].isna().sum().sum()),unique_ids=int(allx.sample_id.nunique()),train_pos=int(tr.abnormal.sum()),val_pos=int(va.abnormal.sum()),ranges={c:[float(allx[c].min()),float(allx[c].max())] for c in FEATURES}),geometry=dict(w=geo['model'].coef_[0].tolist(),b=float(geo['model'].intercept_[0]),width=float(2*geo['half_width']),candidates=geo['candidates'].to_dict('records'),changes=geo['changes'].to_dict('records'),contradiction=geo['contradiction'].to_dict('records'),records=geo['table'].to_dict('records')),scale_delta=delta,chosen=chosen,test=test.to_dict('records'),noise=pd.concat(noise).to_dict('records'))
(O/'分析结果.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(res,ensure_ascii=False,indent=2))
