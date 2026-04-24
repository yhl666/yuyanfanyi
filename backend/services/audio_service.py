"""
音频处理服务
"""
import io
import wave
import numpy as np
import torch
import services.model_loader as ml

def detect_speech(audio_bytes: bytes, sample_rate: int = 16000) -> bool:
    """使用 Silero VAD 检测语音"""
    try:
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        audio_tensor = torch.from_numpy(audio_np)
        speech_timestamps = ml.get_speech_timestamps(audio_tensor, ml.vad_model, sampling_rate=sample_rate)
        return len(speech_timestamps) > 0
    except Exception as e:
        print(f"VAD检测错误: {e}")
        return False

def transcribe_audio(audio_bytes: bytes, is_raw_pcm: bool = True) -> tuple:
    """使用 Faster-Whisper 转录音频"""
    try:
        if is_raw_pcm:
            # 原始 PCM 数据（来自 WebSocket）
            audio_io = io.BytesIO()
            with wave.open(audio_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_bytes)
            audio_io.seek(0)
        else:
            # 完整的音频文件（来自文件上传）
            audio_io = io.BytesIO(audio_bytes)
        
        # 转录
        segments, info = ml.whisper_model.transcribe(audio_io, language=None)
        text = " ".join([segment.text for segment in segments])
        detected_lang = info.language
        
        return text.strip(), detected_lang
    except Exception as e:
        print(f"转录错误: {e}")
        import traceback
        traceback.print_exc()
        return "", "unknown"

async def text_to_speech(text: str, lang: str) -> bytes:
    """使用 TTS 合成语音（当前禁用）"""
    return b""
