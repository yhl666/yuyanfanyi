"""
模型加载服务
"""
import sys
import os
from pathlib import Path

# 添加父目录到路径
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

# 设置 FFmpeg
os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-7.1.1\bin"

import torch
from faster_whisper import WhisperModel
from openai import OpenAI

# 导入配置
from config import WHISPER_MODEL_PATH, VAD_MODEL_PATH, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# 全局模型实例
whisper_model = None
vad_model = None
get_speech_timestamps = None
deepseek_client = None

def load_models():
    """加载所有模型"""
    global whisper_model, vad_model, get_speech_timestamps, deepseek_client
    
    print("正在加载模型...")
    
    # 加载 Whisper 模型
    print(f"从本地加载 Whisper 模型: {WHISPER_MODEL_PATH}")
    whisper_model = WhisperModel(str(WHISPER_MODEL_PATH), device="cpu", compute_type="int8")
    print("✓ Whisper 模型加载成功")
    
    # 加载 VAD 模型
    print(f"从本地加载 VAD 模型: {VAD_MODEL_PATH}")
    vad_src_path = VAD_MODEL_PATH / 'src'
    if str(vad_src_path) not in sys.path:
        sys.path.insert(0, str(vad_src_path))
    
    from silero_vad.utils_vad import OnnxWrapper, get_speech_timestamps as gst
    
    vad_model_path = VAD_MODEL_PATH / 'src' / 'silero_vad' / 'data' / 'silero_vad.onnx'
    vad_model = OnnxWrapper(str(vad_model_path), force_onnx_cpu=True)
    get_speech_timestamps = gst
    print("✓ VAD 模型加载成功")
    
    print("=" * 60)
    print("✓ 所有模型加载完成！服务器准备就绪")
    print("=" * 60)
    
    # 初始化 DeepSeek 客户端
    deepseek_client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )
    
    print("模型加载完成！")
    
    return whisper_model, vad_model, get_speech_timestamps, deepseek_client
