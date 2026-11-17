import xml.etree.ElementTree as ET,json,re,math
from pathlib import Path
from PIL import ImageFont
root=Path(__file__).resolve().parents[1]
svg=ET.parse(root/'outputs/study_framework/研究设计与假设框架图_暖色可编辑版.svg').getroot()
out=[]
def walk(e,tx=0,ty=0,scale=1,name=''):
    tag=e.tag.split('}')[-1]; a=e.attrib
    if tag in ['defs','style','title','desc']:return
    tr=a.get('transform','')
    m=re.search(r'translate\(([^)]+)\)',tr)
    if m:
        z=list(map(float,m[1].split()));tx+=z[0]*scale;ty+=z[1]*scale
    m=re.search(r'scale\(([^)]+)\)',tr)
    if m:scale*=float(m[1])
    name=a.get('id',name)
    if tag in ['g','svg']:
        for child in e:walk(child,tx,ty,scale,name)
        return
    data=dict(tag=tag,attrs=a,tx=tx,ty=ty,scale=scale,name=name)
    if tag=='text':
        data['text']=''.join(e.itertext());fs=float(a.get('font-size',20))
        font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if a.get('font-weight')=='700' else 'C:/Windows/Fonts/msyh.ttc',round(fs*4))
        data['textWidth']=font.getlength(data['text'])/4+6
    out.append(data)
walk(svg)
(root/'.pptx-native-build/elements.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
print(len(out))
