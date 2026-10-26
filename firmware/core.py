"""OrbitScore deterministic scanner and sample-clock sequencer. Rev A."""
STEPS=16
CHANNELS=4
class Scanner:
    """Light-high signals after HC14. Index is only sampled at clock edges.
    Scan one clockwise revolution in 2–8s; holes must remain light >=2ms.
    A full scan is committed only when next index arrives after 16 steps.
    """
    def __init__(self): self.arm()
    def arm(self):
        self.pending=[]; self.started=False; self.complete=False; self.error=None
        self.clock=False; self.raw=False; self.changed=0; self.last_edge=None
    def feed(self, ms, clock, index, mask):
        if self.complete or self.error: return None
        if clock != self.raw: self.raw=clock;self.changed=ms
        if clock == self.clock or ms-self.changed < 2: return None
        self.clock=clock
        if not clock: return None
        if self.last_edge is not None and ms-self.last_edge<40:
            self.error='Turn more slowly; clock pulses less than 40ms apart';return None
        self.last_edge=ms
        if not self.started:
            if not index:return None
            self.started=True
        elif index:
            if len(self.pending)==STEPS:
                self.complete=True;return self.pending[:]
            self.error='Incomplete revolution: expected 16 steps';return None
        if len(self.pending)>=STEPS:
            self.error='Missing index or extra clock hole';return None
        self.pending.append(mask & 15)
        return None

class Sequencer:
    def __init__(self, rate=16000):
        self.rate=rate;self.pattern=[0]*STEPS;self.muted=0;self.bpm=120
        self.playing=False;self.frame=0;self.next_step=0.;self.step=0;self.swing=0.
    def load(self, pattern):
        if len(pattern)!=16 or any(not isinstance(x,int) or x<0 or x>15 for x in pattern):raise ValueError('16 four-bit steps required')
        self.pattern=list(pattern);self.restart()
    def restart(self):self.frame=0;self.next_step=0.;self.step=0
    def set_tempo(self,bpm):self.bpm=max(60,min(180,int(bpm)))
    def toggle_mute(self,channel):
        if not 0<=channel<4:raise ValueError('channel')
        self.muted ^=1<<channel
    def events(self,count):
        end=self.frame+count;out=[]
        if self.playing:
            while self.next_step<end:
                offset=max(0,int(self.next_step)-self.frame)
                out.append((offset,self.step,self.pattern[self.step]&~self.muted&15))
                self.step=(self.step+1)%16;self.next_step+=self.rate*60/(self.bpm*4)
        else:self.next_step=float(end);self.step=0
        self.frame=end
        return out
