from pathlib import Path
import sys,json
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import roc_curve,precision_recall_curve
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];O=R/'outputs/课程作业';G=O/'figures';G.mkdir(exist_ok=True)
r=json.loads((O/'计算结果.json').read_text(encoding='utf-8'));v=pd.read_csv(O/'validation_predictions.csv')
B='#387DA0';C='#C9714D';BG='#F7F0E6';K='#29343B';names=['发热','恶心','腰痛','尿意频繁','排尿痛','尿道灼痛']
matplotlib.colormaps.register(LinearSegmentedColormap.from_list('course_warm',[BG,'#E9C4A5',C]),force=True)
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':K,'text.color':K,'axes.facecolor':BG,'figure.facecolor':BG,'axes.unicode_minus':False,'svg.fonttype':'none'})
def save(f,n):
 f.set_facecolor(BG)
 for ax in f.axes:
  ax.set_facecolor(BG)
  ax.tick_params(labelsize=10)
  ax.title.set_fontsize(12)
 f.savefig(G/(n+'.png'),dpi=240,bbox_inches='tight',facecolor=BG);f.savefig(G/(n+'.svg'),bbox_inches='tight',facecolor=BG);plt.close(f)
f,ax=plt.subplots(figsize=(10,3.5));ax.set(xlim=(0,10),ylim=(0,3.5));ax.axis('off')
boxes=[(.1,2.2,2.5,'a  六项二元症状\n120 条专家构造记录'),(3.5,2.2,2.8,'b  训练集 72 条\n估计先验与条件概率'),(7,2.2,2.8,'c  验证集 24 条\n比较阈值与预测误差'),(7,.2,2.8,'d  固定六症状模型\nα = 1；阈值 = 0.50'),(3.5,.2,2.8,'e  测试集 24 条\n只评价固定方案'),(.1,.2,2.5,'f  解释与限制\n构造记录 ≠ 临床患者')]
for x,y,w,s in boxes:
 ax.add_patch(FancyBboxPatch((x,y),w,1,boxstyle='round,pad=0.03',facecolor='#F4E4D5',edgecolor='#C7A58A',lw=.9));ax.text(x+w/2,y+.5,s,ha='center',va='center',linespacing=1.7)
for a,b in [((2.65,2.7),(3.45,2.7)),((6.35,2.7),(6.95,2.7)),((8.4,2.15),(8.4,1.25)),((6.95,.7),(6.35,.7)),((3.45,.7),(2.65,.7))]:ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color=K,lw=1.4))
save(f,'fig1')
f,axs=plt.subplots(1,2,figsize=(10,3.2),gridspec_kw={'width_ratios':[1.65,1]});th=np.array(r['theta']);im=axs[0].imshow(th,vmin=0,vmax=1,cmap='course_warm',aspect='auto');axs[0].set_xticks(range(6),names);axs[0].set_yticks([0,1],['阴性类','阳性类']);axs[0].set_title('a  类别内症状出现概率',loc='left')
for i in range(2):
 for j in range(6):axs[0].text(j,i,f'{th[i,j]:.3f}',ha='center',va='center',color='white' if th[i,j]>.65 else K)
axs[1].bar(['阴性','阳性'],[1-r['manual_p'],r['manual_p']],color=[B,C],width=.55);axs[1].set(ylim=(0,1.15),ylabel='查询记录的后验概率');axs[1].set_title('b  六症状合并后的预测',loc='left');axs[1].text(1,1.02,f"{r['manual_p']:.4f}",ha='center');f.tight_layout();save(f,'fig2')
f,axs=plt.subplots(1,3,figsize=(10,3));labs=['仅用先验','六症状 NB','概率压缩后'];keys=['baseline','val','transformed']
for ax,metric,title in zip(axs,['accuracy','auc','logloss'],['a  分类准确率','b  ROC-AUC','c  平均交叉熵']):
 vals=[r[k][metric] for k in keys];ax.bar(range(3),vals,color=['#A8ABA9',B,C],width=.6);ax.set_xticks(range(3),labs,rotation=15);ax.set_title(title,loc='left');ax.set_ylim(0,max(vals)*1.25)
 for i,z in enumerate(vals):ax.text(i,z+.02*max(vals),f'{z:.3f}',ha='center')
f.tight_layout();save(f,'fig3')
f,axs=plt.subplots(1,3,figsize=(10,3));t=np.linspace(0,1,201);y=v.y.values;p=v.probability.values
axs[0].plot(t,[(p[y==1]>=a).mean() for a in t],color=C,label='敏感度');axs[0].plot(t,[(p[y==0]<a).mean() for a in t],color=B,label='特异度');axs[0].axvline(.5,color=K,ls='--',lw=.8);axs[0].set(xlabel='分类阈值',ylim=(-.04,1.06));axs[0].legend(fontsize=9,loc='lower center');axs[0].set_title('a  阈值与错误取舍',loc='left')
fr,tr,_=roc_curve(y,p);axs[1].plot(fr,tr,color=B,lw=2);axs[1].plot([0,1],[0,1],color='gray',ls='--',lw=.8);axs[1].set(xlabel='假阳性率',ylabel='敏感度',xlim=(-.04,1.04),ylim=(-.04,1.04));axs[1].set_title('b  ROC 曲线  AUC = 1.000',loc='left')
pr,re,_=precision_recall_curve(y,p);axs[2].step(re,pr,where='post',color=C,lw=2);axs[2].axhline(.5,color='gray',ls='--',lw=.8);axs[2].set(xlabel='召回率',ylabel='精确率',xlim=(-.04,1.04),ylim=(-.04,1.04));axs[2].set_title('c  PR 曲线  AP = 1.000',loc='left');f.tight_layout();save(f,'fig4')
f,axs=plt.subplots(1,2,figsize=(10,3));axs[0].plot([0,1],[0,1],ls='--',color='gray');
for z in r['bins']:
 axs[0].scatter(z['mean'],z['observed'],s=z['n']*15+25,color=B);axs[0].annotate(f"n = {z['n']}",(z['mean'],z['observed']),xytext=(5,-17 if z['observed'] else 10),textcoords='offset points')
axs[0].set(xlabel='箱内平均预测概率',ylabel='实际阳性比例',xlim=(-.05,1.08),ylim=(-.08,1.12));axs[0].set_title('a  验证集可靠性图',loc='left')
for i,z in enumerate(r['duplicate']):axs[1].plot([0,1],[z['before'],z['after']],marker='o',lw=1.5,color=[B,C,'#8C8176'][i],label=''.join(map(str,z['x'])))
axs[1].axhline(.5,color='gray',ls='--',lw=.8);axs[1].set_xticks([0,1],['原六症状','再复制一列恶心']);axs[1].set(ylim=(.25,.75),ylabel='阳性概率');axs[1].legend(title='六位输入',fontsize=8,loc='upper left');axs[1].set_title('b  重复信息改变预测',loc='left');f.tight_layout();save(f,'fig5')
f,axs=plt.subplots(1,2,figsize=(10,3));axs[0].imshow([[12,0],[0,12]],cmap='course_warm',vmin=0,vmax=16);axs[0].set_xticks([0,1],['预测阴性','预测阳性']);axs[0].set_yticks([0,1],['实际阴性','实际阳性']);axs[0].set_title('a  固定测试集混淆矩阵',loc='left')
for i in range(2):
 for j in range(2):axs[0].text(j,i,str(12 if i==j else 0),ha='center',va='center',fontsize=17)
axs[1].barh(['训练集','验证集','测试集'],[72,24,24],color=[B,C,'#C7A58A']);axs[1].set(xlabel='记录数',xlim=(0,85));axs[1].invert_yaxis();axs[1].set_title('b  二元症状组合覆盖',loc='left')
for i,(n,s) in enumerate([(72,'9 种组合'),(24,'24/24 在训练集出现'),(24,'24/24 在训练集出现')]):axs[1].text(1,i,f'{n} 条；{s}',va='center',color='white' if i==0 else K,fontsize=10)
f.tight_layout();save(f,'fig6')

d=Document();s=d.sections[0];s.page_width=Cm(21);s.page_height=Cm(29.7);s.top_margin=Cm(1.6);s.bottom_margin=Cm(1.6);s.left_margin=Cm(1.7);s.right_margin=Cm(1.7)
for name,size in [('Normal',10.5),('Title',20),('Heading 1',15),('Heading 2',11.5),('Caption',9)]:
 st=d.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体');st.paragraph_format.space_after=Pt(6)
for st in d.styles:
 for el in list(st.element.iter(qn('w:pBdr'))):el.getparent().remove(el)
d.styles['Normal'].paragraph_format.line_spacing=1.15;d.styles['Caption'].font.bold=False;d.styles['Caption'].font.italic=False
def p(text):
 q=d.add_paragraph(text);q.paragraph_format.first_line_indent=Pt(21);q._p.get_or_add_pPr().get_or_add_ind().set(qn('w:firstLineChars'),'200');return q
def h(text,new=True):
 q=d.add_heading(text,1);q.paragraph_format.page_break_before=new
def fig(n,text):
 legends={1:'箭头表示分析顺序，浅棕框表示各阶段。',2:'热图由浅米色至赭橙色表示概率由低至高；数字为概率值。右图蓝色表示阴性，橙色表示阳性。',3:'灰色为先验基线，蓝色为六症状模型，橙色为概率压缩结果。',4:'a中橙线为敏感度，蓝线为特异度；b中蓝线为ROC曲线，灰虚线为随机排序参照；c中橙线为PR曲线。',5:'a中蓝点为各概率箱；b中线条颜色对应图内六位输入图例，灰虚线为分类阈值0.50。',6:'a中格内数字为记录数，色深表示计数大小；b中蓝色、橙色、浅棕色依次表示训练、验证和测试集。'}
 q=d.add_paragraph();q.alignment=1;q.paragraph_format.space_before=Pt(6);q.paragraph_format.keep_with_next=True;q.add_run().add_picture(str(G/f'fig{n}.png'),width=Cm(17.4));q=d.add_paragraph(style='Caption');a,b,c=text.partition('。');q.add_run(a+b).bold=True;q.add_run(c+' 图例：'+legends[n]);q.paragraph_format.line_spacing=1.05
def table(title,headers,rows,widths):
 q=d.add_paragraph(title);q.alignment=1;q.paragraph_format.keep_with_next=True
 t=d.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for c,txt in zip(t.rows[0].cells,headers):c.text=txt
 for row in rows:
  for c,txt in zip(t.add_row().cells,row):c.text=str(txt)
 for i,row in enumerate(t.rows):
  row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
  for j,c in enumerate(row.cells):
   c.width=Cm(widths[j]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;bd=OxmlElement('w:tcBorders')
   for edge in ['top','bottom','left','right']:
    e=OxmlElement('w:'+edge);on=(edge=='top' and i==0) or (edge=='bottom' and i in [0,len(t.rows)-1]);e.set(qn('w:val'),'single' if on else 'nil');e.set(qn('w:sz'),'6' if i==0 and edge=='bottom' else '12');bd.append(e)
   c._tc.get_or_add_tcPr().append(bd)
   for q in c.paragraphs:
    q.alignment=1;q.paragraph_format.space_after=Pt(3);q.paragraph_format.space_before=Pt(3);q.paragraph_format.line_spacing=1.05
    for run in q.runs:run.font.size=Pt(9);run.bold=i==0
 t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
def eq(text):
 q=d.add_paragraph();q.alignment=1;om=OxmlElement('m:oMath')
 def run(t):
  a=OxmlElement('m:r');b=OxmlElement('m:t');b.text=t;a.append(b);return a
 def sub(t,i):
  a=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(run(t));s=OxmlElement('m:sub');s.append(run(i));a.extend([e,s]);return a
 def power(nodes,t):
  a=OxmlElement('m:sSup');e=OxmlElement('m:e');e.extend(nodes);s=OxmlElement('m:sup');s.append(run(t));a.extend([e,s]);return a
 def frac(a,b):
  z=OxmlElement('m:f');n=OxmlElement('m:num');n.extend(a);den=OxmlElement('m:den');den.extend(b);z.extend([n,den]);return z
 if text.startswith('θ'):
  om.extend([sub('θ','cj'),run(' = '),frac([sub('k','cj'),run(' + 1')],[sub('n','c'),run(' + 2')]),run('    '),sub('S','c'),run(' = '),sub('π','c'),sub('∏','j'),power([sub('θ','cj')],'xⱼ'),power([run('(1 − '),sub('θ','cj'),run(')')],'1 − xⱼ'),run('    p = '),frac([sub('S','1')],[sub('S','0'),run(' + '),sub('S','1')])])
 else:
  om.extend([run('平均交叉熵 = −'),frac([run('1')],[run('n')]),sub('∑','i'),run('['),sub('y','i'),run(' ln('),sub('p','i'),run(') + (1 − '),sub('y','i'),run(') ln(1 − '),sub('p','i'),run(')]')])
 q._p.append(om)

d.add_heading('六项症状的朴素贝叶斯分类与评价',0)
h('问题一 如何把症状记录变成预测任务',False)
p('本次作业利用六项二元症状预测膀胱炎症，依次分析模型参数、预测误差、分类阈值和推广范围。六症状模型在验证集与固定测试集均判对全部24条记录，但两部分的症状组合都已在训练集中出现。这说明模型能够区分本批构造记录，尚不能证明其对真实新患者同样有效。')
p('数据来自 Jacek Czerniak 的 UCI Acute Inflammations（DOI 10.24432/C5V59S，CC BY 4.0）。120条记录由专家构造，用于专家系统测试。每行是一条记录，输入依次为发热、恶心、腰痛、尿意频繁、排尿痛和尿道灼痛；1表示出现，0表示未出现。课程文件以体温≥38°C定义发热。输出标签为膀胱炎症，阳性记为1。')
fig(1,'图1 数据划分与分析流程。训练集估计参数，验证集比较表现，测试集评价固定方案。数据沿用课程划分，不合并训练与验证集重新拟合。工作单已提供部分测试汇总，本报告为独立计算复核，不称为前瞻盲测。')
table('表1 三部分数据的组成',['数据部分','阴性','阳性','合计','用途'],[['训练集',37,35,72,'估计参数'],['验证集',12,12,24,'比较预测表现'],['固定测试集',12,12,24,'评价固定模型']],[3.4,2,2,2,8])
p('120个编号互不重复，无缺失值；去掉编号后有21条重复记录，六项二元输入仅有9种不同组合。保留全部原始记录，同时报告重复与组合覆盖。编号、原始体温和两个疾病标签不进入六症状输入，避免标识信息或答案本身参与预测。')
p('模型先输出阳性概率p，再按p≥0.50判为阳性。训练会改变从数据估计的参数；预测只应用既定参数。若仅按相同症状组合统计频率，遇到未见组合便缺乏直接依据；朴素贝叶斯通过组合各项条件概率给出预测，但这一步依赖模型假设。')

h('问题二 六项症状如何得到一个预测概率')
p('采用 Bernoulli 朴素贝叶斯，各特征取0或1。训练集阳性先验为35/72，阴性先验为37/72。每项条件概率使用加一平滑：若某类别有n条记录，其中k条出现某症状，则该症状出现的概率估计为(k+1)/(n+2)。平滑避免零计数使整个乘积归零。')
eq('θcj = (kcj + 1)/(nc + 2)    Sc = πc ∏j θcj^xj (1 − θcj)^(1 − xj)    p = S1/(S0 + S1)')
table('表2 训练计数与平滑后的条件概率',['症状','阴性计数 / 37','阳性计数 / 35','P(x=1 | y=0)','P(x=1 | y=1)'],[[n,r['counts'][0][i],r['counts'][1][i],f'{th[0,i]:.4f}',f'{th[1,i]:.4f}'] for i,n in enumerate(names)],[3.3,3.3,3.3,3.75,3.75])
fig(2,'图2 类别内参数与单条记录预测。a，色深表示加一平滑后的症状出现概率。b，查询输入为(0,0,0,1,1,1)，依次对应表2六项症状；柱形为模型后验概率，不是临床风险验证结果。')
p('以输入(0,0,0,1,1,1)为例，前三项未出现，因此必须乘各自的1−θ，不能跳过。阳性得分为(35/72)×(23/37)³×(36/37)×(29/37)×(18/37)=0.0433193；阴性得分为(37/72)×(13/39)×(33/39)×(8/39)×(14/39)×(6/39)×(14/39)=0.000589435。')
p('归一化后，阳性概率为0.0433193/(0.0433193+0.000589435)=0.986576，阈值0.50下预测阳性。手算结果与程序一致。这里的条件概率描述本批训练记录的特征分布，不能据此把某个症状解释为疾病的原因。')

h('问题三 预测全部正确是否代表概率也可靠')
p('准确率只计算类别是否正确，无法区分0.60和0.99的预测。交叉熵按真实类别评价概率，错误且过分自信的预测受到更大惩罚。对一条实际阴性记录，预测阳性概率0.60的损失为−ln(0.40)=0.916；若报0.99，损失升为−ln(0.01)=4.605。')
eq('平均交叉熵 = −(1/n) ∑i [yi ln(pi) + (1 − yi) ln(1 − pi)]')
table('表3 训练与验证中的分类和概率评价',['模型及数据','准确率','ROC-AUC','交叉熵','Brier分数'],[[lab]+[f"{r[k][met]:.4f}" for met in ['accuracy','auc','logloss','brier']] for lab,k in [('六症状 训练集','train'),('仅用先验 验证集','baseline'),('六症状 验证集','val'),('概率压缩 验证集','transformed')]],[5.2,3,3,3.1,3.1])
fig(3,'图3 分类 排序和概率评价的区别。三种结果均来自同一验证集。先验基线对所有记录输出35/72；概率压缩将六症状模型的p替换为0.25+0.50p，不重新训练。准确率使用阈值0.50；交叉熵越小越好。')
p('六症状模型验证集交叉熵为0.0872，低于先验基线的0.6935。先验基线在0.50阈值下将所有记录判为阴性，准确率仍有0.50，但漏掉全部12条阳性记录。它没有预测阳性，精确率的分母为0，因而没有定义。')
p('概率压缩保持记录的排序与0.50阈值下的类别不变，准确率和ROC-AUC仍为1.000，交叉熵却升至0.3442。因此，排序好不等于概率准确。Brier分数是预测概率与0/1标签之间的均方误差，越小越好，但并非纯粹的校准误差。')
p('本模型直接从训练计数估计参数，没有通过迭代优化验证集交叉熵来训练。交叉熵在本报告中是评价量；训练表现用于描述拟合，验证表现用于比较方案，两者都不能替代独立来源数据的评价。')

h('问题四 改变阈值会改变哪些错误')
p('敏感度的分母是实际阳性，特异度的分母是实际阴性，精确率的分母是预测阳性。三者回答不同问题。阈值降低会让更多记录被判阳性，通常减少漏判并增加误报；阈值提高则反向变化。')
table('表4 验证集阈值比较',['阈值','TN','FP','FN','TP','准确率','敏感度','特异度','精确率','F1'],[[t]+[r['thresholds'][t][k] for k in ['tn','fp','fn','tp']]+[f"{r['thresholds'][t][k]:.3f}" for k in ['accuracy','sensitivity','specificity','precision','f1']] for t in ['0.1','0.5','0.9']],[1.5,1,1,1,1,2.4,2.4,2.4,2.5,2.2])
p('阈值0.10时，准确率=(12+7)/24=0.792，敏感度=12/12=1.000，特异度=7/12=0.583，精确率=12/17=0.706，F1=24/29=0.828。与0.50相比，多出5次误报而没有减少漏判；升到0.90后，则新增2次漏判。当前验证结果支持保留0.50，无需为本批记录调整阈值。')
fig(4,'图4 验证集阈值与排序曲线。a，虚线表示固定阈值0.50。b，ROC曲线概括阳性与阴性的排序。c，PR曲线展示召回率和精确率的关系，灰线为验证集阳性比例0.50；报告AP而不将其混称为梯形PR面积。')
p('阈值0.10在ROC图中对应(5/12,12/12)，在PR图中对应(12/12,12/17)。ROC-AUC=1表示本批验证记录中，每条阳性的得分都高于阴性；它不是固定阈值的准确率。AP=1同样反映本批记录的排序，且PR表现会受阳性比例影响。')
p('实际使用时，阈值还应依据漏诊与误报的代价、后续检查负担及目标人群决定。本作业没有这些资料，因此只保留课堂基线：六项输入、加一平滑、阈值0.50。测试结果只评价该方案，不用于再改模型。')
d.add_heading('二症状模型的简化实验',2)
p('仅保留尿意频繁与排尿痛，仍用训练集计数拟合。阴性类两项条件概率为14/39、6/39，阳性类为36/37、29/37。验证集得到TN=12、FP=0、FN=1、TP=11，准确率23/24=0.958，敏感度11/12=0.917。简化模型少用四项信息，却新增一次漏判，本次仍保留六症状模型。')

h('问题五 条件独立与概率校准有什么限制')
p('朴素贝叶斯假设给定类别后，各症状相互独立；并不是说全部记录中的症状彼此无关。以阴性类为例，尿意频繁与排尿痛同时出现的经验概率为0/37=0，而边缘概率乘积为(13/37)×(5/37)=0.0475。两者不相等，提示训练记录不完全符合条件独立的描述。有限样本的差值不能单独证明总体中的关系。')
fig(5,'图5 校准观察与重复信息实验。a，以宽度0.20的固定概率箱汇总验证记录，只绘制非空箱，点大小表示记录数；虚线表示平均预测概率与实际比例一致。b，穷举64种二元输入，展示额外复制一列恶心后概率变化最大的3种输入。这些向量不是新增患者，也未用于修改主模型。')
table('表5 验证集非空概率箱',['概率范围','记录数','阳性数','平均预测概率','实际阳性比例'],[['[0.0, 0.2)',12,0,'0.0890','0.0000'],['[0.6, 0.8)',1,1,'0.6854','1.0000'],['[0.8, 1.0]',11,11,'0.9503','1.0000']],[3.5,2.4,2.4,4.3,4.3])
p('中间概率箱只有1条记录，实际阳性比例减平均预测概率为1−0.6854=0.3146。它提示该箱的预测与观察存在差距，但单条记录不足以评价整体校准；其余两个概率箱也只有12条和11条记录。全部判对不意味着可以直接将模型概率作为真实患病风险报告。')
p('复制一列恶心后，输入(0,1,1,0,1,1)的阳性概率从0.3755升至0.5966，在0.50阈值下甚至改变了类别。复制没有新增信息，却让同一证据被再次乘入类别得分。这说明相关或重复特征可能改变概率与分类，更多列不一定意味着更多有效信息。')
p('模型的优点是参数由计数得到，计算快，能逐项解释一次预测。其限制在于概率乘积依赖条件独立近似，对重复信息和数据构造方式敏感。当前不额外拟合校准器，因为24条验证记录及稀疏概率箱不足以支持稳定的复杂调整。')

h('问题六 当前结果能够支持多大的应用范围')
p('固定测试集得到TN=12、FP=0、FN=0、TP=12，准确率、敏感度、特异度与精确率均为1.000，交叉熵为0.0745。结果支持该固定模型能够区分本批测试记录。训练与测试编号没有重叠，但测试24条记录的六位症状组合都在训练集中出现，不能据此声称模型已经通过新组合或外部患者验证。')
fig(6,'图6 固定测试表现与组合覆盖。a，六症状模型在阈值0.50下的测试计数。b，训练集包含全部9种已观察到的二元组合，验证和测试记录均落在这些组合内。组合相同不自动等于标签泄漏，但限制了泛化结论。')
table('表6 低患病率假设场景中的预期人数',['方案','TP','FP','FN','TN','准确率','精确率'],[['全部判阴性',0,0,10,990,'99.0%','未定义'],['敏感度90% 特异度95%',9,49.5,1,940.5,'94.95%','15.4%']],[5.2,1.4,1.7,1.4,1.9,2.9,3.1])
p('表6是假设场景：1,000人中阳性比例为1%，并假定模型敏感度90%、特异度95%在该人群中成立。小数人数表示期望值，不是实测人数。模型精确率为9/(9+49.5)=0.154；全部判阴性虽然准确率更高，却漏掉所有阳性。因此，医学分类不能只看accuracy，还应报告漏判、误报与预测阳性中的真实阳性比例。')
p('本次结果主要受数据来源和重复组合限制。专家构造记录不能代表医院就诊人群；测试集只有12条阳性和12条阴性，未观察到错误也不意味着真实错误率为零。应在独立收集的真实记录中检查症状测量、患者独立性、患病率、校准与错误代价，才能讨论实际使用。')
d.add_heading('结论',2)
p('本次保留六症状朴素贝叶斯作为课堂基线：采用训练集计数与加一平滑，固定阈值0.50。验证与测试均全部判对，交叉熵优于仅用先验的基线；降低或提高阈值、删减症状均未改善当前验证结果。但仅有9种症状组合，且重复症状可明显改变概率，因此结论限于这批构造记录的分类练习，不能推广为经过临床验证的诊断工具。')
foot=s.footer.paragraphs[0];foot.alignment=1;fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');foot._p.append(fld)
for st in d.styles:
 if st.type in [1,2]:
  st.font.name='Times New Roman'
  rf=st._element.get_or_add_rPr().get_or_add_rFonts()
  for key,val in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia','宋体'),('cs','Times New Roman')]:rf.set(qn('w:'+key),val)
  for key in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
   if qn('w:'+key) in rf.attrib:del rf.attrib[qn('w:'+key)]
for run in d.element.iter(qn('w:r')):
 rp=run.find(qn('w:rPr'))
 if rp is None:rp=OxmlElement('w:rPr');run.insert(0,rp)
 rf=rp.find(qn('w:rFonts'))
 if rf is None:rf=OxmlElement('w:rFonts');rp.insert(0,rf)
 for key,val in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia','宋体')]:rf.set(qn('w:'+key),val)
out=O/'朴素贝叶斯课程作业_完成稿_统一排版版.docx';d.save(out);print(out)
