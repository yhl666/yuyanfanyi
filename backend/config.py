"""
配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# FFmpeg 路径
os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-7.1.1\bin"

# 获取当前文件所在目录
BACKEND_DIR = Path(__file__).parent

# 模型路径
WHISPER_MODEL_PATH = BACKEND_DIR / "faster-whisper-small"
VAD_MODEL_PATH = BACKEND_DIR / "snakers4-silero-vad"
TTS_MODELS_DIR = BACKEND_DIR / "tts-models"

# 日志目录
LOGS_DIR = BACKEND_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

# TTS 语音映射（暂时禁用）
TTS_MODELS = {
    "zh": None,
    "en": None,
    "th": None
}
