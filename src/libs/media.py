from __future__ import annotations
from pydub import AudioSegment
from scipy.io import wavfile
from moviepy import *
import shutil
import numpy as np
import os
import base64

class Media:
    file_path: str
    clip: VideoFileClip
    dub: AudioSegment
    
    def __init__(self, file_path) -> None:
        file_format = file_path.split('.')[-1]
        if file_format not in ['mp4', 'mp3', 'wav', 'avi', 'mov']:
            raise ValueError(f"Unsupported media format: {file_format}")
        
        self.file_path = file_path
        if file_format in ['mp4', 'avi', 'mov']:
            self.clip = VideoFileClip(file_path)
            pass
        else:
            self.dub = AudioSegment.from_file(file_path, format=file_format)
            pass

        return
    

    def get_duration(self) -> float:
        return self.clip.duration

    def get_fps(self) -> float:
        return self.clip.fps

    def get_resolution(self) -> tuple[int, int]:
        return self.clip.size
    
    def extract_audio(self, output_path) -> Media:
        audio = self.clip.audio
        audio.write_audiofile(output_path)
        return Media(output_path)
    
    def reverse_audio(self, output_path) -> Media:
        reversed_clip = self.dub.reverse()
        reversed_clip.export(output_path, format="mp3")
        return Media(output_path)
    

    def encrypt_audio(self, seed: int, row: int, high: int, output_path) -> Media:
        # MP3などの場合、一時的にWAVに変換
        temp_wav_path = None
        if hasattr(self, "dub"):
            temp_wav_path = "temp_encrypt_input.wav"
            self.dub.export(temp_wav_path, format="wav")
            input_path = temp_wav_path
        else:
            input_path = self.file_path

        # WAVを正しく読み込む（サンプルレートとデータを取得）
        rate, data = wavfile.read(input_path)

        # 一時ファイル削除
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

        # モノラル化（必要なら）
        if data.ndim > 1:
            data = data[:, 0]

        # --- base64エンコードして人間に判別できない音声に変換 ---
        raw_bytes = data.tobytes()
        b64 = base64.b64encode(raw_bytes)  # base64の結果（ASCII文字列バイト列）を音声として使う
        
        # base64の結果をint16の音声データとして解釈
        # 長さを偶数に調整（int16は2バイト単位）
        if len(b64) % 2 != 0:
            b64 = b64 + b'='
        
        # base64バイト列を音声サンプルとして解釈
        encrypted = np.frombuffer(b64, dtype=np.uint8).astype(np.int16)

        # -1.0 ～ +1.0 に正規化
        encrypted = (encrypted - 128) / 128.0

        # 音声っぽく振幅制限
        encrypted *= 0.3

        # 疑似乱数（鍵）でノイズを追加
        np.random.seed(seed)
        noise = np.random.randint(low=row, high=high, size=encrypted.shape)
        encrypted = encrypted.astype(np.int32) + noise
        encrypted = np.clip(encrypted, -32768, 32767).astype(np.int16)
        
        # pydubを使って正しいWAV形式で保存
        # int16のnumpy配列をbytesに変換
        audio_bytes = encrypted.tobytes()
        
        # AudioSegmentを作成（モノラル、16bit、元のサンプルレート）
        audio_segment = AudioSegment(
            data=audio_bytes,
            sample_width=1,  # 16bit = 2bytes
            frame_rate=rate,
            channels=1
        )
        
        # ステレオに変換して出力（互換性向上）
        audio_segment = audio_segment.set_channels(2)
        audio_segment.export(output_path, format="wav")

        return Media(output_path)

    def convert_to_mp3(self, output_path) -> Media:
        if hasattr(self, "dub"):
            self.dub.export(output_path, format="mp3")
        elif hasattr(self, "clip"):
            audio = self.clip.audio
            audio.write_audiofile(output_path)
        else:
            raise ValueError("No audio or video data to convert.")
        return Media(output_path)
    
    def mix_audio(self, other: Media, output_path: str, volume_ratio: float) -> Media:
        mixed = self.dub.overlay(other.dub, gain_during_overlay=-20 * (1 - volume_ratio))
        mixed.export(output_path, format="mp3")
        return Media(output_path)
    
    def render_video(self, image_path: str, output_path: str) -> Media:
        # WAVファイルの長さを取得
        if self.file_path.endswith(".wav"):
            rate, data = wavfile.read(self.file_path)
            duration = len(data) / rate
            audio_path = self.file_path
        elif hasattr(self, "dub"):
            duration = len(self.dub) / 1000.0
            audio_path = "temp_audio_for_ffmpeg.wav"
            self.dub.export(audio_path, format="wav")
        elif hasattr(self, "clip") and self.clip.audio is not None:
            duration = self.clip.duration
            audio_path = "temp_audio_for_ffmpeg.wav"
            self.clip.audio.write_audiofile(audio_path)
        else:
            raise ValueError("No audio available to render with image.")

        # ffmpegで黒背景の動画と音声を合成
        import subprocess
        cmd = [
            "ffmpeg", "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=30",
            "-i", audio_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a aac",
            "-shortest", output_path
        ]
        

        subprocess.run(cmd, check=True)

        # 一時ファイルを削除
        if audio_path != self.file_path and os.path.exists(audio_path):
            os.remove(audio_path)

        return Media(output_path)
    

    def close(self) -> None:
        if hasattr(self, 'clip'):
            self.clip.close()
            pass
        return