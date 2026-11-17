from pathlib import Path
import sys,json,warnings
sys.path.insert(0,'D:/课程/大数据实践课/第五课/hypothesis/.analysis-deps')
warnings.filterwarnings('ignore',category=FutureWarning)
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from lab_utils import load_development,geometry_experiment,make_model,FEATURES,svc_of
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];O=R/'outputs';G=O/'figures';G.mkdir(exist_ok=True)
r=json.loads((O/'分析结果.json').read_text(encoding='utf-8'));grid=pd.read_csv(O/'参数网格.csv');scale=pd.read_csv(O/'尺度实验.csv');noise=pd.read_csv(O/'扰动实验.csv');tr,va=load_development();geo=geometry_experiment(tr)
B='#387DA0';C='#C9714D';BG='#F7F0E6';K='#29343B';GRAY='#8C8176'
plt.rcParams.update({'font.family':['Times New Roman','SimSun'],'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':BG,'axes.facecolor':BG,'axes.unicode_minus':False,'text.color':K,'axes.labelcolor':K,'svg.fonttype':'none','legend.frameon':False})
def save(f,n):
 f.savefig(G/f'图{n}.png',dpi=300,bbox_inches='tight',facecolor=BG);f.savefig(G/f'图{n}.svg',bbox_inches='tight',facecolor=BG);plt.close(f)
f=plt.figure(figsize=(12,4.7));a=f.add_axes([0,0,1,1]);a.axis('off');a.set(xlim=(0,12),ylim=(0,4.7))
def box(x,y,w,h,title,body):
 a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.025,rounding_size=.07',facecolor=BG,edgecolor='#C7B29C',lw=.9));a.text(x+.15,y+h-.25,title,fontsize=12,va='center',color=K);a.text(x+.2,y+h-.72,body,fontsize=10.5,va='top',linespacing=1.65)
def arrow(points,col=K,ls='-'):
 for p,q in zip(points[:-2],points[1:-1]):a.plot([p[0],q[0]],[p[1],q[1]],lw=1,color=col,ls=ls)
 a.annotate('',xy=points[-1],xytext=points[-2],arrowprops=dict(arrowstyle='-|>',color=col,lw=1,linestyle=ls))
box(.15,3.25,11.65,1.25,'a  研究任务与固定划分','310 条脊柱测量记录  ·  骨盆入射角 + 滑脱程度  →  NO / AB 标签')
a.text(.35,3.47,'训练 186 条：拟合 scaler 与模型',fontsize=10.5,color=B);a.text(4.45,3.47,'验证 62 条：参数比较与选择',fontsize=10.5,color=C);a.text(8.5,3.47,'测试 62 条：固定后评价',fontsize=10.5,color=GRAY)
box(.15,1.35,3.65,1.55,'b  间隔与支持向量','八点子集：边界、距离与 margin\n删除支持向量 / 非支持向量\n矛盾标签与 hinge loss')
box(4.05,1.35,3.65,1.55,'c  受控参数实验','完整训练集：soft margin 与 C\nlinear / polynomial / RBF\n固定 C 改 gamma；检验尺度影响')
box(7.95,1.35,3.85,1.55,'d  验证与稳定性','以平衡准确率选择各家族配置\n默认决策分数阈值为 0\n输入扰动实验；分数不是概率')
arrow([(2,3.25),(2,2.9)],B);arrow([(3.8,2.1),(4.05,2.1)]);arrow([(7.7,2.1),(7.95,2.1)])
box(.15,.15,7.55,.85,'e  固定方案','')
a.text(.35,.40,'Linear：C = 1     |     RBF：C = 10，gamma = 10     |     不合并验证集重训',fontsize=10.5,color=B)
box(7.95,.15,3.85,.85,'f  留出评价与解释边界','');a.text(8.15,.40,'混淆矩阵、AUC与两类召回率',fontsize=10.5)
arrow([(9.85,1.35),(9.85,1.16),(2,1.16),(2,1.0)]);arrow([(7.7,.57),(7.95,.57)],B);arrow([(11.85,3.45),(11.96,3.45),(11.96,.57),(11.8,.57)],GRAY,'--')
save(f,1)
f,axs=plt.subplots(1,3,figsize=(11,3.3));z=geo['z'];y=geo['subset'].abnormal.to_numpy();w=geo['model'].coef_[0];b=geo['model'].intercept_[0];xx=np.linspace(-2.1,1.8,100)
for ax in axs[:2]:
 for c,col,marker in [(0,B,'o'),(1,C,'^')]:ax.scatter(z[y==c,0],z[y==c,1],c=col,marker=marker,s=33)
 ax.set(xlabel='z₁ 骨盆入射角',ylabel='z₂ 滑脱程度',xlim=(-2.1,1.8),ylim=(-1.4,2.2));ax.set_aspect('equal',adjustable='box')
for off,col,ls in [(-.6,GRAY,'--'),(0,K,'-'),(.6,C,'--')]:axs[0].plot(xx,-(w[0]*xx+b+off)/w[1],color=col,ls=ls,lw=1.3,label=f'偏移 {off:+.1f}')
axs[0].legend(fontsize=8,loc='upper left');axs[0].set_title('a  三条零错误边界',loc='left')
for lev,ls in [(-1,'--'),(0,'-'),(1,'--')]:axs[1].plot(xx,(lev-w[0]*xx-b)/w[1],color=K,ls=ls,lw=1)
sv=geo['model'].support_;axs[1].scatter(z[sv,0],z[sv,1],s=100,facecolors='none',edgecolors=K)
for i in sv:axs[1].annotate(geo['subset'].iloc[i].sample_id,z[i],xytext=(4,-13),textcoords='offset points',fontsize=8)
axs[1].set_title('b  支持向量与参考带',loc='left');q=np.linspace(-1,2,100);axs[2].plot(q,np.maximum(0,1-q),color=C,lw=2);axs[2].scatter([-.5,.4,1,1.8],[1.5,.6,0,0],color=B,s=25);axs[2].axvline(0,color=GRAY,ls=':',lw=.8);axs[2].set(xlabel='带标签分数 y·f',ylabel='Hinge loss');axs[2].set_title('c  分对仍可能有损失',loc='left');f.tight_layout();save(f,2)
# Use the same central window for all 186-record boundary panels; all records remain in fitting.
Z=geo['scaler'].transform(tr[FEATURES]);low,high=np.percentile(Z,[0,98],axis=0);pad=.12*(high-low);low-=pad;high+=pad
outside=int(np.any((Z<low)|(Z>high),axis=1).sum());(O/'边界图显示范围.json').write_text(json.dumps(dict(lower=low.tolist(),upper=high.tolist(),outside=outside)),encoding='utf-8')
def boundary(ax,kernel,c,g,title):
 m=make_model(kernel,c,g).fit(tr[FEATURES],tr.abnormal);s=svc_of(m);gx,gy=np.meshgrid(np.linspace(low[0],high[0],220),np.linspace(low[1],high[1],220));sc=s.decision_function(np.c_[gx.ravel(),gy.ravel()]).reshape(gx.shape)
 ax.contourf(gx,gy,sc>=0,levels=[-.5,.5,1.5],colors=['#E8E8DF','#F1DAC8'],alpha=.8)
 ax.contour(gx,gy,sc,levels=[-1,0,1],colors=[GRAY,K,GRAY],linestyles=['--','-','--'],linewidths=[.6,1.1,.6])
 for cls,col,marker in [(0,B,'o'),(1,C,'^')]:mask=tr.abnormal.to_numpy()==cls;ax.scatter(Z[mask,0],Z[mask,1],s=12,c=col,marker=marker,alpha=.7)
 ax.scatter(Z[s.support_,0],Z[s.support_,1],s=27,facecolors='none',edgecolors=K,lw=.35)
 ax.set(xlim=low[[0]].tolist()+high[[0]].tolist(),ylim=low[[1]].tolist()+high[[1]].tolist(),xlabel='z₁',ylabel='z₂');ax.set_title(title,loc='left',fontsize=11)
f,axs=plt.subplots(1,3,figsize=(10,3.0))
for ax,c,letter in zip(axs,[.01,1,100],'abc'):boundary(ax,'linear',c,.1,f'{letter}  Linear  C = {c:g}')
f.tight_layout();save(f,3)
f,axs=plt.subplots(1,4,figsize=(12,3))
for ax,g,letter in zip(axs[:3],[.01,1,10],'abc'):boundary(ax,'rbf',1,g,f'{letter}  C = 1，γ = {g:g}')
heat=grid[grid.kernel=='rbf'].pivot(index='C',columns='gamma',values='val_balanced_accuracy');axs[3].imshow(heat,cmap=LinearSegmentedColormap.from_list('warm',[BG,C]),vmin=.5,vmax=.85,aspect='auto');axs[3].set_xticks(range(4),['.01','.1','1','10']);axs[3].set_yticks(range(4),['.1','1','10','100']);axs[3].set(xlabel='gamma',ylabel='C');axs[3].set_title('d  验证平衡准确率',loc='left',fontsize=11)
for i in range(4):
 for j in range(4):axs[3].text(j,i,f'{heat.iloc[i,j]:.2f}',ha='center',va='center',fontsize=9)
f.tight_layout();save(f,4)
f,axs=plt.subplots(1,2,figsize=(10,3));pos=np.arange(2);axs[0].bar(pos-.16,scale[scale.unit=='original'].val_balanced_accuracy,width=.3,color=B,label='原单位');axs[0].bar(pos+.16,scale[scale.unit=='x1_times_100'].val_balanced_accuracy,width=.3,color=C,label='x₁ × 100');axs[0].set_xticks(pos,['不标准化','训练集标准化']);axs[0].set(ylim=(0,1),ylabel='验证平衡准确率');axs[0].legend(fontsize=9);axs[0].set_title('a  数值尺度改变的后果',loc='left')
for fam,col in [('linear',B),('rbf',C)]:ns=noise[noise.family==fam];axs[1].plot(ns.noise_sd_fraction,ns.mean_flip_rate,marker='o',color=col,label=fam)
axs[1].set(xlabel='人工噪声标准差 / 训练标准差',ylabel='平均类别翻转率',ylim=(0,.26));axs[1].legend(fontsize=9);axs[1].set_title('b  固定模型的扰动实验',loc='left');f.tight_layout();save(f,5)
f,axs=plt.subplots(1,3,figsize=(10,3));warm=LinearSegmentedColormap.from_list('warm2',[BG,C])
for ax,row,letter in zip(axs[:2],r['test'],'ab'):
 mat=np.array([[row['TN'],row['FP']],[row['FN'],row['TP']]]);ax.imshow(mat,cmap=warm,vmin=0,vmax=42);ax.set_xticks([0,1],['预测 NO','预测 AB']);ax.set_yticks([0,1],['实际 NO','实际 AB']);ax.set_title(f"{letter}  {row['family']} 固定测试",loc='left')
 for i in range(2):
  for j in range(2):ax.text(j,i,str(mat[i,j]),ha='center',va='center',fontsize=15)
for fam,col in [('linear',B),('rbf',C)]:row=next(z for z in r['test'] if z['family']==fam);axs[2].plot([0,1,2],[row['sensitivity'],row['specificity'],row['balanced_accuracy']],marker='o',color=col,label=fam)
axs[2].set_xticks([0,1,2],['AB召回','NO召回','平衡准确率'],rotation=15);axs[2].set(ylim=(0,1.05));axs[2].legend(fontsize=9);axs[2].set_title('c  两类识别表现',loc='left');f.tight_layout();save(f,6)

d=Document();sec=d.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(1.6);sec.bottom_margin=Cm(1.6);sec.left_margin=Cm(1.7);sec.right_margin=Cm(1.7)
for name,size in [('Normal',10.5),('Title',20),('Heading 1',15),('Heading 2',11.5),('Caption',9)]:
 st=d.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),'宋体');st.paragraph_format.space_after=Pt(6)
for st in d.styles:
 if st.type in [1,2]:
  rf=st._element.get_or_add_rPr().get_or_add_rFonts()
  for k,v in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia','宋体')]:rf.set(qn('w:'+k),v)
  for k in ['asciiTheme','hAnsiTheme','eastAsiaTheme']:
   if qn('w:'+k) in rf.attrib:del rf.attrib[qn('w:'+k)]
 for el in list(st.element.iter(qn('w:pBdr'))):el.getparent().remove(el)
d.styles['Normal'].paragraph_format.line_spacing=1.15;d.styles['Caption'].font.bold=False;d.styles['Caption'].font.italic=False
def p(t):
 q=d.add_paragraph(t);q.paragraph_format.first_line_indent=Pt(21);q._p.get_or_add_pPr().get_or_add_ind().set(qn('w:firstLineChars'),'200');return q
def h(t,new=True):q=d.add_heading(t,1);q.paragraph_format.page_break_before=new
def fig(n,title,cap):
 q=d.add_paragraph();q.alignment=1;q.paragraph_format.keep_with_next=True;q.add_run().add_picture(str(G/f'图{n}.png'),width=Cm(17.4));q=d.add_paragraph(style='Caption');q.add_run(f'图{n} {title}。').bold=True;q.add_run(cap);q.paragraph_format.line_spacing=1.05
def table(title,head,rows,widths):
 q=d.add_paragraph(title);q.alignment=1;q.paragraph_format.keep_with_next=True;t=d.add_table(rows=1,cols=len(head));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for c,txt in zip(t.rows[0].cells,head):c.text=txt
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
    q.alignment=1;q.paragraph_format.space_before=Pt(3);q.paragraph_format.space_after=Pt(3);q.paragraph_format.line_spacing=1.05
    for a in q.runs:a.font.size=Pt(9);a.bold=i==0
 t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
def f3(x):return f'{x:.3f}'
d.add_heading('脊柱测量数据中的支持向量机分析',0)
h('问题一 如何建立可解释的分类实验',False)
p('本作业以脊柱测量记录为例，分析支持向量机如何通过间隔与训练违例确定分类边界。重点考察支持向量、C、核函数、gamma及标准化的作用。固定配置后，线性核与RBF核在62条测试记录上的平衡准确率分别为0.832和0.844，但RBF在人工扰动中更容易改变类别。因此，训练贴合程度与单次验证分数都不足以概括模型的适用性。')
p('数据来自UCI Vertebral Column（Guilherme Barreto、Ajalmar Neto，CC BY 4.0），共310条患者测量记录。正常NO为100条，异常AB为210条；AB合并椎间盘突出与脊椎滑脱，表示已有类别，不能解释为未来风险或疾病严重程度。本报告沿用当前Notebook的两输入方案：骨盆入射角与滑脱程度；Word工作单中的六输入方案不与本次结果混用。')
fig(1,'SVM整体研究与评价流程','a，保留原训练、验证和测试划分。b，八点子集用于几何解释。c–d，正式实验使用完整训练与验证集。e–f，固定两类配置后评价保留记录。蓝色突出训练与固定方案，橙色突出验证，灰虚线为预留测试通路；各阶段均不将决策分数解释为患病概率。')
table('表1 数据组成及使用范围',['部分','NO','AB','合计','职责'],[['训练集',60,126,186,'拟合StandardScaler与SVM'],['验证集',20,42,62,'参数比较、选参及扰动实验'],['测试集',20,42,62,'配置固定后一次评价']],[2.8,1.7,1.7,1.7,9.5])
p('两项输入无缺失，310个追踪编号互不重复，各集合ID无交叉；编号不进入模型。骨盆入射角取值26.15–129.83，滑脱程度为−11.06–418.54。极端值保留，不能仅凭散点图删除。来源未给出逐字段单位，原数据只称source scale，标准化后的z₁、z₂均无量纲。')
p('划分沿用课程两次分层抽样，随机种子9，未重新分组。标准化只在186条训练记录上拟合。按可分条件有意选择的八点子集只用于解释几何，不能用其零错误代表整批患者的识别效果。')

h('问题二 零训练错误之外 间隔提供什么原则')
p('线性SVM学习决策函数f(z)=wᵀz+b，f≥0判为AB，f<0判为NO。点到边界的距离为|f|/‖w‖，带标签距离为y·f/‖w‖，其中y取−1或+1。将w和b同乘正数3，分数放大3倍，边界、类别和归一化距离不变，因此不能只比较不同模型的原始分数大小。')
fig(2,'候选边界 支持向量与hinge loss','a–b，蓝圆为NO、橙三角为AB，均为有意选择的8条训练记录；a中线型与颜色区分截距偏移。b中实线为f=0，虚线为f=±1，黑色空心圈表示支持向量。c，橙线为hinge函数，蓝点为独立算式示例，不是新增患者。')
table('表2 三条可分边界的几何比较',['相对截距偏移','训练错误','最小带标签距离'],[[f"{z['offset']:+.1f}",z['training_errors'],f3(z['min_signed_distance'])] for z in r['geometry']['candidates']],[5.8,5.8,5.8])
p('三条候选线都分对八条记录，但基准线的最小带标签距离为0.957，其余两条约为0.383。硬间隔原则关注距离边界最近的约束点，而非把所有点距离相加。规范化为y·f≥1后，两条参考线的宽度为2/‖w‖=1.914，等于点到中线最小距离的两倍；这里的距离属于标准化空间。')
p('对V061，w≈(0.7287,0.7492)、b≈−0.0200，z≈(0.7108,0.6700)。代入得到f≈1.000，预测AB；‖w‖≈1.045，距离≈0.957。该分数没有百分比含义。几何模型使用C=10000，并核对无实质间隔违例，作为近似硬间隔示例。')
p('支持向量是当前解中具有非零对偶权重的训练点。冻结原scaler后，删除远离边界的非支持向量V072，八点上的最大分数变化为0；删除支持向量V061，最大变化为0.427。该结果说明某些点直接约束当前边界，但不能推出删除任何支持向量都会改变解，也不能把支持向量当作病情最重或最典型的患者。')
p('若复制同一坐标并赋相反标签，硬间隔同时要求f≥1和f≤−1，不存在可行解，非线性核也不能消除这一逻辑矛盾。允许软间隔后可以拟合；该人工九点实验在C=1时仍有1次误分类、总hinge为2。反事实数据仅用于说明容错必要性，不进入正式评价。')

h('问题三 C怎样权衡间隔宽度与训练违例')
p('软间隔目标为½‖w‖²+C∑max(0,1−yᵢfᵢ)。第一项偏好较小权重范数，第二项惩罚间隔违例。C增大意味着相对更重视训练违例；它不是误差比例，也不是分类阈值。对y·f分别为−0.5、0.4、1、1.8的四种情况，hinge依次为1.5、0.6、0、0；前者误分类，而0.4虽分对仍位于参考带内并产生损失。')
fig(3,'仅改变C的线性边界实验',f'完整186条训练记录用于拟合。蓝圆为NO、橙三角为AB，黑色空心圈为支持向量；实线为f=0，虚线为f=±1，淡色背景表示预测区域。各面板使用相同标准化坐标窗口，{outside}条记录位于显示范围外但保留拟合。软间隔参考带内允许存在记录。')
lin=grid[grid.kernel=='linear']
table('表3 线性C实验的训练与验证结果',['C','参考带宽','平均hinge','训练错误','SV数','验证平衡准确率'],[[f'{z.C:g}',f3(z.linear_width),f3(z.mean_hinge),int(z.train_errors),int(z.n_sv),f3(z.val_balanced_accuracy)] for z in lin.itertuples()],[1.5,3,3,2.6,2,5.3])
p('C从0.01增至100，参考带宽从12.414降至0.489，平均hinge从0.631降至0.399，训练错误从60降至35。然而验证平衡准确率在C=1时达到0.760，到C=10和100反而降至0.710。这表明减少训练违例不能保证对未参与拟合的记录同样有效。')
p('C=0.01的带宽很大，却把验证记录都判为AB，平衡准确率只有0.500。因此，宽参考带只有结合分类与违例情况才有意义。软间隔中的2/‖w‖不是到最近训练点的距离，带内也不必为空。')
p('误分类只关心分数符号，hinge同时关心点是否达到y·f≥1。两者并非同一量，支持向量也可能被误分类。不同C对应不同目标函数权重，不能拿各自目标值的绝对大小直接给模型排名。本报告最终按验证平衡准确率选参，不追求训练误差归零。')

h('问题四 核函数与gamma怎样改变相似度')
p('核函数给出某个特征空间中的内积，使SVM可以表达非线性关系。线性核为zᵀu；二次多项式核为(γzᵀu+1)²；RBF核为exp(−γ‖z−u‖²)。当距离为1和2时，γ=0.1的RBF相似度分别为0.905、0.670，γ=1时降为0.368、0.018。较大的gamma让相似度随距离下降更快，影响更局部。')
fig(4,'RBF局部性与验证参数网格',f'a–c，固定C=1，只改变gamma；点、支持向量和线型含义同图3，使用同一窗口，{outside}条训练记录在图外。d，单元格为验证平衡准确率，颜色越深表示数值越高；网格仅用于验证选参。RBF曲线f=±1并非原二维平面上的等距线。')
subset=grid[((grid.kernel=='rbf')&(grid.gamma==10)&grid.C.isin([1,10,100]))|((grid.kernel=='poly'))]
table('表4 固定gamma的C实验与多项式参照',['核与配置','训练错误','SV数','验证平衡准确率'],[[('RBF γ=10，C='+f'{z.C:g}') if z.kernel=='rbf' else '二次多项式 C=1，γ=0.1',int(z.train_errors),int(z.n_sv),f3(z.val_balanced_accuracy)] for z in subset.itertuples()],[7.7,2.7,2,5])
p('固定C=1时，gamma从0.01增至1，验证平衡准确率由0.500升至0.785，再增至10则降至0.769。固定gamma=10时，C=10的验证结果为0.805，但C=100虽将训练错误从25减至16，验证结果却降至0.669。局部性与违例惩罚共同决定边界，不能同时改变两项后把全部差异归因于gamma。')
p('线性核在输入平面形成直线，二次多项式允许特征组合，RBF可形成更局部的弯曲区域。本次多项式只作为预设代表配置，未搜索其整个家族，因此不将它与完成网格搜索的家族作“最佳模型”比较。RBF的间隔定义在核特征空间，不能用图上两条曲线的距离与线性2/‖w‖直接比较。')
p('正式网格为线性C∈{0.01,0.1,1,10,100}，RBF的C∈{0.1,1,10,100}、gamma∈{0.01,0.1,1,10}。每个家族取验证平衡准确率最高者，并列时依次取较小C、较小gamma。固定结果为线性C=1、RBF C=10且gamma=10；线性核不使用gamma。')

h('问题五 为什么尺度与输入扰动影响边界')
p('将骨盆入射角x₁乘以100并未增加信息，但未标准化的平方欧氏距离中，该分量贡献会放大10000倍，改变RBF相似度。固定C=1、gamma=0.1，比较有无训练标准化下的单位变换，可以直接检验这种影响。标准化必须只在训练集拟合；即使不用标签，在全310条上估计均值与标准差仍使用了保留集信息。')
fig(5,'尺度变换与固定模型扰动','a，蓝柱为原单位、橙柱为x₁乘100，模型均为RBF C=1、gamma=0.1。b，蓝线为固定线性模型，橙线为固定RBF模型；对验证输入加入独立高斯噪声，强度按训练标准差定义，每个非零水平重复100次。曲线为平均类别翻转率，不表示真实仪器误差。')
table('表5 同一信息的尺度变换实验',['预处理','数值单位','验证平衡准确率','支持向量数'],[['训练标准化' if z.scaled else '不标准化','原始' if z.unit=='original' else 'x₁ × 100',f3(z.val_balanced_accuracy),int(z.n_sv)] for z in scale.itertuples()],[4.2,3.6,5.4,4.2])
p('不标准化时，单位变化使验证平衡准确率由0.705降至0.488，最大决策分数变化为1.538。训练标准化后，两种单位的结果均为0.773，最大分数差约1.78×10⁻¹⁴，属于数值误差。这证明本次线性单位变换可被标准化抵消，不代表任何分布变化或异常值都能由标准化消除。')
p('对已经固定的两类模型，加入0.10倍训练标准差的人工噪声后，线性与RBF的平均类别翻转率分别为5.44%和13.76%；噪声增至0.20倍时，分别为12.11%和22.03%。原验证表现较高的RBF在这组扰动假设下更敏感，说明验证分数与局部稳定性需要分开观察。')
p('边界附近的点较容易跨过决策面；较局部的RBF边界可能让相近位置产生不同预测。该实验没有重新拟合或修改标签，也没有据扰动结果再调参数。人工噪声独立、等比例的设定未必符合真实测量过程，因此只能描述当前假设下的敏感性，不能代替仪器重复测量或外部验证。')

h('问题六 固定测试能支持怎样的结论')
p('配置记录后，保留186条训练记录拟合的scaler与模型，不合并验证集重训，分数阈值固定为0。测试集62条中有20条NO和42条AB。课程作者此前已预跑过保留测试，本次属于固定流程复算与教学演示，不称为一次全新的独立科研确认。')
fig(6,'固定测试的混淆矩阵与两类识别表现','a–b，行表示真实类别、列表示预测类别，数字为记录数，暖色深浅表示计数大小。c，蓝线为线性核，橙线为RBF，连接线只帮助比较各项指标，不表示连续变量关系。AB召回率即敏感度，NO召回率即特异度。')
table('表6 验证选参后的固定测试结果',['家族','验证平衡准确率','测试平衡准确率','AB召回','NO召回','测试AUC'],[[z['family'],f3(r['chosen'][i]['val_balanced_accuracy']),f3(z['balanced_accuracy']),f3(z['sensitivity']),f3(z['specificity']),f3(z['roc_auc'])] for i,z in enumerate(r['test'])],[2.4,3.4,3.4,2.5,2.5,3.2])
p('线性模型测试中误报1条NO、漏判12条AB；RBF误报1条NO、漏判11条AB。两者在分类计数上只相差一条记录，不能据此宣称RBF普遍更好。线性AUC为0.824，略高于RBF的0.814，而RBF平衡准确率略高，说明排序与固定阈值分类表现可以给出不同比较结果。AUC使用决策分数，不需要概率输出。')
p('始终预测AB，在验证集的accuracy可达42/62=0.677，但NO召回率为0、平衡准确率仅0.500。平衡准确率是两类召回率的平均，能揭示只识别多数类的问题。若额外采用Word版工作单的门槛（验证平衡准确率≥0.75，且两类召回率均≥0.65），本次两输入线性配置因AB召回0.619而未达标，RBF的0.810与0.800则满足；这只是规则对照，不能称为完成了六输入方案的验收。')
d.add_heading('综合判断',2)
p('SVM把间隔大小与训练违例共同纳入学习目标，借助核函数表达不同相似度结构；其优势是可在不显式展开复杂特征的情况下学习非线性边界。使用条件是输入尺度、参数选择和验证设计合理。局限是对尺度与局部扰动可能敏感，决策分数也不直接代表风险概率。本次可将固定RBF作为两输入离线比较候选，同时保留线性模型作简单参照；不据测试结果追加搜索。')
p('当前只有单次划分、两个预设输入和有限记录，且缺少重复测量标识、真实噪声资料与外部队列。不能由此推断未来患病风险、病情严重程度或新医院表现。新任务应先明确输入测量与尺度、类别重叠、误判代价和概率需求，再确定核与参数范围；若需要可信概率，还需单独校准并用未参与选择的数据验证。')
foot=sec.footer.paragraphs[0];foot.alignment=1;fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');foot._p.append(fld)
out=R/'SVM课程作业_完成稿.docx';d.save(out);print(out);print('boundary display outside:',outside)
