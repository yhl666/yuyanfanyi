"""
BabelBridge 主程序
智能同声传译系统
"""
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# 导入配置和服务
from config import TTS_MODELS
from models import TranslateRequest
from services.model_loader import load_models
from services.audio_service import detect_speech, transcribe_audio, text_to_speech
from services.translation_service import correct_text, translate_text
from services.logger_service import save_log
from services.history_service import get_available_dates, get_history_by_date, search_history, get_statistics

# 创建 FastAPI 应用
app = FastAPI(title="BabelBridge API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载模型
load_models()

print("=" * 60)
print("⚠ TTS 功能暂时禁用")
print("提示: 系统将正常工作，但不会播放语音")
print("     翻译结果会显示在界面上")
print("=" * 60)

# ==================== API 路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {"message": "BabelBridge API is running", "version": "1.0.0"}

@app.post("/api/translate")
async def translate_api(request: TranslateRequest):
    """文本翻译 API"""
    try:
        text = request.text
        src_lang = request.src_lang
        target_lang = request.target_lang
        
        if not text:
            return {"error": "文本不能为空"}
        
        # 自动检测语言
        if src_lang == "auto":
            if any('\u4e00' <= char <= '\u9fff' for char in text):
                src_lang = "zh"
            else:
                src_lang = "en"
        
        # 翻译
        translated = await translate_text(text, src_lang, target_lang)
        
        return {
            "success": True,
            "original": text,
            "translated": translated,
            "src_lang": src_lang,
            "target_lang": target_lang
        }
    except Exception as e:
        print(f"翻译 API 错误: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/api/transcribe")
async def transcribe_api(file: UploadFile = File(...)):
    """音频转文字 API"""
    try:
        print(f"收到文件上传: {file.filename}, 类型: {file.content_type}")
        
        audio_data = await file.read()
        
        if not audio_data:
            return {"error": "没有上传文件"}
        
        print(f"文件大小: {len(audio_data)} 字节")
        
        # 转录音频
        text, detected_lang = transcribe_audio(audio_data, is_raw_pcm=False)
        
        if not text:
            return {"error": "无法识别音频内容"}
        
        print(f"识别成功: {text[:50]}...")
        
        return {
            "success": True,
            "text": text,
            "language": detected_lang,
            "filename": file.filename
        }
    except Exception as e:
        print(f"音频识别 API 错误: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# ==================== 历史记录 API ====================

@app.get("/api/history/dates")
async def get_dates_api():
    """获取所有有记录的日期"""
    try:
        dates = get_available_dates()
        return {"success": True, "dates": dates}
    except Exception as e:
        print(f"获取日期列表错误: {e}")
        return {"error": str(e)}

@app.get("/api/history/{date}")
async def get_history_api(date: str):
    """获取指定日期的历史记录"""
    try:
        records = get_history_by_date(date)
        return {"success": True, "records": records, "count": len(records)}
    except Exception as e:
        print(f"获取历史记录错误: {e}")
        return {"error": str(e)}

@app.get("/api/history/search/{keyword}")
async def search_history_api(keyword: str, date: str = None):
    """搜索历史记录"""
    try:
        results = search_history(keyword, date)
        return {"success": True, "results": results, "count": len(results)}
    except Exception as e:
        print(f"搜索历史记录错误: {e}")
        return {"error": str(e)}

@app.get("/api/history/stats")
async def get_stats_api():
    """获取统计信息"""
    try:
        stats = get_statistics()
        return {"success": True, "stats": stats}
    except Exception as e:
        print(f"获取统计信息错误: {e}")
        return {"error": str(e)}

# ==================== WebSocket 路由 ====================

@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket):
    """实时翻译 WebSocket - 优化版"""
    print("收到 WebSocket 连接请求...")
    await websocket.accept()
    print("✓ 客户端已连接")
    
    # 状态变量
    audio_buffer = b""
    silence_count = 0
    speech_count = 0
    speech_detected = False
    last_speech_time = None
    mode = "zh-th"
    start_time = asyncio.get_event_loop().time()
    
    # 优化后的配置参数
    min_audio_length = 16000 * 1.0  # 最少 1 秒音频
    min_silence_duration = 2.0  # 需要 2 秒连续静音才停止
    protection_period = 2.0  # 前 2 秒保护期（不检测静音）
    min_speech_duration = 0.5  # 至少检测到 0.5 秒的语音才算有效
    check_interval = 16000 * 0.3  # 每 0.3 秒检测一次
    
    try:
        while True:
            data = await websocket.receive()
            
            # 处理模式切换
            if "text" in data:
                message = json.loads(data["text"])
                if message.get("type") == "mode":
                    mode = message.get("mode", "zh-th")
                    print(f"切换模式: {mode}")
                    continue
            
            # 处理音频数据
            if "bytes" in data:
                audio_chunk = data["bytes"]
                audio_buffer += audio_chunk
                
                current_time = asyncio.get_event_loop().time()
                elapsed_time = current_time - start_time
                
                # 每 0.3 秒检测一次（更频繁的检测）
                if len(audio_buffer) >= check_interval:
                    # 检测最近 1 秒的音频
                    recent_audio = audio_buffer[-16000:] if len(audio_buffer) >= 16000 else audio_buffer
                    has_speech = detect_speech(recent_audio)
                    
                    if has_speech:
                        speech_detected = True
                        speech_count += 1
                        silence_count = 0
                        last_speech_time = current_time
                    else:
                        # 只有在保护期后且检测到过语音才计数静音
                        if speech_detected and elapsed_time > protection_period:
                            silence_count += 1
                            # 计算静音时长
                            if last_speech_time:
                                silence_duration = current_time - last_speech_time
                            else:
                                silence_duration = 0
                        else:
                            silence_count = 0
                    
                    # 判断是否应该处理
                    # 条件：
                    # 1. 检测到语音
                    # 2. 有足够的语音时长（至少 0.5 秒）
                    # 3. 静音时长超过 2 秒
                    # 4. 超过保护期
                    # 5. 有足够的音频数据
                    should_process = (
                        speech_detected and 
                        speech_count >= 2 and  # 至少检测到 2 次语音
                        silence_count >= int(min_silence_duration / 0.3) and  # 2秒静音 = 约7次检测
                        elapsed_time > protection_period and
                        len(audio_buffer) >= min_audio_length
                    )
                    
                    if should_process:
                        print(f"检测到语音结束（时长: {elapsed_time:.1f}s，语音次数: {speech_count}，静音次数: {silence_count}），开始处理...")
                        
                        # 转录
                        text, detected_lang = transcribe_audio(audio_buffer)
                        
                        if text:
                            print(f"原始识别 ({detected_lang}): {text}")
                            
                            # 纠错
                            corrected_text = await correct_text(text, detected_lang)
                            print(f"纠正后文本: {corrected_text}")
                            
                            # 确定目标语言
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
                                translated = await translate_text(corrected_text, detected_lang, target_lang)
                                print(f"翻译结果 ({target_lang}): {translated}")
                                
                                # 发送结果
                                await websocket.send_json({
                                    "type": "transcript",
                                    "original": corrected_text,
                                    "translated": translated,
                                    "src_lang": detected_lang,
                                    "target_lang": target_lang,
                                    "timestamp": datetime.now().isoformat()
                                })
                                print("✓ 文本结果已发送")
                                
                                # 保存日志
                                save_log(mode, detected_lang, corrected_text, translated)
                                
                                # TTS（当前禁用）
                                audio_data = await text_to_speech(translated, target_lang)
                                if audio_data:
                                    await websocket.send_bytes(audio_data)
                                    print("✓ 音频已发送")
                                else:
                                    print("⚠ TTS 禁用，仅发送文本")
                        
                        # 重置所有状态
                        audio_buffer = b""
                        silence_count = 0
                        speech_count = 0
                        speech_detected = False
                        last_speech_time = None
                        start_time = asyncio.get_event_loop().time()
                        print("✓ 状态已重置，等待下一次语音输入...")
    
    except WebSocketDisconnect:
        print("客户端断开连接")
    except RuntimeError as e:
        if "disconnect" in str(e).lower():
            print("客户端已断开")
        else:
            print(f"WebSocket运行时错误: {e}")
    except Exception as e:
        print(f"WebSocket错误: {e}")
        try:
            await websocket.close()
        except:
            pass

# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
