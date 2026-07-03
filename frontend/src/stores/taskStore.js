import { defineStore } from 'pinia'

// 工具函数：格式化日期
function fmt(d) {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

// 初始数据（完全迁移自你的 HTML）
const defaultTasks = [
  { id: 1, title: '给导师发邮件汇报本周进度', due: '2026-07-02 15:00', priority: 'high', tags: ['工作'], project: 'work', done: false },
  { id: 2, title: '项目进度讨论会议', due: '2026-07-02 09:00', priority: 'high', tags: ['工作', '会议'], project: 'work', done: true },
  { id: 3, title: '完成季度报告并提交审核', due: '2026-07-03 23:59', priority: 'high', tags: ['工作'], project: 'work', done: false },
  { id: 4, title: '预约财务对账时间', due: '2026-07-04 12:00', priority: 'medium', tags: ['工作'], project: 'work', done: false },
  { id: 5, title: '查阅 NLP 相关文献并做笔记', due: '2026-07-05 18:00', priority: 'low', tags: ['学习'], project: 'learn', done: false },
  { id: 6, title: '更新项目 README 和技术文档', due: '2026-07-03 17:00', priority: 'medium', tags: ['工作'], project: 'work', done: false },
  { id: 7, title: '跑步 5 公里', due: '2026-07-02 07:00', priority: 'medium', tags: ['个人'], project: 'personal', done: true },
  { id: 8, title: '整理桌面和下载文件夹', due: '2026-07-06 12:00', priority: 'low', tags: ['个人'], project: 'personal', done: false },
]

export const useTaskStore = defineStore('task', {
  state: () => ({
    tasks: [],
    currentView: 'today',
    selectedTaskId: null,
  }),

  getters: {
    // 根据当前视图筛选任务
    filteredTasks(state) {
      const todayStr = fmt(new Date())
      const view = state.currentView

      switch (view) {
        case 'today':
          return state.tasks.filter(t => !t.done && t.due.startsWith(todayStr))
        case 'upcoming':
          return state.tasks.filter(t => !t.done && t.due > todayStr + ' 23:59')
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

    // 选中的任务详情
    selectedTask(state) {
      return state.tasks.find(t => t.id === state.selectedTaskId) || null
    },

    // 各视图的任务数量（用于侧边栏角标）
    // 在 getters 中替换 counts
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
			.sort((a, b) => a.due.localeCompare(b.due))
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
		default:
			filtered = []
		}
		result[v] = filtered.length
	}
	return result
	}
  },

  actions: {
    // 初始化/加载数据（可从 localStorage 恢复）
    loadTasks() {
      const saved = localStorage.getItem('todomaster_tasks')
      if (saved) {
        try { this.tasks = JSON.parse(saved) } catch { this.tasks = defaultTasks }
      } else {
        this.tasks = defaultTasks
      }
    },

    // 保存到 localStorage
    saveTasks() {
      localStorage.setItem('todomaster_tasks', JSON.stringify(this.tasks))
    },

    // 添加任务
    addTask(title, due, priority, tags, project) {
      const newTask = {
        id: Date.now(),
        title,
        due: due || fmt(new Date()) + ' 23:59',
        priority: priority || 'medium',
        tags: tags || [],
        project: project || 'personal',
        done: false,
      }
      this.tasks.unshift(newTask)
      this.saveTasks()
    },

    // 切换完成状态
    toggleTask(id) {
      const task = this.tasks.find(t => t.id === id)
      if (task) {
        task.done = !task.done
        this.saveTasks()
      }
    },

    // 删除任务
    deleteTask(id) {
      const idx = this.tasks.findIndex(t => t.id === id)
      if (idx !== -1) {
        this.tasks.splice(idx, 1)
        if (this.selectedTaskId === id) this.selectedTaskId = null
        this.saveTasks()
      }
    },

    // 切换视图
    setView(view) {
      this.currentView = view
    },

    // 选择任务（详情面板）
    selectTask(id) {
      this.selectedTaskId = id
    },

    // 关闭详情
    closeDetail() {
      this.selectedTaskId = null
    }
  }
})