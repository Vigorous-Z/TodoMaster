import { defineStore } from 'pinia'

// ========== 工具函数 ==========
function fmt(d) {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

// ========== API 适配器 ==========
const STORAGE_KEY = 'todomaster_tasks'

/** localStorage 模式（Vite 开发环境无 PyWebView 时使用） */
const localAdapter = {
  _read() {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try { return JSON.parse(saved) } catch { return [] }
    }
    return []
  },
  _write(tasks) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks))
  },
  getTasks() {
    return Promise.resolve(this._read())
  },
  addTask(title, due, priority, tags, project, description) {
    const tasks = this._read()
    const newTask = {
      id: String(Date.now()),
      title,
      due: due || fmt(new Date()) + ' 23:59',
      priority: priority || 'medium',
      tags: tags || [],
      project: project || 'personal',
      description: description || '',
      done: false,
    }
    tasks.unshift(newTask)
    this._write(tasks)
    return Promise.resolve(newTask)
  },
  toggleTask(id) {
    const tasks = this._read()
    const task = tasks.find(t => t.id === id)
    if (task) {
      task.done = !task.done
      this._write(tasks)
    }
    return Promise.resolve()
  },
  deleteTask(id) {
    const tasks = this._read()
    const idx = tasks.findIndex(t => t.id === id)
    if (idx !== -1) {
      tasks.splice(idx, 1)
      this._write(tasks)
    }
    return Promise.resolve()
  },
  updateTask(id, data) {
    const tasks = this._read()
    const idx = tasks.findIndex(t => t.id === id)
    if (idx !== -1) {
      tasks[idx] = { ...tasks[idx], ...data }
      this._write(tasks)
    }
    return Promise.resolve()
  },
}

/** PyWebView 模式——js_api 同步调用 */
const bridgeAdapter = {
  getTasks(ownerId) {
    const raw = window.pywebview.api.api_get_tasks(ownerId ? { owner_id: ownerId } : {})
    return raw || []
  },
  getGuestTaskCount() {
    return window.pywebview.api.api_get_guest_task_count({})
  },
  bindGuestTasks(ownerId) {
    return window.pywebview.api.api_bind_guest_tasks({ owner_id: ownerId })
  },
  unbindUserTasks(ownerId) {
    return window.pywebview.api.api_unbind_user_tasks({ owner_id: ownerId })
  },
  addTask(title, due, priority, tags, project, description, ownerId) {
    return window.pywebview.api.api_add_task({
      title,
      due_date: due || fmt(new Date()) + ' 23:59',
      priority: priority || 'medium',
      tags: tags || [],
      project: project || 'personal',
      description: description || '',
      user_id: ownerId || null,
    })
  },
  toggleTask(id) {
    return window.pywebview.api.api_toggle_task(id)
  },
  deleteTask(id) {
    window.pywebview.api.api_delete_task(id)
  },
  updateTask(id, data) {
    return window.pywebview.api.api_update_task(id, data)
  },
  cloudSync(userId) {
    return window.pywebview.api.api_cloud_sync({ user_id: userId })
  },
  cloudPull(userId) {
    return window.pywebview.api.api_cloud_pull({ user_id: userId })
  },
  cloudPush(userId) {
    return window.pywebview.api.api_cloud_push({ user_id: userId })
  },
}

/** 就绪检测：PyWebView 注入 api 是异步的，轮询等待 */
function isBridgeReady() {
  return typeof window !== 'undefined'
    && window.pywebview
    && window.pywebview.api
    && typeof window.pywebview.api.api_get_tasks === 'function'
}

function getAdapter() {
  if (isBridgeReady()) return bridgeAdapter
  return localAdapter
}

// ========== Pinia Store ==========
export const useTaskStore = defineStore('task', {
  state: () => ({
    tasks: [],
    currentView: 'today',
    selectedTaskId: null,
    currentOwnerId: null,
    syncStatus: 'idle',  // idle | syncing | done
  }),

  getters: {
    filteredTasks(state) {
      const todayStr = fmt(new Date())
      const view = state.currentView
      switch (view) {
        case 'today':
          return state.tasks.filter(t => !t.done && t.due && t.due.startsWith(todayStr))
        case 'upcoming':
          return state.tasks.filter(t => !t.done && t.due && t.due > todayStr + ' 23:59')
            .sort((a, b) => a.due.localeCompare(b.due))
        case 'all':
          return [...state.tasks.filter(t => !t.done), ...state.tasks.filter(t => t.done)]
        case 'done':
          return state.tasks.filter(t => t.done)
        case 'work':
        case 'personal':
        case 'learn':
          return state.tasks.filter(t => t.project === view && !t.done)
        default:
          return state.tasks
      }
    },
    selectedTask(state) {
      return state.tasks.find(t => t.id === state.selectedTaskId) || null
    },
    counts(state) {
      const views = ['today', 'upcoming', 'all', 'done', 'work', 'personal', 'learn']
      const result = {}
      const todayStr = fmt(new Date())
      for (const v of views) {
        let filtered = []
        switch (v) {
          case 'today':
            filtered = state.tasks.filter(t => !t.done && t.due && t.due.startsWith(todayStr))
            break
          case 'upcoming':
            filtered = state.tasks.filter(t => !t.done && t.due && t.due > todayStr + ' 23:59')
            break
          case 'all':
            filtered = [...state.tasks.filter(t => !t.done), ...state.tasks.filter(t => t.done)]
            break
          case 'done':
            filtered = state.tasks.filter(t => t.done)
            break
          case 'work':
          case 'personal':
          case 'learn':
            filtered = state.tasks.filter(t => t.project === v && !t.done)
            break
        }
        result[v] = filtered.length
      }
      return result
    },
  },

  actions: {
    async loadTasks(ownerId) {
      let adapter = getAdapter()
      let data = await adapter.getTasks(ownerId)
      if (!isBridgeReady() && data.length === 0) {
        await new Promise(r => setTimeout(r, 300))
        if (isBridgeReady()) {
          adapter = bridgeAdapter
          data = adapter.getTasks(ownerId)
        }
      }
      this.tasks = data
      this.currentOwnerId = ownerId || null
    },
    async addTask(title, due, priority, tags, description, project) {
      const adapter = getAdapter()
      await adapter.addTask(title, due, priority, tags, project || 'personal', description || '', this.currentOwnerId)
      await this.loadTasks(this.currentOwnerId)
    },
    async toggleTask(id) {
      const task = this.tasks.find(t => t.id === id)
      if (task) {
        task.done = !task.done
        const adapter = getAdapter()
        await adapter.toggleTask(id)
      }
    },
    async deleteTask(id) {
      this.tasks = this.tasks.filter(t => t.id !== id)
      if (this.selectedTaskId === id) this.selectedTaskId = null
      const adapter = getAdapter()
      await adapter.deleteTask(id)
    },
    async updateTask(id, data) {
      const adapter = getAdapter()
      await adapter.updateTask(id, data)
      await this.loadTasks(this.currentOwnerId)
    },
    async bindGuestTasks(ownerId) {
      if (isBridgeReady() && ownerId) {
        bridgeAdapter.bindGuestTasks(ownerId)
        await this.loadTasks(ownerId)
      }
    },
    async getGuestTaskCount() {
      if (isBridgeReady()) {
        return bridgeAdapter.getGuestTaskCount()
      }
      return 0
    },
    async cloudSync() {
      if (!isBridgeReady() || !this.currentOwnerId) return
      this.syncStatus = 'syncing'
      try {
        const result = bridgeAdapter.cloudSync(this.currentOwnerId)
        await this.loadTasks(this.currentOwnerId)
        this.syncStatus = 'done'
        setTimeout(() => { this.syncStatus = 'idle' }, 3000)
        return result
      } catch {
        this.syncStatus = 'idle'
      }
    },
    async cloudPull() {
      if (!isBridgeReady() || !this.currentOwnerId) return { count: 0 }
      const result = bridgeAdapter.cloudPull(this.currentOwnerId)
      await this.loadTasks(this.currentOwnerId)
      return result
    },
    async cloudPush() {
      if (!isBridgeReady() || !this.currentOwnerId) return { count: 0 }
      return bridgeAdapter.cloudPush(this.currentOwnerId)
    },
    setView(view) {
      this.currentView = view
    },
    selectTask(id) {
      this.selectedTaskId = id
    },
    closeDetail() {
      this.selectedTaskId = null
    },
  },
})