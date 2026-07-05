<template>
  <aside class="sidebar">
    <div class="sidebar-brand">TodoMaster</div>
    <div class="settings-header">
      <span class="settings-title">设置</span>
      <button class="settings-close" @click="userStore.toggleSettings()">&times;</button>
    </div>
    <div class="settings-body">

      <!-- 已登录 -->
      <template v-if="userStore.isLoggedIn">
        <div class="settings-user">
          <div class="user-avatar">{{ userStore.displayName.charAt(0) }}</div>
          <div class="user-info">
            <div class="user-id">{{ userStore.user?.user_id }}</div>
            <div class="user-label">已登录</div>
          </div>
        </div>
        <button class="btn-logout" @click="doLogout">退出登录</button>
      </template>

      <!-- 未登录 -->
      <template v-else>
        <div class="settings-tabs">
          <button :class="{ active: tab === 'login' }" @click="tab = 'login'">登录</button>
          <button :class="{ active: tab === 'register' }" @click="tab = 'register'">注册</button>
        </div>

        <!-- 登录表单 -->
        <form v-if="tab === 'login'" class="settings-form" @submit.prevent="doLogin">
          <label>用户 ID</label>
          <input v-model="loginId" placeholder="用户名#12345" />
          <label>密码</label>
          <input v-model="loginPwd" type="password" placeholder="输入密码" />
          <p v-if="error" class="form-error">{{ error }}</p>
          <button type="submit" class="btn-submit">登录</button>
        </form>

        <!-- 注册表单 -->
        <form v-else class="settings-form" @submit.prevent="doRegister">
          <label>用户名</label>
          <input v-model="regPrefix" placeholder="自定义用户名（不含 # 号）" />
          <label>密码</label>
          <input v-model="regPwd" type="password" placeholder="至少4位" />
          <p v-if="showId" class="form-hint">你的 ID 将为：{{ showId }}</p>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button type="submit" class="btn-submit">注册</button>
        </form>
      </template>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '../stores/userStore'
import { useTaskStore } from '../stores/taskStore'

const userStore = useUserStore()
const taskStore = useTaskStore()

const tab = ref('login')
const error = ref('')
const showId = ref('')

// 登录
const loginId = ref('')
const loginPwd = ref('')

async function doLogin() {
  error.value = ''
  try {
    await userStore.login(loginId.value.trim(), loginPwd.value)
    loginId.value = ''
    loginPwd.value = ''
    const uid = userStore.user?.user_id
    // 先加载本地数据
    await taskStore.loadTasks(uid)
    const localCount = taskStore.tasks.length
    // 从云端拉取——云端优先
    const result = await taskStore.cloudPull()
    const cloudCount = result?.count || 0
    // 云端空但本地有数据：首次使用，把本地数据推到云端
    if (cloudCount === 0 && localCount > 0) {
      await taskStore.cloudPush()
      await taskStore.loadTasks(uid)
    }
  } catch (e) {
    error.value = e.message
  }
}

// 注册
const regPrefix = ref('')
const regPwd = ref('')

async function doRegister() {
  error.value = ''
  try {
    await userStore.register(regPrefix.value.trim(), regPwd.value)
    const uid = userStore.user?.user_id
    // 新账号独立数据空间，加载空任务列表
    await taskStore.loadTasks(uid)
    regPrefix.value = ''
    regPwd.value = ''
    showId.value = ''
  } catch (e) {
    error.value = e.message
  }
}

async function doLogout() {
  const currentUid = userStore.user?.user_id
  await userStore.logout()
  // 不修改任务归属——只切换视图到游客任务列表
  await taskStore.loadTasks()
}
</script>

<style scoped>
.sidebar {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  user-select: none;
  overflow-y: auto;
  z-index: 10;
  transform: translateX(-100%);
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
}

.sidebar-brand {
  padding: 20px 20px 16px;
  font-size: 15px;
  font-weight: 650;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px 12px;
}

.settings-title {
  font-size: 13px;
  font-weight: 550;
  color: var(--text-secondary);
}

.settings-close {
  width: 24px; height: 24px;
  border: none; background: transparent;
  font-size: 16px; cursor: pointer;
  color: var(--text-tertiary);
  border-radius: var(--radius-sm);
}
.settings-close:hover { background: var(--bg-hover); }

.settings-body {
  flex: 1;
  padding: 0 20px 20px;
  overflow-y: auto;
}

/* 用户信息 */
.settings-user {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  margin-bottom: 12px;
}

.user-avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: var(--accent-subtle);
  color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-weight: 600; font-size: 16px;
}

.user-id { font-size: 14px; font-weight: 500; }
.user-label { font-size: 11px; color: var(--text-tertiary); margin-top: 1px; }

.btn-logout {
  width: 100%; border: 1px solid var(--border);
  background: var(--bg-page);
  border-radius: var(--radius-sm);
  padding: 6px 0; font-size: 13px;
  cursor: pointer; color: var(--text-secondary);
}
.btn-logout:hover { background: var(--bg-hover); }

/* 标签切换 */
.settings-tabs {
  display: flex; gap: 4px; margin-bottom: 12px;
  background: var(--bg-active); border-radius: var(--radius-sm);
  padding: 3px;
}

.settings-tabs button {
  flex: 1; border: none; background: transparent;
  padding: 5px 0; font-size: 12px; font-family: inherit;
  color: var(--text-tertiary); cursor: pointer;
  border-radius: var(--radius-sm); transition: all var(--transition);
}
.settings-tabs button.active {
  background: var(--bg-surface); color: var(--text-primary);
  font-weight: 500; box-shadow: 0 1px 2px rgba(0,0,0,.06);
}

/* 表单 */
.settings-form {
  display: flex; flex-direction: column; gap: 6px;
}

.settings-form label {
  font-size: 11px; font-weight: 550;
  text-transform: uppercase; letter-spacing: 0.04em;
  color: var(--text-tertiary);
}

.settings-form input {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 6px 10px; font-size: 13px;
  font-family: inherit; color: var(--text-primary);
  background: var(--bg-surface); outline: none;
}
.settings-form input:focus { border-color: var(--accent); }

.btn-submit {
  margin-top: 6px; border: none;
  background: var(--accent); color: #fff;
  border-radius: var(--radius-sm);
  padding: 7px 0; font-size: 13px;
  font-family: inherit; cursor: pointer;
  transition: background var(--transition);
}
.btn-submit:hover { background: var(--accent-hover); }

.form-error { font-size: 12px; color: var(--accent); margin: 0; }
.form-hint { font-size: 12px; color: var(--green); margin: 0; }
</style>

<style>
/* 非 scoped：匹配外部传入的 settings-visible class */
.sidebar.settings-visible {
  transform: translateX(0);
  pointer-events: auto;
}
</style>
