#!/usr/bin/env python
"""
患者会話システム（連続リップシンク対応版）
LLM(ELYZA) -> VOICEVOX -> Audio2Face -> MetaHuman

使用方法:
  1. UE5でPlayモードを開始
  2. python patient_conversation.py
  3. 看護師として話しかける

終了: q を入力

注意: Blueprint Async API (PendingWavPath変数方式) を使用
"""

import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.6\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python')
import remote_execution as re
import requests
import time

# 共通設定モジュール
from patient_config import (
    get_metahuman_config,
    get_patient_profile,
    get_system_config,
    get_blueprint_name
)

# 設定読み込み
_sys_config = get_system_config()
_profile = get_patient_profile()
_mh_config = get_metahuman_config()

VOICEVOX_URL = _sys_config.get("voicevox_url", "http://localhost:50021")
OLLAMA_URL = _sys_config.get("ollama_url", "http://localhost:11434")
SPEAKER_ID = _profile.get("voice_speaker_id", 11)
WAV_PATH = _sys_config.get("wav_output_path", "C:/UE_Projects/PatientSim56/Saved/patient_response.wav")
LLM_MODEL = _sys_config.get("llm_model", "hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF:latest")
PATIENT_NAME = _profile.get("name", "啓二")
BLUEPRINT_NAME = get_blueprint_name()

# Patient system prompt
PATIENT_PROMPT = _profile.get("llm_prompt", f"""あなたは病院に入院中の患者「{PATIENT_NAME}」です。
看護師の質問に対して、自然で短い日本語で答えてください。
1〜2文で簡潔に回答してください。""")

def generate_llm_response(user_input):
    """Generate patient response using ELYZA"""
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": f"{PATIENT_PROMPT}\n\n看護師: {user_input}\n患者({PATIENT_NAME}):",
            "stream": False
        }, timeout=60)
        text = response.json().get("response", "").strip()
        # Clean up - take first meaningful response
        text = text.split('\n')[0].strip()
        if len(text) > 100:
            text = text[:100]
        return text if text else "はい。"
    except Exception as e:
        print(f"LLM Error: {e}")
        return "すみません、よく聞こえませんでした。"

def generate_voice(text):
    """Generate voice using VOICEVOX"""
    try:
        # Audio query
        response = requests.post(f"{VOICEVOX_URL}/audio_query?speaker={SPEAKER_ID}&text={text}")
        query = response.json()

        # Synthesis
        response = requests.post(f"{VOICEVOX_URL}/synthesis?speaker={SPEAKER_ID}", json=query)
        with open(WAV_PATH, 'wb') as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"VOICEVOX Error: {e}")
        return False

def run_lipsync(remote, wav_path):
    """Run lipsync animation using PendingWavPath variable (Blueprint Async API)"""
    # Normalize path for UE5 (use forward slashes)
    wav_path_ue = wav_path.replace('\\', '/')

    result = remote.run_command(f'''
import unreal

editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = editor_subsystem.get_game_world()

character = None
if game_world:
    actors = unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor)
    for a in actors:
        if "{BLUEPRINT_NAME}" in a.get_name():
            character = a
            break

if character:
    # Set PendingWavPath variable - Blueprint will handle the rest
    character.set_editor_property("PendingWavPath", "{wav_path_ue}")
    print("Lipsync triggered: " + character.get_name())
else:
    print("Character not found! ({BLUEPRINT_NAME})")
    print("Make sure UE5 is in Play mode.")
''', unattended=True)
    return result

def main():
    print("=" * 50)
    print(f"  患者会話システム - {PATIENT_NAME}")
    print("  LLM -> VOICEVOX -> Audio2Face -> MetaHuman")
    print("=" * 50)
    print("")
    print(f"患者: {PATIENT_NAME} (Blueprint: {BLUEPRINT_NAME})")
    print(f"Voice Speaker ID: {SPEAKER_ID}")
    print("")

    # Connect to UE5
    print("UE5に接続中...")
    remote = re.RemoteExecution()
    remote.start()
    time.sleep(1)

    if not remote.remote_nodes:
        print("ERROR: UE5に接続できません。エディタを開いてください。")
        return

    remote.open_command_connection(remote.remote_nodes[0]['node_id'])

    # Configure ACE
    remote.run_command('''
import unreal
unreal.ACEBlueprintLibrary.allocate_a2f3d_resources("LocalA2F-Mark")
unreal.ACEBlueprintLibrary.override_a2f3d_inference_mode(force_burst_mode=False)
unreal.ACEBlueprintLibrary.override_a2f3d_realtime_initial_chunk_size(0.2)
''', unattended=True)

    print("準備完了！看護師として話しかけてください。")
    print("終了するには 'q' を入力")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n看護師> ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() == 'q':
            break
        if not user_input:
            continue

        start_total = time.time()

        # Step 1: LLM Response
        response = generate_llm_response(user_input)
        llm_time = time.time() - start_total

        print(f"{PATIENT_NAME}: {response}")

        # Step 2: Voice Generation
        if generate_voice(response):
            voice_time = time.time() - start_total - llm_time

            # Step 3: Lipsync (using PendingWavPath variable)
            run_lipsync(remote, WAV_PATH)

            total_time = time.time() - start_total
            print(f"  [{total_time:.1f}秒]")

    remote.stop()
    print("\n終了しました。")

if __name__ == "__main__":
    main()
