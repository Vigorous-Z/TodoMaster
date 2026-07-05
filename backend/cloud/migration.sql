-- ============================================
-- Supabase 云端迁移 SQL（完整版，含三张表）
-- 在 Supabase SQL Editor 中执行
-- ============================================

-- 1. tasks 表（如果还没建）
CREATE TABLE IF NOT EXISTS tasks (
  uuid        TEXT PRIMARY KEY,
  version     INTEGER DEFAULT 1,
  title       TEXT NOT NULL,
  description TEXT DEFAULT '',
  due_date    TEXT,
  priority    TEXT DEFAULT 'medium',
  status      TEXT DEFAULT 'active',
  project     TEXT DEFAULT 'inbox',
  tags        JSONB DEFAULT '[]'::jsonb,
  created_at  TEXT,
  updated_at  TEXT,
  synced_at   TEXT,
  deleted_at  TEXT,
  parent_uuid TEXT,
  sort_order  INTEGER DEFAULT 0,
  extras      JSONB DEFAULT '{}'::jsonb,
  user_id     TEXT NOT NULL
);

-- 2. chat_sessions 表
CREATE TABLE IF NOT EXISTS chat_sessions (
  session_id  TEXT PRIMARY KEY,
  user_id     TEXT NOT NULL,
  title       TEXT,
  messages    JSONB NOT NULL DEFAULT '[]'::jsonb,
  is_starred  BOOLEAN DEFAULT false,
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL,
  deleted_at  TEXT
);

-- 3. local_users 表
CREATE TABLE IF NOT EXISTS local_users (
  user_id       TEXT PRIMARY KEY,
  prefix        TEXT NOT NULL,
  suffix        INTEGER NOT NULL,
  password_hash TEXT NOT NULL,
  created_at    TEXT NOT NULL
);

-- ============================================
-- 索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_tasks_user_id    ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);
CREATE INDEX IF NOT EXISTS idx_chat_user_id     ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_users_prefix     ON local_users(prefix);

-- ============================================
-- RLS——用 service_role key 调用时全部放行
-- ============================================
ALTER TABLE tasks         ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE local_users   ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON tasks;
CREATE POLICY "service_role_all" ON tasks         USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all" ON chat_sessions;
CREATE POLICY "service_role_all" ON chat_sessions USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all" ON local_users;
CREATE POLICY "service_role_all" ON local_users   USING (true) WITH CHECK (true);
