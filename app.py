import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube
import openai
from openai import OpenAIError

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    data = request.json
    url = data.get('url')

    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(filename='audio.mp4')

        with open(audio_file, "rb") as audio:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio,
                response_format="json"
            )

        os.remove(audio_file)

        return jsonify({"transcript": transcript["text"][:3500]})

    except OpenAIError as oe:
        print("OpenAI API Error:", oe)
        return jsonify({"error": f"OpenAI API Error: {str(oe)}"}), 400
    except Exception as e:
        print("General Exception:", e)
        return jsonify({"error": f"Auto-transcription failed: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)
