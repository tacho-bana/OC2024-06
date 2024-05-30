import numpy as np
import scipy.signal
import sounddevice as sd
from scipy.io.wavfile import write


def square_wave(frequency, duration, amplitude=0.5, sampling_rate=44100):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
    return wave

def sawtooth_wave(frequency, duration, amplitude=0.5, sampling_rate=44100):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    wave = amplitude * scipy.signal.sawtooth(2 * np.pi * frequency * t)
    return wave

def white_noise(duration, amplitude=1.0, sampling_rate=44100):
    noise = amplitude * (np.random.rand(int(sampling_rate * duration)) * 2 - 1)
    return noise

def silence(duration, sampling_rate=44100):
    return np.zeros(int(sampling_rate * duration))

def note_duration(bpm, note_length):
    return 60 / bpm / note_length

def generate_waveforms(melody, base, base2, noise_sections, bpm=120, melody_amplitude=0.5, base_amplitude=0.4, base2_amplitude=0.4, noise_amplitude=1.0, base_frequency=100, sampling_rate=44100):
    melody_wave = np.array([])
    base_wave = np.array([])
    base2_waveform = np.array([])
    noise_wave = np.array([])

    for semitone, length in melody:
        duration = note_duration(bpm, length)
        frequency = base_frequency * 2**(semitone / 12.0)
        note_wave = sawtooth_wave(frequency, duration, amplitude=melody_amplitude)
        melody_wave = np.concatenate([melody_wave, note_wave])

    for semitone, length in base:
        duration = note_duration(bpm, length)
        frequency = base_frequency * 2**(semitone / 12.0)
        note_wave = square_wave(frequency, duration, amplitude=base_amplitude)
        base_wave = np.concatenate([base_wave, note_wave])

    for semitone, length in base2:
        duration = note_duration(bpm, length)
        frequency = base_frequency * 2**(semitone / 12.0)
        note_wave = square_wave(frequency, duration, amplitude=base2_amplitude)
        base2_waveform = np.concatenate([base2_waveform, note_wave])

    for i in range(0, len(noise_sections), 2):
        noise_duration = noise_sections[i]
        silence_duration = noise_sections[i+1] if i+1 < len(noise_sections) else 0

        noise_section = white_noise(noise_duration, amplitude=noise_amplitude, sampling_rate=sampling_rate)
        silence_section = silence(silence_duration, sampling_rate=sampling_rate)

        noise_wave = np.concatenate([noise_wave, noise_section, silence_section])

    return base_wave, melody_wave, base2_waveform, noise_wave

# Sample input data
melody = [[26, 2], [21, 2], [26, 2], [33, 1], [31, 2], [-100, 2], [30, 2], [28, 2], [25, 2], [-100, 1],
          [21, 2], [-100, 2], [16, 2], [-100, 2], [25, 2], [21, 2], [25, 2], [30, 1], [28, 2], [-100, 2],
          [25, 2], [26, 2], [30, 2], [-100, 1], [21, 2], [-100, 2], [16, 2], [-100, 2], [26, 2], [21, 2],
          [26, 2], [33, 1], [31, 2], [-100, 2], [30, 2], [28, 2], [25, 2], [-100, 1], [21, 2], [-100, 2],
          [16, 2], [-100, 2], [25, 2], [21, 2], [25, 2], [30, 1], [28, 2], [-100, 2], [25, 2], [26, 2],
          [-100, 1], [14, 2], [-100, 2], [16, 2], [-100, 1], [30, 1], [-100, 1], [33, 1], [-100, 1], [31, 2],
          [33, 2], [31, 2], [30, 2], [28, 1], [-100, 1], [25, 1], [-100, 1], [28, 1], [-100, 1], [30, 2],
          [31, 2], [30, 2], [28, 2], [26, 1], [-100, 1], [30, 1], [-100, 1], [33, 1], [-100, 1], [31, 2],
          [30, 2], [31, 2], [33, 2], [35, 1], [-100, 1], [33, 2], [-100, 2], [31, 2], [30, 2], [31, 1],
          [-100, 1], [30, 2], [31, 2], [30, 2], [28, 2], [26, 1], [-100, 1]]

base = [[18, 2], [16, 2], [18, 2], [26, 1], [25, 2], [23, 2], [21, 2], [23, 2], [21, 2], [19, 2],
        [18, 2], [16, 2], [18, 2], [19, 2], [21, 2], [21, 2], [16, 2], [21, 2], [25, 1], [23, 2],
        [21, 2], [19, 2], [18, 2], [21, 2], [23, 2], [25, 2], [26, 2], [25, 2], [23, 2], [21, 2],
        [18, 2], [16, 2], [18, 2], [26, 1], [25, 2], [23, 2], [21, 2], [23, 2], [21, 2], [19, 2],
        [18, 2], [16, 2], [18, 2], [19, 2], [21, 2], [21, 2], [16, 2], [21, 2], [25, 1], [23, 2],
        [21, 2], [19, 2], [18, 2], [16, 2], [14, 2], [16, 2], [18, 2], [19, 2], [21, 2], [23, 2],
        [18, 2], [16, 2], [14, 2], [-100, 2], [16, 2], [18, 2], [19, 2], [21, 2], [23, 2], [21, 2],
        [19, 2], [-100, 2], [16, 2], [18, 2], [19, 2], [21, 2], [19, 2], [18, 2], [16, 2], [-100, 2],
        [13, 2], [14, 2], [16, 2], [19, 2], [16, 2], [19, 2], [21, 2], [23, 2], [21, 1], [-100, 1],
        [26, 2], [25, 2], [23, 2], [-100, 2], [21, 2], [23, 2], [25, 2], [26, 2], [28, 2], [26, 2],
        [25, 2], [-100, 2], [23, 2], [25, 2], [26, 2], [28, 2], [25, 2], [23, 2], [21, 2], [-100, 2],
        [19, 2], [21, 2], [23, 2], [19, 2], [21, 2], [19, 2], [18, 2], [16, 2], [14, 2], [16, 2],
        [18, 2], [19, 2]]

base2 = [[2, 2], [6, 2], [2, 2], [6, 2], [2, 2], [6, 2], [7, 2], [6, 2], [4, 2], [9, 2], [4, 2], [9, 2],
         [4, 2], [9, 2], [4, 2], [9, 2], [4, 2], [9, 2], [4, 2], [9, 2], [4, 2], [9, 2], [7, 2], [9, 2],
         [6, 2], [9, 2], [6, 2], [9, 2], [6, 2], [9, 2], [7, 2], [9, 2], [2, 2], [6, 2], [2, 2], [6, 2],
         [2, 2], [6, 2], [7, 2], [6, 2], [4, 2], [9, 2], [4, 2], [9, 2], [4, 2], [9, 2], [4, 2], [9, 2],
         [4, 2], [9, 2], [4, 2], [9, 2], [4, 2], [9, 2], [7, 2], [9, 2], [2, 2], [6, 2], [2, 2], [6, 2],
         [2, 2], [9, 2], [7, 2], [6, 2], [6, 2], [9, 2], [6, 2], [9, 2], [6, 2], [9, 2], [6, 2], [9, 2],
         [7, 2], [11, 2], [7, 2], [11, 2], [7, 2], [11, 2], [7, 2], [11, 2], [4, 2], [7, 2], [4, 2], [7, 2],
         [4, 2], [7, 2], [4, 2], [7, 2], [4, 2], [7, 2], [4, 2], [7, 2], [4, 2], [7, 2], [4, 2], [7, 2],
         [6, 2], [9, 2], [6, 2], [9, 2], [6, 2], [9, 2], [6, 2], [9, 2], [7, 2], [11, 2], [7, 2], [11, 2],
         [7, 2], [11, 2], [7, 2], [11, 2], [4, 2], [7, 2], [4, 2], [7, 2], [4, 2], [7, 2], [4, 2], [7, 2],
         [4, 2], [7, 2], [4, 2], [7, 2], [4, 2], [7, 2], [4, 2], [7, 2]]
noise_sections = [0.1, 30]

# BPM
bpm = 200

# Generate waveforms
base_wave, melody_wave, base2_waveform, noise_wave = generate_waveforms(melody, base, base2, noise_sections, bpm)

# Ensure all waveforms are of the same length
min_length = min(len(base_wave), len(melody_wave), len(base2_waveform), len(noise_wave))
base_wave = base_wave[:min_length]
melody_wave = melody_wave[:min_length]
base2_waveform = base2_waveform[:min_length]
noise_wave = noise_wave[:min_length]

# Combine all waveforms
final_wave = base_wave + melody_wave + base2_waveform + noise_wave

# Save the combined waveform as a WAV file
write("output.wav", 44100, final_wave.astype(np.float32))

# Play the audio
sd.play(final_wave, 44100)
sd.wait()  # Wait until the sound has finished playing
