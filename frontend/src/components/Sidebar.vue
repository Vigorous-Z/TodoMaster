<template>
  <aside class="sidebar">
    <div class="sidebar-brand">TodoMaster</div>
    <nav class="sidebar-nav">
      <div class="sidebar-section">
        <div class="sidebar-label">视图</div>
        <a
          v-for="item in mainViews"
          :key="item.key"
          class="nav-item"
          :class="{ active: store.currentView === item.key }"
          @click="store.setView(item.key)"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          {{ item.label }}
          <span class="nav-count">{{ store.counts[item.key] || 0 }}</span>
        </a>
      </div>

      <div class="sidebar-section">
        <div class="sidebar-label">项目</div>
        <a
          v-for="item in projectViews"
          :key="item.key"
          class="nav-item"
          :class="{ active: store.currentView === item.key }"
          @click="store.setView(item.key)"
        >
          <span class="nav-icon" :style="{ color: item.color }" v-html="item.icon"></span>
          {{ item.label }}
          <span class="nav-count">{{ store.counts[item.key] || 0 }}</span>
        </a>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="hint">
        输入自然语言，AI 自动解析为日程<br />
        <kbd>Ctrl</kbd> + <kbd>N</kbd> 快速添加
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useTaskStore } from '../stores/taskStore'

const store = useTaskStore()

const mainViews = [
  { key: 'today', label: '今天', icon: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>` },
  { key: 'upcoming', label: '计划', icon: `<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>` },
  { key: 'all', label: '全部', icon: `<svg viewBox="0 0 24 24"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>` },
  { key: 'done', label: '已完成', icon: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M8 12l2.5 2.5L16 9"/></svg>` },
]

const projectViews = [
  { key: 'work', label: '工作', color: 'var(--accent)', icon: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/></svg>` },
  { key: 'personal', label: '个人', color: 'var(--green)', icon: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/></svg>` },
  { key: 'learn', label: '学习', color: 'var(--yellow)', icon: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/></svg>` },
]
</script>

<style>
/* 从原 CSS 中复制 .sidebar 相关样式 */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  user-select: none;
}

.sidebar-brand {
  padding: 20px 20px 16px;
  font-size: 15px;
  font-weight: 650;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.sidebar-nav {
  flex: 1;
  padding: 0 12px;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 20px;
}

.sidebar-label {
  font-size: 11px;
  font-weight: 550;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-tertiary);
  padding: 0 8px;
  margin-bottom: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 8px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  cursor: pointer;
  transition: background var(--transition);
  font-size: 13.5px;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.nav-item.active {
  background: var(--bg-active);
  color: var(--text-primary);
  font-weight: 500;
}

.nav-count {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 400;
  min-width: 20px;
  text-align: center;
}

.nav-item.active .nav-count {
  color: var(--text-secondary);
}

.nav-icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.nav-icon svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  fill: none;
  stroke-width: 1.6;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border);
}
.sidebar-footer .hint {
  font-size: 11.5px;
  color: var(--text-tertiary);
  padding: 6px 8px;
  line-height: 1.5;
}
.sidebar-footer .hint kbd {
  display: inline-block;
  font-family: inherit;
  font-size: 10.5px;
  background: var(--bg-active);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 0 4px;
  color: var(--text-secondary);
}

@media (max-width: 640px) {
  .sidebar {
    display: none;
  }
}
</style>