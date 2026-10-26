"""Copy main.py/core.py/synth.py to Raspberry Pi Pico running MicroPython 1.26.
Hardware-specific execution remains untested. See docs/bring-up.txt first.
"""
from machine import Pin, ADC, I2S
from time import ticks_ms,ticks_diff,sleep_ms
import gc,json,os
from core import Scanner,Sequencer
from synth import Mixer,make_samples,RATE

# All optical inputs are light-high after 74HC14; never connect a 5V signal.
sensors=[Pin(i,Pin.IN) for i in range(2,8)]
buttons=[Pin(i,Pin.IN,Pin.PULL_UP) for i in range(8,14)]
scan_led=Pin(14,Pin.OUT,value=0);play_led=Pin(15,Pin.OUT,value=0)
amp=Pin(19,Pin.OUT,value=0)
tempo=ADC(26);volume=ADC(27)
seq=Sequencer(RATE);scanner=Scanner();mode='idle';samples=make_samples();mix=Mixer(samples)
audio=None;buffer=bytearray(256);previous=[1]*6;stable=[1]*6;changed=[ticks_ms()]*6
scan_start=0;scan_elapsed=0;scan_last=0

def output():
    return I2S(0,sck=Pin(16),ws=Pin(17),sd=Pin(18),mode=I2S.TX,bits=16,format=I2S.MONO,rate=RATE,ibuf=1024)

def save_pattern(pattern):
    # Never overwrite a complete pattern with a partial scan.
    with open('pattern.tmp','w') as f:json.dump(pattern,f)
    os.rename('pattern.tmp','pattern.json')

try:
    with open('pattern.json') as f:seq.load(json.load(f))
except (OSError,ValueError,TypeError):pass

try:
 while True:
    now=ticks_ms();pressed=[]
    for i,b in enumerate(buttons):
        raw=b.value()
        if raw!=previous[i]:previous[i]=raw;changed[i]=now
        if raw!=stable[i] and ticks_diff(now,changed[i])>=20:
            stable[i]=raw
            if raw==0:pressed.append(i)
    for i in pressed:
        if i<4:seq.toggle_mute(i);print('Mute mask:',seq.muted)
        elif i==4:
            amp.off();seq.playing=False
            if audio:audio.deinit();audio=None
            scanner.arm();mode='scan';scan_start=now;scan_last=now;scan_elapsed=0;scan_led.on();play_led.off();print('Rotate clockwise once, starting before index. Continue to second index.')
        elif i==5:
            if mode=='scan':mode='idle';scan_led.off();print('Scan cancelled; previous pattern preserved')
            elif seq.playing:
                seq.playing=False;amp.off();play_led.off()
                if audio:audio.deinit();audio=None
                mode='idle'
            else:
                seq.restart();seq.playing=True;audio=output();audio.write(bytes(256));amp.on();play_led.on();mode='play'
    if mode=='scan':
        # Accumulate wrap-safe elapsed milliseconds for the pure scanner.
        scan_elapsed+=ticks_diff(now,scan_last);scan_last=now
        mask=sum((sensors[i].value()<<i) for i in range(4))
        pattern=scanner.feed(scan_elapsed,bool(sensors[4].value()),bool(sensors[5].value()),mask)
        if scanner.error or scan_elapsed>30000:
            print(scanner.error or 'Scan timeout');mode='idle';scan_led.off()
        elif pattern is not None:
            seq.load(pattern);save_pattern(pattern);mode='idle';scan_led.off();print('Captured:',pattern)
        sleep_ms(1)
    elif mode=='play':
        seq.set_tempo(60+tempo.read_u16()*120//65535)
        mix.volume=volume.read_u16()/65535*.8
        events=seq.events(len(buffer)//2);mix.render(buffer,events)
        audio.write(buffer)
        # No filesystem writes during audio playback.
    else:sleep_ms(1)
except KeyboardInterrupt:pass
finally:
    amp.off();scan_led.off();play_led.off()
    if audio:audio.deinit()
