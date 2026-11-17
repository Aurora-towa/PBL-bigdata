from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.analysis-deps'))
p=Path(__file__).with_name('render_with_word.py')
s=p.read_text(encoding='utf-8').replace("('worksheet-render' if name.endswith('worksheet') else 'reference-render')", "'final-render'")
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
