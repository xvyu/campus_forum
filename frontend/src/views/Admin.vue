<template>
  <div class="admin-page">
    <!-- ===== Hero 管理后台区 ===== -->
    <div class="admin-hero">
      <div class="hero-deco-circle c1"></div>
      <div class="hero-deco-circle c2"></div>
      <div class="hero-text">
        <div class="hero-badge">🛡 Campus Forum · 管理后台</div>
        <h1 class="hero-title">管理后台</h1>
        <p class="hero-sub">维护帖子、用户与板块，保持校园社区健康</p>
      </div>
    </div>

    <!-- ===== 4 个统计卡 ===== -->
    <div class="stat-grid">
      <div class="stat-card-admin">
        <div class="stat-top-bar bar-blue"></div>
        <div class="stat-num blue">{{ stats.active_posts ?? '...' }}</div>
        <div class="stat-label">正常帖子</div>
      </div>
      <div class="stat-card-admin">
        <div class="stat-top-bar bar-pink"></div>
        <div class="stat-num pink">{{ stats.deleted_posts ?? '...' }}</div>
        <div class="stat-label">已删除帖子</div>
      </div>
      <div class="stat-card-admin">
        <div class="stat-top-bar bar-green"></div>
        <div class="stat-num green">{{ stats.total_users ?? '...' }}</div>
        <div class="stat-label">普通用户</div>
      </div>
      <div class="stat-card-admin">
        <div class="stat-top-bar bar-amber"></div>
        <div class="stat-num amber">{{ stats.admin_users ?? '...' }}</div>
        <div class="stat-label">管理员</div>
      </div>
    </div>

    <!-- ===== Tab 栏 ===== -->
    <div class="admin-tabs">
      <button
        v-for="t in tabList"
        :key="t.key"
        class="admin-tab-btn"
        :class="{ active: activeTab === t.key }"
        @click="switchTab(t.key)"
      >
        {{ t.label }}
      </button>
    </div>

    <!-- ===== 正常帖子 / 已删除帖子 ===== -->
    <template v-if="activeTab === 'active' || activeTab === 'deleted'">
      <!-- 工具栏 -->
      <div class="toolbar-row">
        <div class="toolbar-left">
          <label class="toolbar-checkbox" @click.stop>
            <input
              type="checkbox"
              class="toolbar-cb"
              :checked="isAllSelected"
              :indeterminate.prop="isIndeterminate"
              @change="toggleSelectAll"
            />
            <span class="toolbar-title">
              {{ activeTab === 'active' ? '📝 正常帖子列表' : '🗑 已删除帖子列表' }}
            </span>
          </label>
          <span class="toolbar-count">· 共 {{ displayedTotal }} 条</span>
          <transition name="fade">
            <span v-if="selectedIds.length" class="toolbar-selected">
              已选 <b>{{ selectedIds.length }}</b> 项
              <button class="toolbar-batch-btn" @click="batchDelete">
                <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                {{ activeTab === 'active' ? '批量软删除' : '批量彻底删除' }}
              </button>
              <button class="toolbar-clear-btn" @click="selectedIds = []">取消选择</button>
            </span>
          </transition>
        </div>
        <div class="toolbar-right">
          <el-select
            v-model="boardFilter"
            placeholder="按板块"
            size="small"
            class="toolbar-select"
          >
            <el-option label="全部" value="all" />
            <el-option
              v-for="b in boards"
              :key="b.id"
              :label="b.name"
              :value="b.id"
            />
          </el-select>
          <el-select
            v-model="sortBy"
            placeholder="按时间"
            size="small"
            class="toolbar-select"
          >
            <el-option label="最新发布" value="newest" />
            <el-option label="最早发布" value="oldest" />
            <el-option label="最多浏览" value="most_viewed" />
          </el-select>
        </div>
      </div>

      <!-- 帖子卡片列表 -->
      <div v-loading="loading" class="post-card-list">
        <div v-if="!displayedPosts.length && !loading" class="empty-state">
          <div class="empty-icon">🗂</div>
          <div class="empty-title">暂无帖子</div>
          <div class="empty-desc">当前条件下没有帖子记录</div>
        </div>

        <div
          v-for="p in displayedPosts"
          :key="p.id"
          class="post-card-admin"
          :class="{ 'post-card-selected': selectedIds.includes(p.id) }"
        >
          <label class="post-card-checkbox" @click.stop>
            <input
              type="checkbox"
              class="post-cb"
              :checked="selectedIds.includes(p.id)"
              @change="toggleSelect(p.id)"
            />
          </label>
          <div class="post-bar" :class="boardColorClass(p.board_id)"></div>
          <div class="post-avatar" :class="boardColorClass(p.board_id)">
            {{ (p.board_name || '匿').charAt(0) }}
          </div>
          <div class="post-body">
            <div class="post-title-row">
              <span class="post-id">#{{ p.id }}</span>
              <span class="post-title" :class="{ 'text-strike': activeTab === 'deleted' }">
                {{ p.title || '(无标题)' }}
              </span>
            </div>
            <div class="post-tags">
              <span class="pill-board" :class="boardColorClass(p.board_id)">
                {{ p.board_name || '默认板块' }}
              </span>
              <span v-if="p.is_pinned" class="pill-meta">置顶</span>
              <span v-if="p.is_essence" class="pill-meta pill-essence">精华</span>
            </div>
            <div class="post-meta">
              <span class="meta-item">{{ p.author_name || '匿名' }}</span>
              <span class="meta-item meta-dot">·</span>
              <span class="meta-item">{{ p.created_at }}</span>
            </div>
            <div class="post-preview" v-html="formatPostPreview(p)"></div>
          </div>

          <div class="post-data">
            <div class="data-label">互动数据</div>
            <div class="data-row">
              <span class="data-item">👍 {{ p.like_count ?? 0 }}</span>
              <span class="data-item">💬 {{ p.comment_count ?? 0 }}</span>
              <span class="data-item">👁 {{ p.view_count ?? 0 }}</span>
            </div>
            <div v-if="activeTab === 'deleted'" class="data-last-comment">
              <span v-if="p.last_comment_preview">💬 {{ p.last_comment_preview }}</span>
              <span v-else class="muted">（无评论）</span>
            </div>
          </div>

          <div class="post-actions">
            <span
              class="status-pill"
              :class="statusClass(p)"
            >
              {{ statusLabel(p) }}
            </span>
            <div class="action-btns">
              <template v-if="activeTab === 'active'">
                <button class="action-btn" @click="$router.push('/posts/' + p.id)">
                  <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>
                  <span>查看</span>
                </button>
                <button class="action-btn action-danger" @click="softDeletePost(p)">
                  <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                  <span>删除</span>
                </button>
              </template>
              <template v-else>
                <button class="action-btn" @click="openDetail(p)">
                  <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>
                  <span>查看详情</span>
                </button>
                <button class="action-btn action-success" @click="restorePost(p)">
                  <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M21 12a9 9 0 1 1-3-6.7M21 4v5h-5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  <span>恢复</span>
                </button>
                <button class="action-btn action-danger" @click="hardDeletePost(p)">
                  <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                  <span>彻底删除</span>
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页（筛选/排序已改为前端处理，列表通常不大，省略分页） -->
      <div v-if="displayedTotal > pageSize" class="pagination-wrap">
        <div class="pagination-inner">
          <span class="page-total">共 {{ displayedTotal }} 条</span>
          <div class="page-btns">
            <button
              v-for="pg in visiblePages"
              :key="pg"
              class="page-btn"
              :class="{ active: pg === page }"
              @click="goPage(pg)"
            >{{ pg }}</button>
          </div>
          <button class="page-next" @click="goPage(page + 1)" :disabled="page >= totalPages">下一页 →</button>
          <span class="page-size">每页 <b>{{ pageSize }}</b> 条</span>
        </div>
      </div>
    </template>

    <!-- ===== 注册用户 ===== -->
    <template v-if="activeTab === 'users'">
      <div class="toolbar-row">
        <div class="toolbar-left">
          <span class="toolbar-title">👥 注册用户列表</span>
          <span class="toolbar-count">· 共 {{ totalUsers }} 条</span>
        </div>
      </div>
      <div class="user-table-wrap">
        <el-table :data="users" v-loading="loadingUsers" stripe style="width:100%;font-size:13px;" size="small" class="user-table">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="student_id" label="学号" width="150" />
          <el-table-column prop="nickname" label="昵称" width="120" />
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <span :class="['user-status', row.status === 1 ? 'user-status-ok' : 'user-status-off']">
                {{ row.status === 1 ? '正常' : '已禁用' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" width="150" />
        </el-table>
      </div>
      <p class="muted-tip">注：只显示普通用户的人数（共 {{ stats.total_users }} 人）</p>
    </template>

    <!-- ===== 数据看板 / 系统设置 占位 ===== -->
    <template v-if="false"></template>

    <!-- ===== 帖子详情对话框（保留快照功能） ===== -->
    <el-dialog v-model="detailVisible" :title="`帖子 #${currentPost?.id} 详情`" width="800px" top="5vh">
      <div v-if="currentPost" class="post-detail">
        <h3 class="detail-title">{{ currentPost.title }}</h3>
        <div class="detail-meta">
          <el-tag size="small">{{ currentPost.board_name }}</el-tag>
          <span>作者：{{ currentPost.author_name }}</span>
          <span>发布：{{ currentPost.created_at }}</span>
          <el-tag v-if="currentPost.is_deleted" type="danger" size="small">已删除</el-tag>
        </div>

        <el-divider />

        <div v-if="currentPost.snapshot" class="snapshot-section">
          <el-alert type="info" :closable="false" show-icon style="margin-bottom: 12px;">
            <template #title>
              <b>📸 删除前快照</b>（{{ currentPost.snapshot_at }} 保存）
            </template>
            这是帖子删除前最后一次更新时的完整快照，包含帖子内容、浏览量、点赞数、全部评论等所有信息。
          </el-alert>

          <h4>📊 最终数据</h4>
          <el-row :gutter="12" class="snapshot-stats">
            <el-col :span="6"><div class="stat-tile"><div class="stat-num-s">{{ currentPost.snapshot.view_count || 0 }}</div><div class="stat-lab">浏览量</div></div></el-col>
            <el-col :span="6"><div class="stat-tile"><div class="stat-num-s">{{ currentPost.snapshot.like_count || 0 }}</div><div class="stat-lab">点赞数</div></div></el-col>
            <el-col :span="6"><div class="stat-tile"><div class="stat-num-s">{{ currentPost.snapshot.dislike_count || 0 }}</div><div class="stat-lab">点踩数</div></div></el-col>
            <el-col :span="6"><div class="stat-tile"><div class="stat-num-s">{{ currentPost.snapshot.comments?.length || 0 }}</div><div class="stat-lab">评论数</div></div></el-col>
          </el-row>

          <h4>📝 帖子最终内容</h4>
          <div class="content-block" v-html="currentPost.snapshot.content || '(无内容)'"></div>

          <h4>💬 全部评论 ({{ currentPost.snapshot.comments?.length || 0 }})</h4>
          <div v-if="!currentPost.snapshot.comments?.length" class="muted">（无评论）</div>
          <div v-else class="all-comments">
            <div v-for="(c, idx) in currentPost.snapshot.comments" :key="c.id" class="comment-item" :class="c.is_deleted ? 'comment-deleted' : ''">
              <div class="comment-head">
                <span class="comment-num">#{{ idx + 1 }}</span>
                <span class="comment-id">(ID: {{ c.id }})</span>
                <span class="comment-author">{{ c.author_name }}</span>
                <span class="comment-time">{{ c.created_at }}</span>
                <el-tag v-if="c.is_deleted" type="danger" size="small">已删除</el-tag>
              </div>
              <div class="comment-content">{{ c.content }}</div>
              <div class="comment-meta">👍 {{ c.like_count }}</div>
            </div>
          </div>
        </div>

        <div v-else class="no-snapshot">
          <h4>📝 帖子当前内容</h4>
          <div class="content-block" v-html="currentPost.content_preview || '(无内容)'"></div>
          <h4>💬 最后一次评论</h4>
          <div v-if="currentPost.last_comment_detail" class="content-block last-comment-detail">
            <div class="meta-row">
              <span>评论ID: {{ currentPost.last_comment_detail.id }}</span>
              <span>时间: {{ currentPost.last_comment_detail.created_at }}</span>
              <el-tag v-if="currentPost.last_comment_detail.is_deleted" type="danger" size="small">已删除</el-tag>
            </div>
            <div class="meta-content">{{ currentPost.last_comment_detail.content }}</div>
          </div>
          <div v-else class="muted">（无评论）</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { showConfirm } from '@/utils/confirm'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const userStore = useUserStore()
const activeTab = ref<'active' | 'deleted' | 'users'>('active')
const posts = ref<any[]>([])
const users = ref<any[]>([])
const boards = ref<any[]>([])
const loading = ref(false)
const loadingUsers = ref(false)
const page = ref(1)
const total = ref(0)
const totalUsers = ref(0)
const pageSize = 10
const boardFilter = ref<number | 'all'>('all')
const sortBy = ref<string>('newest')
// 多选删除
const selectedIds = ref<number[]>([])
const stats = ref<any>({
  active_posts: 0, deleted_posts: 0, total_users: 0, admin_users: 0,
})
const detailVisible = ref(false)
const currentPost = ref<any>(null)

const tabList = computed(() => [
  { key: 'active', label: `📝 正常帖子 ${stats.value.active_posts ?? 0}` },
  { key: 'deleted', label: `🗑 已删除 ${stats.value.deleted_posts ?? 0}` },
  { key: 'users', label: `👥 注册用户 ${stats.value.total_users ?? 0}` },
] as const)

/** 过滤后的真实条数（用于显示"共 N 条"） */
const displayedTotal = computed(() => displayedPosts.value.length)

// 已改为前端筛选/排序，分页由 displayedPosts 长度决定（仅超过 pageSize 才显示）
const totalPages = computed(() => Math.ceil(displayedTotal.value / pageSize))
const visiblePages = computed(() => {
  const t = totalPages.value
  const c = page.value
  if (t <= 5) return Array.from({ length: t }, (_, i) => i + 1)
  if (c <= 3) return [1, 2, 3, 4, 5]
  if (c >= t - 2) return [t - 4, t - 3, t - 2, t - 1, t]
  return [c - 2, c - 1, c, c + 1, c + 2]
})

// 板块颜色映射
const colors = ['blue', 'pink', 'green', 'amber', 'purple', 'coral']
function boardColorClass(id?: number | string) {
  if (id === undefined || id === null) return 'green'
  const n = typeof id === 'string' ? id.length : id
  return colors[n % colors.length]
}

// 状态显示：已删除 Tab → 已删除；正常 Tab → 正常
function statusClass(p: any): string {
  if (activeTab.value === 'deleted') return 'status-deleted'
  return 'status-ok'
}
function statusLabel(p: any): string {
  if (activeTab.value === 'deleted') return '已删除'
  return '正常'
}

// ==== 智能格式化帖子预览（不显示 base64）====
const FILE_ICONS: Record<string, string> = {
  pdf: '📄', doc: '📝', docx: '📝', txt: '📃', md: '📋',
  xls: '📊', xlsx: '📊', csv: '📊',
  ppt: '📽', pptx: '📽',
  zip: '🗜', rar: '🗜', '7z': '🗜',
  png: '🖼', jpg: '🖼', jpeg: '🖼', gif: '🖼', webp: '🖼', svg: '🖼',
}
function getFileIcon(name: string): string {
  if (!name) return '📎'
  const ext = name.split('.').pop()?.toLowerCase() || ''
  return FILE_ICONS[ext] || '📎'
}
function formatPostPreview(row: any): string {
  const preview = row.content_preview || ''
  if (!preview) return ''
  const imgMatch = preview.match(/<img[^>]*data-file-name="([^"]*)"[^>]*>/i)
    || preview.match(/<img[^>]*alt="([^"]*)"[^>]*>/i)
  if (imgMatch && imgMatch[1] && imgMatch[1] !== 'undefined') {
    return `🖼 ${imgMatch[1]}`
  }
  const fileMatch = preview.match(/<span[^>]*class="editor-file"[^>]*data-filename="([^"]*)"[^>]*>/i)
  if (fileMatch && fileMatch[1]) {
    return `${getFileIcon(fileMatch[1])} ${fileMatch[1]}`
  }
  const text = preview.replace(/<[^>]+>/g, '').trim()
  return text.length > 60 ? text.slice(0, 60) + '...' : text
}

onMounted(async () => {
  if (!userStore.isLoggedIn || userStore.user?.role !== 3) {
    ElMessage.error('无权访问管理后台')
    return
  }
  await loadStats()
  await loadBoards()
  await loadCurrent()
})

watch(activeTab, () => loadCurrent())

async function loadStats() {
  try {
    const res = await api.get('/admin/stats')
    stats.value = res.data || stats.value
  } catch (e) { console.error(e) }
}

async function loadBoards() {
  try {
    const res = await api.get('/boards')
    boards.value = res.data?.list || res.data || []
  } catch { boards.value = [] }
}

async function loadCurrent() {
  page.value = 1
  if (activeTab.value === 'users') {
    await loadUsers()
  } else {
    await loadPosts()
  }
}

async function loadPosts() {
  loading.value = true
  try {
    const params: any = {
      page: 1,
      limit: 100,  // 一次拉足够多，前端筛选/排序
      status: activeTab.value === 'deleted' ? 'deleted' : 'active',
    }
    const res = await api.get('/admin/posts', { params })
    posts.value = res.data.list || []
    total.value = posts.value.length
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '加载失败')
  } finally { loading.value = false }
}

/** 前端筛选+排序后的展示列表（因为后端暂不支持 board_id / sort 参数） */
const displayedPosts = computed(() => {
  let list = [...posts.value]
  // 按板块过滤（'all' 表示全部，双重匹配：先 id，失败时按 name 兜底）
  if (boardFilter.value !== 'all') {
    const selectedBoard = boards.value.find((b) => String(b.id) === String(boardFilter.value))
    const targetName = selectedBoard?.name
    const targetId = Number(boardFilter.value)
    list = list.filter((p) => {
      if (Number(p.board_id) === targetId) return true
      if (targetName && p.board_name === targetName) return true
      return false
    })
  }
  // 排序
  list.sort((a, b) => {
    if (sortBy.value === 'newest') {
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
    }
    if (sortBy.value === 'oldest') {
      return new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime()
    }
    if (sortBy.value === 'most_viewed') {
      return (b.view_count || 0) - (a.view_count || 0)
    }
    return 0
  })
  return list
})

async function loadUsers() {
  loadingUsers.value = true
  try {
    const res = await api.get('/admin/users')
    users.value = res.data.list || []
    totalUsers.value = res.data.total || 0
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '加载失败')
  } finally { loadingUsers.value = false }
}

function switchTab(key: string) {
  activeTab.value = key as 'active' | 'deleted' | 'users'
}

function goPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  loadPosts()
}

async function softDeletePost(row: any) {
  try {
    await showConfirm(`确定删除帖子「${row.title}」吗？可在「已删除帖子」标签恢复。`, '管理员删除', 'danger', `标题：${row.title}`)
  } catch { return }
  try {
    await api.delete(`/admin/posts/${row.id}`)
    ElMessage.success('已删除')
    await loadPosts()
    await loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

async function restorePost(row: any) {
  try {
    await showConfirm(`确定恢复帖子「${row.title}」吗？`, '恢复帖子', 'info')
  } catch { return }
  try {
    await api.post(`/admin/posts/${row.id}/restore`)
    ElMessage.success('已恢复')
    await loadPosts()
    await loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '恢复失败')
  }
}

async function hardDeletePost(row: any) {
  try {
    await showConfirm(`彻底删除「${row.title}」将永久消失！包括所有评论。此操作不可恢复！`, '彻底删除', 'danger', `标题：${row.title} · 含所有评论及附件`)
  } catch { return }
  try {
    await api.delete(`/admin/posts/${row.id}/hard-delete`)
    ElMessage.success('已彻底删除')
    await loadPosts()
    await loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

async function openDetail(row: any) {
  try {
    const res = await api.get(`/admin/posts/${row.id}`)
    currentPost.value = res.data
    detailVisible.value = true
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '加载详情失败')
  }
}

/** 多选删除相关 */
function toggleSelect(id: number) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(id)
  }
}
function toggleSelectAll(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  if (checked) {
    selectedIds.value = displayedPosts.value.map((p) => p.id)
  } else {
    selectedIds.value = []
  }
}
const isAllSelected = computed(() =>
  displayedPosts.value.length > 0 &&
  selectedIds.value.length === displayedPosts.value.length
)
const isIndeterminate = computed(() =>
  selectedIds.value.length > 0 &&
  selectedIds.value.length < displayedPosts.value.length
)

/** 批量删除：正常 Tab → 软删除；已删除 Tab → 彻底删除 */
async function batchDelete() {
  if (!selectedIds.value.length) return
  const isActive = activeTab.value === 'active'
  const action = isActive ? '批量删除' : '批量彻底删除'
  const detail = `共 ${selectedIds.value.length} 个帖子，操作不可恢复`

  try {
    await showConfirm(`确定${action}选中的 ${selectedIds.value.length} 个帖子吗？`, action, 'danger', detail)
  } catch { return }

  loading.value = true
  try {
    // 逐个调用（后端暂不支持批量接口）
    const promises = selectedIds.value.map((id) =>
      api.delete(isActive ? `/admin/posts/${id}` : `/admin/posts/${id}/hard-delete`)
    )
    const results = await Promise.allSettled(promises)
    const successCount = results.filter((r) => r.status === 'fulfilled').length
    const failCount = results.length - successCount
    if (successCount) ElMessage.success(`成功${action} ${successCount} 个`)
    if (failCount) ElMessage.warning(`${failCount} 个失败`)
    selectedIds.value = []
    await loadPosts()
    await loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '批量删除失败')
  } finally { loading.value = false }
}

// 切换 Tab 时清空选择
watch(activeTab, () => { selectedIds.value = [] })
</script>

<style scoped>
.admin-page { max-width: 1000px; margin: 0 auto; padding: 20px 16px; }

/* ===== Hero 区 ===== */
.admin-hero {
  position: relative;
  background: linear-gradient(90deg, #0C447C 0%, #1D9E75 100%);
  border-radius: 14px;
  padding: 22px 28px;
  margin-bottom: 16px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  overflow: hidden;
}
.hero-deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
}
.hero-deco-circle.c1 { width: 72px; height: 72px; right: 90px; top: -18px; }
.hero-deco-circle.c2 { width: 40px; height: 40px; right: 20px; bottom: -12px; background: rgba(255,255,255,0.08); }
.hero-text { position: relative; z-index: 1; }
.hero-badge { font-size: 11px; color: rgba(255, 255, 255, 0.65); margin-bottom: 4px; }
.hero-title { font-size: 20px; font-weight: 500; margin: 0 0 4px; }
.hero-sub { font-size: 12px; color: rgba(255, 255, 255, 0.7); margin: 0; }

.hero-stats {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 18px;
  background: rgba(255, 255, 255, 0.18);
  border-radius: 10px;
  padding: 10px 18px;
}
.hero-stat { display: flex; flex-direction: column; }
.hs-label { font-size: 10px; color: rgba(255, 255, 255, 0.7); }
.hs-num { font-size: 20px; font-weight: 500; line-height: 1.2; }
.hs-growth { font-size: 11px; color: #9FE1CB; font-weight: 500; }
.hero-stat-divider { width: 1px; height: 28px; background: rgba(255, 255, 255, 0.25); }

/* ===== 统计卡 ===== */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px; }
.stat-card-admin {
  background: #fff;
  border: 0.5px solid #D3D1C7;
  border-radius: 10px;
  padding: 16px 0;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.2s;
}
.stat-card-admin:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.stat-top-bar { position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.bar-blue { background: #378ADD; }
.bar-pink { background: #D4537E; }
.bar-green { background: #639922; }
.bar-amber { background: #BA7517; }
.stat-num { font-size: 28px; font-weight: 500; margin-bottom: 2px; }
.stat-num.blue { color: #378ADD; }
.stat-num.pink { color: #D4537E; }
.stat-num.green { color: #639922; }
.stat-num.amber { color: #BA7517; }
.stat-label { font-size: 11px; color: #888780; }

/* ===== Tab 栏 ===== */
.admin-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  background: #F1EFE8;
  border-radius: 10px;
  padding: 5px 6px;
  margin-bottom: 14px;
}
.admin-tab-btn {
  border: none;
  background: transparent;
  color: #5F5E5A;
  font-size: 12px;
  padding: 6px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.admin-tab-btn:hover { background: rgba(255,255,255,0.7); }
.admin-tab-btn.active { background: #1D9E75; color: #fff; font-weight: 500; }

/* ===== 工具栏 ===== */
.toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border: 0.5px solid #D3D1C7;
  border-radius: 10px;
  padding: 10px 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 10px;
}
.toolbar-title { font-size: 13px; font-weight: 500; color: #2C2C2A; }
.toolbar-count { font-size: 11px; color: #B4B2A9; margin-left: 4px; }
.toolbar-checkbox { display: inline-flex; align-items: center; gap: 8px; cursor: pointer; }
.toolbar-cb {
  width: 16px; height: 16px;
  accent-color: #1D9E75;
  cursor: pointer;
}
.toolbar-selected {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 4px 12px;
  background: #FCEBEB;
  border: 0.5px solid #E24B4A;
  border-radius: 14px;
  font-size: 11px;
  color: #791F1F;
  margin-left: 12px;
}
.toolbar-selected b { color: #E24B4A; font-weight: 600; }
.toolbar-batch-btn {
  display: inline-flex; align-items: center; gap: 4px;
  background: #E24B4A; color: #fff;
  border: none; border-radius: 12px;
  padding: 4px 12px; font-size: 10px; font-weight: 500;
  cursor: pointer; font-family: inherit;
}
.toolbar-batch-btn .action-icon { width: 11px; height: 11px; }
.toolbar-batch-btn:hover { background: #A32D2D; }
.toolbar-clear-btn {
  background: transparent; color: #5F5E5A;
  border: none; font-size: 10px;
  cursor: pointer;
  text-decoration: underline;
}
.toolbar-clear-btn:hover { color: #E24B4A; }
.fade-enter-active, .fade-leave-active { transition: all 0.18s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateX(-6px); }

.toolbar-right { display: flex; gap: 8px; align-items: center; }
.toolbar-select { width: 130px; }

/* ===== 帖子卡片 ===== */
.post-card-list { display: flex; flex-direction: column; gap: 10px; min-height: 100px; }
.post-card-admin {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff;
  border: 0.5px solid #D3D1C7;
  border-radius: 10px;
  padding: 14px 14px 14px 18px;
  transition: all 0.2s;
}
.post-card-admin.post-card-selected {
  background: #FAFDFC;
  border-color: #1D9E75;
  box-shadow: 0 2px 8px rgba(29, 158, 117, 0.08);
}
.post-card-checkbox {
  display: inline-flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  padding-top: 18px;
  cursor: pointer;
}
.post-cb {
  width: 16px; height: 16px;
  accent-color: #1D9E75;
  cursor: pointer;
}
.post-card-admin {
  position: relative;
  overflow: hidden;
  transition: all 0.2s;
}
.post-card-admin:hover { border-color: #1D9E75; box-shadow: 0 2px 8px rgba(29,158,117,0.08); }

.post-bar { position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }
.post-bar.blue { background: #378ADD; }
.post-bar.pink { background: #D4537E; }
.post-bar.green { background: #1D9E75; }
.post-bar.amber { background: #BA7517; }
.post-bar.purple { background: #7F77DD; }
.post-bar.coral { background: #D85A30; }

.post-avatar {
  width: 30px; height: 30px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 500; flex-shrink: 0;
}
.post-avatar.blue { background: #E6F1FB; color: #185FA5; }
.post-avatar.pink { background: #FBEAF0; color: #993556; }
.post-avatar.green { background: #E1F5EE; color: #0F6E56; }
.post-avatar.amber { background: #FAEEDA; color: #854F0B; }
.post-avatar.purple { background: #EEEDFE; color: #534AB7; }
.post-avatar.coral { background: #FAECE7; color: #993C1D; }

.post-body { flex: 1; min-width: 0; }
.post-title-row { display: flex; align-items: baseline; gap: 8px; margin-bottom: 6px; }
.post-id { font-size: 11px; color: #B4B2A9; flex-shrink: 0; }
.post-title {
  font-size: 14px; font-weight: 500; color: #2C2C2A;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.text-strike { text-decoration: line-through; opacity: 0.7; }

.post-tags { display: flex; gap: 6px; margin-bottom: 6px; flex-wrap: wrap; }
.pill-board {
  display: inline-flex; align-items: center;
  padding: 1px 8px; border-radius: 8px;
  font-size: 10px; font-weight: 500;
}
.pill-board.blue { background: #E6F1FB; color: #185FA5; }
.pill-board.pink { background: #FBEAF0; color: #993556; }
.pill-board.green { background: #E1F5EE; color: #0F6E56; }
.pill-board.amber { background: #FAEEDA; color: #854F0B; }
.pill-board.purple { background: #EEEDFE; color: #534AB7; }
.pill-board.coral { background: #FAECE7; color: #993C1D; }

.pill-meta { display: inline-flex; align-items: center; padding: 1px 8px; border-radius: 8px; font-size: 10px; background: #F1EFE8; color: #888780; }
.pill-essence { background: #FAEEDA; color: #BA7517; }

.post-meta { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #888780; margin-bottom: 4px; }
.meta-dot { color: #D3D1C7; }
.post-preview {
  font-size: 11px; color: #B4B2A9;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.post-data { width: 150px; flex-shrink: 0; padding-left: 4px; border-left: 0.5px solid #F1EFE8; }
.data-label { font-size: 10px; color: #B4B2A9; margin-bottom: 4px; }
.data-row { display: flex; gap: 10px; font-size: 11px; color: #888780; margin-bottom: 4px; }
.data-last-comment {
  font-size: 10px; color: #B4B2A9;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.post-actions { width: 150px; flex-shrink: 0; display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.status-pill {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 0 10px; height: 20px; border-radius: 10px;
  font-size: 10px; font-weight: 500;
}
.status-ok { background: #EAF3DE; color: #27500A; }
.status-deleted { background: #FCEBEB; color: #791F1F; }

.action-btns { display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; }
.action-btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: 4px;
  padding: 0 10px; height: 24px; border-radius: 12px;
  background: #fff; color: #5F5E5A;
  border: 0.5px solid #D3D1C7; font-size: 10px;
  cursor: pointer; transition: all 0.2s;
  font-family: inherit;
  white-space: nowrap;
}
.action-btn .action-icon { width: 11px; height: 11px; flex-shrink: 0; }
.action-btn:hover { background: #F1EFE8; }
.action-danger { color: #E24B4A; border-color: #E24B4A; }
.action-danger:hover { background: #FCEBEB; }
.action-success { color: #639922; border-color: #639922; }
.action-success:hover { background: #EAF3DE; }

/* ===== 空状态 ===== */
.empty-state { background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px; padding: 40px 20px; text-align: center; }
.empty-icon { font-size: 32px; margin-bottom: 8px; }
.empty-title { font-size: 13px; font-weight: 500; color: #5F5E5A; margin-bottom: 4px; }
.empty-desc { font-size: 11px; color: #B4B2A9; }

/* ===== 分页 ===== */
.pagination-wrap { margin-top: 14px; }
.pagination-inner {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px;
  padding: 10px 16px; flex-wrap: wrap;
}
.page-total { font-size: 11px; color: #888780; }
.page-btns { display: flex; gap: 6px; }
.page-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; border-radius: 50%;
  font-size: 11px; cursor: pointer;
  color: #5F5E5A; background: transparent;
  border: 0.5px solid #D3D1C7;
  transition: all 0.2s;
}
.page-btn:hover { background: #F1EFE8; }
.page-btn.active { background: #1D9E75; color: #fff; border-color: #1D9E75; }
.page-next {
  display: inline-flex; align-items: center;
  padding: 0 12px; height: 24px; border-radius: 12px;
  background: transparent; color: #5F5E5A;
  border: 0.5px solid #D3D1C7; font-size: 10px;
  cursor: pointer; transition: all 0.2s;
}
.page-next:hover { background: #F1EFE8; }
.page-next:disabled { opacity: 0.4; cursor: not-allowed; }
.page-size { font-size: 11px; color: #888780; }
.page-size b { color: #5F5E5A; font-weight: 500; }

/* ===== 用户表 ===== */
.user-table-wrap { background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px; padding: 8px; }
.user-status { display: inline-flex; padding: 1px 10px; border-radius: 10px; font-size: 10px; font-weight: 500; }
.user-status-ok { background: #EAF3DE; color: #27500A; }
.user-status-off { background: #FCEBEB; color: #791F1F; }
.muted-tip { color: #888780; font-size: 11px; text-align: center; margin: 12px 0 0; }

/* ===== 占位卡 ===== */
.placeholder-card {
  background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px;
  padding: 60px 20px; text-align: center;
}
.placeholder-icon { font-size: 36px; margin-bottom: 10px; }
.placeholder-title { font-size: 14px; font-weight: 500; color: #2C2C2A; margin-bottom: 6px; }
.placeholder-desc { font-size: 12px; color: #B4B2A9; }

/* ===== 详情弹窗（保留原有） ===== */
.post-detail .detail-title { margin: 0 0 8px; }
.post-detail .detail-meta { display: flex; gap: 12px; align-items: center; font-size: 13px; color: #606266; }
.post-detail h4 { margin: 16px 0 8px; font-size: 14px; color: #303133; }
.content-block {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #409EFF;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.6;
}
.last-comment-detail { border-left-color: #67C23A; }
.snapshot-stats { margin: 8px 0 16px; }
.stat-tile { text-align: center; padding: 10px 0; background: #f0f9ff; border-radius: 6px; }
.stat-num-s { font-size: 20px; font-weight: 700; color: #409EFF; }
.stat-lab { font-size: 11px; color: #909399; margin-top: 2px; }
.all-comments { max-height: 360px; overflow-y: auto; border: 1px solid #ebeef5; border-radius: 6px; padding: 8px; background: #fafbfc; }
.comment-item { padding: 10px; border-bottom: 1px dashed #ebeef5; }
.comment-item:last-child { border-bottom: none; }
.comment-item.comment-deleted { opacity: 0.6; }
.comment-head { display: flex; gap: 8px; align-items: center; font-size: 12px; color: #606266; margin-bottom: 6px; flex-wrap: wrap; }
.comment-num { font-weight: 700; color: #409EFF; }
.comment-id { color: #909399; font-size: 11px; }
.comment-author { font-weight: 500; color: #67C23A; }
.comment-time { color: #909399; }
.comment-content { font-size: 13px; line-height: 1.6; color: #303133; padding: 6px 0; }
.comment-meta { font-size: 11px; color: #909399; }
.meta-row { display: flex; gap: 12px; font-size: 12px; color: #909399; margin-bottom: 8px; }
.meta-content { color: #303133; }

/* ===== 响应式 ===== */
@media (max-width: 860px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .post-data { display: none; }
  .post-actions { width: auto; }
  .hero-stats { display: none; }
}
</style>
