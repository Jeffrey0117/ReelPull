<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { api } from './api/index.js'

// State
const urlInput = ref('')
const inputMode = ref('url') // 'url' or 'account'
const queue = ref([])
const history = ref([])
const videos = ref([])
const activeTab = ref('queue')
const editingVideo = ref(null)
const editingName = ref('')
const serviceStatus = ref({
  status: 'idle',
  is_running: false,
  current_task: null,
  stats: { completed_count: 0, failed_count: 0, queue_count: 0 }
})
const settings = ref({
  download_path: './downloads',
  headless_mode: false,
  auto_remove: true,
  show_notification: true
})
const isLoading = ref({
  addQueue: false,
  start: false,
  stop: false
})

// Toast
const toasts = ref([])
let toastId = 0

function showToast(message, type = 'info', duration = 3000) {
  const id = ++toastId
  toasts.value.push({ id, message, type })

  if (duration > 0) {
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, duration)
  }
}

function removeToast(id) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

// Modal
const showModal = ref(false)
const modalConfig = ref({ title: '', message: '', onConfirm: null })

function openModal(title, message, onConfirm) {
  modalConfig.value = { title, message, onConfirm }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function confirmModal() {
  if (modalConfig.value.onConfirm) {
    modalConfig.value.onConfirm()
  }
  closeModal()
}

// WebSocket
let ws = null
let reconnectTimer = null

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws = new WebSocket(`${protocol}//${window.location.host}/ws`)

  ws.onopen = () => {
    console.log('WebSocket connected')
  }

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data)
    handleWebSocketMessage(message)
  }

  ws.onclose = () => {
    console.log('WebSocket disconnected, reconnecting...')
    reconnectTimer = setTimeout(connectWebSocket, 3000)
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
}

function handleWebSocketMessage(message) {
  switch (message.type) {
    case 'status_update':
      handleStatusUpdate(message.data)
      break
    case 'download_started':
      serviceStatus.value.status = 'running'
      serviceStatus.value.is_running = true
      showToast('開始下載...', 'info')
      break
    case 'download_stopping':
      serviceStatus.value.status = 'stopping'
      showToast('正在停止...', 'warning')
      break
    case 'download_finished':
      serviceStatus.value.status = 'idle'
      serviceStatus.value.is_running = false
      serviceStatus.value.current_task = null
      const { completed, failed } = message.data
      if (completed > 0 || failed > 0) {
        showToast(`下載完成！成功 ${completed} 個，失敗 ${failed} 個`, completed > 0 ? 'success' : 'error', 5000)
      }
      loadData()
      break
    case 'error':
      showToast(message.data.message, 'error', 5000)
      break
  }
}

function handleStatusUpdate(data) {
  const index = queue.value.findIndex(item => item.id === data.id)
  if (index !== -1) {
    queue.value[index] = {
      ...queue.value[index],
      ...data,
      progress_percent: data.progress_percent || 0
    }

    if (data.status === 'completed') {
      showToast(`下載完成：${data.filename || '影片'}`, 'success')
      history.value.unshift({ ...queue.value[index], ...data })
      if (settings.value.auto_remove) {
        queue.value.splice(index, 1)
      }
    } else if (data.status === 'failed') {
      showToast(`下載失敗：${data.error_message || '未知錯誤'}`, 'error', 5000)
      history.value.unshift({ ...queue.value[index], ...data })
      if (settings.value.auto_remove) {
        queue.value.splice(index, 1)
      }
    }
  }

  // 更新當前任務
  if (data.status === 'processing') {
    serviceStatus.value.current_task = {
      id: data.id,
      url: data.url,
      progress: data.progress_percent || 0,
      step: data.progress
    }
  }
}

// Actions
async function addUrls() {
  const urls = urlInput.value.split('\n').filter(u => u.trim())
  if (urls.length === 0) {
    showToast('請輸入至少一個網址', 'warning')
    return
  }

  isLoading.value.addQueue = true
  try {
    const added = await api.addToQueue(urls)
    if (added.length > 0) {
      queue.value.push(...added)
      urlInput.value = ''
      showToast(`已加入 ${added.length} 個網址`, 'success')
    } else {
      showToast('網址已存在', 'warning')
    }
  } catch (e) {
    showToast('加入失敗：' + (e.message || '請檢查網址格式'), 'error')
  } finally {
    isLoading.value.addQueue = false
  }
}

async function removeItem(id) {
  try {
    await api.removeFromQueue(id)
    queue.value = queue.value.filter(item => item.id !== id)
    showToast('已從佇列移除', 'info')
  } catch (e) {
    showToast('移除失敗', 'error')
  }
}

async function retryItem(id) {
  try {
    const item = await api.retryDownload(id)
    history.value = history.value.filter(h => h.id !== id)
    queue.value.push(item)
    showToast('已加入重試佇列', 'info')
  } catch (e) {
    showToast('重試失敗', 'error')
  }
}

async function startDownload() {
  if (queue.value.length === 0) {
    showToast('佇列是空的，請先加入網址', 'warning')
    return
  }

  isLoading.value.start = true
  try {
    const result = await api.startDownload()
    if (result.success === false) {
      showToast(result.message || '已在執行中', 'warning')
    }
  } catch (e) {
    showToast('啟動失敗：' + e.message, 'error')
  } finally {
    isLoading.value.start = false
  }
}

async function stopDownload() {
  isLoading.value.stop = true
  try {
    await api.stopDownload()
  } catch (e) {
    showToast('停止失敗', 'error')
  } finally {
    isLoading.value.stop = false
  }
}

async function clearHistory() {
  openModal(
    '確認清除',
    '確定要清除所有歷史紀錄嗎？此操作無法復原。',
    async () => {
      try {
        await api.clearHistory()
        history.value = []
        showToast('歷史紀錄已清除', 'success')
      } catch (e) {
        showToast('清除失敗', 'error')
      }
    }
  )
}

async function updateSetting(key, value) {
  settings.value[key] = value
  try {
    await api.updateSettings({ [key]: value })
  } catch (e) {
    showToast('設定更新失敗', 'error')
  }
}

// Videos Management
async function loadVideos() {
  try {
    videos.value = await api.getVideos()
  } catch (e) {
    showToast('載入影片失敗', 'error')
  }
}

function startEdit(video) {
  editingVideo.value = video.filename
  // 移除副檔名方便編輯
  const name = video.filename
  const lastDot = name.lastIndexOf('.')
  editingName.value = lastDot > 0 ? name.substring(0, lastDot) : name
}

function cancelEdit() {
  editingVideo.value = null
  editingName.value = ''
}

async function saveRename(oldFilename) {
  if (!editingName.value.trim()) {
    showToast('名稱不能為空', 'warning')
    return
  }

  try {
    const result = await api.renameVideo(oldFilename, editingName.value.trim())
    showToast('重命名成功', 'success')
    // 更新列表中的檔名
    const video = videos.value.find(v => v.filename === oldFilename)
    if (video) {
      video.filename = result.new_filename
    }
    cancelEdit()
  } catch (e) {
    showToast('重命名失敗：' + e.message, 'error')
  }
}

async function deleteVideo(filename) {
  openModal(
    '確認刪除',
    `確定要刪除影片「${filename}」嗎？此操作無法復原。`,
    async () => {
      try {
        await api.deleteVideo(filename)
        videos.value = videos.value.filter(v => v.filename !== filename)
        showToast('影片已刪除', 'success')
      } catch (e) {
        showToast('刪除失敗：' + e.message, 'error')
      }
    }
  )
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// Load initial data
async function loadData() {
  try {
    const [queueData, historyData, settingsData, statusData, videosData] = await Promise.all([
      api.getQueue(),
      api.getHistory(),
      api.getSettings(),
      api.getDownloadStatus(),
      api.getVideos()
    ])
    queue.value = queueData
    history.value = historyData
    settings.value = settingsData
    serviceStatus.value = statusData
    videos.value = videosData
  } catch (e) {
    showToast('載入資料失敗', 'error')
  }
}

// Computed
const isRunning = computed(() => serviceStatus.value.is_running)
const isStopping = computed(() => serviceStatus.value.status === 'stopping')
const currentTask = computed(() => serviceStatus.value.current_task)
const pendingCount = computed(() => queue.value.filter(i => i.status === 'pending').length)

// Helpers
function getStatusIcon(status) {
  switch (status) {
    case 'pending': return '⏳'
    case 'processing': return '🔄'
    case 'completed': return '✅'
    case 'failed': return '❌'
    default: return '❓'
  }
}

function formatUrl(url) {
  return url.length > 45 ? url.substring(0, 45) + '...' : url
}

function getToastClass(type) {
  return {
    'toast-success': type === 'success',
    'toast-error': type === 'error',
    'toast-warning': type === 'warning',
    'toast-info': type === 'info'
  }
}

// Lifecycle
onMounted(() => {
  loadData()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) ws.close()
  if (reconnectTimer) clearTimeout(reconnectTimer)
})
</script>

<template>
  <div class="container">
    <!-- Toast Container -->
    <div class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="getToastClass(toast.type)"
      >
        <span class="toast-icon">
          {{ toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : toast.type === 'warning' ? '⚠️' : 'ℹ️' }}
        </span>
        <span class="toast-message">{{ toast.message }}</span>
        <button class="toast-close" @click="removeToast(toast.id)">×</button>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3 class="modal-title">{{ modalConfig.title }}</h3>
        <p class="modal-message">{{ modalConfig.message }}</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closeModal">取消</button>
          <button class="btn btn-danger" @click="confirmModal">確認</button>
        </div>
      </div>
    </div>

    <!-- Header -->
    <header class="header">
      <h1>ReelPull</h1>
      <p>Download Instagram Reels</p>
    </header>

    <!-- Mode Toggle -->
    <div class="mode-toggle">
      <button
        :class="['mode-btn', { active: inputMode === 'url' }]"
        @click="inputMode = 'url'"
      >網址</button>
      <button
        :class="['mode-btn', { active: inputMode === 'account' }]"
        @click="inputMode = 'account'"
      >帳號</button>
    </div>

    <!-- URL Input -->
    <div v-if="inputMode === 'url'" class="input-section">
      <textarea
        v-model="urlInput"
        class="url-input"
        placeholder="貼上 Instagram Reel 網址..."
        :disabled="isLoading.addQueue"
      ></textarea>

      <div class="btn-group">
        <button
          class="btn btn-primary"
          @click="addUrls"
          :disabled="!urlInput.trim() || isLoading.addQueue"
        >
          <span v-if="isLoading.addQueue" class="spinner"></span>
          {{ isLoading.addQueue ? '加入中...' : '加入佇列' }}
        </button>

        <button
          v-if="!isRunning"
          class="btn btn-secondary"
          @click="startDownload"
          :disabled="queue.length === 0 || isLoading.start"
        >
          <span v-if="isLoading.start" class="spinner"></span>
          {{ isLoading.start ? '啟動中...' : '開始下載' }}
        </button>

        <button
          v-else
          class="btn btn-danger"
          @click="stopDownload"
          :disabled="isStopping || isLoading.stop"
        >
          <span v-if="isLoading.stop" class="spinner"></span>
          {{ isStopping ? '停止中...' : '停止' }}
        </button>
      </div>
    </div>

    <!-- Account Mode - 提示用外部工具 -->
    <div v-else class="input-section">
      <div class="external-tool-hint">
        <p class="hint-title">如何批量下載帳號的所有 Reels？</p>
        <ol class="hint-steps">
          <li>前往 <a href="https://saveclip.app/zh-tw/instagram-reels-download" target="_blank">SaveClip.app</a></li>
          <li>貼上帳號的 Reels 頁面網址（如 instagram.com/帳號/reels/）</li>
          <li>依照指示複製頁面源碼</li>
          <li>取得所有 Reel 連結後，切回「網址」模式貼上</li>
        </ol>
        <button class="btn btn-secondary" @click="inputMode = 'url'">
          切換到網址模式
        </button>
      </div>
    </div>

    <!-- Progress -->
    <div v-if="currentTask" class="progress-section">
      <div class="progress-url">{{ formatUrl(currentTask.url) }}</div>
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: currentTask.progress + '%' }"></div>
      </div>
      <div class="progress-info">
        <span>{{ currentTask.step }}</span>
        <span>{{ currentTask.progress }}%</span>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab" :class="{ active: activeTab === 'queue' }" @click="activeTab = 'queue'">
        佇列 ({{ queue.length }})
      </button>
      <button class="tab" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
        歷史 ({{ history.length }})
      </button>
      <button class="tab" :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">
        設定
      </button>
    </div>

    <!-- Queue -->
    <section v-if="activeTab === 'queue'" class="section">
      <div v-if="queue.length === 0" class="empty-state">
        <div class="empty-title">佇列是空的</div>
        <div class="empty-desc">貼上網址開始下載</div>
      </div>

      <div v-else>
        <div v-for="item in queue" :key="item.id" class="queue-item">
          <span class="queue-icon">{{ getStatusIcon(item.status) }}</span>
          <div class="queue-content">
            <div class="queue-url">{{ formatUrl(item.url) }}</div>
            <div class="queue-status" :class="'status-' + item.status">
              <template v-if="item.status === 'pending'">等待中</template>
              <template v-else-if="item.status === 'processing'">
                <div class="mini-progress">
                  <div class="mini-progress-bar" :style="{ width: (item.progress_percent || 0) + '%' }"></div>
                </div>
                <span>{{ item.progress || '處理中' }}</span>
              </template>
              <template v-else-if="item.status === 'completed'">{{ item.filename }}</template>
              <template v-else-if="item.status === 'failed'">{{ item.error_message }}</template>
            </div>
          </div>
          <button
            class="btn btn-secondary btn-small"
            @click="removeItem(item.id)"
            :disabled="item.status === 'processing'"
          >刪除</button>
        </div>
      </div>
    </section>

    <!-- History -->
    <section v-if="activeTab === 'history'" class="section">
      <div v-if="history.length === 0" class="empty-state">
        <div class="empty-title">沒有紀錄</div>
      </div>

      <div v-else>
        <div class="section-header">
          <span></span>
          <button class="btn btn-secondary btn-small" @click="clearHistory">清除</button>
        </div>
        <div v-for="item in history" :key="item.id" class="queue-item">
          <span class="queue-icon">{{ getStatusIcon(item.status) }}</span>
          <div class="queue-content">
            <div class="queue-url">{{ formatUrl(item.url) }}</div>
            <div class="queue-status" :class="'status-' + item.status">
              <template v-if="item.status === 'completed'">{{ item.filename }}</template>
              <template v-else>{{ item.error_message }}</template>
            </div>
          </div>
          <button v-if="item.status === 'failed'" class="btn btn-secondary btn-small" @click="retryItem(item.id)">重試</button>
        </div>
      </div>
    </section>

    <!-- Settings Section -->
    <section v-if="activeTab === 'settings'" class="section">
      <div class="setting-item">
        <span class="setting-label">下載路徑</span>
        <span class="setting-value">{{ settings.download_path }}</span>
      </div>

      <div class="setting-item">
        <span class="setting-label">下載完成後自動從佇列移除</span>
        <label class="toggle">
          <input type="checkbox" :checked="settings.auto_remove" @change="updateSetting('auto_remove', $event.target.checked)">
          <span class="toggle-slider"></span>
        </label>
      </div>

      <div class="setting-item">
        <span class="setting-label">無頭模式（隱藏瀏覽器視窗）</span>
        <label class="toggle">
          <input type="checkbox" :checked="settings.headless_mode" @change="updateSetting('headless_mode', $event.target.checked)">
          <span class="toggle-slider"></span>
        </label>
      </div>

      <div class="setting-item">
        <span class="setting-label">顯示通知</span>
        <label class="toggle">
          <input type="checkbox" :checked="settings.show_notification" @change="updateSetting('show_notification', $event.target.checked)">
          <span class="toggle-slider"></span>
        </label>
      </div>
    </section>
  </div>
</template>
