import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    data = request.json
    url = data.get('url')
    video_id = url.split("v=")[-1].split("&")[0]

    # First, attempt native YouTube transcript fetch
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript])
        return jsonify({"transcript": full_text[:3500]})
    except Exception as yt_e:
        print("Native transcript fetch failed:", yt_e)

    # If native fails, try auto-transcription via Whisper
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(filename='audio.mp4')

        # Make sure file is fully downloaded and closed before opening
        with open(audio_file, "rb") as audio:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio,
                response_format="json"
            )

        os.remove(audio_file)

        return jsonify({"transcript": transcript["text"][:3500]})

    except openai.error.OpenAIError as oe:
        print("OpenAI API Error:", oe)
        return jsonify({"error": f"OpenAI API Error: {str(oe)}"}), 400
    except Exception as e:
        print("General Exception:", e)
        return jsonify({"error": f"Auto-transcription failed: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)
