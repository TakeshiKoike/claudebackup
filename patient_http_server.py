#!/usr/bin/env python
"""
AI模擬患者 HTTPサーバー
UE5 BlueprintからHTTPリクエストを受けてLLM応答を返す

使用方法:
  1. python patient_http_server.py
  2. UE5のBlueprintからHTTPリクエストを送信

エンドポイント:
  POST http://localhost:8080/chat
  Body: {"message": "看護師のメッセージ"}
  Response: {"response": "患者の応答", "wav_path": "音声ファイルパス"}
"""

import http.server
import json
import requests
import re as regex
import sys
import os

# Add UE5 Python path
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.6\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python')

# Configuration
VOICEVOX_URL = "http://localhost:50021"
OLLAMA_URL = "http://localhost:11434"
SPEAKER_ID = 11  # 玄野武宏
WAV_PATH = "C:/UE_Projects/PatientSim56/Saved/patient_response.wav"
LLM_MODEL = "hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF:latest"
SERVER_PORT = 8080

# Patient prompt
PATIENT_PROMPT = """あなたは入院中の60歳男性患者です。名前は啓二。軽い腰痛で入院しています。
看護師の質問に、患者として自然に短く答えてください。
名前や役割は言わず、会話の返答だけを出力してください。"""


def generate_llm_response(user_input):
    """Generate patient response using ELYZA"""
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": f"{PATIENT_PROMPT}\n\n看護師: {user_input}\n返答:",
            "stream": False
        }, timeout=60)
        text = response.json().get("response", "").strip()

        # 後処理
        text = text.split('\n')[0].strip()
        text = regex.sub(r'^(患者|啓二|返答)[\(（]?[^）\)]*[\)）]?[:：]?\s*', '', text)
        text = regex.sub(r'\s*\|.*$', '', text)
        if len(text) > 100:
            text = text[:100]
        return text if text else "はい。"
    except Exception as e:
        print(f"LLM Error: {e}")
        return "すみません、よく聞こえませんでした。"


def generate_voice(text):
    """Generate voice using VOICEVOX"""
    try:
        response = requests.post(f"{VOICEVOX_URL}/audio_query?speaker={SPEAKER_ID}&text={text}")
        query = response.json()
        response = requests.post(f"{VOICEVOX_URL}/synthesis?speaker={SPEAKER_ID}", json=query)

        wav_path_win = WAV_PATH.replace('/', '\\')
        with open(wav_path_win, 'wb') as f:
            f.write(response.content)
        return WAV_PATH
    except Exception as e:
        print(f"VOICEVOX Error: {e}")
        return None


class PatientHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')

                print(f"看護師: {message}")

                # Generate LLM response
                response_text = generate_llm_response(message)
                print(f"啓二: {response_text}")

                # Generate voice
                wav_path = generate_voice(response_text)

                # Send response
                result = {
                    'response': response_text,
                    'wav_path': wav_path if wav_path else ''
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

            except Exception as e:
                print(f"Error: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # カスタムログ
        pass


def main():
    print("=" * 50)
    print("  AI模擬患者 HTTPサーバー")
    print("=" * 50)
    print(f"ポート: {SERVER_PORT}")
    print(f"エンドポイント: POST http://localhost:{SERVER_PORT}/chat")
    print("")
    print("UE5 Blueprintから接続してください")
    print("停止するには Ctrl+C")
    print("-" * 50)

    server = http.server.HTTPServer(('localhost', SERVER_PORT), PatientHTTPHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバー停止")
        server.shutdown()


if __name__ == "__main__":
    main()
