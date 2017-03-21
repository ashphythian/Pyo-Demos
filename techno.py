from pyo import *

s = Server().boot()
s.start()

bpm = 125

# Metronomes
bar_met = Metro(bpm/60.0).play()
four_bar_met = Metro(bpm/15).play()
kick_met = Metro(bpm/240.0).play()
offbeat_met = Metro(bpm/480.0).play()

# Counters
kick_counter = Counter(kick_met, min=0, max=4)
offbeat_counter = Counter(offbeat_met, min=0, max=8)
offbeat = Select(offbeat_counter % 2, 1)
offbeat_2 = Select(offbeat_counter % 2, 1)

# Timings
beat_s = 60/125.0
bar_s = beat_s * 4
four_bar_s = bar_s * 4

# Kick
kick_env = CosTable([(0,0),(10,1),(1000,0.5),(8191,0)])
kick_trigger = TrigEnv(kick_met, table=kick_env, dur=0.45, mul=0.5)
kick = Sine(freq=61, mul=kick_trigger).mix(2).out()

# Open Hi-hat
hat_env = LinTable([(0,0),(100,1),(800,0.7),(8191,0)])
hat_trigger = TrigEnv(offbeat, hat_env, dur=0.2, mul=0.3)
open_hat = (Noise(0.1).mix(2) * hat_trigger).out()

# Closed Hi-hats
hat_2_env = CosTable([(0,0),(100,1),(200,0.1),(800,0)])
hat_2_pattern = Beat(time=bpm/960.0, taps=16, w1=0, w2=40, w3=60).play()
hat_2_trigger = TrigEnv(hat_2_pattern, hat_2_env)
closed_hat = (Noise(0.03).mix(2) * hat_2_trigger).out()

# Bass
bass_mid = TrigXnoiseMidi(offbeat_counter, dist=12, mrange=(38,48))
bass_hz = Snap(bass_mid, choice=[0,2,3], scale=1)
bass_env = CosTable([(0,0),(500,1),(1000,0.8),(8191,0)])
bass_trigger = TrigEnv(offbeat_2, bass_env, dur=0.4, mul=0.3)
bassline = SumOsc(freq=[bass_hz,bass_hz-1], ratio=[0.2498, 0.2503], index=bass_trigger, mul=bass_trigger).out()

# Chord
chord_count = Counter(kick_met, min=0, max=8)
chord_start = Select(chord_count, 4)
chord_trigger = NextTrig(bar_met, chord_start)
chord_env = CosTable([(0,0),(3000,1),(4000,0.5),(5500,0.6),(8191,0)])
melody = [midiToHz(m) for m in [48,50,51.93,53,55.01,57,59,60]]
dur = RandDur(min=bpm/240.0, max=bpm/120.0)
amp = TrigEnv(chord_trigger, table=chord_env, dur=dur, mul=0.5)
saw = SuperSaw(freq=melody, detune=0.65, bal=0.7, mul=amp)
filter = MoogLP(saw, freq=880, res=0.5)
delayed = Delay(filter, delay=[bpm/240.0,bpm/480.0], feedback=0.3, mul=0.5).out()

# Chord 2
chord_env_2 = CosTable([(0,0),(3000,0.4),(5000,1),(5500,0.6),(8191,0)])
melody_2 = [x/2 for x in melody]
dur_2 = RandDur(min=bpm/180.0, max=bpm/120.0)
amp_2 = TrigEnv(four_bar_met, table=chord_env_2, dur=dur_2, mul=0.3)
saw_2 = SuperSaw(freq=melody_2, detune=0.8, bal=0.7, mul=amp_2)
filter_2 = MoogLP(saw_2, freq=770, res=0.8)
delayed_2 = Delay(filter_2, delay=[bpm/240.0,bpm/480.0], feedback=0.3, mul=0.2)
dist_chords = Disto(delayed_2).out()

# Bass2
t = CosTable([(0,0),(100,1),(500,.3),(8191,0)])
#melody_pattern = Beat(time=bpm/960.0, taps=16, w1=60, w2=10, w3=50, poly=1).play(delay=four_bar_s)
melody_pattern = Beat(time=bpm/960.0, taps=16, w1=60, w2=10, w3=50, poly=1).play(delay=7.68)
trmid = TrigXnoiseMidi(melody_pattern, dist=12, mrange=(48,60))
trhz = Snap(trmid, choice=[0,3], scale=1)
tr2 = TrigEnv(melody_pattern, table=t, dur=melody_pattern['dur'], mul=melody_pattern['amp'])
f = FM(carrier=trhz, ratio=[0.2498, 0.2503], index=tr2, mul=tr2*0.3)
dist = Disto(f, drive=0.85, mul=0.2,).out()

# Atmohere
snd = SndTable(SNDS_PATH + '/transparent.aif')
env = HannTable()
pos = Phasor(snd.getRate()*0.25, 0, snd.getSize())
dur = Noise(0.001, 0.01)
g = Granulator(snd, env, [1, 1.001], pos, dur, 24, mul=0.05, basedur=0.1).out()

# Blit
blit_env = CosTable([(0,0),(100,1),(200,0.1),(800,0)])
blit_pattern = Beat(time=bpm/960.0, taps=16, w1=20, w2=20, w3=30).play(delay=2*four_bar_s)
blit_trigger = TrigEnv(blit_pattern, blit_env)
lfo = Sine(freq=4, mul=.02, add=1)
lfo2 = Sine(freq=.25, mul=10, add=30)
blit = Blit(freq=[100,99.7]*lfo, harms=lfo2, mul=.2*blit_trigger).out()

# GUI
s.gui(locals())