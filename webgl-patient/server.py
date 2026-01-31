#!/usr/bin/env python
"""
WebGL模擬患者 - Flaskサーバー
LLM (Ollama ELYZA) + TTS (VOICEVOX) API

起動: python server.py
アクセス: http://localhost:8000
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
import requests
import os
import time
import uuid
import re

app = Flask(__name__, static_folder='.')

# Japanese text to viseme mapping
VOWEL_MAP = {
    'あ': 'aa', 'か': 'aa', 'さ': 'aa', 'た': 'aa', 'な': 'aa', 'は': 'aa', 'ま': 'aa', 'や': 'aa', 'ら': 'aa', 'わ': 'aa',
    'が': 'aa', 'ざ': 'aa', 'だ': 'aa', 'ば': 'aa', 'ぱ': 'aa',
    'い': 'ih', 'き': 'ih', 'し': 'ih', 'ち': 'ih', 'に': 'ih', 'ひ': 'ih', 'み': 'ih', 'り': 'ih',
    'ぎ': 'ih', 'じ': 'ih', 'ぢ': 'ih', 'び': 'ih', 'ぴ': 'ih',
    'う': 'ou', 'く': 'ou', 'す': 'ou', 'つ': 'ou', 'ぬ': 'ou', 'ふ': 'ou', 'む': 'ou', 'ゆ': 'ou', 'る': 'ou',
    'ぐ': 'ou', 'ず': 'ou', 'づ': 'ou', 'ぶ': 'ou', 'ぷ': 'ou',
    'え': 'E', 'け': 'E', 'せ': 'E', 'て': 'E', 'ね': 'E', 'へ': 'E', 'め': 'E', 'れ': 'E',
    'げ': 'E', 'ぜ': 'E', 'で': 'E', 'べ': 'E', 'ぺ': 'E',
    'お': 'oh', 'こ': 'oh', 'そ': 'oh', 'と': 'oh', 'の': 'oh', 'ほ': 'oh', 'も': 'oh', 'よ': 'oh', 'ろ': 'oh', 'を': 'oh',
    'ご': 'oh', 'ぞ': 'oh', 'ど': 'oh', 'ぼ': 'oh', 'ぽ': 'oh',
    'ん': 'sil', 'っ': 'sil',
}

def text_to_visemes(text, duration_per_char=0.12):
    """Convert Japanese text to viseme timeline"""
    import jaconv
    # Convert to hiragana
    hiragana = jaconv.kata2hira(text)

    visemes = []
    current_time = 0.0

    for char in hiragana:
        if char in VOWEL_MAP:
            visemes.append({
                'time': round(current_time, 3),
                'viseme': VOWEL_MAP[char]
            })
            current_time += duration_per_char
        elif char in 'ぁぃぅぇぉゃゅょ':
            # Small characters - shorter duration
            current_time += duration_per_char * 0.5
        elif char in '、。！？':
            # Punctuation - pause
            visemes.append({'time': round(current_time, 3), 'viseme': 'sil'})
            current_time += 0.3

    # End with silence
    visemes.append({'time': round(current_time, 3), 'viseme': 'sil'})

    return visemes

# Configuration
VOICEVOX_URL = "http://localhost:50021"
OLLAMA_URL = "http://localhost:11434"
SPEAKER_ID = 11  # 玄野武宏
LLM_MODEL = "hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF:latest"
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audio')

# Ensure audio directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# Patient system prompt
PATIENT_PROMPT = """あなたは病院に入院中の患者「啓二」です。
設定：60歳男性、腰痛で入院中。穏やかな性格。
看護師からの質問や声かけに対して、患者として短く自然に答えてください。
1〜2文で簡潔に。"""


@app.route('/')
def index():
    return send_file('index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)


@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    start = time.time()

    # 1. LLM Response
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": f"{PATIENT_PROMPT}\n\n看護師: {user_message}\n啓二:",
            "stream": False
        }, timeout=60)
        llm_response = response.json().get("response", "").strip()
        # Clean up
        llm_response = llm_response.split('\n')[0].strip()
        for prefix in ['啓二:', '患者:', '啓二：', '患者：']:
            if llm_response.startswith(prefix):
                llm_response = llm_response[len(prefix):].strip()
        llm_response = llm_response[:100]
        if not llm_response:
            llm_response = "はい。"
    except Exception as e:
        print(f"LLM Error: {e}")
        llm_response = "すみません、よく聞こえませんでした。"

    # 2. VOICEVOX TTS
    audio_url = None
    try:
        # Audio query
        query_resp = requests.post(
            f"{VOICEVOX_URL}/audio_query",
            params={"speaker": SPEAKER_ID, "text": llm_response}
        )
        query = query_resp.json()

        # Synthesis
        synth_resp = requests.post(
            f"{VOICEVOX_URL}/synthesis",
            params={"speaker": SPEAKER_ID},
            json=query
        )

        # Save audio file
        filename = f"{uuid.uuid4().hex}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(synth_resp.content)

        audio_url = f"/audio/{filename}"

        # Clean old audio files (keep last 10)
        cleanup_old_audio()

    except Exception as e:
        print(f"VOICEVOX Error: {e}")

    # 3. Generate visemes from text
    visemes = []
    try:
        visemes = text_to_visemes(llm_response)
    except Exception as e:
        print(f"Viseme Error: {e}")

    elapsed = round(time.time() - start, 2)
    print(f"[{elapsed}s] {user_message} -> {llm_response}")

    return jsonify({
        "response": llm_response,
        "audio_url": audio_url,
        "visemes": visemes,
        "time": elapsed
    })


def cleanup_old_audio():
    """Keep only the last 10 audio files"""
    try:
        files = []
        for f in os.listdir(AUDIO_DIR):
            if f.endswith('.wav'):
                path = os.path.join(AUDIO_DIR, f)
                files.append((path, os.path.getmtime(path)))

        files.sort(key=lambda x: x[1], reverse=True)

        for path, _ in files[10:]:
            os.remove(path)
    except:
        pass


if __name__ == '__main__':
    print("=" * 50)
    print("  WebGL模擬患者システム")
    print("  http://localhost:8888")
    print("=" * 50)
    print("\n必要なサービス:")
    print("  - VOICEVOX: localhost:50021")
    print("  - Ollama: localhost:11434")
    print("\nモデル (patient.glb) がない場合はデモモードで動作します")
    print("-" * 50)
    app.run(host='0.0.0.0', port=8888, debug=False)
