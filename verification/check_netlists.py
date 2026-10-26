import json,xml.etree.ElementTree as E,sys
from pathlib import Path
import pcbnew as p
r=Path(__file__).resolve().parents[1];design=json.loads((r/'hardware/design.json').read_text());failed=[]
for name,bd in design.items():
 root=E.parse(r/'verification'/f'{name}.net.xml').getroot(); actual={}
 for n in root.findall('./nets/net'):
  for node in n.findall('node'):actual[(node.get('ref'),node.get('pin'))]=n.get('name').lstrip('/')
 board=p.LoadBoard(str(r/'hardware'/name/(name+'.kicad_pcb')))
 pads={(f.GetReference(),pad.GetNumber()):pad.GetNetname() for f in board.GetFootprints() for pad in f.Pads()}
 count=0
 for c in bd['parts']:
  for pin,net in c['pins'].items():
   if net.startswith('NC_'):continue
   key=(c['ref'],pin);count+=1
   if actual.get(key)!=net:failed.append((name,'schematic',key,net,actual.get(key)))
   if pads.get(key)!=net:failed.append((name,'pcb',key,net,pads.get(key)))
 print(name,count,'pin assignments compared')
print('Mismatches:',len(failed));print(*failed,sep='\n');sys.exit(bool(failed))
