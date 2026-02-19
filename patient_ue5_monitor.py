#!/usr/bin/env python
"""
AI模擬患者システム - UE5内部UI連携版
PendingMessage を監視し、看護師音声 → LLM → TTS → リップシンク を実行

使用方法:
  1. UE5でPlayモードを開始
  2. python patient_ue5_monitor.py
  3. UE5内のチャットUIからメッセージを送信
"""

import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.6\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python')

import time
import requests
import re as regex
import subprocess
import remote_execution as re
from concurrent.futures import ThreadPoolExecutor

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

# Voice settings
PATIENT_SPEAKER_ID = _profile.get("voice_speaker_id", 11)
NURSE_SPEAKER_ID = 8      # 春日部つむぎ（女性・看護師）
PATIENT_VOLUME = 2.0      # 患者音量（1.0が標準、2.0で2倍）
NURSE_VOLUME = 1.0        # 看護師音量

# File paths
WAV_PATH = _sys_config.get("wav_output_path", "C:/UE_Projects/PatientSim56/Saved/patient_response.wav")
NURSE_WAV_PATH = _sys_config.get("nurse_wav_path", "C:/UE_Projects/PatientSim56/Saved/nurse_voice.wav")
LLM_MODEL = _sys_config.get("llm_model", "hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF:latest")
PATIENT_NAME = _profile.get("name", "啓二")
BLUEPRINT_NAME = get_blueprint_name()

# Patient system prompt
PATIENT_PROMPT = _profile.get("llm_prompt", """あなたは入院中の60歳男性患者です。
名前: 啓二
年齢: 60歳
症状: 軽い腰痛で3日前から入院中
性格: 穏やかで話し好き、少し心配性

看護師の質問に、患者として自然に会話してください。
- 具体的なエピソードや感情を交えて話す
- 2〜3文程度で答える
- 必要に応じて質問を返したり、世間話をしたりする
- 名前や役割は言わず、会話の返答だけを出力する""")


def connect_ue5():
    """UE5に接続"""
    remote = re.RemoteExecution()
    remote.start()
    time.sleep(1)

    if not remote.remote_nodes:
        print("ERROR: UE5に接続できません")
        return None

    remote.open_command_connection(remote.remote_nodes[0]['node_id'])
    return remote


def setup_ace(remote):
    """ACE リップシンクの初期設定"""
    remote.run_command('''
import unreal
unreal.ACEBlueprintLibrary.allocate_a2f3d_resources("LocalA2F-Mark")
unreal.ACEBlueprintLibrary.override_a2f3d_inference_mode(force_burst_mode=False)
unreal.ACEBlueprintLibrary.override_a2f3d_realtime_initial_chunk_size(0.2)
''', unattended=True)


def get_pending_message(remote):
    """MetaHumanのPendingMessageを取得"""
    result = remote.run_command(f'''
import unreal
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = editor_subsystem.get_game_world()
if game_world:
    for a in unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor):
        if "{BLUEPRINT_NAME}" in a.get_name():
            # Try multiple property name formats
            for prop_name in ["PendingMessage", "Pending Message", "pending_message"]:
                try:
                    msg = a.get_editor_property(prop_name)
                    if msg and str(msg).strip():
                        print("MSG:" + str(msg))
                        break
                except:
                    pass
            break
''', unattended=True)

    for item in result.get('output', []):
        if isinstance(item, dict) and 'output' in item:
            for line in item['output'].split('\n'):
                if line.startswith('MSG:'):
                    return line[4:].strip()
    return ""


def clear_pending_message(remote):
    """PendingMessageをクリア"""
    remote.run_command(f'''
import unreal
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = editor_subsystem.get_game_world()
if game_world:
    for a in unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor):
        if "{BLUEPRINT_NAME}" in a.get_name():
            for prop_name in ["PendingMessage", "Pending Message", "pending_message"]:
                try:
                    a.set_editor_property(prop_name, "")
                    break
                except:
                    pass
            break
''', unattended=True)


def set_pending_wav_path(remote, wav_path):
    """PendingWavPathを設定してリップシンクをトリガー"""
    remote.run_command(f'''
import unreal
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = editor_subsystem.get_game_world()
if game_world:
    for a in unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor):
        if "{BLUEPRINT_NAME}" in a.get_name():
            a.set_editor_property("PendingWavPath", "{wav_path}")
            break
''', unattended=True)


def set_subtitle(remote, speaker, text):
    """字幕を設定"""
    # 話者名とテキストを組み合わせ
    subtitle = f"{speaker}: {text}" if text else ""
    remote.run_command(f'''
import unreal
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = editor_subsystem.get_game_world()
if game_world:
    for a in unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor):
        if "{BLUEPRINT_NAME}" in a.get_name():
            a.set_editor_property("CurrentSubtitle", "{subtitle}")
            break
''', unattended=True)


def clear_subtitle(remote):
    """字幕をクリア"""
    set_subtitle(remote, "", "")


def generate_llm_response(user_input):
    """LLMで患者応答を生成"""
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": f"{PATIENT_PROMPT}\n\n看護師: {user_input}\n返答:",
            "stream": False
        }, timeout=60)
        text = response.json().get("response", "").strip()

        # 後処理
        text = text.split('\n')[0].strip()
        text = regex.sub(r'^(患者|' + PATIENT_NAME + r'|返答)[\(（]?[^）\)]*[\)）]?[:：]?\s*', '', text)
        text = regex.sub(r'\s*\|.*$', '', text)
        if len(text) > 200:
            text = text[:200]
        return text if text else "はい。"
    except Exception as e:
        print(f"LLM Error: {e}")
        return "すみません、よく聞こえませんでした。"


def generate_voice(text, speaker_id=None, output_path=None, volume=1.0):
    """VOICEVOXで音声生成"""
    if speaker_id is None:
        speaker_id = PATIENT_SPEAKER_ID
    if output_path is None:
        output_path = WAV_PATH
    try:
        response = requests.post(f"{VOICEVOX_URL}/audio_query?speaker={speaker_id}&text={text}")
        query = response.json()
        # 音量調整
        query['volumeScale'] = volume
        response = requests.post(f"{VOICEVOX_URL}/synthesis?speaker={speaker_id}", json=query)

        wav_path_win = output_path.replace('/', '\\')
        with open(wav_path_win, 'wb') as f:
            f.write(response.content)
        return output_path
    except Exception as e:
        print(f"VOICEVOX Error: {e}")
        return None


def play_wav_file(remote, wav_path):
    """WAVファイルを再生（Windows標準機能）"""
    wav_path_win = wav_path.replace('/', '\\')
    # winsoundはブロッキングなのでsubprocessで非同期実行
    subprocess.Popen(
        ['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path_win}").PlaySync()'],
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def generate_nurse_voice(text):
    """看護師音声を生成"""
    return generate_voice(text, NURSE_SPEAKER_ID, NURSE_WAV_PATH, NURSE_VOLUME)


def main():
    print("=" * 50)
    print("  AI模擬患者システム - UE5内部UI連携版")
    print("  (看護師音声でLLM待機時間をマスク)")
    print("=" * 50)
    print("")
    print(f"患者: {PATIENT_NAME} (Blueprint: {BLUEPRINT_NAME})")
    print(f"看護師ボイス: Speaker {NURSE_SPEAKER_ID} (春日部つむぎ) 音量:{NURSE_VOLUME}")
    print(f"患者ボイス: Speaker {PATIENT_SPEAKER_ID} 音量:{PATIENT_VOLUME}")
    print("")
    print("UE5に接続中...")

    remote = connect_ue5()
    if not remote:
        return

    print("[OK] UE5接続完了")
    print("")
    print("ACE リップシンク初期化中...")
    setup_ace(remote)
    print("[OK] ACE 初期化完了")
    print("")
    print("PendingMessage 監視開始...")
    print("UE5内のチャットUIからメッセージを送信してください")
    print("-" * 50)

    try:
        while True:
            # PendingMessageをチェック
            message = get_pending_message(remote)

            if message:
                print(f"\n看護師: {message}")

                # PendingMessageをクリア
                clear_pending_message(remote)

                # 看護師音声生成とLLM応答を並行実行
                print("[NURSE] 看護師音声生成中...")
                print("[LLM] 応答生成中...")

                with ThreadPoolExecutor(max_workers=2) as executor:
                    # 両方のタスクを同時に開始
                    nurse_future = executor.submit(generate_nurse_voice, message)
                    llm_future = executor.submit(generate_llm_response, message)

                    # 看護師音声が先に完了するのを待つ
                    nurse_wav = nurse_future.result()

                    if nurse_wav:
                        # 看護師字幕を表示
                        set_subtitle(remote, "看護師", message)
                        # 看護師音声を再生（LLMはまだ処理中）
                        print("[NURSE] 看護師音声再生中...")
                        play_wav_file(remote, nurse_wav)

                    # LLM応答を待つ
                    response_text = llm_future.result()

                print(f"{PATIENT_NAME}: {response_text}")

                # 患者音声生成
                print("[TTS] 患者音声生成中...")
                wav_path = generate_voice(response_text, PATIENT_SPEAKER_ID, WAV_PATH, PATIENT_VOLUME)

                if wav_path:
                    # 患者字幕を表示
                    set_subtitle(remote, PATIENT_NAME, response_text)
                    # リップシンクをトリガー
                    print("[LIPSYNC] リップシンク実行中...")
                    set_pending_wav_path(remote, wav_path)
                    print("[OK] 完了")

            time.sleep(0.5)  # 0.5秒ごとにチェック

    except KeyboardInterrupt:
        print("\n停止中...")
    finally:
        remote.stop()
        print("終了")


if __name__ == "__main__":
    main()
