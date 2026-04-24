<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 p-8">
    <div class="container mx-auto max-w-4xl">
      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-purple-900 mb-2">🧪 BabelBridge 测试页面</h1>
        <p class="text-gray-600">测试翻译和语音识别功能</p>
        <div class="mt-2 flex justify-center gap-4">
          <router-link to="/" class="text-blue-600 hover:underline">← 返回主页</router-link>
          <router-link to="/history" class="text-blue-600 hover:underline">📚 历史记录</router-link>
        </div>
      </div>

      <!-- 文本翻译测试 -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">📝 文本翻译测试</h2>
        
        <div class="space-y-4">
          <!-- 输入区域 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">输入文本</label>
            <textarea
              v-model="inputText"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              rows="4"
              placeholder="输入要翻译的文本..."
            ></textarea>
          </div>

          <!-- 语言选择 -->
          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-2">源语言</label>
              <select
                v-model="srcLang"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="auto">自动检测</option>
                <option value="zh">中文</option>
                <option value="en">英语</option>
                <option value="th">泰语</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-2">目标语言</label>
              <select
                v-model="targetLang"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="zh">中文</option>
                <option value="en">英语</option>
                <option value="th">泰语</option>
              </select>
            </div>
          </div>

          <!-- 翻译按钮 -->
          <button
            @click="translateText"
            :disabled="translating || !inputText"
            class="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ translating ? '翻译中...' : '翻译' }}
          </button>

          <!-- 翻译结果 -->
          <div v-if="translationResult" class="mt-4 p-4 bg-purple-50 rounded-lg">
            <div class="text-sm text-gray-600 mb-2">
              翻译结果 ({{ translationResult.src_lang }} → {{ translationResult.target_lang }})
            </div>
            <div class="text-lg text-gray-800">{{ translationResult.translated }}</div>
          </div>

          <!-- 错误提示 -->
          <div v-if="translationError" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {{ translationError }}
          </div>
        </div>
      </div>

      <!-- 音频文件测试 -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">🎤 音频转文字测试</h2>
        
        <div class="space-y-4">
          <!-- 文件上传 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">上传音频文件</label>
            <input
              type="file"
              @change="handleFileUpload"
              accept="audio/*,.wav,.mp3,.m4a,.ogg"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <p class="text-sm text-gray-500 mt-2">支持格式: WAV, MP3, M4A, OGG</p>
          </div>

          <!-- 上传按钮 -->
          <button
            @click="transcribeAudio"
            :disabled="transcribing || !audioFile"
            class="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ transcribing ? '识别中...' : '开始识别' }}
          </button>

          <!-- 识别结果 -->
          <div v-if="transcriptionResult" class="mt-4 p-4 bg-green-50 rounded-lg">
            <div class="text-sm text-gray-600 mb-2">
              识别结果 (语言: {{ transcriptionResult.language }})
            </div>
            <div class="text-lg text-gray-800">{{ transcriptionResult.text }}</div>
            <div class="text-sm text-gray-500 mt-2">文件: {{ transcriptionResult.filename }}</div>
          </div>

          <!-- 错误提示 -->
          <div v-if="transcriptionError" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {{ transcriptionError }}
          </div>
        </div>
      </div>

      <!-- 测试统计 -->
      <div class="mt-6 bg-white rounded-lg shadow-lg p-6">
        <h3 class="text-xl font-semibold text-gray-800 mb-4">📊 测试统计</h3>
        <div class="grid grid-cols-2 gap-4">
          <div class="p-4 bg-blue-50 rounded-lg">
            <div class="text-sm text-gray-600">翻译次数</div>
            <div class="text-2xl font-bold text-blue-600">{{ stats.translations }}</div>
          </div>
          <div class="p-4 bg-green-50 rounded-lg">
            <div class="text-sm text-gray-600">识别次数</div>
            <div class="text-2xl font-bold text-green-600">{{ stats.transcriptions }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 文本翻译
const inputText = ref('')
const srcLang = ref('auto')
const targetLang = ref('en')
const translating = ref(false)
const translationResult = ref(null)
const translationError = ref('')

// 音频识别
const audioFile = ref(null)
const transcribing = ref(false)
const transcriptionResult = ref(null)
const transcriptionError = ref('')

// 统计
const stats = ref({
  translations: 0,
  transcriptions: 0
})

const translateText = async () => {
  if (!inputText.value) return
  
  translating.value = true
  translationError.value = ''
  translationResult.value = null
  
  try {
    const response = await fetch('http://localhost:8000/api/translate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: inputText.value,
        src_lang: srcLang.value,
        target_lang: targetLang.value
      })
    })
    
    const data = await response.json()
    
    if (data.error) {
      translationError.value = data.error
    } else {
      translationResult.value = data
      stats.value.translations++
    }
  } catch (error) {
    translationError.value = '翻译失败: ' + error.message
  } finally {
    translating.value = false
  }
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    audioFile.value = file
    transcriptionResult.value = null
    transcriptionError.value = ''
  }
}

const transcribeAudio = async () => {
  if (!audioFile.value) return
  
  transcribing.value = true
  transcriptionError.value = ''
  transcriptionResult.value = null
  
  try {
    const formData = new FormData()
    formData.append('file', audioFile.value)
    
    const response = await fetch('http://localhost:8000/api/transcribe', {
      method: 'POST',
      body: formData
    })
    
    const data = await response.json()
    
    if (data.error) {
      transcriptionError.value = data.error
    } else {
      transcriptionResult.value = data
      stats.value.transcriptions++
    }
  } catch (error) {
    transcriptionError.value = '识别失败: ' + error.message
  } finally {
    transcribing.value = false
  }
}
</script>
