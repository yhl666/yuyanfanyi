# BabelBridge 后端结构说明

## 📁 项目结构

```
backend/
├── main.py                      # 主程序入口（FastAPI 应用）
├── config.py                    # 配置文件（路径、API密钥等）
├── models.py                    # 数据模型（Pydantic）
├── services/                    # 服务模块
│   ├── __init__.py
│   ├── model_loader.py         # 模型加载服务
│   ├── audio_service.py        # 音频处理服务（VAD、ASR）
│   ├── translation_service.py  # 翻译服务（纠错、翻译）
│   └── logger_service.py       # 日志服务
├── faster-whisper-small/        # Whisper 模型
├── snakers4-silero-vad/         # VAD 模型
├── logs/                        # 对话日志
├── .env                         # 环境变量
└── requirements.txt             # 依赖包

```

## 📝 模块说明

### main.py
- FastAPI 应用主程序
- 定义所有 API 路由
- WebSocket 处理逻辑
- 启动入口

### config.py
- 全局配置
- 模型路径
- API 密钥
- 常量定义

### models.py
- Pydantic 数据模型
- 请求/响应格式定义

### services/model_loader.py
- 加载 Whisper 模型
- 加载 VAD 模型
- 初始化 DeepSeek 客户端
- 全局模型实例管理

### services/audio_service.py
- `detect_speech()` - VAD 语音检测
- `transcribe_audio()` - 语音转文字
- `text_to_speech()` - 文字转语音（当前禁用）

### services/translation_service.py
- `correct_text()` - AI 文本纠错
- `translate_text()` - AI 翻译

### services/logger_service.py
- `save_log()` - 保存对话记录

## 🚀 启动方式

```bash
# 方式 1: 直接运行
python main.py

# 方式 2: 使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 方式 3: 使用启动脚本
.\start.bat
```

## 🔧 修改配置

### 修改模型路径
编辑 `config.py`:
```python
WHISPER_MODEL_PATH = BACKEND_DIR / "your-model-path"
```

### 修改 API 密钥
编辑 `.env`:
```
DEEPSEEK_API_KEY=your-key
```

### 修改 VAD 参数
编辑 `main.py` 中的配置参数:
```python
min_audio_length = 16000 * 0.5  # 最少音频长度
max_silence_count = 3            # 静音检测次数
protection_period = 3.0          # 保护期时长
```

## 📊 优势

1. **模块化** - 每个功能独立模块，易于维护
2. **可读性** - 代码结构清晰，注释完整
3. **可扩展** - 易于添加新功能
4. **可测试** - 每个模块可独立测试
5. **可配置** - 配置集中管理

## 🔄 旧版本

旧版本的 main.py 已备份为 `main_old.py`，如需回滚：
```bash
Move-Item main.py main_new.py
Move-Item main_old.py main.py
```
