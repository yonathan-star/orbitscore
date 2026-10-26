"""Four deterministic synthesized drums, no copyrighted samples or libraries."""
from array import array
import math
RATE=16000

def make_samples():
    out=[];seed=0x12345678
    for voice,duration in enumerate((.32,.19,.065,.28)):
        a=array('h');phase=0.
        for n in range(int(duration*RATE)):
            t=n/RATE;seed=(1664525*seed+1013904223)&0xffffffff
            noise=((seed>>16)/32768.-1.)
            if voice==0:
                phase+=2*math.pi*(45+110*math.exp(-t*45))/RATE
                x=math.sin(phase)*math.exp(-t*17)+noise*math.exp(-t*250)*.16
            elif voice==1:x=(noise*.78+math.sin(2*math.pi*185*t)*.22)*math.exp(-t*24)
            elif voice==2:x=noise*math.exp(-t*85)
            else:
                phase+=2*math.pi*(110+80*math.exp(-t*32))/RATE
                x=math.sin(phase)*math.exp(-t*18)
            # Fixed maximum four-voice sum <= 4*6500 < int16 clipping.
            a.append(max(-6500,min(6500,int(x*6000))))
        out.append(a)
    return out

class Mixer:
    def __init__(self,samples):self.samples=samples;self.positions=[-1]*4;self.volume=0.5
    def render(self,buf,events):
        ei=0
        for frame in range(len(buf)//2):
            while ei<len(events) and events[ei][0]==frame:
                mask=events[ei][2]
                for v in range(4):
                    if mask&(1<<v):self.positions[v]=0
                ei+=1
            total=0
            for v in range(4):
                j=self.positions[v]
                if j>=0:
                    total+=self.samples[v][j];j+=1
                    self.positions[v]=j if j<len(self.samples[v]) else -1
            sample=max(-32768,min(32767,int(total*self.volume)))
            buf[2*frame]=sample&255;buf[2*frame+1]=(sample>>8)&255
