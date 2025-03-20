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

    # Attempt to fetch existing transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript])
        return jsonify({"transcript": full_text[:3500]})
    except:
        pass  # Continue to auto-transcribe if no transcript available

    # Auto-transcribe using Whisper if transcript unavailable
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(filename='audio.mp4')

        audio = open(audio_file, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio)
        audio.close()

        os.remove(audio_file)  # Cleanup the audio file

        return jsonify({"transcript": transcript["text"][:3500]})
    except Exception as e:
        print("Detailed error:", str(e))
        return jsonify({"error": f"Auto-transcription failed: {str(e)}"}), 400


if __name__ == '__main__':
    app.run(debug=True)
