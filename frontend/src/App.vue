<template>
  <div class="app">
    <Sidebar />
    <Settings :class="{ 'settings-visible': userStore.showSettings }" />
    <main class="main">
      <header class="main-header">
        <div class="main-header-top">
          <h1>{{ viewTitle }}</h1>
          <button class="btn-refresh" @click="store.loadTasks(store.currentOwnerId)" title="刷新任务列表">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" width="15" height="15">
              <path d="M1 4v6h6M23 20v-6h-6"/>
              <path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15"/>
            </svg>
          </button>
        </div>
        <span class="date">{{ todayStr }}</span>
      </header>

      <AddTask />
      <TaskList />
    </main>
    <DetailPanel />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { computed } from 'vue'
import { useTaskStore } from './stores/taskStore.js'
import { useUserStore } from './stores/userStore.js'
import Sidebar from './components/Sidebar.vue'
import TaskList from './components/TaskList.vue'
import AddTask from './components/addTask.vue'
import DetailPanel from './components/DetailPanel.vue'
import Settings from './components/Settings.vue'

// 键盘快捷键
onMounted(() => {
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
      e.preventDefault()
      // 聚焦到输入框
      const addTaskComp = document.querySelector('.add-task-input')
      if (addTaskComp) addTaskComp.focus()
    }
    if (e.key === 'Escape') {
      store.closeDetail()
      document.activeElement?.blur()
    }
  })

  // 加载数据——PyWebView API 异步注入，需等待就绪
  // 用户状态和任务数据一起加载
  const loadAll = () => {
    userStore.loadUser()
    store.loadTasks()
  }
  if (window.pywebview?.api?.api_get_tasks) {
    loadAll()
  } else {
    window.addEventListener('pywebviewready', () => loadAll())
    // 500ms 兜底：纯浏览器无 PyWebView 时用 localStorage
    setTimeout(() => {
      if (!window.pywebview?.api) loadAll()
    }, 500)
  }
})

const store = useTaskStore()
const userStore = useUserStore()

const viewMap = {
  today: '今天',
  upcoming: '计划',
  all: '全部任务',
  done: '已完成',
  work: '工作',
  personal: '个人',
  learn: '学习',
}

const viewTitle = computed(() => viewMap[store.currentView] || '任务')

const now = new Date()
const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
const todayStr = `${months[now.getMonth()]}${now.getDate()}日 ${days[now.getDay()]}`
</script>

<style>
/* 把你的所有 CSS 复制到这里，或者拆到各个组件中 */
/* 为节省篇幅，这里只保留关键全局样式，完整 CSS 见下文 "样式迁移" 部分 */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --bg-page: #fafaf7;
  --bg-sidebar: #f3f1ec;
  --bg-surface: #ffffff;
  --bg-hover: #f4f2ed;
  --bg-active: #eeebe4;
  --border: #e6e4df;
  --border-light: #eeede9;
  --text-primary: #1c1c1c;
  --text-secondary: #6e6d6a;
  --text-tertiary: #9e9d99;
  --text-disabled: #c5c3be;
  --accent: #d45d3c;
  --accent-hover: #c44a2a;
  --accent-subtle: #fdf0eb;
  --green: #5d8a76;
  --green-subtle: #edf5f1;
  --yellow: #c9a23b;
  --yellow-subtle: #faf6ed;
  --blue-gray: #7d919e;
  --sidebar-width: 260px;
  --radius-sm: 4px;
  --radius-md: 6px;
  --transition: 120ms ease;
}

html,
body {
  height: 100%;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
  background: var(--bg-page);
  -webkit-font-smoothing: antialiased;
}

.app {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-page);
}

.main-header {
  padding: 24px 32px 0;
  flex-shrink: 0;
}

.main-header-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-header-top h1 {
  font-size: 22px;
  font-weight: 650;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.btn-refresh {
  width: 28px; height: 28px;
  border: none; background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-tertiary);
  display: flex; align-items: center; justify-content: center;
  transition: all var(--transition);
}
.btn-refresh:hover { background: var(--bg-hover); color: var(--text-secondary); }
.btn-refresh:active { color: var(--accent); }

.main-header .date {
  display: block;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

::-webkit-scrollbar {
  width: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-disabled);
}

@media (max-width: 640px) {
  .main-header {
    padding: 20px 16px 0;
  }
}
</style>