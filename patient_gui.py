#!/usr/bin/env python
"""
AI模擬患者システム - GUI版
LLMリアルタイムリップシンクによる患者表現

使用方法:
  1. UE5でPlayモードを開始
  2. python patient_gui.py
  3. テキストを入力して送信
"""

import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.6\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python')

import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import requests
import time
import re as regex
import remote_execution as re

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
PATIENT_PROMPT = _profile.get("llm_prompt", """あなたは入院中の60歳男性患者です。名前は啓二。軽い腰痛で入院しています。
看護師の質問に、患者として自然に短く答えてください。
名前や役割は言わず、会話の返答だけを出力してください。""")


class PatientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"AI模擬患者システム - {PATIENT_NAME}")
        self.root.geometry("600x500")
        self.root.configure(bg='#2b2b2b')

        # UE5 connection
        self.remote = None
        self.connected = False

        self.setup_ui()
        self.connect_ue5()

    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Title
        title_frame = tk.Frame(self.root, bg='#1e5128')
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="🏥 AI模擬患者システム",
                               font=('Arial', 16, 'bold'), fg='white', bg='#1e5128', pady=10)
        title_label.pack()

        # Status
        self.status_var = tk.StringVar(value="接続中...")
        status_label = tk.Label(self.root, textvariable=self.status_var,
                                font=('Arial', 10), fg='#aaa', bg='#2b2b2b')
        status_label.pack(pady=5)

        # Chat display
        chat_frame = tk.Frame(self.root, bg='#2b2b2b')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, font=('Arial', 11),
            bg='#1e1e1e', fg='white', insertbackground='white',
            state=tk.DISABLED, height=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colors
        self.chat_display.tag_configure('nurse', foreground='#5dade2')
        self.chat_display.tag_configure('patient', foreground='#58d68d')
        self.chat_display.tag_configure('system', foreground='#aaa')
        self.chat_display.tag_configure('time', foreground='#888')

        # Input frame
        input_frame = tk.Frame(self.root, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.input_entry = tk.Entry(
            input_frame, font=('Arial', 12),
            bg='#3c3c3c', fg='white', insertbackground='white'
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.on_send)

        self.send_button = tk.Button(
            input_frame, text="送信", font=('Arial', 11, 'bold'),
            bg='#1e5128', fg='white', padx=20, pady=5,
            command=self.on_send
        )
        self.send_button.pack(side=tk.RIGHT)

        # Processing indicator
        self.processing_var = tk.StringVar(value="")
        processing_label = tk.Label(self.root, textvariable=self.processing_var,
                                    font=('Arial', 10), fg='#f39c12', bg='#2b2b2b')
        processing_label.pack(pady=5)

    def connect_ue5(self):
        """Connect to UE5"""
        def do_connect():
            try:
                self.remote = re.RemoteExecution()
                self.remote.start()
                time.sleep(1)

                if self.remote.remote_nodes:
                    self.remote.open_command_connection(self.remote.remote_nodes[0]['node_id'])

                    # Configure ACE
                    self.remote.run_command('''
import unreal
unreal.ACEBlueprintLibrary.allocate_a2f3d_resources("LocalA2F-Mark")
unreal.ACEBlueprintLibrary.override_a2f3d_inference_mode(force_burst_mode=False)
unreal.ACEBlueprintLibrary.override_a2f3d_realtime_initial_chunk_size(0.2)
''', unattended=True)

                    self.connected = True
                    self.status_var.set("✓ UE5接続完了 - Playモードで動作中")
                    self.add_message("システム", "接続完了。看護師として話しかけてください。", 'system')
                else:
                    self.status_var.set("✗ UE5に接続できません - エディタを確認してください")
                    self.add_message("システム", "UE5に接続できません。エディタを開いてPlayモードを開始してください。", 'system')
            except Exception as e:
                self.status_var.set(f"✗ エラー: {str(e)}")

        threading.Thread(target=do_connect, daemon=True).start()

    def add_message(self, sender, message, tag):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'time')
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{message}\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def on_send(self, event=None):
        """Handle send button click"""
        user_input = self.input_entry.get().strip()
        if not user_input:
            return

        self.input_entry.delete(0, tk.END)
        self.add_message("看護師", user_input, 'nurse')

        # Disable input during processing
        self.input_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

        # Process in background thread
        threading.Thread(target=self.process_conversation, args=(user_input,), daemon=True).start()

    def process_conversation(self, user_input):
        """Process conversation: LLM -> TTS -> Lipsync"""
        try:
            start_total = time.time()

            # Step 1: LLM Response
            self.processing_var.set("🤔 LLM応答生成中...")
            response_text = self.generate_llm_response(user_input)
            llm_time = time.time() - start_total

            # Step 2: Voice Generation
            self.processing_var.set("🎤 音声生成中...")
            voice_start = time.time()
            self.generate_voice(response_text)
            voice_time = time.time() - voice_start

            # Step 3: Lipsync
            self.processing_var.set("👄 リップシンク実行中...")
            self.run_lipsync()

            total_time = time.time() - start_total

            # Update UI
            self.root.after(0, lambda: self.add_message(PATIENT_NAME, response_text, 'patient'))
            self.root.after(0, lambda: self.add_message("",
                f"[LLM: {llm_time:.1f}秒 / 音声: {voice_time:.1f}秒 / 合計: {total_time:.1f}秒]", 'system'))

        except Exception as e:
            self.root.after(0, lambda: self.add_message("エラー", str(e), 'system'))
        finally:
            self.root.after(0, self.enable_input)
            self.root.after(0, lambda: self.processing_var.set(""))

    def enable_input(self):
        """Re-enable input controls"""
        self.input_entry.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.input_entry.focus()

    def generate_llm_response(self, user_input):
        """Generate patient response using ELYZA"""
        try:
            response = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": LLM_MODEL,
                "prompt": f"{PATIENT_PROMPT}\n\n看護師: {user_input}\n返答:",
                "stream": False
            }, timeout=60)
            text = response.json().get("response", "").strip()
            # 後処理: 不要な部分を除去
            text = text.split('\n')[0].strip()
            text = regex.sub(r'^(患者|啓二|返答)[\(（]?[^）\)]*[\)）]?[:：]?\s*', '', text)
            text = regex.sub(r'\s*\|.*$', '', text)
            if len(text) > 100:
                text = text[:100]
            return text if text else "はい。"
        except Exception as e:
            return f"すみません、よく聞こえませんでした。"

    def generate_voice(self, text):
        """Generate voice using VOICEVOX"""
        response = requests.post(f"{VOICEVOX_URL}/audio_query?speaker={SPEAKER_ID}&text={text}")
        query = response.json()
        response = requests.post(f"{VOICEVOX_URL}/synthesis?speaker={SPEAKER_ID}", json=query)
        with open(WAV_PATH.replace('/', '\\'), 'wb') as f:
            f.write(response.content)

    def run_lipsync(self):
        """Trigger lipsync animation"""
        if not self.connected or not self.remote:
            return

        self.remote.run_command(f'''
import unreal
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = editor_subsystem.get_game_world()
if game_world:
    for a in unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor):
        if "{BLUEPRINT_NAME}" in a.get_name():
            a.set_editor_property("PendingWavPath", "{WAV_PATH}")
            break
''', unattended=True)

    def run(self):
        """Start the GUI"""
        self.input_entry.focus()
        self.root.mainloop()

        # Cleanup
        if self.remote:
            self.remote.stop()


if __name__ == "__main__":
    app = PatientGUI()
    app.run()
