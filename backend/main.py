import os
os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-7.1.1\bin"

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
import json
import io
import wave
from datetime import datetime
from pathlib import Path
import torch
import numpy as np
from faster_whisper import WhisperModel
import edge_tts
from openai import OpenAI

load_dotenv()

app = FastAPI()

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化模型
print("正在加载模型...")
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
vad_model, vad_utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
(get_speech_timestamps, _, read_audio, *_) = vad_utils

# DeepSeek客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

# 日志目录
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

print("模型加载完成！")

# TTS语音映射
TTS_VOICES = {
    "zh": "zh-CN-XiaoxiaoNeural",
    "th": "th-TH-PremwadeeNeural",
    "en": "en-US-ChristopherNeural"
}

def save_log(mode: str, src_lang: str, original: str, translated: str):
    """保存对话记录"""
    today = datetime.now().strftime("%Y%m%d")
    log_file = LOGS_DIR / f"transcript_{today}.jsonl"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "src_lang": src_lang,
        "original": original,
        "translated": translated
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

async def translate_text(text: str, src_lang: str, target_lang: str) -> str:
    """使用DeepSeek翻译文本"""
    lang_map = {"zh": "中文", "th": "泰语", "en": "英语"}
    
    prompt = f"请将以下{lang_map[src_lang]}口语化地翻译成{lang_map[target_lang]}，保持自然流畅：\n{text}"
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"翻译错误: {e}")
        return text

async def text_to_speech(text: str, lang: str) -> bytes:
    """使用Edge TTS合成语音"""
    voice = TTS_VOICES.get(lang, TTS_VOICES["zh"])
    communicate = edge_tts.Communicate(text, voice)
    
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    return audio_data

def detect_speech(audio_bytes: bytes, sample_rate: int = 16000) -> bool:
    """使用Silero VAD检测语音"""
    try:
        # 转换为numpy数组
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        audio_tensor = torch.from_numpy(audio_np)
        
        # VAD检测
        speech_timestamps = get_speech_timestamps(audio_tensor, vad_model, sampling_rate=sample_rate)
        return len(speech_timestamps) > 0
    except Exception as e:
        print(f"VAD检测错误: {e}")
        return False

def transcribe_audio(audio_bytes: bytes) -> tuple:
    """使用Faster-Whisper转录音频"""
    try:
        # 创建临时WAV文件
        audio_io = io.BytesIO()
        with wave.open(audio_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_bytes)
        
        audio_io.seek(0)
        
        # 转录
        segments, info = whisper_model.transcribe(audio_io, language=None)
        text = " ".join([segment.text for segment in segments])
        detected_lang = info.language
        
        return text.strip(), detected_lang
    except Exception as e:
        print(f"转录错误: {e}")
        return "", "unknown"

@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("客户端已连接")
    
    audio_buffer = b""
    silence_duration = 0
    mode = "zh-th"  # 默认模式
    
    try:
        while True:
            data = await websocket.receive()
            
            if "text" in data:
                # 接收模式切换消息
                message = json.loads(data["text"])
                if message.get("type") == "mode":
                    mode = message.get("mode", "zh-th")
                    print(f"切换模式: {mode}")
                    continue
            
            if "bytes" in data:
                audio_chunk = data["bytes"]
                audio_buffer += audio_chunk
                
                # 检测静音（简单实现：累积足够数据后处理）
                if len(audio_buffer) > 16000 * 2:  # 约1秒数据
                    has_speech = detect_speech(audio_buffer)
                    
                    if has_speech:
                        silence_duration = 0
                    else:
                        silence_duration += 1
                    
                    # 检测到静音超过500ms，处理音频
                    if silence_duration > 0 and len(audio_buffer) > 16000 * 0.5:
                        print("检测到语音结束，开始处理...")
                        
                        # ASR转录
                        text, detected_lang = transcribe_audio(audio_buffer)
                        
                        if text:
                            print(f"识别文本 ({detected_lang}): {text}")
                            
                            # 根据模式决定翻译方向
                            target_lang = None
                            if mode == "zh-th":
                                if detected_lang == "zh":
                                    target_lang = "th"
                                elif detected_lang == "th":
                                    target_lang = "zh"
                                elif detected_lang == "en":
                                    target_lang = "zh"
                            elif mode == "zh-en":
                                if detected_lang == "zh":
                                    target_lang = "en"
                                elif detected_lang == "en":
                                    target_lang = "zh"
                            
                            if target_lang:
                                # 翻译
                                translated = await translate_text(text, detected_lang, target_lang)
                                print(f"翻译结果 ({target_lang}): {translated}")
                                
                                # TTS合成
                                audio_data = await text_to_speech(translated, target_lang)
                                
                                # 保存日志
                                save_log(mode, detected_lang, text, translated)
                                
                                # 发送结果
                                await websocket.send_json({
                                    "type": "transcript",
                                    "original": text,
                                    "translated": translated,
                                    "src_lang": detected_lang,
                                    "target_lang": target_lang,
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                # 发送音频
                                await websocket.send_bytes(audio_data)
                        
                        # 清空缓冲区
                        audio_buffer = b""
                        silence_duration = 0
    
    except WebSocketDisconnect:
        print("客户端断开连接")
    except Exception as e:
        print(f"WebSocket错误: {e}")
        await websocket.close()

@app.get("/")
async def root():
    return {"message": "BabelBridge API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
