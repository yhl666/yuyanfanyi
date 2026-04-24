<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-indigo-900 mb-2">🌉 BabelBridge</h1>
        <p class="text-gray-600">智能同声传译系统</p>
        <a href="/test" class="text-blue-600 hover:underline mt-2 inline-block">🧪 测试页面</a>
      </div>

      <!-- 控制面板 -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
          <!-- 模式选择 -->
          <div class="flex items-center gap-3">
            <label class="text-gray-700 font-medium">翻译模式:</label>
            <select 
              v-model="mode" 
              @change="changeMode"
              :disabled="isConnected"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100"
            >
              <option value="zh-th">中文 ⇄ 泰语</option>
              <option value="zh-en">中文 ⇄ 英语</option>
            </select>
          </div>

          <!-- 控制按钮 -->
          <div class="flex gap-3">
            <button
              v-if="!isConnected"
              @click="start"
              class="px-6 py-2 bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg transition-colors shadow-md"
            >
              🎤 开始
            </button>
            <button
              v-else
              @click="stop"
              class="px-6 py-2 bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg transition-colors shadow-md"
            >
              ⏸️ 暂停
            </button>
          </div>
        </div>

        <!-- 状态指示 -->
        <div class="mt-4 flex items-center gap-2">
          <div 
            :class="[
              'w-3 h-3 rounded-full',
              isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
            ]"
          ></div>
          <span class="text-sm text-gray-600">
            {{ isConnected ? '正在监听...' : '未连接' }}
          </span>
        </div>
      </div>

      <!-- 聊天记录 -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">对话记录</h2>
        
        <div 
          ref="chatContainer"
          class="space-y-4 max-h-96 overflow-y-auto pr-2"
        >
          <div 
            v-for="(msg, index) in messages" 
            :key="index"
            class="border-l-4 border-indigo-400 bg-gray-50 p-4 rounded-r-lg"
          >
            <div class="flex justify-between items-start mb-2">
              <span class="text-xs text-gray-500">{{ formatTime(msg.timestamp) }}</span>
              <span class="text-xs font-medium text-indigo-600">
                {{ getLangName(msg.src_lang) }} → {{ getLangName(msg.target_lang) }}
              </span>
            </div>
            <div class="space-y-2">
              <p class="text-gray-800">
                <span class="font-medium">原文:</span> {{ msg.original }}
              </p>
              <p class="text-indigo-700">
                <span class="font-medium">译文:</span> {{ msg.translated }}
              </p>
            </div>
          </div>

          <div v-if="messages.length === 0" class="text-center text-gray-400 py-8">
            暂无对话记录，点击"开始"按钮开始翻译
          </div>
        </div>
      </div>
    </div>

    <!-- 音频播放器 (隐藏) -->
    <audio ref="audioPlayer" style="display: none;"></audio>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { AudioResampler } from './utils/audioResampler.js'

const mode = ref('zh-th')
const isConnected = ref(false)
const messages = ref([])
const chatContainer = ref(null)
const audioPlayer = ref(null)

let ws = null
let resampler = null

const getLangName = (lang) => {
  const names = {
    'zh': '中文',
    'th': '泰语',
    'en': '英语'
  }
  return names[lang] || lang
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const changeMode = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'mode',
      mode: mode.value
    }))
  }
}

const start = async () => {
  try {
    // 初始化音频重采样器
    resampler = new AudioResampler(16000)
    const initialized = await resampler.init()
    
    if (!initialized) {
      alert('无法访问麦克风，请检查权限设置')
      return
    }

    // 连接WebSocket
    ws = new WebSocket('ws://localhost:8000/ws/translate')
    
    ws.onopen = () => {
      console.log('WebSocket已连接')
      isConnected.value = true
      
      // 发送模式信息
      ws.send(JSON.stringify({
        type: 'mode',
        mode: mode.value
      }))

      // 开始发送音频
      resampler.start((audioData) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(audioData)
        }
      })
    }

    ws.onmessage = async (event) => {
      if (typeof event.data === 'string') {
        // 接收文本消息
        const data = JSON.parse(event.data)
        if (data.type === 'transcript') {
          messages.value.push({
            timestamp: data.timestamp,
            src_lang: data.src_lang,
            target_lang: data.target_lang,
            original: data.original,
            translated: data.translated
          })
          scrollToBottom()
        }
      } else {
        // 接收音频数据并播放
        const audioBlob = new Blob([event.data], { type: 'audio/mpeg' })
        const audioUrl = URL.createObjectURL(audioBlob)
        
        if (audioPlayer.value) {
          audioPlayer.value.src = audioUrl
          audioPlayer.value.play().catch(err => {
            console.error('播放音频失败:', err)
          })
        }
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error)
      alert('连接失败，请确保后端服务已启动')
      stop()
    }

    ws.onclose = () => {
      console.log('WebSocket已断开')
      isConnected.value = false
    }

  } catch (error) {
    console.error('启动失败:', error)
    alert('启动失败: ' + error.message)
  }
}

const stop = () => {
  if (resampler) {
    resampler.stop()
    resampler = null
  }

  if (ws) {
    ws.close()
    ws = null
  }

  isConnected.value = false
}
</script>
