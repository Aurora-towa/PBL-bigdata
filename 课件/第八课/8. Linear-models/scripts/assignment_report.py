from pathlib import Path
import sys,json
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from sklearn.metrics import roc_curve
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];O=R/'outputs';G=O/'figures';G.mkdir(exist_ok=True)
r=json.loads((O/'分析结果.json').read_text(encoding='utf-8'));co=pd.read_csv(O/'系数与OR.csv');dv=pd.read_csv(O/'开发集折外预测.csv');te=pd.read_csv(O/'测试预测.csv')
B='#387DA0';C='#C9714D';BG='#F7F0E6';K='#29343B';GRAY='#8C8176'
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.facecolor':BG,'figure.facecolor':BG,'axes.unicode_minus':False,'svg.fonttype':'none','text.color':K,'axes.labelcolor':K,'legend.frameon':False})
def save(f,n):
 f.savefig(G/f'fig{n}.png',dpi=260,bbox_inches='tight',facecolor=BG);f.savefig(G/f'fig{n}.svg',bbox_inches='tight',facecolor=BG);plt.close(f)
f,axs=plt.subplots(1,2,figsize=(10,3.3),gridspec_kw={'width_ratios':[1.2,1]});a=axs[0];a.axis('off');a.set(xlim=(0,6),ylim=(0,4))
for x,y,w,text in [(.1,2.9,5.6,'270 条记录  →  分层固定划分'),(.1,1.6,2.6,'开发集 216 条\n5 折 × 5 次重复'),(3.1,1.6,2.6,'测试集 54 条\n固定方案后评价'),(.1,.2,2.6,'训练折内填补与编码\n折外比较与阈值选择'),(3.1,.2,2.6,'L2 Logistic  C = 1\n阈值 0.20')]:
 a.add_patch(FancyBboxPatch((x,y),w,.85,boxstyle='round,pad=.03',facecolor='#EFDCC8',edgecolor='#C7A58A'));a.text(x+w/2,y+.425,text,ha='center',va='center',fontsize=11)
for x in [1.4,4.4]:a.annotate('',xy=(x,2.5),xytext=(3,2.9),arrowprops=dict(arrowstyle='->',color=K));a.annotate('',xy=(x,1.1),xytext=(x,1.6),arrowprops=dict(arrowstyle='->',color=K))
a.set_title('a  分析流程',loc='left');miss=r['audit']['missing'];ks=list(miss)[:9];vals=[miss[k]/270*100 for k in ks];axs[1].barh(ks,vals,color=C);axs[1].invert_yaxis();axs[1].set(xlabel='原始缺失比例（%）',xlim=(0,80));axs[1].set_title('b  数据审计',loc='left')
for i,z in enumerate(vals):axs[1].text(z+1,i,f'{z:.1f}',va='center',fontsize=9)
f.tight_layout();save(f,1)
f,axs=plt.subplots(1,3,figsize=(10,3));z=np.linspace(-5,5,300);sig=1/(1+np.exp(-z));axs[0].plot(z,sig,color=B,lw=2);axs[0].axhline(.2,color=C,ls='--');axs[0].axhline(.5,color=GRAY,ls=':');axs[0].set(xlabel='线性评分 z',ylabel='阳性概率 p');axs[0].set_title('a  Logistic 概率映射',loc='left')
xx=np.linspace(-4,5,300)
for mu,col,lab in [(-.5,B,'类别 0'),(1.5,C,'类别 1')]:axs[1].plot(xx,np.exp(-.5*(xx-mu)**2)/np.sqrt(2*np.pi),color=col,label=lab)
axs[1].set(xlabel='一维输入（概念示意）',ylabel='类条件密度');axs[1].legend(fontsize=9);axs[1].set_title('b  LDA 共享方差示意',loc='left')
pp=np.arange(1,31);axs[2].plot(pp,pp+1,label='Logistic',color=B);axs[2].plot(pp,2*pp+pp*(pp+1)/2+1,label='LDA',color=C);axs[2].scatter([20,20],[21,251],color=[B,C]);axs[2].set(xlabel='编码后维度 p',ylabel='名义参数数目');axs[2].legend(fontsize=9);axs[2].set_title('c  参数规模',loc='left');f.tight_layout();save(f,2)
f,axs=plt.subplots(1,3,figsize=(10,3));models=['Logistic','LDA','Gaussian NB','先验基线'];cols=[B,C,GRAY,'#B8ADA0']
for j,(met,title) in enumerate([('auc','a  ROC-AUC'),('brier','b  Brier 分数'),('loss','c  平均交叉熵')]):
 vals=[r['summary'][k][met] for k in models];axs[j].bar(range(4),vals,color=cols);axs[j].set_xticks(range(4),['Logistic','LDA','GNB','先验'],rotation=20);axs[j].set_title(title,loc='left');axs[j].set_ylim(0,max(vals)*1.25)
 for i,v in enumerate(vals):axs[j].text(i,v+max(vals)*.03,f'{v:.3f}',ha='center',fontsize=9)
f.tight_layout();save(f,3)
f,axs=plt.subplots(1,2,figsize=(10,3));ts=r['thresholds'];tt=[z['t'] for z in ts];axs[0].plot(tt,[z['cost'] for z in ts],color=B,marker='o',label='平均代价');axs[0].axvline(.2,color=C,ls='--',label='固定阈值 0.20');axs[0].set(xlabel='分类阈值',ylabel='5 × FN + FP');axs[0].legend(fontsize=9);axs[0].set_title('a  开发集阈值选择',loc='left');axs[1].plot(tt,[z['fn'] for z in ts],color=C,marker='o',label='FN 漏判');axs[1].plot(tt,[z['fp'] for z in ts],color=B,marker='s',label='FP 误报');axs[1].set(xlabel='分类阈值',ylabel='平均记录数');axs[1].legend(fontsize=9);axs[1].set_title('b  错误类型的取舍',loc='left');f.tight_layout();save(f,4)
f,axs=plt.subplots(1,3,figsize=(10,3.2));bb=np.load(O/'年龄系数bootstrap.npy');bp=axs[0].boxplot(bb,tick_labels=['原年龄','新增后\n年龄','年龄\n近重复列'],patch_artist=True,showfliers=False)
for p,c in zip(bp['boxes'],[B,C,GRAY]):p.set_facecolor(c);p.set_alpha(.55)
axs[0].axhline(0,color=GRAY,ls='--',lw=.8);axs[0].set(ylabel='标准化变量的系数');axs[0].set_title('a  系数重采样分布',loc='left')
axs[1].barh(['age','trestbps','chol','thalach','oldpeak'],r['cov_ratio'],color=C);axs[1].axvline(1,color=GRAY,ls='--');axs[1].set(xlabel='阳性 / 阴性类方差');axs[1].set_title('b  共享方差压力',loc='left')
axs[2].plot([0,1],[0,1],color=GRAY,ls='--');axs[2].plot([b['mean'] for b in r['bins']],[b['obs'] for b in r['bins']],color=B,marker='o');axs[2].set(xlabel='箱内平均预测概率',ylabel='实际阳性比例',xlim=(0,1),ylim=(0,1));axs[2].set_title('c  折外可靠性图',loc='left');f.tight_layout();save(f,5)
f,axs=plt.subplots(1,2,figsize=(10,3));mat=np.array([[14,16],[1,23]]);from matplotlib.colors import LinearSegmentedColormap
axs[0].imshow(mat,cmap=LinearSegmentedColormap.from_list('warm',[BG,C]),vmin=0,vmax=24);axs[0].set_xticks([0,1],['预测阴性','预测阳性']);axs[0].set_yticks([0,1],['实际阴性','实际阳性']);axs[0].set_title('a  固定测试混淆矩阵',loc='left')
for i in range(2):
 for j in range(2):axs[0].text(j,i,str(mat[i,j]),ha='center',va='center',fontsize=16)
for i,(k,label) in enumerate([('auc','ROC-AUC'),('sensitivity','敏感度'),('specificity','特异度'),('precision','精确率')]):
 val=r['test'][k];lo,hi=r['ci'][k];axs[1].errorbar(val,i,xerr=[[val-lo],[hi-val]],fmt='o',capsize=4,color=B if i==0 else C)
axs[1].set_yticks(range(4),['ROC-AUC','敏感度','特异度','精确率']);axs[1].set(xlim=(0,1.06),xlabel='指标及 bootstrap 95% 区间');axs[1].invert_yaxis();axs[1].set_title('b  评价不确定性',loc='left');f.tight_layout();save(f,6)

# Reuse the established report's table, paragraph and page styles.
old=Path('D:/课程/大数据实践课/第七课/7. Naive-Bayes/scripts/course_report_build.py').read_text(encoding='utf-8');start=old.index('d=Document();');end=old.index("d.add_heading('六项")
exec(old[start:end])
def fig(n,title,caption):
 q=d.add_paragraph();q.alignment=1;q.paragraph_format.keep_with_next=True;q.paragraph_format.space_before=Pt(5);q.add_run().add_picture(str(G/f'fig{n}.png'),width=Cm(17.4));q=d.add_paragraph(style='Caption');q.add_run(f'图{n} {title}。').bold=True;q.add_run(caption);q.paragraph_format.line_spacing=1.05
def f3(v):return f'{v:.3f}'
d.add_heading('心脏病数据中的线性分类模型比较',0)
h('问题一 数据条件允许我们回答什么',False)
p('本作业比较 Logistic 回归与线性判别分析（LDA）如何产生预测概率，并分析参数规模、缺失数据、分类阈值及系数稳定性。开发集重复交叉验证中，Logistic 的平均ROC-AUC为0.825，LDA为0.812。固定Logistic模型与0.20阈值后，54条测试记录中漏判1条、误报16条。这一方案体现了题设对漏判的较高代价，但不意味着模型已具备临床应用条件。')
p('数据包含270条教学记录，阳性120条、阴性150条，来自Cleveland、Hungary、VA Long Beach和Switzerland，分别为87、85、71、27条。沿用课程80%/20%分层划分，随机种子2026，得到216条开发记录和54条测试记录。该教学文件由既有UCI多站点资料整理，不是新招募的独立临床队列。')
fig(1,'数据划分与缺失审计','a，浅棕框表示各分析阶段；测试数据只评价已固定方案。b，橙色条形为原始缺失比例；图中尚未计入胆固醇的42个零值。所有填补、标准化、编码和模型拟合均在训练折内完成。')
table('表1 分析数据与预处理',['项目','实际情况','处理方法'],[['划分','开发216条：96阳性；测试54条：24阳性','保留固定测试集'],['连续变量','age、trestbps、chol、thalach、oldpeak','训练折中位数填补后标准化'],['分类变量','sex、cp、fbs、restecg、exang、slope、ca、thal','训练折众数填补；删除参照水平编码'],['排除字段','sample_id、record_id、site、num、目标标签','标识或审计字段；num含结局信息']],[2.5,8.4,6.5])
p('实际文件与README的“无缺失”描述不一致：ca、thal、slope分别缺失181、151、103条。胆固醇另有42个零值，本分析将其视为无效测量并转为缺失，与原有9个缺失合计51条。该处理在建模前固定，并非按预测结果选择。未删除高缺失列，所得结果因此依赖填补规则。')
p('record_id没有重复，但不足以证明不同编号一定来自独立患者。采用随机分层划分也不能替代跨中心验证。site仅用于审计，不进入模型；高缺失率及中心差异仍可能影响模型的推广范围。')

h('问题二 相同的线性边界来自怎样的建模过程')
table('表2 Logistic 与 LDA 的对象 参数和目标',['比较内容','Logistic 回归','LDA'],[['建模对象','直接建模P(Y=1 | X)','建模P(X | Y=k)及类别先验πk'],['主要参数','截距β₀与系数β','两类均值μ₀、μ₁，共享协方差Σ及先验'],['估计目标','最小化二分类交叉熵；本次加入L2惩罚','估计类均值、共享类内协方差及先验'],['概率来源','z=β₀+xᵀβ，经sigmoid得到p','类条件密度乘先验，经Bayes归一化'],['主要假设','log-odds与编码后输入呈线性关系','类别内多元正态，且两类共享协方差'],['本次设置','L2惩罚，C=1，拟合截距','SVD求解；不额外调节收缩参数']],[2.6,7.4,7.4])
fig(2,'概率来源与参数规模','a，蓝线为sigmoid，橙虚线与灰点线分别标出0.20和0.50。b，仅为同方差正态密度概念示意，蓝色和橙色表示两类，并非实际数据分布。c，蓝色为Logistic，橙色为LDA；圆点表示本次p=20。')
p('Logistic中的z是线性评分，p=1/(1+exp(−z))，log[p/(1−p)]=z。训练寻找使真实标签对应的预测概率较大、平均交叉熵较小的系数；L2惩罚限制系数过大。它不要求输入服从正态分布，也不假设各输入相互独立，但线性log-odds、数据质量和泛化能力仍需检查。')
p('LDA假设X | Y=k服从N(μk,Σ)。比较两类对数密度时，共同的二次项−xᵀΣ⁻¹x/2抵消，留下关于x的线性判别分数，因此也能得到线性边界和后验概率。若允许类别各有协方差，便成为QDA，一般产生二次边界。')
p('5个连续变量加15个非参照哑变量，共p=20。八个分类变量的参照水平依次为sex=0、cp=1、fbs=0、restecg=0、exang=0、slope=1、ca=0、thal=3。Logistic名义参数为p+1=21；两类LDA为2p+p(p+1)/2+1=251，其中共享协方差占210项；QDA为2p+p(p+1)+1=461。惩罚与矩阵秩会影响有效复杂度，不能把名义参数数目机械地当作有效自由度。')
p('分类阈值t对应边界z=log[t/(1−t)]。从0.50降到0.20，边界常数从0变为−1.386，方向不变、参数不变。改变阈值不会重新训练模型，也不会改变原始概率或排序。')

h('问题三 开发集证据支持哪一种方法')
p('预先指定Logistic为阈值分析候选：本题输入为混合变量，目标是条件概率与错误代价，且高缺失率和哑变量给LDA的类内正态假设带来压力。采用5折分层交叉验证，重复5次，随机种子2026至2030。每次重复中每条开发记录恰有一次折外预测；先计算该次指标，再对5次取平均，不把重复预测当成新样本。')
table('表3 开发集重复折外评价',['模型','ROC-AUC','AP','Brier','交叉熵','FN','FP','代价'],[[k]+[f3(r['summary'][k][z]) for z in ['auc','ap','brier','loss']]+[f"{r['summary'][k][z]:.1f}" for z in ['fn','fp','cost']] for k in models],[3.8,1.9,1.7,1.8,1.8,1.5,1.5,1.8])
fig(3,'区分能力与概率误差','蓝色为Logistic，橙色为LDA，深灰色为Gaussian NB，浅灰色为先验基线。ROC-AUC越大越好，Brier与交叉熵越小越好。各柱为5次重复的指标平均值；表3的错误计数使用阈值0.50，代价为5×FN+FP。')
p('Logistic在本次平均AUC、Brier和交叉熵上均优于LDA，但AUC差值仅0.013，不能据此宣称其在所有人群中更优。LDA仍是有意义的生成式对照；若连续输入的类条件分布较接近正态、协方差结构稳定，或可以合理收缩协方差，它可能具有优势。方法选择应同时依据假设、样本量和任务目标。')
p('Gaussian NB对one-hot后的二元列使用正态近似，并忽略特征相关性，在这里属于假设压力较大的对照。其平均交叉熵3.685明显较高，说明只看排序会遗漏概率质量问题。它的表现不能代表Bernoulli NB，也不能据此否定所有朴素贝叶斯模型。')
p('先验基线只使用训练折阳性比例。不同折的比例略有不同，使汇总折外AUC为0.496而非恰好0.500；这不是有用的排序能力。AP为average precision，不与梯形积分PR面积混用。Brier与交叉熵综合反映概率误差，不能单独证明校准良好。')
p('与课程Notebook相比，本报告明确使用删除参照水平的编码，避免全套哑变量的线性依赖，并增加重复验证及无效胆固醇处理。因此结果应与这里保存的脚本配套复核，不能直接套用原Notebook的数字。')

h('问题四 漏判代价怎样决定分类阈值')
p('按题设把一次漏判的代价设为5，一次误报设为1，比较0.10至0.90、步长0.10的固定阈值网格。对Logistic的每次重复折外预测计算5×FN+FP，再对5次取平均；选择平均代价最低者，并列时取较低阈值。最终阈值为0.20，在查看测试指标前保存方案，随后以全部开发集拟合一次最终模型。')
fig(4,'阈值与错误代价的取舍','a，蓝线为平均代价，橙虚线为固定阈值0.20。b，橙线为漏判FN，蓝线为误报FP。每个点均来自同一开发集的5次重复折外预测；小数计数表示重复平均，不是部分个体。')
table('表4 代表性阈值的平均错误与代价',['阈值','FN','FP','5×FN+FP'],[[f"{z['t']:.2f}",f"{z['fn']:.1f}",f"{z['fp']:.1f}",f"{z['cost']:.1f}"] for z in r['thresholds'] if z['t'] in [.1,.2,.3,.5,.9]],[3.7,4.3,4.3,5.1])
p('阈值从0.50降至0.20时，平均漏判从27.2条降至9.2条，误报从23.8条升至60.2条，代价从159.8降至106.2。0.10的代价为107.4，与0.20相差仅1.2，提示阈值选择并不十分稳健；不能把0.20写成精确、普适的临床最佳阈值。')
p('第一轮折外预测在0.20下得到TP=86、FN=10、TN=60、FP=60，敏感度86/96=0.896、特异度60/120=0.500、精确率86/146=0.589。降低阈值主要改善的是漏判代价，并未提高所有指标。重复平均表与单轮计数对应不同汇总层次，不应混算。')
p('若概率已可靠校准且上述代价适用于目标人群，理论行动阈值为1/(5+1)=0.167；本报告按规定离散网格比较，选择0.20。实际资料没有证明这些前提，故理论值只帮助解释代价方向。用于选阈值的折外结果仍是开发证据，最低代价可能受选择乐观偏差影响，需要固定测试评价。')

h('问题五 系数稳定是否意味着预测稳定')
p(f"最终开发模型的年龄系数为0.328，OR=exp(0.328)=1.388。年龄标准化使用开发集标准差{r['age_sd']:.2f}岁，因此解释为：其他编码变量固定时，年龄每增加约10.06岁，模型中的阳性优势乘以1.388。这是带L2惩罚的条件关联，不是因果效应。OR=2时，若原概率为0.20，新概率为2×0.20/(1−0.20+2×0.20)=0.333，并非0.40。")
fig(5,'系数稳定性与模型假设检查','a，开发记录成对bootstrap重采样200次，每次重新填补、标准化和拟合；蓝、橙、灰箱分别表示原模型年龄、加入近重复列后的年龄和近重复列，箱体为四分位范围，中线为中位数，须为1.5倍IQR，未绘制离群点。b，橙条为开发集填补后连续变量的类内方差比，灰虚线为1。c，蓝点为首轮折外预测的五个等宽概率箱，灰虚线为理想一致线。')
table('表5 近重复变量实验与LDA压力实验',['实验','ROC-AUC','Brier','交叉熵'],[['原Logistic 首轮',f3(r['first_repeat']['Logistic']['auc']),f3(r['first_repeat']['Logistic']['brier']),f3(r['first_repeat']['Logistic']['loss'])],['加入年龄近重复列',f3(r['duplicate']['auc']),f3(r['duplicate']['brier']),f3(r['duplicate']['loss'])],['原LDA 首轮',f3(r['first_repeat']['LDA']['auc']),f3(r['first_repeat']['LDA']['brier']),f3(r['first_repeat']['LDA']['loss'])],['LDA 年龄非线性变换',f3(r['stress']['auc']),f3(r['stress']['brier']),f3(r['stress']['loss'])]],[6.3,3.7,3.7,3.7])
p('近重复列为年龄加标准差0.5岁的固定随机噪声，种子8。加入后首轮AUC几乎不变，但年龄的信息在两列系数之间重新分配。原模型年龄系数的bootstrap中位数为0.336，加入后原年龄与近重复列分别为0.292和0.040；二者各自的2.5%–97.5%范围为[0.022,0.603]和[−0.214,0.344]。预测相近不意味着单个系数可以稳定解释。')
p('本实验使用L2惩罚，所以不能预设近重复变量一定导致系数大幅发散；这里主要观察到信息分配变化。bootstrap范围是描述性重采样结果，并非无偏的因果效应置信区间。每次重采样的标准差重新估计，系数对应各次样本内的一标准差变化。')
p('LDA检查中，oldpeak的阳性/阴性类内方差比为2.875，提示共享协方差近似存在压力；二元哑变量本身也不严格正态。将年龄替换为exp((age−50)/10)后，LDA首轮AUC由0.789降为0.785，Brier由0.199升为0.202，变化较小。该人为压力实验改变了特征表示，不是对正态性假设的单独因果检验，也不据此调整最终方案。')

h('问题六 固定测试结果能支持什么结论')
p('固定方案为13项原始输入、折内填补与标准化、删除参照水平编码、L2 Logistic（C=1）及阈值0.20。模型仅在216条开发记录上拟合。测试54条中有24条阳性和30条阴性，得到TP=23、FN=1、TN=14、FP=16，代价5×1+16=21。未根据测试结果更换模型或阈值。')
fig(6,'固定测试评价及不确定性','a，格内数字为实际记录数，暖色深浅表示计数大小。b，圆点为测试指标，横线为对测试记录重采样2000次所得百分位95%区间，蓝色表示排序指标，橙色表示分类指标。每次保留已拟合模型和阈值，不重新训练。')
table('表6 固定测试的主要指标',['指标','点估计','bootstrap 95%区间'],[[lab,f3(r['test'][k]),f"[{r['ci'][k][0]:.3f}, {r['ci'][k][1]:.3f}]"] for k,lab in [('auc','ROC-AUC'),('ap','AP'),('brier','Brier'),('loss','交叉熵'),('accuracy','准确率'),('sensitivity','敏感度'),('specificity','特异度'),('precision','精确率')]],[5.2,4.5,7.7])
p('敏感度为23/24=0.958，而特异度仅14/30=0.467，精确率23/39=0.590。漏判较少伴随较多误报，符合本题代价设定，但是否值得仍取决于后续检查负担。AUC=0.814描述排序，Brier=0.181描述概率误差，固定阈值计数描述行动后果，三者不能互相替代。')
p('区间仅描述这54条测试记录在固定模型下的抽样波动，不涵盖训练集变化、阈值选择、填补误差和中心迁移。可靠性图各箱记录数为70、39、39、31、37；其中平均预测0.702的箱实际阳性比例0.613，提示应关注概率偏差，但不足以断言整体已校准。')
p('综合当前任务，Logistic具有更直接的条件概率建模方式、较少的名义参数，且本次开发证据较好，因此作为主方案有充分理由。LDA仍有比较价值，不能因小幅分数差异而否定。下一步应以独立患者及中心验证，核查高缺失字段和中心效应，并重新评价目标人群的校准与错误代价。本作业不支持因果解释、临床部署或跨医院有效性结论。')
for st in d.styles:
 if st.type in [1,2]:
  st.font.name='Times New Roman';rf=st._element.get_or_add_rPr().get_or_add_rFonts()
  for k,val in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia','宋体')]:rf.set(qn('w:'+k),val)
  for k in ['asciiTheme','hAnsiTheme','eastAsiaTheme']:
   if qn('w:'+k) in rf.attrib:del rf.attrib[qn('w:'+k)]
foot=s.footer.paragraphs[0];foot.alignment=1;fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');foot._p.append(fld)
out=R/'线性模型课程作业_完成稿.docx';d.save(out);print(out)
