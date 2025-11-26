# 🌉 BabelBridge - 智能同声传译系统

一个基于 Web 全栈 + AI 的实时双向语音翻译系统，支持中文⇄泰语、中文⇄英语的无感交互翻译。

## ✨ 核心特性

- 🎤 **无感交互**: 基于 VAD (Voice Activity Detection) 自动断句，无需手动按键
- 🔄 **实时翻译**: WebSocket 流式传输，低延迟响应
- 🌍 **多语言支持**: 中文、泰语、英语三语互译
- 💾 **自动存档**: 所有对话自动保存到本地日志
- 🎨 **现代界面**: Vue 3 + Tailwind CSS 打造的优雅 UI

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
├── backend/
│   ├── logs/                 # 对话记录存储
│   ├── main.py              # 核心后端逻辑
│   ├── .env                 # API密钥配置
│   └── requirements.txt     # Python依赖
├── frontend/
│   ├── src/
│   │   ├── utils/
│   │   │   └── audioResampler.js  # 音频重采样工具
│   │   ├── App.vue          # 主界面
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── README.md
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

## 🎯 翻译模式

### 模式 A: 中文 ⇄ 泰语
- 中文 → 泰语
- 泰语 → 中文
- 英语 → 中文 (备用)

### 模式 B: 中文 ⇄ 英语
- 中文 → 英语
- 英语 → 中文

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

### 4. 模型加载慢
首次运行时会下载模型文件，请耐心等待

## 🚀 性能优化建议

- 使用 GPU 加速 Whisper (修改 `device="cuda"`)
- 调整 VAD 灵敏度参数
- 使用更小的 Whisper 模型 (如 `tiny` 或 `base`)

## 📄 许可证

MIT License

## 👨‍💻 作者

开发者：大三学生
项目目标：解决跨语言沟通障碍

---

**提示**: 这是一个学习项目，展示了 Web 全栈 + AI 工程化的完整实践。适合作为简历项目展示。
