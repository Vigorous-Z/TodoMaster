<template>
  <aside class="detail-panel">
    <template v-if="!store.selectedTask">
      <div class="detail-empty">选择任务查看详情</div>
    </template>
    <template v-else>
      <div class="detail-content">
        <button class="detail-close" @click="store.closeDetail()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
        <div class="detail-field">
          <label>任务名称</label>
          <div class="value">{{ store.selectedTask.title }}</div>
        </div>
        <div class="detail-field">
          <label>截止时间</label>
          <div class="value">{{ store.selectedTask.due || '未设置' }}</div>
        </div>
        <div class="detail-field">
          <label>优先级</label>
          <div class="value">{{ priorityLabel(store.selectedTask.priority) }}</div>
        </div>
        <div class="detail-field">
          <label>标签</label>
          <div class="value">{{ store.selectedTask.tags.length ? store.selectedTask.tags.join('、') : '无' }}</div>
        </div>
        <div class="detail-field">
          <label>备注</label>
          <div class="value" style="color:var(--text-tertiary)">暂无备注</div>
        </div>
      </div>
    </template>
  </aside>
</template>

<script setup>
import { useTaskStore } from '../stores/taskStore'

const store = useTaskStore()

function priorityLabel(p) {
  return p === 'high' ? '高' : p === 'medium' ? '中' : p === 'low' ? '低' : '未设置'
}
</script>

<style scoped>
.detail-panel {
  width: 320px;
  min-width: 320px;
  background: var(--bg-surface);
  border-left: 1px solid var(--border);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.detail-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-disabled);
  font-size: 13px;
}

.detail-content {
  position: relative;
}

.detail-close {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-close:hover {
  background: var(--bg-hover);
  color: var(--text-secondary);
}

.detail-field label {
  display: block;
  font-size: 11px;
  font-weight: 550;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-tertiary);
  margin-bottom: 3px;
}

.detail-field .value {
  font-size: 13.5px;
  color: var(--text-primary);
  padding: 4px 0;
}

@media (max-width: 900px) {
  .detail-panel {
    display: none;
  }
}
</style>