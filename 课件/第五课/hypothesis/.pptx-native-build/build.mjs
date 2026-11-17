import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from 'file:///C:/Users/340/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import {finalizePresentation} from 'file:///C:/Users/340/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root=process.cwd(),stage=path.join(root,'.pptx-native-build');
const p=Presentation.create({slideSize:{width:1536,height:1024}}); const slide=p.slides.add();slide.background.fill='#FFFFFF';
const elements=JSON.parse(await fs.readFile(path.join(stage,'elements.json'),'utf8'));
let n=0;
function shape(config){return slide.shapes.add({...config,name:config.name||`元素${++n}`});}
function custom(cmds,stroke,fill,sw,name){
 const pts=cmds.flatMap(c=>Object.values(c).flatMap(v=>v&&'x'in v?[{x:v.x,y:v.y},...('x1'in v?[{x:v.x1,y:v.y1}]:[])]:[]));
 const l=Math.min(...pts.map(x=>x.x)),t=Math.min(...pts.map(x=>x.y));
 const w=Math.max(1,Math.max(...pts.map(x=>x.x))-l),h=Math.max(1,Math.max(...pts.map(x=>x.y))-t);
 const local=cmds.map(c=>Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Object.fromEntries(Object.entries(v).map(([key,val])=>[key,val-(key.startsWith('x')?l:t)]))])));
 return shape({geometry:'custom',name,position:{left:l,top:t,width:w,height:h},fill,line:{fill:stroke,width:sw,style:'solid'},customPaths:[{width:w,height:h,commands:local}]});
}
for(const el of elements){
 const {tag,attrs:a,tx,ty,scale:s}=el; const X=v=>tx+Number(v)*s,Y=v=>ty+Number(v)*s; const sw=Number(a['stroke-width']||1)*s, stroke=a.stroke||'none',fill=a.fill||'none';
 const name=`${el.name} ${tag} ${++n}`;
 if(tag==='rect')shape({geometry:'rect',name,position:{left:X(a.x||0),top:Y(a.y||0),width:Number(a.width)*s,height:Number(a.height)*s},fill,borderRadius:Number(a.rx||0)*s,line:{fill:stroke,width:sw}});
 if(tag==='circle')shape({geometry:'ellipse',name,position:{left:X(Number(a.cx)-Number(a.r)),top:Y(Number(a.cy)-Number(a.r)),width:2*Number(a.r)*s,height:2*Number(a.r)*s},fill,line:{fill:stroke,width:sw}});
 if(tag==='text'){
   const fs=Number(a['font-size']||20),anchor=a['text-anchor']||'start',w=el.textWidth+4,h=fs*1.5;let left=X(a.x)-(anchor==='middle'?w/2:0),top=Y(a.y)-fs*1.12;
   let rotation=0;
   if(a.transform?.startsWith('rotate')){rotation=-90;left=X(a.x)-w/2;top=Y(a.y)-h/2;}
   const sh=shape({geometry:'textbox',name:el.text,position:{left,top,width:w,height:h,rotation},fill:'none',line:{fill:'none',width:0}});
   sh.text=el.text;sh.text.style={fontSize:fs,typeface:'Microsoft YaHei',color:a.style?.match(/fill:([^;]+)/)?.[1]||'#172028',bold:a['font-weight']==='700',alignment:anchor==='middle'?'center':'left',verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'none'};
 }
 if(tag==='line'){
   const x1=X(a.x1),y1=Y(a.y1),x2=X(a.x2),y2=Y(a.y2);
   if(a['stroke-dasharray']){const len=Math.hypot(x2-x1,y2-y1);for(let j=0;j<len;j+=13){const k=Math.min(j+7,len);custom([{moveTo:{x:x1+(x2-x1)*j/len,y:y1+(y2-y1)*j/len}},{lineTo:{x:x1+(x2-x1)*k/len,y:y1+(y2-y1)*k/len}}],stroke,'none',sw,name);}}
   else custom([{moveTo:{x:x1,y:y1}},{lineTo:{x:x2,y:y2}}],stroke,'none',sw,name);
   if(a['marker-end']){const angle=Math.atan2(y2-y1,x2-x1),len=10,width=5;custom([{moveTo:{x:x2,y:y2}},{lineTo:{x:x2-len*Math.cos(angle)+width*Math.sin(angle),y:y2-len*Math.sin(angle)-width*Math.cos(angle)}},{lineTo:{x:x2-len*Math.cos(angle)-width*Math.sin(angle),y:y2-len*Math.sin(angle)+width*Math.cos(angle)}},{close:{}}],stroke,stroke,0,name+' 箭头');}
 }
 if(tag==='path'){
   const tokens=a.d.match(/[MLQZmlqz]|[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?/g); const cmds=[];let i=0;
   while(i<tokens.length){const command=tokens[i++];if(command==='Z'){cmds.push({close:{}});continue;}if(command==='M'||command==='L'){const point={x:X(tokens[i++]),y:Y(tokens[i++])};cmds.push(command==='M'?{moveTo:point}:{lineTo:point});}else if(command==='Q')cmds.push({quadBezTo:{x1:X(tokens[i++]),y1:Y(tokens[i++]),x:X(tokens[i++]),y:Y(tokens[i++])}});else throw new Error('Unsupported '+command);}
   custom(cmds,stroke,fill,sw,name);
 }
}
const candidate=path.join(stage,'candidate.pptx');await(await PresentationFile.exportPptx(p)).save(candidate);
const skill='C:/Users/340/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const dest=path.join(root,'outputs/study_framework/研究设计与假设框架图_全部元素可编辑.pptx');
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:dest,pythonExecutable:'C:/Users/340/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu',`${1536*9525},${1024*9525}`],explicitTotalSlideCount:1,verifyArtifactToolImport:true,receiptPath:path.join(stage,'validation.json')});
console.log('Native shapes: '+slide.shapes.items.length+'; '+dest);
