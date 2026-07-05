<template>
  <div class="task-item" :class="{ completed: task.done }" @click="emit('select')">
    <div class="task-check" :class="{ done: task.done }" @click.stop="emit('toggle')"></div>
    <div class="task-body">
      <div class="task-title">{{ task.title }}</div>
      <div class="task-meta">
        <span v-if="task.due" class="task-meta-item">
          <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg>
          {{ relDate(task.due) }}
        </span>
        <span v-if="task.priority" class="priority" :class="task.priority">
          {{ priorityLabel(task.priority) }}
        </span>
        <span v-for="tag in task.tags" :key="tag" class="tag">{{ tag }}</span>
      </div>
    </div>
    <div class="task-actions">
      <button class="btn-icon" @click.stop="emit('edit')" title="编辑">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
      </button>
      <button class="btn-icon danger" @click.stop="emit('delete')" title="删除">
        <svg viewBox="0 0 24 24"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps(['task'])
const emit = defineEmits(['toggle', 'delete', 'select', 'edit'])

// 相对日期显示
function relDate(dueStr) {
  const due = new Date(dueStr.replace(' ', 'T'))
  const now = new Date()
  const diffMs = due - now
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const time = dueStr.split(' ')[1]?.slice(0, 5) || ''

  if (diffDays < 0) return `已过期 ${time}`
  if (diffDays === 0) return `今天 ${time}`
  if (diffDays === 1) return `明天 ${time}`
  if (diffDays <= 5) return `${diffDays}天后 ${time}`
  return dueStr.slice(0, 10)
}

function priorityLabel(p) {
  return p === 'high' ? '高' : p === 'medium' ? '中' : '低'
}
</script>

<style scoped>
.task-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 8px;
  border-radius: var(--radius-md);
  cursor: default;
  transition: background var(--transition);
  border-bottom: 1px solid transparent;
}

.task-item:hover {
  background: var(--bg-hover);
}

.task-item:not(:last-child) {
  border-bottom-color: var(--border-light);
}

.task-check {
  flex-shrink: 0;
  width: 19px;
  height: 19px;
  margin-top: 2px;
  border-radius: 50%;
  border: 1.5px solid var(--border);
  cursor: pointer;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}

.task-check:hover {
  border-color: var(--green);
}

.task-check.done {
  background: var(--green);
  border-color: var(--green);
}

.task-check.done::after {
  content: '';
  display: block;
  width: 5px;
  height: 9px;
  border: solid #fff;
  border-width: 0 1.5px 1.5px 0;
  transform: rotate(45deg) translateY(-1px);
}

.task-body {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
  transition: color var(--transition);
}

.task-item.completed .task-title {
  color: var(--text-disabled);
  text-decoration: line-through;
  text-decoration-color: var(--border);
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 3px;
  flex-wrap: wrap;
}

.task-meta-item {
  font-size: 12px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  gap: 3px;
}

.task-meta-item svg {
  width: 12px;
  height: 12px;
  stroke: currentColor;
  fill: none;
  stroke-width: 1.5;
}

.priority {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 550;
  padding: 1px 6px;
  border-radius: 3px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.priority.high {
  color: var(--accent);
  background: var(--accent-subtle);
}
.priority.medium {
  color: var(--yellow);
  background: var(--yellow-subtle);
}
.priority.low {
  color: var(--blue-gray);
  background: #f2f5f7;
}

.tag {
  display: inline-block;
  font-size: 11px;
  color: var(--text-tertiary);
  background: var(--bg-hover);
  padding: 1px 6px;
  border-radius: 3px;
}

.task-actions {
  display: flex;
  gap: 2px;
  visibility: hidden;
  opacity: 0;
  transition: opacity var(--transition), visibility var(--transition);
}

.task-item:hover .task-actions {
  visibility: visible;
  opacity: 1;
}

.task-actions .btn-icon {
  width: 26px;
  height: 26px;
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

.task-actions .btn-icon svg {
  width: 14px;
  height: 14px;
  stroke: currentColor;
  fill: none;
  stroke-width: 1.6;
}

.task-actions .btn-icon.danger:hover {
  color: var(--accent);
  background: var(--accent-subtle);
}
</style>