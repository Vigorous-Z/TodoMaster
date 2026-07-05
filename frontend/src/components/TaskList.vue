<template>
  <div class="task-list-wrap">
    <template v-if="store.filteredTasks.length === 0">
      <div class="empty-state">
        <p>没有任务</p>
        <span class="sub">在上方输入框添加新任务</span>
      </div>
    </template>

    <template v-else>
      <div v-for="(group, key) in groupedTasks" :key="key" class="task-group">
        <div v-if="key !== 'no-date'" class="task-group-header">{{ groupLabel(key) }}</div>
        <TaskItem
          v-for="task in group"
          :key="task.id"
          :task="task"
          @toggle="store.toggleTask(task.id)"
          @delete="store.deleteTask(task.id)"
          @select="store.selectTask(task.id)"
          @edit="$emit('edit', task)"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTaskStore } from '../stores/taskStore.js'
import TaskItem from './TaskItem.vue'

defineEmits(['edit'])

const store = useTaskStore()

// 按日期分组
const groupedTasks = computed(() => {
  const groups = {}
  for (const t of store.filteredTasks) {
    const key = t.done ? 'completed' : (t.due?.slice(0, 10) || 'no-date')
    if (!groups[key]) groups[key] = []
    groups[key].push(t)
  }
  return groups
})

// 分组标题
const today = new Date()
const todayStr = (d) => {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}
const todayKey = todayStr(today)
const tomorrowKey = todayStr(new Date(today.getTime() + 86400000))
const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

const groupLabel = (key) => {
  if (key === 'completed') return '已完成'
  if (key === todayKey) return '今天'
  if (key === tomorrowKey) return '明天'
  const d = new Date(key + 'T00:00:00')
  return `${months[d.getMonth()]}${d.getDate()}日 ${days[d.getDay()]}`
}
</script>

<style scoped>
.task-list-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 16px 32px 40px;
}

.task-group {
  margin-bottom: 24px;
}

.task-group-header {
  font-size: 12px;
  font-weight: 550;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 6px;
  padding-left: 2px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: 6px;
}

.empty-state .sub {
  font-size: 12.5px;
  color: var(--text-disabled);
}

@media (max-width: 640px) {
  .task-list-wrap {
    padding: 12px 16px 40px;
  }
}
</style>