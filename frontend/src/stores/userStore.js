import { defineStore } from 'pinia'

// ========== 工具函数 ==========
function isBridgeReady() {
  return typeof window !== 'undefined'
    && window.pywebview
    && window.pywebview.api
    && typeof window.pywebview.api.api_get_tasks === 'function'
}

// ========== API 适配器 ==========
const STORAGE_KEY_USER = 'todomaster_user'
const STORAGE_KEY_TOKEN = 'todomaster_token'

/** localStorage 模式 */
const localAdapter = {
  _read(key) {
    try { return JSON.parse(localStorage.getItem(key) || 'null') } catch { return null }
  },
  _write(key, val) {
    localStorage.setItem(key, JSON.stringify(val))
  },
  _remove(key) {
    localStorage.removeItem(key)
  },
  getUser() {
    const user = this._read(STORAGE_KEY_USER)
    const token = this._read(STORAGE_KEY_TOKEN)
    return Promise.resolve({ user, token })
  },
  register(prefix, password) {
    if (!prefix.trim()) throw new Error('用户名不能为空')
    if (!password || password.length < 4) throw new Error('密码至少4位')
    const suffix = String(Math.floor(10000 + Math.random() * 90000))
    const user = { user_id: `${prefix}#${suffix}`, prefix, created_at: new Date().toISOString() }
    const token = 'tok_' + (crypto?.randomUUID?.() || Date.now())
    this._write(STORAGE_KEY_USER, user)
    this._write(STORAGE_KEY_TOKEN, token)
    return Promise.resolve({ user, token })
  },
  login(userId, password) {
    const user = this._read(STORAGE_KEY_USER)
    if (!user || user.user_id !== userId) throw new Error('用户不存在')
    if (!password || password.length < 4) throw new Error('密码错误')
    const token = 'tok_' + (crypto?.randomUUID?.() || Date.now())
    this._write(STORAGE_KEY_TOKEN, token)
    return Promise.resolve({ user, token })
  },
  logout() {
    this._remove(STORAGE_KEY_USER)
    this._remove(STORAGE_KEY_TOKEN)
    return Promise.resolve()
  },
}

/** PyWebView 模式——同步调用 */
const bridgeAdapter = {
  getUser() {
    const user = localAdapter._read(STORAGE_KEY_USER)
    const token = localAdapter._read(STORAGE_KEY_TOKEN)
    return { user, token }
  },
  register(prefix, password) {
    return window.pywebview.api.api_register({ prefix, password })
  },
  login(userId, password) {
    return window.pywebview.api.api_login({ user_id: userId, password })
  },
  logout() {
    window.pywebview.api.api_logout({})
  },
}

function getAdapter() {
  if (isBridgeReady()) return bridgeAdapter
  return localAdapter
}

// ========== Pinia Store ==========
export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: null,
    showSettings: false,
  }),

  getters: {
    isLoggedIn: (s) => !!s.token,
    displayName: (s) => s.user?.prefix || '游客',
  },

  actions: {
    async loadUser() {
      const adapter = getAdapter()
      const { user, token } = await adapter.getUser()
      this.user = user
      this.token = token
    },
    async register(prefix, password) {
      const adapter = getAdapter()
      const result = await adapter.register(prefix.trim(), password)
      this.user = result.user
      this.token = result.token
    },
    async login(userId, password) {
      const adapter = getAdapter()
      const result = await adapter.login(userId.trim(), password)
      this.user = result.user
      this.token = result.token
    },
    async logout() {
      const adapter = getAdapter()
      await adapter.logout()
      this.user = null
      this.token = null
      this.showSettings = false
    },
    toggleSettings() {
      this.showSettings = !this.showSettings
    },
  },
})