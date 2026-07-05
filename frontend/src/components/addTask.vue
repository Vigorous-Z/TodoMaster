<template>
  <div class="add-task-area">
    <div class="add-task-row" :class="{ focused: isFocused }">
      <span class="plus" @click="handleAdd">+</span>
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
        <button class="btn-icon" :class="{ active: panelOpen }" title="更多设置" @click="panelOpen = !panelOpen">
          <svg viewBox="0 0 24 24"><path d="M6 12l4-8 4 8H6zM14 16l-4 8-4-8h8z"/></svg>
        </button>
      </div>
    </div>

    <!-- 展开的设置面板 -->
    <div class="panel-wrapper" :class="{ open: panelOpen }">
      <div class="add-task-panel">
      <div class="panel-field">
        <label>截止日期</label>
        <input type="datetime-local" v-model="dueDate" />
      </div>
      <div class="panel-field">
        <label>优先级</label>
        <div class="priority-options">
          <button
            v-for="p in priorities"
            :key="p.key"
            class="priority-btn"
            :class="{ selected: priority === p.key }"
            @click="priority = p.key"
          >{{ p.label }}</button>
        </div>
      </div>
      <div class="panel-field">
        <label>标签</label>
        <div class="tag-options">
          <button
            v-for="t in tagCandidates"
            :key="t"
            class="tag-btn"
            :class="{ selected: tags.includes(t) }"
            @click="toggleTag(t)"
          >{{ t }}</button>
        </div>
      </div>
        <div class="panel-field panel-field-desc">
          <label>任务描述</label>
          <input type="text" v-model="description" placeholder="可添加任务细节说明…" />
        </div>
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
const panelOpen = ref(false)

// 面板内的选项
function getDefaultDue() {
  const now = new Date()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${m}-${d}T23:59`
}
const dueDate = ref(getDefaultDue())
const priority = ref('medium')
const tags = ref([])
const description = ref('')

const priorities = [
  { key: 'high', label: '高' },
  { key: 'medium', label: '中' },
  { key: 'low', label: '低' },
]

const tagCandidates = ['工作', '个人', '学习', '会议']

function toggleTag(tag) {
  const idx = tags.value.indexOf(tag)
  if (idx === -1) {
    tags.value.push(tag)
  } else {
    tags.value.splice(idx, 1)
  }
}

const handleAdd = () => {
  const title = newTaskTitle.value.trim()
  if (!title) return

  const due = dueDate.value ? dueDate.value.replace('T', ' ') : undefined
store.addTask(title, due, priority.value, [...tags.value], description.value, null)

  // 重置状态
  newTaskTitle.value = ''
  dueDate.value = getDefaultDue()
  priority.value = 'medium'
  tags.value = []
  description.value = ''
  panelOpen.value = false
}

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
  cursor: pointer;
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

.btn-icon.active {
  color: var(--accent);
  background: var(--accent-subtle);
}

.btn-icon svg {
  width: 15px;
  height: 15px;
  stroke: currentColor;
  fill: none;
  stroke-width: 1.6;
}

/* 面板包裹层——max-height 动画实现平滑下拉/收起 */
.panel-wrapper {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.panel-wrapper.open {
  max-height: 400px;
}

/* 展开面板 */
.add-task-panel {
  margin-top: 8px;
  padding: 12px 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 16px 24px;
}

.panel-field {
  min-width: 160px;
}

.panel-field label {
  display: block;
  font-size: 11px;
  font-weight: 550;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-tertiary);
  margin-bottom: 6px;
}

.panel-field input[type="datetime-local"] {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text-primary);
  background: var(--bg-page);
  outline: none;
}

.panel-field input[type="datetime-local"]:focus {
  border-color: var(--accent);
}

/* 描述输入框独占一行，宽度拉满 */
.panel-field-desc {
  flex-basis: 100%;
}

.panel-field input[type="text"] {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text-primary);
  background: var(--bg-page);
  outline: none;
}

.panel-field input[type="text"]:focus {
  border-color: var(--accent);
}

.panel-field input[type="text"]::placeholder {
  color: var(--text-tertiary);
}

.priority-options,
.tag-options {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.priority-btn,
.tag-btn {
  border: 1px solid var(--border);
  background: var(--bg-page);
  border-radius: var(--radius-sm);
  padding: 3px 10px;
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition);
}

.priority-btn:hover,
.tag-btn:hover {
  background: var(--bg-hover);
}

.priority-btn.selected,
.tag-btn.selected {
  background: var(--accent-subtle);
  color: var(--accent);
  border-color: var(--accent);
}

@media (max-width: 640px) {
  .add-task-area {
    padding: 16px 16px 0;
  }
}
</style>