from pathlib import Path
import sys,warnings
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
warnings.filterwarnings('ignore',category=FutureWarning)
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];O=R/'outputs/补充实验';G=O/'figures';G.mkdir(exist_ok=True)
metrics=pd.read_csv(O/'训练验证指标.csv');raw=pd.read_csv(O/'逐条原始预测.csv');weights=pd.read_csv(O/'类别权重实验.csv');lc=pd.read_csv(O/'学习曲线重复结果.csv');grid=pd.read_csv(R/'outputs/参数网格.csv')
weights['weight']=weights['weight'].fillna('未加权')
B='#387DA0';C='#C9714D';BG='#F7F0E6';GRAY='#8C8176';K='#29343B'
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':BG,'axes.facecolor':BG,'axes.unicode_minus':False,'text.color':K,'svg.fonttype':'none','legend.frameon':False})
def save(f,n):f.savefig(G/f'图{n}.png',dpi=300,bbox_inches='tight',facecolor=BG);f.savefig(G/f'图{n}.svg',bbox_inches='tight',facecolor=BG);plt.close(f)
names=['Linear C=1','RBF C=10 γ=10'];warm=LinearSegmentedColormap.from_list('warm',[BG,C])
f,axs=plt.subplots(2,2,figsize=(10,4.8))
for row,name in enumerate(names):
 for col,part in enumerate(['train','validation']):
  z=raw[(raw.model==name)&(raw.part==part)].sort_values(['abnormal','sample_id']).reset_index(drop=True);a=axs[row,col]
  for y,c,mark in [(0,B,'o'),(1,C,'^')]:q=z[z.abnormal==y];a.scatter(q.index,q.score,c=c,marker=mark,s=16,label='真实 NO' if y==0 else '真实 AB')
  er=z[z.error==1];a.scatter(er.index,er.score,s=40,facecolors='none',edgecolors=K,lw=.7,label='误分类');a.axhline(0,color=GRAY,ls='--');a.set(xlabel='记录顺序（按真实类别、ID排列）',ylabel='决策分数 f');a.set_title(f"{'abcd'[row*2+col]}  {name} · {'训练' if col==0 else '验证'}",loc='left',fontsize=10)
  if row==0 and col==0:a.legend(fontsize=8,ncol=3)
f.tight_layout();save(f,7)
f,axs=plt.subplots(2,2,figsize=(8,5))
for i,name in enumerate(names):
 for j,part in enumerate(['train','validation']):
  z=metrics[(metrics.model==name)&(metrics.part==part)].iloc[0];mat=np.array([[z.TN,z.FP],[z.FN,z.TP]],dtype=int);a=axs[i,j];a.imshow(mat/mat.sum(axis=1,keepdims=True),vmin=0,vmax=1,cmap=warm);a.set_xticks([0,1],['预测 NO','预测 AB']);a.set_yticks([0,1],['真实 NO','真实 AB']);a.set_title(f"{'abcd'[i*2+j]}  {name} · {'训练' if j==0 else '验证'}",loc='left',fontsize=10)
  for rr in range(2):
   for cc in range(2):a.text(cc,rr,f'{mat[rr,cc]}\n{mat[rr,cc]/mat[rr].sum():.1%}',ha='center',va='center',fontsize=11)
f.tight_layout();save(f,8)
f,axs=plt.subplots(1,3,figsize=(11,3.4));rbf=grid[grid.kernel=='rbf'].copy();rbf['gap']=rbf.train_balanced_accuracy-rbf.val_balanced_accuracy
for a,key,title in zip(axs,['train_balanced_accuracy','val_balanced_accuracy','gap'],['a  训练平衡准确率','b  验证平衡准确率','c  训练 − 验证差值']):
 z=rbf.pivot(index='C',columns='gamma',values=key);a.imshow(z,cmap=LinearSegmentedColormap.from_list('difference',[B,BG,C]) if key=='gap' else warm,vmin=-.25 if key=='gap' else .5,vmax=.25 if key=='gap' else 1,aspect='auto');a.set_xticks(range(4),['.01','.1','1','10']);a.set_yticks(range(4),['.1','1','10','100']);a.set(xlabel='gamma',ylabel='C');a.set_title(title,loc='left')
 for i in range(4):
  for j in range(4):a.text(j,i,f'{z.iloc[i,j]:.3f}',ha='center',va='center',fontsize=9)
f.tight_layout();save(f,9)
f=plt.figure(figsize=(10,4));a=f.add_subplot(121,projection='polar');b=f.add_subplot(122)
keys=['accuracy','balanced_accuracy','sensitivity','specificity','f1','roc_auc'];labels=['准确率','平衡准确率','AB召回','NO召回','F1','ROC-AUC'];ang=np.linspace(0,2*np.pi,6,endpoint=False);ang=np.r_[ang,ang[0]]
for name,c in zip(metrics.model.unique(),[GRAY,B,'#B9A27D',C]):
 vals=metrics[(metrics.model==name)&(metrics.part=='validation')].iloc[0][keys].to_numpy(dtype=float);v=np.r_[vals,vals[0]];a.plot(ang,v,color=c,lw=1.4,label=name);a.fill(ang,v,color=c,alpha=.025)
a.set_xticks(ang[:-1],labels);a.set_ylim(0,1);a.set_yticks([.25,.5,.75,1]);a.tick_params(labelsize=9);a.set_title('a  固定配置的验证指标',pad=24,loc='left',fontsize=11);a.legend(loc='lower center',bbox_to_anchor=(.5,-.32),fontsize=8,ncol=2)
for i,name in enumerate(names):
 z=weights[weights.model==name];b.bar(np.arange(2)+i*.32-.16,z.balanced_accuracy,width=.3,color=[B,C][i],label=name)
b.set_xticks([0,1],['无类别加权','balanced']);b.set(ylim=(0,1),ylabel='验证平衡准确率');b.set_title('b  类别权重的实际影响',loc='left',fontsize=11);b.legend(fontsize=8);f.tight_layout();save(f,10)
f,axs=plt.subplots(1,2,figsize=(10,3.4))
summary=lc.groupby(['model','n']).agg(train_mean=('train_ba','mean'),val_mean=('val_ba','mean'),val_sd=('val_ba','std')).reset_index()
for ax,name,letter in zip(axs,names,'ab'):
 z=summary[summary.model==name];sd=z.val_sd.fillna(0);ax.plot(z.n,z.train_mean,color=GRAY,marker='s',ls='--',label='子训练集');ax.plot(z.n,z.val_mean,color=B if letter=='a' else C,marker='o',label='固定验证集');ax.fill_between(z.n,z.val_mean-sd,z.val_mean+sd,color=B if letter=='a' else C,alpha=.15);ax.set(xlabel='训练记录数',ylabel='平衡准确率',ylim=(.45,1));ax.set_title(f'{letter}  {name}',loc='left');ax.legend(fontsize=9)
f.tight_layout();save(f,11)
# Use the same document styles and three-line table helper as the single-column source.
s=(R/'scripts/assignment_report.py').read_text(encoding='utf-8');exec(s[s.index('d=Document();'):s.index("d.add_heading('脊柱")]);d=Document(R/'SVM课程作业_完成稿.docx')
pic=d.inline_shapes[0];rid=pic._inline.graphic.graphicData.pic.blipFill.blip.embed;d.part.related_parts[rid]._blob=(R/'outputs/figures/图1_期刊流程图.png').read_bytes();pic.width=Cm(17.4);pic.height=Cm(17.4*4.1/12)
for sec in d.sections:sec._sectPr.find(qn('w:cols')).set(qn('w:num'),'1')
for q in d.paragraphs:
 if q.text.startswith('图1 '):
  q.clear();q.add_run('图1 SVM研究与评价流程。').bold=True;q.add_run('蓝色为数据准备与训练实验，橙色为验证、配置固定和留出评价。完整训练集用于正式参数实验，测试数据不用于再次选参。新增实验在原测试结果已知后开展，限于训练和验证资料的探索性分析。')
def val(model,part,key):return metrics[(metrics.model==model)&(metrics.part==part)].iloc[0][key]
h('补充实验一 训练与验证记录的逐条预测')
p('本次扩展恢复单栏，并新增逐条预测审计、训练与验证混淆矩阵、泛化差值热力图、参数雷达图、类别权重及训练样本量实验。所有新增模型比较只使用原训练与验证集合；已有测试结果已经公开，因此这些补充分析属于后续探索，不构成新的独立确认，也不回头替换原固定测试配置。')
fig(7,'逐条决策分数与预测错误','每点为一条实际记录，横轴按真实类别和ID排序；蓝圆为真实NO，橙三角为真实AB，黑圈标记误分类，灰虚线为固定阈值0。虚线上方预测AB，下方预测NO。各面板纵轴自动适应完整分数范围，模型间分数大小不直接比较，也不作为风险概率。')
sample=raw[(raw.model==names[1])&(raw.part=='validation')].sort_values('sample_id').head(10)
table('表7 验证集原始逐条结果摘录（RBF C=10，gamma=10）',['ID','骨盆入射角','滑脱程度','真实','分数','预测','错误'],[[z.sample_id,f'{z.pelvic_incidence:.2f}',f'{z.degree_spondylolisthesis:.2f}',int(z.abnormal),f'{z.score:.4f}',int(z.prediction),'是' if z.error else '否'] for z in sample.itertuples()],[2,3,3,1.5,3,1.5,2.4])
p('表7按ID取最前10条验证记录，未按预测成败挑选。两项输入保留source scale，0为NO、1为AB。全部4种配置、两个数据部分的992行逐条预测保存在“逐条原始预测.csv”，可按ID复核输入、真实标签、分数、预测类别和错误标记。训练结果属于拟合表现，验证结果反映未参与参数拟合的记录，但已用于选参。')
h('补充实验二 混淆矩阵显示了哪些错误')
fig(8,'训练与验证的混淆矩阵','a–d分别对应两类模型与训练、验证集合。行是真实类别，列是预测类别；格内第一行为原始人数，第二行为该真实类别中的百分比。色深按行比例统一映射至0–1，避免训练与验证样本量不同导致误读。')
table('表8 原始计数与分类指标',['模型 / 数据','TN','FP','FN','TP','准确率','平衡准确率'],[[('Linear' if n==names[0] else 'RBF')+(' / 训练' if part=='train' else ' / 验证')]+[int(val(n,part,k)) for k in ['TN','FP','FN','TP']]+[f'{val(n,part,k):.3f}' for k in ['accuracy','balanced_accuracy']] for n in names for part in ['train','validation']],[4.2,1.5,1.5,1.5,1.5,3.3,3.9])
p('线性模型在训练集的NO召回率为57/60=0.950，AB召回率为92/126=0.730；验证集分别为18/20=0.900和26/42=0.619。较高的NO识别率掩盖了较多AB漏判，因此不能只报告总体准确率。')
p('RBF在验证集把AB漏判由16条降为8条，同时NO误报由2条增为4条，平衡准确率从0.760增至0.805。它改善了两类识别的均衡性，但这种取舍是否适合实际任务仍取决于误报与漏判的代价。混淆矩阵中的原始人数比单个综合指标更直接。')
h('补充实验三 参数热力图如何揭示过度拟合')
fig(9,'训练 验证与差值热力图','在原16组RBF网格上复算训练和验证指标，不扩大搜索。a–b颜色范围统一为0.50–1.00；c范围为−0.25至0.25，蓝色为负差、米色为零、橙色为正差，数值为训练减验证的平衡准确率。每格为一次固定划分结果，没有统计显著性含义。')
sel=rbf[rbf.gamma==10]
table('表9 gamma=10时的原始训练验证结果',['C','训练错误','验证FN','验证FP','训练BA','验证BA','差值'],[[f'{z.C:g}',int(z.train_errors),int(z.val_FN),int(z.val_FP),f'{z.train_balanced_accuracy:.3f}',f'{z.val_balanced_accuracy:.3f}',f'{z.gap:.3f}'] for z in sel.itertuples()],[1.5,2.5,2.5,2.5,2.8,2.8,2.8])
last=sel[sel.C==100].iloc[0]
p(f'gamma=10、C=100时，训练平衡准确率达到{last.train_balanced_accuracy:.3f}，验证却只有{last.val_balanced_accuracy:.3f}，差值为{last.gap:.3f}。这与训练错误减少但验证识别下降一致，提示该设置对当前训练记录贴合较强。差值是诊断线索，并不是过拟合程度的无偏估计。')
p('C=10、gamma=10仍是原验证规则选出的配置。补充热力图用于解释其附近参数变化，不再依据已知测试表现追加网格或修改配置。低C和低gamma区域训练与验证都较差，说明差值小也可能只是模型表达或惩罚设置不足，不能把“小差值”等同于“好模型”。')
h('补充实验四 参数雷达图与类别权重对照')
fig(10,'不同配置的综合指标与类别加权','a，雷达图使用同一验证集、同一0–1坐标范围，所有指标均为越高越好；各线的参数见图例，F1与召回率以AB为阳性。雷达面积不用于排名，相关指标也不能视作独立证据。b，固定C和gamma，只改变class_weight；蓝色为线性，橙色为RBF。')
table('表10 四种固定配置的验证指标',['配置','准确率','平衡准确率','AB召回','NO召回','F1','AUC'],[[z.model]+[f'{getattr(z,k):.3f}' for k in ['accuracy','balanced_accuracy','sensitivity','specificity','f1','roc_auc']] for z in metrics[metrics.part=='validation'].itertuples()],[4.5,2.1,2.5,2.1,2.1,2,2.1])
table('表11 类别权重实验的原始计数',['模型','权重','TN','FP','FN','TP','平衡准确率'],[[z.model,z.weight,int(z.TN),int(z.FP),int(z.FN),int(z.TP),f'{z.balanced_accuracy:.3f}'] for z in weights.itertuples()],[4.5,2.7,1.5,1.5,1.5,1.5,4.2])
p('训练集NO为60条、AB为126条，balanced权重为NO 1.550、AB约0.738，因此更重视少数类NO。RBF加权后，NO误报由4条降至2条，但AB漏判由8条升至18条，验证平衡准确率从0.805降为0.736。类别加权并不自动提高平衡准确率，也不等于按临床错误代价加权。')
p('雷达图显示RBF C=10、gamma=10有较高AB召回与F1，但其验证AUC低于其余三组。改变排序指标与分类指标的侧重点，可能改变对配置的偏好。因此保持各轴原始数值与相同尺度，不进行有利于某个模型的极差归一化，也不计算雷达图面积作为总分。')
h('补充实验五 训练样本量怎样影响预测')
fig(11,'固定模型配置的学习曲线','每个样本量40、80、120、160均从原训练集进行20次分层子抽样，两个模型使用相同子集；每次重新拟合scaler与SVM，始终评价同一62条验证记录。灰虚线为子训练集平均值，蓝或橙实线为验证平均值，阴影为重复间±1标准差。186条为全训练集的一次拟合，没有重复区间。')
table('表12 学习曲线的实际重复结果',['模型','训练n','重复次数','训练BA均值','验证BA均值','验证BA标准差'],[[z.model,int(z.n),1 if z.n==186 else 20,f'{z.train_mean:.3f}',f'{z.val_mean:.3f}','不适用' if pd.isna(z.val_sd) else f'{z.val_sd:.3f}'] for z in summary.itertuples()],[4,1.8,2.2,3.2,3.2,3])
p('RBF使用40条记录时，平均训练平衡准确率为0.963，验证仅0.675；使用全部186条时，训练为0.870、验证为0.805。训练拟合分数下降的同时验证表现提高，说明更高训练分数不一定意味着学到更可推广的边界。线性模型从40条到80条的验证平均值由0.724升至0.756，后续变化较小且并非严格单调。')
p('这些子集不一定互相嵌套，重复结果也共享原训练池和同一个验证集，因此阴影只是对训练抽样敏感性的描述，不是泛化性能的置信区间。新增实验提供了更完整的内部证据，但不能把同一验证集上的多轮分析当成多份独立验证；原测试结果和结论边界保持不变。')
out=R/'SVM课程作业_单栏实验扩展版.docx';d.save(out);print(out)
