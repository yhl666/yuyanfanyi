<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-teal-100 p-8">
    <div class="container mx-auto max-w-6xl">
      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-green-900 mb-2">📚 历史对话记录</h1>
        <p class="text-gray-600">查看和搜索历史翻译记录</p>
        <div class="mt-4 flex justify-center gap-4">
          <router-link to="/" class="text-blue-600 hover:underline">← 返回主页</router-link>
          <router-link to="/test" class="text-blue-600 hover:underline">🧪 测试页面</router-link>
        </div>
      </div>

      <!-- 统计信息 -->
      <div v-if="stats" class="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">📊 统计信息</h2>
        <div class="grid grid-cols-3 gap-4">
          <div class="p-4 bg-blue-50 rounded-lg text-center">
            <div class="text-sm text-gray-600">总记录数</div>
            <div class="text-3xl font-bold text-blue-600">{{ stats.total }}</div>
          </div>
          <div class="p-4 bg-green-50 rounded-lg text-center">
            <div class="text-sm text-gray-600">中英模式</div>
            <div class="text-3xl font-bold text-green-600">{{ stats.by_mode['zh-en'] || 0 }}</div>
          </div>
          <div class="p-4 bg-purple-50 rounded-lg text-center">
            <div class="text-sm text-gray-600">中泰模式</div>
            <div class="text-3xl font-bold text-purple-600">{{ stats.by_mode['zh-th'] || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div class="flex gap-4">
          <!-- 日期选择 -->
          <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700 mb-2">选择日期</label>
            <select
              v-model="selectedDate"
              @change="loadHistory"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">全部日期</option>
              <option v-for="date in dates" :key="date.date" :value="date.date">
                {{ date.formatted }} ({{ date.file }})
              </option>
            </select>
          </div>

          <!-- 搜索框 -->
          <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700 mb-2">搜索关键词</label>
            <div class="flex gap-2">
              <input
                v-model="searchKeyword"
                @keyup.enter="searchHistory"
                type="text"
                placeholder="输入关键词搜索..."
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                @click="searchHistory"
                class="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
              >
                搜索
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 记录列表 -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold text-gray-800">
            对话记录 
            <span v-if="records.length > 0" class="text-sm text-gray-500">(共 {{ records.length }} 条)</span>
          </h2>
          <button
            v-if="records.length > 0"
            @click="exportRecords"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
          >
            📥 导出记录
          </button>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="text-center py-8 text-gray-500">
          加载中...
        </div>

        <!-- 记录列表 -->
        <div v-else-if="records.length > 0" class="space-y-4 max-h-[600px] overflow-y-auto">
          <div
            v-for="(record, index) in records"
            :key="index"
            class="border-l-4 border-green-400 bg-gray-50 p-4 rounded-r-lg hover:bg-gray-100 transition-colors"
          >
            <div class="flex justify-between items-start mb-2">
              <span class="text-xs text-gray-500">{{ formatTime(record.timestamp) }}</span>
              <div class="flex gap-2">
                <span class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                  {{ getModeText(record.mode) }}
                </span>
                <span class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                  {{ getLangName(record.src_lang) }} → {{ getTargetLang(record.mode, record.src_lang) }}
                </span>
              </div>
            </div>
            <div class="space-y-2">
              <p class="text-gray-800">
                <span class="font-medium">原文:</span> {{ record.original }}
              </p>
              <p class="text-green-700">
                <span class="font-medium">译文:</span> {{ record.translated }}
              </p>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="text-center py-12 text-gray-400">
          <div class="text-6xl mb-4">📭</div>
          <div class="text-lg">暂无记录</div>
          <div class="text-sm mt-2">{{ selectedDate ? '该日期没有对话记录' : '开始使用翻译功能后会显示记录' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const dates = ref([])
const selectedDate = ref('')
const searchKeyword = ref('')
const records = ref([])
const stats = ref(null)
const loading = ref(false)

const getModeText = (mode) => {
  const modes = {
    'zh-th': '中文⇄泰语',
    'zh-en': '中文⇄英语'
  }
  return modes[mode] || mode
}

const getLangName = (lang) => {
  const names = {
    'zh': '中文',
    'th': '泰语',
    'en': '英语'
  }
  return names[lang] || lang
}

const getTargetLang = (mode, srcLang) => {
  if (mode === 'zh-en') {
    return srcLang === 'zh' ? '英语' : '中文'
  } else if (mode === 'zh-th') {
    return srcLang === 'zh' ? '泰语' : '中文'
  }
  return '未知'
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const loadDates = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/history/dates')
    const data = await response.json()
    if (data.success) {
      dates.value = data.dates
    }
  } catch (error) {
    console.error('加载日期列表失败:', error)
  }
}

const loadHistory = async () => {
  if (!selectedDate.value) {
    records.value = []
    return
  }

  loading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/history/${selectedDate.value}`)
    const data = await response.json()
    if (data.success) {
      records.value = data.records
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

const searchHistory = async () => {
  if (!searchKeyword.value.trim()) {
    if (selectedDate.value) {
      loadHistory()
    }
    return
  }

  loading.value = true
  try {
    const url = selectedDate.value
      ? `http://localhost:8000/api/history/search/${encodeURIComponent(searchKeyword.value)}?date=${selectedDate.value}`
      : `http://localhost:8000/api/history/search/${encodeURIComponent(searchKeyword.value)}`
    
    const response = await fetch(url)
    const data = await response.json()
    if (data.success) {
      records.value = data.results
    }
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/history/stats')
    const data = await response.json()
    if (data.success) {
      stats.value = data.stats
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const exportRecords = () => {
  const dataStr = JSON.stringify(records.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `history_${selectedDate.value || 'all'}.json`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadDates()
  loadStats()
})
</script>
