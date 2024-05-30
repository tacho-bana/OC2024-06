import numpy as np
import scipy.signal
import sounddevice as sd
from scipy.io.wavfile import write
import ipywidgets as widgets
from IPython.display import display

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

def read_data_from_file(file_content):
    sections = {'melody': [], 'base': [], 'base2': []}
    current_section = None

    for line in file_content.decode().splitlines():
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
        elif current_section in sections:
            sections[current_section].append(list(map(int, line.split(','))))

    return sections['melody'], sections['base'], sections['base2']

# File uploader widget
uploader = widgets.FileUpload(accept='.txt', multiple=False)
display(uploader)

def on_upload_change(change):
    if uploader.value:
        file_content = list(uploader.value.values())[0]['content']
        melody, base, base2 = read_data_from_file(file_content)
        
        # Input BPM from the user
        bpm = int(input("Enter the BPM: "))

        # Noise sections
        noise_sections = [0.1, 30]

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

uploader.observe(on_upload_change, names='value')
