from pathlib import Path
import json,sys
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.analysis-deps'))
import pandas as pd
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path('C:/Users/340/Desktop/6. multiple-test');OUT=ROOT/'outputs/2026-10-14';FIG=OUT/'figures'
r=json.loads((OUT/'results.json').read_text(encoding='utf-8'));c=pd.read_csv(OUT/'candidate_validation.csv');sm=pd.read_csv(OUT/'simulation_summary.csv');bias=pd.read_csv(OUT/'selection_bias_example.csv')
doc=Document();sec=doc.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(1.6);sec.bottom_margin=Cm(1.6);sec.left_margin=Cm(1.6);sec.right_margin=Cm(1.6)
for name,size in [('Normal',10.5),('Title',21),('Heading 1',15),('Heading 2',12),('Caption',9)]:
 st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体');st.paragraph_format.space_after=Pt(6)
doc.styles['Normal'].paragraph_format.line_spacing=1.16
doc.styles['Caption'].font.bold=False
doc.styles['Caption'].font.italic=False
doc.styles['Heading 1'].paragraph_format.space_before=Pt(2)
doc.styles['Heading 2'].paragraph_format.space_before=Pt(9)
def p(t,size=None):
 q=doc.add_paragraph(t)
 if size:
  for a in q.runs:a.font.size=Pt(size)
 return q
def h(t):doc.add_heading(t,1)
def page(t):
 q=doc.add_heading(t,1);q.paragraph_format.page_break_before=True
def fig(name,caption,width=17.6):
 q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.paragraph_format.space_before=Pt(5);q.paragraph_format.space_after=Pt(3);q.paragraph_format.keep_with_next=True;q.add_run().add_picture(str(FIG/(name+'.png')),width=Cm(width))
 q=doc.add_paragraph(style='Caption');a,b,rest=caption.partition('。');q.add_run(a+b).bold=True;q.add_run(rest).bold=False;q.paragraph_format.line_spacing=1.08;q.paragraph_format.space_after=Pt(8)
def table(title,headers,rows,widths):
 q=p(title,10);q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.paragraph_format.keep_with_next=True
 t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for col,w in zip(t.columns,widths):col.width=Cm(w)
 for cell,txt in zip(t.rows[0].cells,headers):cell.text=txt
 for row in rows:
  for cell,txt in zip(t.add_row().cells,row):cell.text=str(txt)
 for i,row in enumerate(t.rows):
  row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
  for j,cell in enumerate(row.cells):
   cell.width=Cm(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;cp=cell._tc.get_or_add_tcPr();bd=OxmlElement('w:tcBorders')
   for edge in ['top','bottom','left','right']:
    e=OxmlElement('w:'+edge);on=(edge=='top' and i==0) or (edge=='bottom' and i in [0,len(t.rows)-1]);e.set(qn('w:val'),'single' if on else 'nil');e.set(qn('w:sz'),'6' if i==0 and edge=='bottom' else '12');e.set(qn('w:color'),'000000');bd.append(e)
   cp.append(bd)
   for q in cell.paragraphs:
    q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.paragraph_format.space_before=Pt(4);q.paragraph_format.space_after=Pt(4);q.paragraph_format.line_spacing=1.05
    for a in q.runs:a.font.size=Pt(9);a.bold=i==0
 t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
 q=p('');q.paragraph_format.space_after=Pt(0);q.paragraph_format.space_before=Pt(0);q.paragraph_format.line_spacing=Pt(3)
 return t
def fmt(x):return f'{x:.3g}'
doc.add_heading('白血病表达差异的多重检验与验证',0)
p('第六课研究报告',11)
p('本研究比较 ALL 与 AML 两种白血病亚型的探针表达，关注大量检验中哪些差异值得进一步验证。发现部分包含 38 份样本和 7,129 个探针：原始 p≤0.05 得到 1,694 个显著结果，Bonferroni 与 BH 校正后分别保留 26 和 535 个。按发现结果锁定的 10 个候选，在历史留出样本中方向全部一致，其中 7 个通过预设验证标准。结果支持一组可重复的表达差异候选，但不足以确认致病机制或临床标志物。')
fig('figure1_design','图 1 发现与留出验证的分析框架。a，原始数据无健康对照，分析单位为一份表达样本。b–c，仅在 train 中检验全部 7,129 个探针并作完整家族校正。d，先锁定 10 个候选及其发现方向。e–f，再检验 test 中对应探针，以候选家族 Bonferroni≤0.05 且方向一致作为验证标准。图中数字来自本次计算。')
table('表 1 数据组成与分析用途',['分析部分','ALL','AML','合计','用途'],[['发现 train',27,11,38,'筛选并锁定候选'],['留出 test',20,14,34,'评价预设候选的重复性'],['合计',47,25,72,'同一研究的历史样本']],[3.2,1.5,1.5,1.5,10])
p('研究围绕五个问题展开：如何定义检验家族与错误风险；不同校正方法如何平衡错误率和检出力；校正怎样改变真实数据的发现；候选筛选如何避免夸大证据；留出样本能够支持多强的结论。',10)

page('问题一 为什么检验越多越容易得到显著结果')
p('对每个探针 j，零假设 H₀ⱼ 为 μAML,j−μALL,j=0，备择假设为差值不为零。发现部分固定使用全部 7,129 个探针，包括 58 个 AFFX 控制探针。样本编号、原始划分和诊断标签不属于检验家族。阈值均为 0.05，效应方向固定为 AML−ALL。保留控制探针是为了透明地固定本次家族，不能据此将其视为功能基因。')
doc.add_heading('检验数量与错误概率',2)
p('若 1,000 个零假设全部为真，且每个检验的假阳性概率为 0.05，假阳性个数的期望为 1,000×0.05=50；5,000 个检验时为 250。该期望由线性可加性得到，不要求检验相互独立；若单项检验是保守的，这些值是相应上界。')
p('在检验独立且单项错误率恰为 0.05 时，至少一次假阳性的概率为 1−(1−0.05)ᵐ。m=20 时已约为 64.2%，m=1,000 时几乎为 100%。因此，“1,000 次比较中有 53 个原始显著结果”不能直接证明发现了 53 个真实差异基因。真实表达数据中不知道哪些零假设为真，也不能把观察到的发现数直接当作假发现数。')
table('表 2 三种判定方法控制的对象',['方法','判定方式','控制目标与适用情境'],[
['原始 p 值','pⱼ≤0.05','控制单项第一类错误；不能据此宣称整批发现可靠'],
['Bonferroni','min(m pⱼ,1)≤0.05','FWER：出现至少一个假发现的概率；适合重视避免任何假阳性的确认性分析'],
['Benjamini–Hochberg','排序后取最大 k，使 p₍ₖ₎≤0.05k/m','FDR：重复实验中错误发现比例的期望；适合产生待验证的探索性候选列表']],[3.3,5,9.4])
p('定义 R 为发现总数、V 为假发现数，FDP=V/max(R,1)。FWER=P(V≥1)，FDR=E[FDP]。FDR 不是“平均 V 除以平均 R”，也不是某个探针为假的概率。全零效应时，只要出现发现，FDP 就等于 1，因此 FDR 与 FWER 相同。')
p('p 值是在零假设及检验模型成立时，出现当前或更极端统计量的概率；不是零假设成立的概率。校正 p 值的解释依赖完整检验家族及所选程序；本报告使用 BH adjusted p，不计算需要估计零假设比例的 Storey q-value。Bonferroni 在单项 p 值有效时不要求检验独立；BH 的标准控制结论依赖独立性或规定的正依赖条件，不能把任意相关性都视为自动满足条件。')

page('问题二 错误控制与检出力如何取舍')
p('使用真值已知的统计模拟区分假发现和漏检。每次模拟 1,000 个独立正态变量，组样本量为 27 和 11，标准差为 1。全零情境无真实差异；信号情境让 100 个变量的均值偏移 δ=0.5 或 1.0，其余 900 个保持零差异。三种情境复用同一随机噪声，每种重复 1,000 次，NumPy default_rng 种子为 42；已知等方差，采用双侧合并方差 t 检验。模拟变量不是实测探针。')
fig('figure2_simulation','图 2 多重校正的长期错误率与检出力。a，FWER 为 1,000 次重复中 V≥1 的比例。b，FDR 为逐次 FDP 的平均值。c，检出力为真实信号中被发现的比例；全零情境无真实信号，因此不绘制其检出力。灰色、蓝色和橙色分别表示原始阈值、Bonferroni 和 BH。紫色虚线为 0.05；所有结果均为有限次模拟估计。')
table('表 3 真值已知模拟的汇总结果',['δ','方法','平均 R','平均 V','FWER','FDR','检出力'],[[f'{x.delta:g}',x.method,f'{x.mean_R:.2f}',f'{x.mean_V:.2f}',f'{x.FWER:.3f}',f'{x.FDR:.3f}','不适用' if pd.isna(x.power) else f'{x.power:.3f}'] for x in sm.itertuples()],[1,3.1,2.2,2.2,2.2,2.2,2.8])
p('全零情境中，原始阈值平均得到 49.94 个假发现，与理论期望 50 相符。Bonferroni 和 BH 的 FWER 均为 0.051，略高于 0.05 属于模拟波动：该比例的 Monte Carlo 标准误约为 0.007，不能据此认定方法失效。')
p('δ=1.0 时，BH 的检出力为 0.286，Bonferroni 为 0.060；BH 的 FDR 为 0.046，但 FWER 为 0.754。这说明控制错误发现比例不等于避免任何假发现。δ 降至 0.5 后，BH 检出力仅为 0.003，未显著并不能证明真实差异不存在。')

page('问题三 多重校正怎样改变真实数据的发现')
p('发现部分每个探针进行双侧 Welch t 检验，不要求两组等方差。所有校正使用同一组原始 p 值及同一个 7,129 项家族，不能只给最后报告的探针校正。Bonferroni 对应原始 p 阈值为 0.05/7,129=7.01×10⁻⁶；BH 找到的最大拒绝秩为 535。')
fig('figure3_discovery','图 3 发现部分的全探针证据。a，7,129 个原始 p 值的直方图。b，三种方法的发现数量。c，横轴为描述性 Cohen d，即原始均值差除以合并组内标准差，纵轴为 −log₁₀(raw p)；不是 log₂ fold change。灰点为 BH 不显著，橙点仅通过 BH，蓝点通过 Bonferroni。d，对数坐标下的排序 p 值、BH 阈值及 Bonferroni 固定阈值。所有检验来自 train 的 27 份 ALL 与 11 份 AML 样本。')
table('表 4 完整检验家族中的发现数量',['判定标准','发现数','占全部探针比例','解释'],[['原始 p≤0.05',1694,'23.76%','未经多重控制的初筛结果'],['Bonferroni≤0.05',26,'0.36%','更严格的家族错误控制'],['BH≤0.05',535,'7.50%','探索性候选集合']],[4.2,2,3.3,8.2])
p('三种数量不同来自控制目标与阈值不同，不表示某种算法算错。BH 集合中有 509 个探针未通过 Bonferroni，但不能把这 509 个全部称为假阳性。真实数据缺少探针真值，无法由本表直接计算真实 FDR、假发现数或检出力。')

page('问题四 怎样避免候选筛选夸大统计证据')
p('检验家族应包含用于同一科学问题的全部比较机会。先看 7,129 个 p 值，再只对最小的 20 个做校正，会忽略选择过程。在此数据中，首位探针 U22376_cds2_s_at 的完整家族 BH 值为 5.98×10⁻⁵；错误地只校正所选 20 项时变为 1.68×10⁻⁷，约缩小 356 倍。这不是新增证据。')
fig('figure4_selection','图 4 事后缩小检验家族对校正值的影响。横轴为发现集原始 p 值最小的 20 个探针的排名；蓝线为完整 7,129 项 BH 校正，橙线为先筛选再只校正 20 项的错误示范。纵轴采用对数尺度。错误流程仅用于解释选择偏倚，未用于确定本报告候选。')
p('本报告在发现集 BH 显著的探针中，按原始 p 值、探针名依次升序取前 10 个，保存候选名单、方向和验证标准后才读取留出表达值。10 个候选均不是 AFFX 控制探针。若某些探针确实在接触本数据前基于独立依据指定，可预先定义较小家族；这与观察结果后缩小家族不同。')
fig('figure5_heatmap','图 5 锁定候选的表达热图。每行为一个候选，每列为一份样本，按发现 ALL、发现 AML、验证 ALL、验证 AML 分组，组内保留源顺序；候选按发现 p 值排序。每个探针用发现部分的均值和标准差计算 z 分数，再用同样参数显示验证样本，未进行按结果聚类。蓝色表示较低、橙色表示较高表达，颜色截断于 ±2.5。标准化仅用于显示，检验始终使用原尺度。')
p('热图只展示已选择的候选，组间颜色分离不能作为另一份独立验证，也不代表所有探针都具有同样模式。发现集的均值差、Cohen d 和逐项 95% CI 有助于理解量级，但筛选后的极端效应可能被高估，普通区间不保证筛选后的覆盖率。')

page('问题五 留出样本是否支持这些候选')
p('在 34 份 test 样本中，只检验已锁定的 10 个候选。验证成功要求双侧 Welch 检验的候选家族 Bonferroni adjusted p≤0.05，且 AML−ALL 的符号与发现部分一致。结果为 10/10 方向一致，7/10 达到完整验证标准；失败者保留在报告中，不替换候选。')
fig('figure6_validation','图 6 候选在发现与验证部分的效应区间。点为原尺度均值差 AML−ALL。a，蓝色为发现部分逐项 95% Welch CI，不是筛选后区间。b，橙色为验证部分逐项 99.5% Welch CI，即对 10 个锁定候选进行 Bonferroni 调整的名义家族 95% 同时区间。虚线为零差异，右侧标注是否达到预设验证标准。区间的可靠性仍取决于单项检验与样本独立性假设。')
table('表 5 全部锁定候选的留出验证结果',['探针','发现 Δ','验证 Δ','验证 Bonf. p','通过'],[[x.probe,f'{x.delta_discovery:.1f}',f'{x.delta_validation:.1f}',fmt(x.bonf_validation),'是' if x.replicated else '否'] for x in c.itertuples()],[5.6,2.8,2.8,3.8,1.7])
p('Δ 为原始表达尺度的均值差，不能解释为倍数变化。L13278_at、U09087_s_at 和 X74262_at 未通过校正后的验证标准，但方向一致；这可能与效应变小、估计不精确或样本差异有关，不能据此证明它们不存在真实差异。',9.5)

page('候选实例与结论边界')
x=c.iloc[0]
p('以发现集排名第一的 U22376_cds2_s_at 为实例，进一步检查原始数据分布和效应，而不是只报告最小 p 值。该探针在两部分的 AML 平均表达均低于 ALL；留出部分的差值绝对值较小，提示不能直接沿用发现集的效应大小。')
fig('figure7_candidate','图 7 首位锁定候选的原始表达分布。每个点代表一份表达样本，横向抖动仅减少重叠；黑色横线为组均值。蓝色为 ALL，橙色为 AML。a，发现部分 27 份 ALL 与 11 份 AML。b，验证部分 20 份 ALL 与 14 份 AML。两个面板使用相同纵轴，未对表达值取对数。此实例按发现排名选择，未按验证结果挑选。')
table('表 6 U22376_cds2_s_at 的完整证据',['指标','发现部分','留出验证部分'],[
['AML / ALL 均值',f'{x.mean_AML_discovery:.2f} / {x.mean_ALL_discovery:.2f}',f'{x.mean_AML_validation:.2f} / {x.mean_ALL_validation:.2f}'],
['Δ 及逐项 95% CI',f'{x.delta_discovery:.2f} [{x.lo_discovery:.2f}, {x.hi_discovery:.2f}]',f'{x.delta_validation:.2f} [{x.lo_validation:.2f}, {x.hi_validation:.2f}]'],
['描述性 Cohen d',f'{x.d_discovery:.3f}',f'{x.d_validation:.3f}'],
['原始 p',fmt(x.p_discovery),fmt(x.p_validation)],
['Bonferroni adjusted p',fmt(x.bonf_discovery)+'（7,129 项）',fmt(x.bonf_validation)+'（10 项）'],
['BH adjusted p',fmt(x.bh_discovery),'验证判定不使用 BH']],[4,6.85,6.85])
doc.add_heading('能够支持的结论',2)
p('该探针在本研究的发现与留出样本中均显示 AML 表达较低，方向一致且通过候选家族校正，因而值得进一步验证。这一结论针对探针层面的亚型表达关联，不能写成“已发现白血病致病基因”，也不能推断对健康人的疾病诊断性能。')
doc.add_heading('仍需要的证据',2)
p('后续研究需要核实探针与现行基因注释的对应关系，实施质量控制，使用独立招募的样本和其他测量平台重复，并研究细胞组成、批次及临床协变量的影响。只有在具有合适设计的功能与临床研究中，才能进一步评价机制或应用价值。')

page('综合结论 方法说明与参考文献')
doc.add_heading('结论',2)
p('多重检验改变的是证据判定规则，而不是表达值本身。本次 7,129 项探索分析中，BH 保留 535 个候选；预先锁定的前 10 个中，7 个在历史留出样本达到方向与校正显著性双重标准。最合适的表述是“识别出值得独立验证的白血病亚型表达差异探针”，而不是已确证的疾病基因或临床标志物。')
doc.add_heading('数据处理与推断限制',2)
p('原始矩阵共 72×7,129 个表达值，无缺失、非有限值、常数探针或完全重复表达行；数值范围为 −28,400 至 71,369，包含 147,174 个负值和 1,615 个零。数据是处理后的微阵列强度，不是 RNA-seq 原始计数。直接保留原尺度，不把非正值当缺失，不作 log/log1p 变换。')
p('一行是一份表达样本，现有字段不足以核验是否来自互不重复的患者，也缺少批次、中心和临床混杂信息。Welch 检验依赖独立性，并可能受小样本、偏态和异常值影响；多重校正不能修复无效的单项 p 值。探针相关性限制 BH 理论控制保证的直接应用。7,129 个探针不等于 7,129 个独立基因。')
p('test 是同一研究的历史留出部分，不是新招募的外部队列。验证所得 7/10 不能推广成全部 535 个 BH 候选的重复率，也不能据此计算真实 FDR。发现集普通 95% CI 未校正选择偏倚，验证同时区间仍是 Welch 模型下的近似推断。')
doc.add_heading('可重复性',2)
stamp=r['lock']['locked_utc'];ver=r['versions']
p(f'分析采用 Python {ver["python"]}、NumPy {ver["numpy"]}、pandas {ver["pandas"]} 与 SciPy {ver["scipy"]}。BH 计算已与 statsmodels 的实现逐项核对。候选锁定记录保存于 locked_candidates.json，UTC 时间为 {stamp}。模拟汇总采用每次 FDP 的平均值；全零情境检出力无定义。',9)
p('源 CSV 的 SHA-256：'+r['lock']['source_sha256'],8)
doc.add_heading('参考文献与图形来源',2)
refs=[
'[1] Golub TR, et al. Molecular classification of cancer: class discovery and class prediction by gene expression monitoring. Science. 1999;286:531–537. doi:10.1126/science.286.5439.531. 数据研究来源。',
'[2] Krzywinski M, Altman N. Comparing samples—part II. Nature Methods. 2014;11:355–356. doi:10.1038/nmeth.2900. 借鉴其模拟、错误控制与分面图解的组织方式。',
'[3] Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. Journal of the Royal Statistical Society Series B. 1995;57:289–300. doi:10.1111/j.2517-6161.1995.tb02031.x. FDR 方法依据。',
'[4] 本课程 data/README.md、student-worksheet.docx 与 OpenML leukemia 元数据快照（ID 1104，version 1）。工作单仅用于确定课程主题；本报告按五个研究问题重新组织。']
for ref in refs:p(ref,8.5)
p('所有图均依据本次计算原创绘制，统一浅米色背景与蓝橙配色；模拟图明确区分于真实数据。图形参考文献不表示复现原论文的全部分析。',8.5)
# Enforce explicit script-specific fonts in every run and style.
for st in doc.styles:
 for border in list(st._element.iter(qn('w:pBdr'))):border.getparent().remove(border)
 if hasattr(st,'font'):
  st.font.name='Times New Roman';st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体');st.font.color.rgb=RGBColor(0,0,0)
for ps in [doc.paragraphs]+[cell.paragraphs for t in doc.tables for row in t.rows for cell in row.cells]:
 for q in ps:
  for border in list(q._element.iter(qn('w:pBdr'))):border.getparent().remove(border)
  for a in q.runs:
   a.font.name='Times New Roman';a.font.color.rgb=RGBColor(0,0,0);rf=a._element.get_or_add_rPr().rFonts
   for key,val in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia','宋体')]:rf.set(qn('w:'+key),val)
# restrained page numbers
foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
DEST=ROOT/'白血病表达差异与多重检验_完成稿.docx';doc.save(DEST)
print(DEST)
