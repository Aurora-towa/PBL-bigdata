"""Build an editable SVG using native text, shapes and paths; no embedded bitmap."""
from pathlib import Path
from html import escape
import math
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent
parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024">
<title>心脏病证据与最大运动心率 研究设计与假设框架</title>
<desc>可编辑矢量图。文字、背景、连接线、图标与统计示意均为 SVG 原生对象。分布与效应量小图为示意，数字为实际统计结果。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#657078"/></marker></defs>
<style>text{font-family:'Microsoft YaHei','Noto Sans CJK SC',Arial,sans-serif;fill:#172028} .muted{fill:#657078}</style>
<rect width="1536" height="1024" fill="white"/>
''']
BLUE='#2878A0'; RED='#C75B45'; INK='#172028'; GREY='#657078'
def group(name):parts.append(f'<g id="{name}">')
def end():parts.append('</g>')
def rect(x,y,w,h,fill='white',stroke='#D8DDE0',r=6,sw=1.2):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def txt(x,y,s,size=20,color=INK,bold=False,anchor='middle'):
    parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{700 if bold else 400}" style="fill:{color}">{escape(s)}</text>')
def line(x1,y1,x2,y2,color=GREY,width=1.7,arrow=False,dash=None):
    attrs=(' marker-end="url(#arrow)"' if arrow else '')+(f' stroke-dasharray="{dash}"' if dash else '')
    parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{attrs}/>')
def path(d,stroke=INK,fill='none',sw=1.5):parts.append(f'<path d="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}"/>')
def circle(x,y,r,stroke=INK,fill='none',sw=1.5):parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}"/>')
def person(x,y,color=GREY,scale=1):
    parts.append(f'<g transform="translate({x} {y}) scale({scale})">')
    circle(0,0,5,color,sw=1.7)
    path('M -8 23 L -8 12 Q -8 7 -3 7 L 3 7 Q 8 7 8 12 L 8 23 M -4 15 L -4 30 M 4 15 L 4 30 M -4 23 L 4 23',color,sw=1.7);end()
def people(x,y,color=GREY):
    person(x+12,y-7,color,.85);person(x,y+7,color,.85);person(x+24,y+7,color,.85)
def boxlines(x,y,w,h,strings,color=INK,fill='white',stroke='#D8DDE0',size=20,bold=False):
    rect(x,y,w,h,fill,stroke)
    step=size*1.4; start=y+h/2-(len(strings)-1)*step/2+size*.35
    for i,s in enumerate(strings):txt(x+w/2,start+i*step,s,size,color,bold)

group('panel-a-cohort-flow')
rect(20,16,548,614,'#FFF9EE','#DFC499',9)
txt(38,55,'a',36,bold=True,anchor='start');txt(85,53,'研究对象与观察性分组',27,bold=True,anchor='start')
group('four-source-centres')
for x,y,name,n in [(44,80,'Cleveland',303),(304,80,'Hungary',294),(44,166,'Switzerland',123),(304,166,'VA Long Beach',200)]:
    rect(x,y,240,71,'#FAFBF8','#C9D4D5'); people(x+30,y+24)
    txt(x+144,y+28,name,19);txt(x+144,y+53,f'n = {n}',19)
# Bracket groups the two rows as four sources, not a causal chain between centres.
line(41,76,35,76);line(35,76,35,245);line(35,245,544,245);line(544,245,544,239)
line(295,245,295,277,arrow=True)
end()
boxlines(164,278,264,56,['原始样本  n = 920'],bold=True)
line(296,334,296,413,arrow=True);line(296,368,433,368,arrow=True)
boxlines(434,341,116,57,['心率缺失','n = 55'],size=18,fill='#F6F7F2')
boxlines(164,414,264,56,['主要分析样本  n = 865'],bold=True)
line(296,470,296,486);line(166,486,425,486);line(166,486,166,503,arrow=True);line(425,486,425,503,arrow=True)
for x,color,head,detail in [(36,BLUE,'无疾病证据','disease = 0，n = 391'),(300,RED,'有疾病证据','disease = 1，n = 474')]:
    rect(x,505,252,73,'#F0F7F9' if color==BLUE else '#FFF2EC',color)
    people(x+25,532,color);txt(x+157,534,head,19,color,True);txt(x+151,561,detail,17,color)
txt(294,607,'观察性分组，非随机分配',19)
end()

group('panel-b-endpoint-analysis')
rect(584,16,932,614,'#FFF4E7','#DFC499',9)
txt(600,55,'b',36,bold=True,anchor='start');txt(647,53,'主要终点与数据分析',27,bold=True,anchor='start')
group('endpoint-definition')
rect(598,82,178,462,'#FFFAF3','#E6CAB1')
txt(687,182,'最大运动心率',21,bold=True);txt(687,215,'thalach（bpm）',21,bold=True)
rect(634,265,106,90,'white',GREY,4,2)
rect(643,277,88,15,'#EBCBA0','none',0)
for row in range(3):
    for col in range(3):rect(643+col*31,299+row*17,25,11,'#B6C0C4','none',0)
txt(687,392,'每名受试者一条记录',17)
end()
line(762,278,792,278,arrow=True)
group('distribution-schematic-and-statistics')
rect(790,82,317,462,'#FFFAF3','#E6CAB1')
txt(948,125,'分组分布（示意）',21,bold=True)
line(842,160,842,335,INK);line(842,335,1080,335,INK)
parts.append('<text x="820" y="248" font-size="18" text-anchor="middle" transform="rotate(-90 820 248)">心率分布</text>')
for x,col,top,qtop,median,qbottom,bottom in [(906,BLUE,201,220,244,265,284),(1025,RED,235,259,283,305,324)]:
    line(x,top,x,bottom,col);line(x-18,top,x+18,top,col);line(x-18,bottom,x+18,bottom,col)
    rect(x-30,qtop,60,qbottom-qtop,'white',col,0,2);line(x-30,median,x+30,median,INK,2)
for x,col,label,n,qs in [(901,BLUE,'无疾病证据',391,['Q1 = 134.5','中位数 = 151','Q3 = 167.5']),(1024,RED,'有疾病证据',474,['Q1 = 112','中位数 = 128','Q3 = 145'])]:
    txt(x,367,label,18);txt(x,394,f'n = {n}',18)
    for i,s in enumerate(qs):txt(x,472+i*25,s,17)
txt(948,430,'实际统计量（bpm）',19,bold=True);line(813,441,1084,441,'#BCA48E',1)
end()
line(1094,278,1132,278,arrow=True)
group('effect-estimate')
rect(1125,82,378,462,'#FFFAF3','#E6CAB1')
txt(1314,125,'均值差与95% CI',21,bold=True)
txt(1314,180,'Δ = μ₁ − μ₀',30)
txt(1314,224,'μ₁：有疾病证据组总体均值',18,RED)
txt(1314,253,'μ₀：无疾病证据组总体均值',18,BLUE)
txt(1314,309,'−20.54 bpm [−23.73, −17.35]',21)
line(1163,434,1483,434,INK);line(1444,338,1444,439,GREY,1.5,dash='7 6')
line(1224,378,1301,378,RED,2);line(1224,370,1224,386,RED,2);line(1301,370,1301,386,RED,2);circle(1262,378,7,RED,RED)
txt(1444,461,'0',18);txt(1314,498,'效应量呈现（示意）',19);txt(1314,528,'有疾病证据组 − 无疾病证据组',18)
end();end()

group('panel-c-hypothesis-test')
rect(20,647,1496,313,'#FFF2EE','#E3B6AA',9)
txt(38,689,'c',36,bold=True,anchor='start');txt(85,686,'统计假设与双侧检验',27,bold=True,anchor='start')
group('null-and-alternative')
rect(54,719,409,196,'#FFFAF7','#E7C7BD')
txt(258,781,'H₀：Δ = 0',29);txt(258,830,'H₁：Δ ≠ 0',29)
txt(258,885,'双侧 Welch t 检验，α = 0.05',22)
end();line(477,804,518,804,arrow=True)
group('null-distribution-schematic')
rect(526,695,497,244,'#FFFAF7','#E7C7BD')
txt(774,724,'检验统计量分布（概念示意）',21,bold=True)
px=lambda z:774+54*z
py=lambda z:861-120*math.exp(-z*z/2)
xx=[-3.9+i*7.8/220 for i in range(221)]
for subset in [[v for v in xx if v<=-1.96],[v for v in xx if v>=1.96]]:
    path(f'M {px(subset[0])} 861 '+' '.join(f'L {px(v):.2f} {py(v):.2f}' for v in subset)+f'L {px(subset[-1])} 861 Z',stroke='none',fill='#D99683',sw=0)
path('M '+' L '.join(f'{px(v):.2f} {py(v):.2f}' for v in xx),sw=2)
line(557,861,991,861,INK)
for z,label in [(-1.96,'−t*'),(0,'0'),(1.96,'+t*')]:
    line(px(z),861,px(z),868,INK,1);txt(px(z),891,label,18)
txt(615,829,'0.025',19,RED);txt(931,829,'0.025',19,RED);txt(774,824,'不拒绝 H₀',18)
txt(774,924,'两侧阴影：拒绝域，总面积为 0.05',18,RED)
end();line(1032,804,1060,804,arrow=True)
group('reporting-and-decision')
rect(1068,718,419,190,'#FFFAF7','#E7C7BD')
path('M 1098 748 L 1141 748 L 1164 771 L 1164 839 L 1098 839 Z M 1141 748 L 1141 771 L 1164 771',sw=2.5)
for y in [780,795,811]:line(1112,y,1146,y,INK,2)
txt(1328,773,'报告均值差、95% CI 与双侧 p 值',18)
txt(1310,821,'p < 0.05：拒绝 H₀',21);txt(1310,858,'p ≥ 0.05：未拒绝 H₀',21)
end();end()
txt(768,998,'研究问题：心脏病证据是否与最大运动心率有关？  |  观察性关联不等于因果关系',21)
parts.append('</svg>')
svg='\n'.join(parts)
target=OUT/'研究设计与假设框架图_暖色可编辑版.svg'
target.write_text(svg,encoding='utf-8')
tree=ET.fromstring(svg); ns={'s':'http://www.w3.org/2000/svg'}
assert not tree.findall('.//s:image',ns)
print(f'{target}\nEditable text nodes: {len(tree.findall(".//s:text",ns))}; embedded raster images: 0')
