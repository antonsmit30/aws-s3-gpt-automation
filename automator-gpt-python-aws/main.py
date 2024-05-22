import os
from utils.bot import MasterBot
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
import random
from pathlib import Path
import base64

import logging
logging.getLogger('socketio').setLevel(logging.DEBUG)
logging.getLogger('engineio').setLevel(logging.DEBUG)

client_audio_file_path = Path(__file__).parent / "data" / "audio" / "client" / "speech.webm"
client_audio_file_path.parent.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

# enable CORS
CORS(app)

master_bot = MasterBot(
        open_ai_key=os.environ.get("OPENAI_API_KEY"),
    )
print(f"master bot instance created: {master_bot}")

@app.route('/health')
def index():
    return jsonify({"message": "healthy"})

# create socketio instance
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('client')
def handle_message(message, enable_audio):
    print(f"Message: {message}")
    print(f"enable_audio: {enable_audio}")
    master_bot.enable_audio = enable_audio
    response = master_bot.speak_with_bot(message)
    print(f"Bot: {response}")
    emit('server', {"type": "text", "data": response, "bot_id": master_bot.get_random_id()}, callback=ack)
    if master_bot.enable_audio:
        emit('server', {"type": "audio", "data": master_bot.get_audio_b64(), "bot_id": master_bot.get_random_id()}, callback=ack)

@socketio.on('audio-message')
def handle_audio_message(blob, enable_audio):
    # print(f"Received an audio blob: {blob}")
    print(f"enable_audio: {enable_audio}")
    # enable audio
    master_bot.enable_audio = enable_audio
    audio_data = base64.b64decode(blob)
    with open(client_audio_file_path, "wb") as f:
        f.write(audio_data)
    # Call the bot to process the audio
    transcription = master_bot.transcribe_audio(path=client_audio_file_path)
    try:
        print(f"Transcribed audio: {transcription.text}")
        # lets emit something back on what we think the user said
        emit('user-said', {"type": "text", "data": transcription.text, "bot_id": "MaybeUser"}, callback=ack)
        # Call master bot to process the text
        response = master_bot.speak_with_bot(transcription.text)
        print(f"Bot: {response}")
        emit('server', {"type": "text", "data": response, "bot_id": master_bot.get_random_id()}, callback=ack)
        emit('server', {"type": "audio", "data": master_bot.get_audio_b64(), "bot_id": master_bot.get_random_id()}, callback=ack)
    except Exception as e:
        print(f"Error: {e}")
        emit('user-said', {"type": "text", "data": "\"Did not quite catch what you said\"", "bot_id": "MaybeUser"}, callback=ack)
    


def ack():
    print('response was receive by client!')

# enable in dev
if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True, host='0.0.0.0')
