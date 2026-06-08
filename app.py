from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file received'}), 400

    audio_file = request.files['audio']

    # Save the uploaded webm audio
    webm_path = 'temp_audio.webm'
    wav_path  = 'temp_audio.wav'
    audio_file.save(webm_path)

    # Convert webm to wav using ffmpeg
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-i', webm_path, wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Audio conversion failed. Is ffmpeg installed?'}), 500

    # Recognize speech in Marathi
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language='mr-IN')
        return jsonify({'text': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'बोलणे ओळखता आले नाही. पुन्हा बोला.'}), 200
    except sr.RequestError as e:
        return jsonify({'error': f'Google API error: {str(e)}'}), 500
    finally:
        # Cleanup temp files
        if os.path.exists(webm_path): os.remove(webm_path)
        if os.path.exists(wav_path):  os.remove(wav_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)