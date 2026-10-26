import sys,unittest,struct,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'firmware'))
from core import Scanner,Sequencer
from synth import make_samples,Mixer
class DesignTests(unittest.TestCase):
 def pulse(self,s,t,index,mask):
  s.feed(t,False,False,0);s.feed(t+3,False,False,0)
  s.feed(t+10,True,index,mask);return s.feed(t+13,True,index,mask)
 def test_capture_requires_closing_index(self):
  s=Scanner();pattern=[i%16 for i in range(16)]
  for i,v in enumerate(pattern):self.assertIsNone(self.pulse(s,i*150,i==0,v))
  self.assertFalse(s.complete)
  self.assertEqual(self.pulse(s,2400,True,0),pattern)
 def test_no_index_no_capture(self):
  s=Scanner()
  for i in range(20):self.pulse(s,i*150,False,15)
  self.assertFalse(s.started);self.assertEqual(s.pending,[])
 def test_bad_revolution_rejected(self):
  s=Scanner();self.pulse(s,0,True,1);self.pulse(s,150,False,2);self.pulse(s,300,True,3)
  self.assertIsNotNone(s.error);self.assertFalse(s.complete)
 def test_fast_scan_rejected(self):
  s=Scanner();self.pulse(s,0,True,1);self.pulse(s,25,False,2);self.assertIsNotNone(s.error)
 def test_bounce_rejected(self):
  s=Scanner();s.feed(0,True,True,15);s.feed(1,False,False,0);s.feed(2,True,True,15);s.feed(3,False,False,0)
  self.assertFalse(s.started)
 def test_timing_no_drift(self):
  s=Sequencer();s.load([15]*16);s.playing=True;events=[]
  for _ in range(1250):events.extend(s.events(128))
  self.assertEqual(len(events),80);self.assertEqual(s.frame,160000)
  self.assertAlmostEqual(s.next_step,160000)
 def test_tempo_bounds_and_mutes(self):
  s=Sequencer();s.load([15]*16);s.toggle_mute(0);s.toggle_mute(3);s.playing=True
  self.assertEqual(s.events(128)[0][2],6);s.set_tempo(999);self.assertEqual(s.bpm,180);s.set_tempo(1);self.assertEqual(s.bpm,60)
 def test_invalid_pattern_rejected(self):
  s=Sequencer()
  for a in ([1]*15,[16]*16,[-1]*16):
   with self.assertRaises(ValueError):s.load(a)
 def test_audio_range_and_end(self):
  samples=make_samples();m=Mixer(samples);m.volume=1.;buf=bytearray(16000*2)
  m.render(buf,[(0,0,15)])
  values=struct.unpack('<16000h',buf);self.assertGreater(max(values),0);self.assertLessEqual(max(abs(x) for x in values),26000);self.assertEqual(list(values[-100:]),[0]*100)
if __name__=='__main__':unittest.main(verbosity=2)
