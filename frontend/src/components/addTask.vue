<template>
  <div class="add-task-area">
    <div class="add-task-row" :class="{ focused: isFocused }">
      <span class="plus">+</span>
      <input
        ref="inputRef"
        class="add-task-input"
        type="text"
        v-model="newTaskTitle"
        placeholder="添加任务，或输入自然语言描述让 AI 解析…"
        autocomplete="off"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @keydown.enter="handleAdd"
      />
      <div class="add-task-actions">
        <button class="btn-icon" title="设置截止日期">
          <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
        </button>
        <button class="btn-icon" title="设置优先级">
          <svg viewBox="0 0 24 24"><path d="M6 12l4-8 4 8H6zM14 16l-4 8-4-8h8z"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useTaskStore } from '../stores/taskStore'

const store = useTaskStore()
const newTaskTitle = ref('')
const isFocused = ref(false)
const inputRef = ref(null)

const handleAdd = () => {
  const title = newTaskTitle.value.trim()
  if (title) {
    store.addTask(title)
    newTaskTitle.value = ''
  }
}

// 暴露给全局快捷键（Ctrl+N）
defineExpose({ inputRef })
</script>

<style scoped>
.add-task-area {
  padding: 20px 32px 0;
  flex-shrink: 0;
}

.add-task-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-light);
  transition: border-color var(--transition);
}

.add-task-row.focused {
  border-bottom-color: var(--accent);
}

.add-task-row .plus {
  color: var(--text-tertiary);
  font-size: 16px;
  font-weight: 350;
  flex-shrink: 0;
  width: 20px;
  text-align: center;
  transition: color var(--transition);
}

.add-task-row.focused .plus {
  color: var(--accent);
}

.add-task-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  font-family: inherit;
  color: var(--text-primary);
  background: transparent;
  padding: 6px 0;
}

.add-task-input::placeholder {
  color: var(--text-tertiary);
}

.add-task-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.btn-icon {
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
  transition: all var(--transition);
}

.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--text-secondary);
}

.btn-icon svg {
  width: 15px;
  height: 15px;
  stroke: currentColor;
  fill: none;
  stroke-width: 1.6;
}

@media (max-width: 640px) {
  .add-task-area {
    padding: 16px 16px 0;
  }
}
</style>