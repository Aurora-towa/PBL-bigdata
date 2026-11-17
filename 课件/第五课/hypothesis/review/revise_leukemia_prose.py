from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
ROOT=Path('C:/Users/340/Desktop/6. multiple-test')
d=Document(ROOT/'白血病表达差异与多重检验_完成稿.docx')
changes={
'本研究比较 ALL':'本研究比较 ALL 与 AML 两种白血病亚型的探针表达差异。发现集包含 38 份样本和 7,129 个探针。按原始 p≤0.05 判断，有 1,694 个探针显著；经 Bonferroni 和 BH 校正后，分别为 26 个和 535 个。根据发现集结果选定的 10 个候选，在留出样本中的差异方向均一致，其中 7 个通过预设验证标准。这些探针可作为后续研究的候选，但目前尚不能认定其为致病基因或临床标志物。',
'对每个探针 j':'对每个探针 j，零假设为 AML 与 ALL 的总体平均表达相等，备择假设为两组均值不同。发现集的检验家族包括全部 7,129 个探针，其中有 58 个 AFFX 控制探针；样本编号、原始划分和诊断标签不参与检验。显著性阈值设为 0.05，均值差统一定义为 AML−ALL。控制探针保留在检验家族中，但不作为功能基因解释。',
'三种数量不同':'三种方法的发现数量不同，是因为控制的错误类型和判定阈值不同。BH 筛出的探针中，有 509 个未通过 Bonferroni 校正，但不能将它们全部视为假阳性。由于不知道每个探针是否确有差异，不能根据发现数量直接计算真实 FDR、假发现数或检出力。',
'检验家族应包含':'检验家族应包含围绕同一研究问题进行的全部比较。先查看 7,129 个 p 值，再只对最小的 20 个校正，会漏掉筛选过程中的检验机会。以 U22376_cds2_s_at 为例，完整家族的 BH 校正值为 5.98×10⁻⁵；若只校正选出的 20 项，则降为 1.68×10⁻⁷，约缩小 356 倍。数值变小来自家族范围的改变，并未增加支持该差异的证据。',
'本报告在发现集':'在发现集 BH 显著的探针中，按原始 p 值从小到大排列；p 值相同时按探针名排序，选取前 10 个。保存名单、差异方向和验证标准后，再读取留出样本的表达值。这 10 个候选均不是 AFFX 控制探针。如果在分析前已有独立依据指定某些探针，可以预先定义较小的检验家族，但不能看完结果后再缩小范围。',
'热图只展示':'热图展示的是经过筛选的 10 个候选，因此不能把图中的组间分离当作额外的独立验证。均值差、Cohen d 和逐项 95% CI 可用于描述差异大小及估计精度，但筛选出的极端效应可能偏大，普通置信区间也不保证筛选后的覆盖率。',
'在 34 份 test':'在 34 份留出样本中检验已选定的 10 个候选。验证标准为：双侧 Welch 检验经候选家族 Bonferroni 校正后 p≤0.05，且均值差方向与发现集一致。10 个候选的方向均一致，7 个满足上述标准，其余 3 个仍保留在结果表中。',
'以发现集排名第一':'U22376_cds2_s_at 在发现集中的原始 p 值最小，以下以该探针说明表达分布和效应大小。发现集和验证集中，AML 的平均表达均低于 ALL，但验证集的均值差绝对值较小，说明发现集估计的差异大小未完全重复。',
'该探针在本研究':'U22376_cds2_s_at 在发现集和留出样本中均表现为 AML 表达较低，并通过候选家族校正，支持其与白血病亚型存在表达关联。该结果不能证明其参与致病，也不能用于判断健康人是否患病。',
'后续研究需要':'后续应核实探针对应的基因，检查测量质量，并在独立招募的样本中重复测量。同时需要考虑细胞组成、批次和临床因素的影响。其生物学作用及临床价值还需功能实验和临床研究验证。',
'多重检验改变的是':'本次分析中，7,129 个探针经 BH 校正后有 535 个显著。预先选定的前 10 个候选中，7 个在留出样本中通过验证。结果支持这些探针与 ALL、AML 亚型之间存在可重复的表达差异，但其生物学意义及临床用途仍需进一步研究。',
'一行是一份表达样本':'数据中每行代表一份表达样本，但现有信息无法确认样本是否均来自不同患者，也缺少批次、中心和临床协变量。Welch 检验要求样本独立，小样本、偏态和异常值都可能影响结果；多重校正无法弥补单项检验的偏差。探针之间的相关性也可能影响 BH 的错误控制效果。此外，多个探针可能对应同一基因，不能将探针数量直接视为基因数量。',
'test 是同一研究':'验证集来自同一研究的历史留出样本，不能替代新招募的外部队列。前 10 个候选中有 7 个通过验证，不代表全部 535 个 BH 候选都具有相同的重复率，也不能据此估计真实 FDR。发现集的普通 95% CI 未校正筛选偏倚，验证集的同时区间仍依赖 Welch 检验的假设。'
}
titles={'综合结论 方法说明与参考文献':'结论与局限','候选实例与结论边界':'候选探针的表达差异','能够支持的结论':'结果解释','仍需要的证据':'后续验证','数据处理与推断限制':'数据与方法的局限','表 6 U22376_cds2_s_at 的完整证据':'表 6 U22376_cds2_s_at 的分析结果'}
remove=False
for p in list(d.paragraphs):
 if p.text=='可重复性':remove=True
 if remove or p.text.startswith('研究围绕五个问题展开'):
  p._element.getparent().remove(p._element);continue
 txt=p.text
 if txt in titles:p.text=titles[txt]
 else:
  for start,new in changes.items():
   if txt.startswith(start):p.text=new;break
 # True two-character indentation for body only; retain figures and captions.
 if p.style.name=='Normal' and p.text.strip() and not p.text.startswith(('表 ','第六课')):
  p.paragraph_format.first_line_indent=Pt(21)
  ind=p._p.get_or_add_pPr().find(qn('w:ind'))
  ind.set(qn('w:firstLineChars'),'200')
 for run in p.runs:
  run.font.name='Times New Roman';run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体')
  if p.style.name=='Normal' and p.text and not p.text.startswith('表 '):run.font.size=Pt(10.5)
dest=ROOT/'白血病表达差异与多重检验_修订稿.docx'
d.save(dest)
print(dest)
