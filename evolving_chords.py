from pyo import *

s = Server().boot()
s.start()

# Metronome
met = Metro(2).play()

# Chords - due t o iter, the individual chords are transposed
root = [midiToHz(m) for m in [60,60,60,58]]
third = [midiToHz(m) for m in [63,63,63,62]]
fifth = [midiToHz(m) for m in [67.01,68,67.01,67.01]]
chords = [root, third, fifth]

# Chord progression
iter = Iter(met, choice=chords)

# Portamento
#port_lfo = Sine(freq=10, add=100, mul=10000)
port = Port(iter, risetime=0.2, falltime=0.5)

# LFO
lfo1 = LFO(freq=1, type=7, mul=100, add=300)
lfo2 = LFO(freq=lfo1, sharp=lfo1, type=3, mul=1)

# Super Saw
saw = SuperSaw(freq=port, detune=lfo2)

# IRPulse filter (comb-like)
rco = RCOsc(freq=100, sharp=0.1, mul=0.2)
fm = FM(carrier=[0.2,0.3], ratio=[0.2498, 0.2503], index=met, mul=0.7)
chen = ChenLee(pitch=0.001, chaos=0.2*lfo1, stereo=True, mul=.5, add=1)
irp = IRPulse(saw, freq=[110*rco, 220*fm], bw=2500*chen, type=2, order=256)

# ResonX
lfo3 = Sine(freq=[0.2,0.25], mul=1000, add=1500)
res = Resonx(irp, freq=0.3*lfo3, q=2)
filter1 = MoogLP(res, freq=560, res=0.5).out()

# ComplexRes
c_min = [midiToHz(m) for m in [60, 63, 67]]
res2 = (ComplexRes(irp, freq=port) * 0.03 * chen )
filter2 = MoogLP(res2, freq=280, res=0.5).out()

# Melody
melody = [midiToHz(m) for m in [58,60,62,63,67.01,68]]
scale_down = [m/2 for m in melody]
scale_up = [m*2 for m in melody]
mel_env = HannTable()
mel_trig = TrigEnv(met, table=mel_env, dur=0.65, mul=0.3)
chx = Choice(choice=melody, freq=[2,4])
sin = SineLoop(freq=chx, feedback=0.2, mul=0.1*mel_trig)
delayed = Delay(sin, delay=[1,2], feedback=0.5, mul=0.5)
w = Waveguide(delayed, freq=scale_down + scale_up, dur=15, minfreq=20, mul=0.1).out()
shift = FreqShift(w, shift=lfo3, mul=0.2).out()

# Bass
bass_met = Metro(4).play(delay=16)
bass_notes = [m / 4 for m in scale_down]
bass_env = CosTable([(0,0),(1000,1),(3000,0.5),(6000,0.1),(8191,0)])
bass_trig = TrigEnv(bass_met, table=bass_env, dur=4, mul=0.35)
bass_melody = Choice(choice=bass_notes, freq=0.25)
sub_bass = Sine(freq=bass_melody, mul=1.5*bass_trig).mix(2).out()
saw_bass = SuperSaw(freq=bass_melody, detune=0, bal=0.3, mul=bass_trig).mix(2)
lfo_chorus = LFO(freq=0.005, type=3, add=1.3)
chorus = Chorus(saw_bass, depth=4*lfo_chorus, feedback=0.5*lfo_chorus).out()

# GUI
s.gui(locals())