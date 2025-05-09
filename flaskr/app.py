from flask import Flask, render_template, send_file, request, redirect, url_for, jsonify, send_from_directory
import numpy as np
import scipy.signal
import scipy.io.wavfile as wavfile
import os
import importlib.util
import json

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload')
    def upload():
        return render_template('upload.html')

    @app.route('/list')
    def uploads():
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.py')]
        file_details = []
        for file in files:
            metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], file + '.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as metadata_file:
                    metadata = json.load(metadata_file)
                    file_details.append({
                        'filename': file,
                        'username': metadata['username'],
                        'songname': metadata['songname'],
                        'recommended_bpm': metadata['recommended_bpm']
                    })
        return render_template('list.html', files=file_details)

    @app.route('/upload_waveform', methods=['POST'])
    def upload_waveform():
        if 'waveformFile' not in request.files or 'username' not in request.form or 'songname' not in request.form or 'recommended_bpm' not in request.form:
            return jsonify(success=False), 400
        file = request.files['waveformFile']
        if file.filename == '':
            return jsonify(success=False), 400
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        metadata = {
            "username": request.form['username'],
            "songname": request.form['songname'],
            "recommended_bpm": request.form['recommended_bpm']
        }
        metadata_path = file_path + '.json'
        with open(metadata_path, 'w') as metadata_file:
            json.dump(metadata, metadata_file)

        return jsonify(success=True)

    @app.route('/download_waveform/<filename>')
    def download_waveform(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    @app.route('/delete_waveform/<filename>', methods=['POST'])
    def delete_waveform(filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        metadata_path = file_path + '.json'
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        return redirect(url_for('uploads'))

    @app.route('/generate_sound', methods=['POST'])
    def generate_sound():
        bpm = int(request.form.get('bpm', 130))

        # Ensure the upload directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        file = request.files['waveformFile']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'waveform_data.py')
        file.save(file_path)

        spec = importlib.util.spec_from_file_location('waveform_data', file_path)
        waveform_data = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(waveform_data)

        melody = waveform_data.melody
        base = waveform_data.base
        base2 = waveform_data.base2
        noise_sections = waveform_data.noise_sections

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
                frequency = base_frequency * 2**((semitone+3) / 12.0)
                note_wave = sawtooth_wave(frequency, duration, amplitude=melody_amplitude)
                melody_wave = np.concatenate([melody_wave, note_wave])

            for semitone, length in base:
                duration = note_duration(bpm, length)
                frequency = base_frequency * 2**((semitone+3) / 12.0)
                note_wave = square_wave(frequency, duration, amplitude=base_amplitude)
                base_wave = np.concatenate([base_wave, note_wave])

            for semitone, length in base2:
                duration = note_duration(bpm, length)
                frequency = base_frequency * 2**((semitone+3) / 12.0)
                note_wave = square_wave(frequency, duration, amplitude=base2_amplitude)
                base2_waveform = np.concatenate([base2_waveform, note_wave])

            for semitone, length in noise_sections:
                if semitone is not None:
                    duration = note_duration(bpm, length)
                    noise_section = white_noise(duration, amplitude=noise_amplitude, sampling_rate=sampling_rate)
                    noise_wave = np.concatenate([noise_wave, noise_section])
                else:
                    duration = note_duration(bpm, length)
                    silence_section = silence(duration, sampling_rate=sampling_rate)
                    noise_wave = np.concatenate([noise_wave, silence_section])

            return base_wave, melody_wave, base2_waveform, noise_wave

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
        wavfile.write('sound.wav', 44100, final_wave.astype(np.float32))

        return send_file('sound.wav', as_attachment=True)

    return app

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('flaskr'):
        os.makedirs('flaskr')
    app = create_app()
    app.run(debug=True)










