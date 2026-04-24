# 🌉 BabelBridge - 智能同声传译系统

一个基于 Web 全栈 + AI 的实时双向语音翻译系统，支持中文⇄英语、中文⇄泰语的无感交互翻译。

> **项目概述**: 本项目是一个完整的实时语音翻译解决方案，采用前后端分离架构，集成了语音识别、AI翻译、语音合成等多项技术，实现了无需手动操作的智能同声传译功能。

## 📋 目录

- [核心特性](#核心特性)
- [技术架构](#技术架构)
- [项目结构](#项目结构)
- [功能模块](#功能模块)
- [API文档](#api文档)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

## ✨ 核心特性

### 主要功能
- 🎤 **实时语音翻译**: 基于 VAD 自动断句，无需手动按键
- 🔄 **双向翻译**: 支持中文⇄泰语、中文⇄英语
- 🧠 **AI 纠错**: 自动纠正语音识别错误
- 💾 **历史记录**: 自动保存并可查询历史对话
- 🧪 **测试工具**: 文本翻译和音频文件识别测试
- 📊 **统计分析**: 对话统计和数据导出

### 技术特点
- **智能 VAD**: 2秒静音检测，前2秒保护期，避免误触发
- **模块化设计**: 前后端代码结构清晰，易于维护
- **本地模型**: Whisper 和 VAD 模型本地运行，保护隐私
- **实时通信**: WebSocket 低延迟传输
- **响应式UI**: 适配各种屏幕尺寸

## 🏗️ 技术架构

### 后端 (Python FastAPI)
- **VAD**: Silero VAD - 实时语音活动检测
- **ASR**: Faster-Whisper - 语音转文字
- **LLM**: DeepSeek V3 - 口语化翻译
- **TTS**: Edge-TTS - 多语言语音合成

### 前端 (Vue 3)
- **音频处理**: Web Audio API + 自定义重采样器
- **实时通信**: WebSocket
- **UI框架**: Tailwind CSS

## 📦 快速开始

### 前置要求

1. **Python 3.10.10**
2. **Node.js 16+**
3. **FFmpeg** (已配置路径: `D:\ffmpeg-7.1.1\bin`)
4. **Whisper 模型** (已配置本地路径: `backend\faster-whisper-small`)

### 安装步骤

#### 1. 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 使用方法

1. 确保后端服务运行在 `http://localhost:8000`
2. 打开浏览器访问前端 (通常是 `http://localhost:3000`)
3. 允许浏览器访问麦克风权限
4. 选择翻译模式（中文⇄泰语 或 中文⇄英语）
5. 点击"开始"按钮
6. 直接说话，系统会自动识别、翻译并播放

## 📁 项目结构

```
BabelBridge/
├── backend/                          # 后端服务
│   ├── services/                     # 服务模块
│   │   ├── model_loader.py          # 模型加载服务
│   │   ├── audio_service.py         # 音频处理（VAD、ASR）
│   │   ├── translation_service.py   # 翻译服务（纠错、翻译）
│   │   ├── logger_service.py        # 日志服务
│   │   └── history_service.py       # 历史记录服务
│   ├── faster-whisper-small/        # Whisper 模型（本地）
│   ├── snakers4-silero-vad/         # VAD 模型（本地）
│   ├── logs/                         # 对话记录存储
│   ├── main.py                       # FastAPI 主程序
│   ├── config.py                     # 配置文件
│   ├── models.py                     # 数据模型
│   ├── .env                          # 环境变量
│   ├── requirements.txt              # Python 依赖
│   ├── test_whisper.py              # Whisper 测试工具
│   └── test_whisper_simple.py       # 简化测试工具
├── frontend/                         # 前端应用
│   ├── src/
│   │   ├── utils/
│   │   │   └── audioResampler.js    # 音频重采样（48k→16k）
│   │   ├── Home.vue                 # 主页（实时翻译）
│   │   ├── Test.vue                 # 测试页面
│   │   ├── History.vue              # 历史记录页面
│   │   ├── RootApp.vue              # 根组件
│   │   ├── main.js                  # 入口文件
│   │   └── style.css                # 样式文件
│   ├── package.json                 # Node 依赖
│   ├── vite.config.js               # Vite 配置
│   └── tailwind.config.js           # Tailwind 配置
├── README.md                         # 项目文档
└── 快速启动.md                       # 快速启动指南
```

## 🔧 配置说明

### 环境变量 (backend/.env)

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### FFmpeg 路径

如果 FFmpeg 安装在其他位置，请修改 `backend/main.py` 第2行：

```python
os.environ["PATH"] += os.pathsep + r"你的FFmpeg路径\bin"
```

## 🎯 功能模块

### 1. 实时翻译（主页）
**路径**: `/`

**功能**:
- 实时语音识别和翻译
- 智能 VAD 自动断句
- AI 文本纠错
- 对话记录实时显示
- 支持两种翻译模式

**翻译模式**:
- **中文 ⇄ 泰语**: 中文→泰语、泰语→中文、英语→中文(备用)
- **中文 ⇄ 英语**: 中文→英语、英语→中文

**VAD 参数**:
- 保护期: 前2秒不检测静音
- 静音阈值: 连续2秒静音才停止
- 检测频率: 每0.3秒检测一次
- 最小音频: 至少1秒音频

### 2. 测试页面
**路径**: `/test`

**功能**:
- **文本翻译测试**: 输入文本直接翻译
- **音频文件识别**: 上传音频文件转文字
- **测试统计**: 显示翻译和识别次数

**支持格式**: WAV, MP3, M4A, OGG, FLAC

### 3. 历史记录
**路径**: `/history`

**功能**:
- **日期筛选**: 按日期查看历史记录
- **关键词搜索**: 在原文和译文中搜索
- **统计信息**: 总记录数、模式分布、语言分布
- **导出功能**: 导出为 JSON 格式

## 📡 API 文档

### WebSocket API

#### `/ws/translate`
实时翻译 WebSocket 连接

**发送消息**:
```json
// 模式切换
{
  "type": "mode",
  "mode": "zh-en"  // 或 "zh-th"
}

// 音频数据（二进制）
ArrayBuffer (PCM 16-bit, 16kHz)
```

**接收消息**:
```json
// 翻译结果
{
  "type": "transcript",
  "original": "你好",
  "translated": "Hello",
  "src_lang": "zh",
  "target_lang": "en",
  "timestamp": "2025-11-30T10:30:45.123456"
}

// 音频数据（二进制，当前禁用）
ArrayBuffer (WAV format)
```

### REST API

#### `POST /api/translate`
文本翻译

**请求**:
```json
{
  "text": "你好",
  "src_lang": "auto",  // 或 "zh", "en", "th"
  "target_lang": "en"
}
```

**响应**:
```json
{
  "success": true,
  "original": "你好",
  "translated": "Hello",
  "src_lang": "zh",
  "target_lang": "en"
}
```

#### `POST /api/transcribe`
音频转文字

**请求**: `multipart/form-data`
- `file`: 音频文件

**响应**:
```json
{
  "success": true,
  "text": "识别的文本内容",
  "language": "zh",
  "filename": "audio.mp3"
}
```

#### `GET /api/history/dates`
获取所有有记录的日期

**响应**:
```json
{
  "success": true,
  "dates": [
    {
      "date": "20251130",
      "formatted": "2025年11月30日",
      "file": "transcript_20251130.jsonl"
    }
  ]
}
```

#### `GET /api/history/{date}`
获取指定日期的历史记录

**响应**:
```json
{
  "success": true,
  "records": [...],
  "count": 10
}
```

#### `GET /api/history/search/{keyword}`
搜索历史记录

**参数**: `?date=20251130` (可选)

**响应**:
```json
{
  "success": true,
  "results": [...],
  "count": 5
}
```

#### `GET /api/history/stats`
获取统计信息

**响应**:
```json
{
  "success": true,
  "stats": {
    "total": 100,
    "by_mode": {
      "zh-en": 60,
      "zh-th": 40
    },
    "by_language": {
      "zh": 50,
      "en": 40,
      "th": 10
    }
  }
}
```

## 📝 日志格式

对话记录保存在 `backend/logs/transcript_YYYYMMDD.jsonl`：

```json
{
  "timestamp": "2025-11-20T10:30:45.123456",
  "mode": "zh-th",
  "src_lang": "zh",
  "original": "你好",
  "translated": "สวัสดี"
}
```

## 🐛 常见问题

### 1. FFmpeg 错误
确保 `main.py` 第一行正确设置了 FFmpeg 路径，且该路径下存在 `ffmpeg.exe`

### 2. 麦克风无法访问
检查浏览器权限设置，确保允许网站访问麦克风

### 3. WebSocket 连接失败
确认后端服务已启动，且前端配置的 WebSocket 地址正确

### 4. 模型路径错误
确保 Whisper 模型文件位于 `backend\faster-whisper-small` 目录下，包含：
- model.bin
- config.json
- tokenizer.json
- vocabulary.txt

## 🔬 技术细节

### 后端技术栈
- **框架**: FastAPI 0.109.2
- **语音识别**: Faster-Whisper 1.2.1 (Whisper Small 模型)
- **VAD**: Silero VAD (ONNX 格式)
- **翻译**: DeepSeek V3 (通过 OpenAI SDK)
- **TTS**: Edge-TTS 6.1.10 (当前禁用)
- **其他**: PyTorch 2.0.1, NumPy 1.24.4

### 前端技术栈
- **框架**: Vue 3.3.4
- **路由**: Vue Router 4.2.5
- **构建工具**: Vite 4.5.0
- **样式**: Tailwind CSS 3.3.5
- **音频处理**: Web Audio API

### 数据流程

#### 实时翻译流程
```
用户说话 
  → 麦克风采集 (48kHz)
  → 前端重采样 (16kHz)
  → WebSocket 发送
  → 后端 VAD 检测
  → 静音判断
  → Whisper 识别
  → DeepSeek 纠错
  → DeepSeek 翻译
  → 返回结果
  → 前端显示
```

#### 音频处理流程
```
浏览器麦克风 (44.1/48kHz, Float32)
  → ScriptProcessorNode 处理
  → 下采样到 16kHz
  → Float32 → Int16 转换
  → ArrayBuffer 发送
  → 后端接收
  → 转换为 WAV 格式
  → Whisper 处理
```

### 模型信息

#### Whisper Small 模型
- **大小**: ~466MB
- **语言**: 支持99种语言
- **准确度**: 中文、英文识别准确度高
- **注意**: 泰语识别效果一般

#### Silero VAD 模型
- **大小**: ~2.3MB
- **格式**: ONNX
- **用途**: 实时语音活动检测
- **性能**: CPU 运行流畅

### 性能指标

**正常运行指标**:
- 模型加载时间: < 10秒
- 语音识别延迟: < 2秒
- 翻译延迟: < 3秒
- 总体响应时间: < 5秒

**资源占用**:
- 内存: 约 2-3GB
- CPU: 中等（识别时较高）
- 磁盘: 约 500MB（模型文件）

## 🚀 性能优化建议

### 后端优化
- 使用 GPU 加速 Whisper: `device="cuda"`
- 使用更小的模型: `tiny` 或 `base`
- 调整 VAD 参数: `min_silence_duration`, `protection_period`
- 启用模型缓存

### 前端优化
- 调整音频缓冲区大小
- 优化重采样算法
- 使用 Web Workers 处理音频
- 实现音频压缩

## 🛠️ 开发工具

### 测试工具
- `backend/test_whisper.py`: 完整测试工具
- `backend/test_whisper_simple.py`: 简化测试工具
- 测试页面: `/test`

### 调试技巧
1. 查看后端日志: 所有操作都有详细日志
2. 查看浏览器控制台: WebSocket 连接状态
3. 检查日志文件: `backend/logs/transcript_*.jsonl`
4. 使用测试工具: 独立测试各个模块

## 📊 项目统计

- **代码行数**: ~3000+ 行
- **文件数量**: ~30 个
- **开发时间**: 约 2 周
- **技术栈**: 10+ 种技术

## 🔐 安全说明

- API 密钥存储在 `.env` 文件中，不要提交到 Git
- 模型文件本地运行，保护用户隐私
- WebSocket 连接仅限本地，生产环境需配置 HTTPS
- 历史记录存储在本地，定期清理

## 📄 许可证

MIT License

## 👨‍💻 作者信息

**开发者**: 大三学生  
**项目目标**: 解决跨语言沟通障碍  
**技术栈**: Python + Vue.js + AI  
**适用场景**: 
- 跨国恋情侣沟通
- 国际商务会议
- 语言学习辅助
- 旅游翻译助手

## 🎓 学习价值

本项目展示了以下技能：
- ✅ 全栈开发（前后端分离）
- ✅ AI 模型集成（Whisper, VAD, LLM）
- ✅ 实时通信（WebSocket）
- ✅ 音频处理（Web Audio API）
- ✅ 模块化设计
- ✅ RESTful API 设计
- ✅ 数据持久化
- ✅ 用户体验优化

**适合作为简历项目展示！**

---

## 📞 联系方式

如有问题或建议，欢迎提 Issue 或 PR。

**最后更新**: 2025-11-30
