from flask import Flask, request, jsonify
from flask_cors import CORS
from livekit import api
import os
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

LIVEKIT_API_KEY = os.getenv('LIVEKIT_API_KEY')
LIVEKIT_API_SECRET = os.getenv('LIVEKIT_API_SECRET')
LIVEKIT_URL = os.getenv('LIVEKIT_URL', 'wss://szabolcslevai.com:7880')
LIVEKIT_PUBLIC_URL = os.getenv('LIVEKIT_PUBLIC_URL', 'wss://szabolcslevai.com:7882')

@app.route('/token')
def get_token():
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return jsonify({"error": "API key or secret not configured"}), 500
    room_name = os.environ.get('ROOM_NAME', 'default')
    
    try:
        token = (
            api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            .with_identity("web_client")
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True
            ))
            .to_jwt()
        )
        
        return jsonify({
            "token": token,
            "url": LIVEKIT_PUBLIC_URL
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)