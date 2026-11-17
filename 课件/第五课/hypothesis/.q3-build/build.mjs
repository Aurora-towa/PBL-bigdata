import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from 'file:///C:/Users/340/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import {finalizePresentation} from 'file:///C:/Users/340/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root=process.cwd(),out=path.join(root,'outputs/method_comparison'),stage=path.join(root,'.q3-build');
await fs.mkdir(out,{recursive:true});
const W=1800,H=1120,p=Presentation.create({slideSize:{width:W,height:H}}),s=p.slides.add();s.background.fill='#FFFFFF';
const C={ink:'#252B30',gray:'#65717A',line:'#D9D2C9',blue:'#387DA0',orange:'#C9714D',warm:'#FAF5ED'};
let svg=[],num=0; const esc=t=>String(t).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function rect(x,y,w,h,fill,stroke='none'){s.shapes.add({name:`背景 ${++num}`,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:1}});svg.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}"/>`);}
function text(t,x,y,w,size=22,bold=false,color=C.ink,align='left'){const a=s.shapes.add({name:t,geometry:'textbox',position:{left:x,top:y,width:w,height:size*1.5},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.style={fontSize:size,typeface:'Microsoft YaHei',color,bold,alignment:align,verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'none'};svg.push(`<text x="${align==='center'?x+w/2:x}" y="${y+size*1.1}" font-size="${size}" font-weight="${bold?700:400}" fill="${color}" text-anchor="${align==='center'?'middle':'start'}">${esc(t)}</text>`);}
function poly(pts,color=C.gray,width=2,fill='none'){const xs=pts.map(a=>a[0]),ys=pts.map(a=>a[1]),x=Math.min(...xs),y=Math.min(...ys),w=Math.max(1,Math.max(...xs)-x),h=Math.max(1,Math.max(...ys)-y);s.shapes.add({name:`线条 ${++num}`,geometry:'custom',position:{left:x,top:y,width:w,height:h},fill,line:{fill:color,width},customPaths:[{width:w,height:h,commands:pts.map((a,i)=>({[i?'lineTo':'moveTo']:{x:a[0]-x,y:a[1]-y}}))}]});svg.push(`<polyline points="${pts.map(a=>a.join(',')).join(' ')}" fill="${fill}" stroke="${color}" stroke-width="${width}"/>`);}
function line(x,y,xx,yy,col=C.gray,width=2){poly([[x,y],[xx,yy]],col,width);}
function dot(x,y,r=4,col=C.blue){s.shapes.add({name:`数据点 ${++num}`,geometry:'ellipse',position:{left:x-r,top:y-r,width:r*2,height:r*2},fill:col,line:{fill:'none',width:0}});svg.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${col}"/>`);}
function arrow(x,y,xx,yy){line(x,y,xx,yy);poly([[xx-5,yy-8],[xx,yy],[xx+5,yy-8]],C.gray,2);}
text('数据结构与统计方法选择',42,24,1400,36,true);
text('问题三：首选方法、关键假设与备选方案',44,76,1400,23,false,C.gray);
const centers=[206,553,900,1247,1594];
rect(40,128,1720,200,C.warm);
text('研究问题与变量类型',650,140,500,25,true,C.ink,'center');
line(900,180,900,198);line(379,198,1594,198);
for(const [x,w,t] of [[226,307,'连续结局：比较均值'],[747,306,'分类变量：比较比例'],[1094,306,'连续变量：分析关联'],[1441,306,'二分类结局：预测概率']]){line(x+w/2,198,x+w/2,214);text(t,x,216,w,21,true,C.ink,'center');}
line(206,263,553,263);line(379,249,379,263);
for(let i=0;i<5;i++){if(i<2)line(centers[i],263,centers[i],275);text(['独立两组','同一人前后测量','sex × disease','age × thalach','多个预测变量'][i],centers[i]-155,277,310,21,false,C.gray,'center');arrow(centers[i],310,centers[i],346);}
const titles=['独立样本比较','配对样本比较','分类变量关联','连续变量关联','二分类预测'];
for(let i=0;i<5;i++){
 const x=40+i*347;
 rect(x,355,332,660,i%2===0?'#FBF7F0':'#FCF1EB');
 text('abcde'[i],x+16,368,30,29,true);text(titles[i],x+50,371,270,25,true);
 text(['两组受试者相互独立','每条线连接同一名患者','观察计数与期望计数','观察关系形态与异常值','结局取值为 0 或 1'][i],x+16,417,300,20,false,C.gray);
 line(x+16,682,x+316,682,C.line,1);
}
// a: independent samples and mean intervals, illustrative values
{const x=40;line(x+45,635,x+288,635);line(x+45,466,x+45,635);text('心率',x+17,448,80,17,false,C.gray);
for(let g=0;g<2;g++){const cx=x+108+g*118,base=530+g*38,col=g?C.orange:C.blue;for(let j=0;j<17;j++)dot(cx-19+(j%5)*9,base+Math.sin(j*2.3)*31+(j%3)*8,3.5,col);line(cx+30,base-17,cx+30,base+25,col,2.5);line(cx+22,base-17,cx+38,base-17,col,2.5);line(cx+22,base+25,cx+38,base+25,col,2.5);dot(cx+30,base+4,5,col);}text('无疾病证据',x+55,642,112,17,false,C.blue,'center');text('有疾病证据',x+188,642,112,17,false,C.orange,'center');}
// b: paired observations
{const x=387;line(x+48,635,x+288,635);line(x+48,466,x+48,635);text('心率',x+18,448,80,17,false,C.gray);for(let j=0;j<9;j++){let y=484+j*15,yy=y+22+Math.sin(j*1.4)*25;line(x+90,y,x+248,yy,'#B9B4AF',1.6);dot(x+90,y,4,C.blue);dot(x+248,yy,4,C.orange);}text('测量前',x+52,642,80,18,false,C.blue,'center');text('测量后',x+208,642,80,18,false,C.orange,'center');}
// c: symbolic contingency table
{const x=734;text('disease',x+135,462,150,18,false,C.gray,'center');text('0',x+148,493,55,20,false,C.blue,'center');text('1',x+230,493,55,20,false,C.orange,'center');text('sex',x+22,553,66,20,false,C.gray);for(let r=0;r<2;r++){text(String(r),x+84,534+r*62,40,20,false,C.gray,'center');for(let c=0;c<2;c++){rect(x+134+c*82,529+r*62,75,55,c?'#F0D6C8':'#DCEAF0');text(['n₀₀','n₀₁','n₁₀','n₁₁'][r*2+c],x+134+c*82,538+r*62,75,22,false,C.ink,'center');}}text('每个单元格表示人数',x+30,649,272,18,false,C.gray,'center');}
// d: scatter with trend
{const x=1081;line(x+48,631,x+288,631);line(x+48,476,x+48,631);text('thalach',x+17,447,130,18,false,C.gray);for(let j=0;j<32;j++){let xx=x+60+j*6.6,yy=497+j*2.7+Math.sin(j*3.1)*23+Math.cos(j*1.3)*12;dot(xx,yy,3.5,C.blue);}line(x+62,499,x+274,590,C.orange,3);text('age',x+144,640,90,19,false,C.gray,'center');}
// e: logistic probability schematic
{const x=1428;line(x+49,632,x+290,632);line(x+49,477,x+49,632);text('P(disease = 1)',x+15,447,290,18,false,C.gray);text('1',x+19,467,25,17,false,C.gray);text('0',x+19,615,25,17,false,C.gray);for(let j=0;j<12;j++)line(x+49+j*20,555,x+59+j*20,555,'#B9B4AF',1);let pts=[];for(let j=0;j<=60;j++){const z=-5+j/6;pts.push([x+56+j*3.7,627-145/(1+Math.exp(-z))]);}poly(pts,C.orange,3);text('模型线性预测值',x+51,640,245,18,false,C.gray,'center');}
const details=[
['Welch t 检验','比较两组总体均值','关键：观测独立','允许两组方差不同','备选：Mann–Whitney U','检验分布／秩差异','不直接等同于均值检验'],
['配对 t 检验','检验个体差值的均值','关键：患者之间独立','小样本关注差值正态性','备选：Wilcoxon 符号秩','要求差值分布对称','本数据无前后配对记录'],
['Pearson χ² 检验','检验两个分类变量独立性','关键：观测独立','期望频数足以支持近似','备选：Fisher 精确检验','适用于稀疏 2×2 表','使用人数而非百分比检验'],
['Pearson 相关','衡量线性关联','关键：独立观测、线性关系','经典推断关注二元正态性','备选：Spearman 秩相关','衡量单调关联','需先检查散点与异常值'],
['Logistic 回归','age + sex + thalach','关键：独立观测','连续变量与 logit 关系合理','备选：惩罚 Logistic 回归','交叉验证评估泛化能力','同时检查区分度与校准']
];
for(let i=0;i<5;i++){const x=56+i*347,d=details[i];text('首选方法',x,697,300,19,false,C.gray);text(d[0],x,728,305,24,true,i===4?C.orange:C.blue);text(d[1],x,765,305,20);text(d[2],x,811,305,20);text(d[3],x,843,305,20);text(d[4],x,893,305,20,true);text(d[5],x,926,305,19);text(d[6],x,962,305,18,false,C.gray);}
text('图中散点、配对线和概率曲线均为概念示意，不代表本数据的分析结果。交叉验证用于模型评价，本身不是假设检验。',44,1031,1710,20,false,C.gray);
text('图形组织参考 Nature Methods “Points of Significance” 系列（2014–2016），按本作业研究问题重新绘制。',44,1070,1710,18,false,C.gray);
await fs.writeFile(path.join(out,'问题三_统计方法选择与对照.svg'),`<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1120" viewBox="0 0 1800 1120"><rect width="1800" height="1120" fill="white"/><g font-family="Microsoft YaHei,Arial,sans-serif">${svg.join('\n')}</g></svg>`);
const cand=path.join(stage,'candidate.pptx');await(await PresentationFile.exportPptx(p)).save(cand);
const skill='C:/Users/340/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
await finalizePresentation({workspaceDir:root,candidatePath:cand,finalPath:path.join(out,'问题三_统计方法选择与对照_可编辑.pptx'),pythonExecutable:'C:/Users/340/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu',`${W*9525},${H*9525}`],explicitTotalSlideCount:1,fontPolicy:{basis:'design',families:['Microsoft YaHei']},verifyArtifactToolImport:true,receiptPath:path.join(stage,'validation.json')});
await fs.writeFile(path.join(out,'图注与参考文献.md'),'# 问题三：数据结构与统计方法选择\n\n本图为方法选择示意，不报告实际数据结果。所有图形均为原生可编辑元素。配对情境为假设场景，本数据没有前后测量。Mann–Whitney U 与 Welch t 的检验目标不同，不能无条件互换。配对符号秩检验要求差值分布对称。Logistic 模型应检查完全分离、样本量及函数形式，交叉验证用于预测评价。\n\n图形组织参考（非原图复制）：\n- Krzywinski & Altman. Comparing samples—part I. Nature Methods (2014). https://www.nature.com/articles/nmeth.2858\n- Krzywinski & Altman. Designing comparative experiments. Nature Methods (2014). https://www.nature.com/articles/nmeth.2974\n- Altman & Krzywinski. Association, correlation and causation. Nature Methods (2015). https://www.nature.com/articles/nmeth.3587\n- Lever et al. Logistic regression. Nature Methods (2016). https://www.nature.com/articles/nmeth.3904\n');
console.log('Created '+s.shapes.items.length+' editable shapes');
