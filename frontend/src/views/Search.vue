<template>
  <div class="search-page">
    <!-- ===== Hero 渐变搜索区 ===== -->
    <div class="search-hero">
      <!-- 大搜索框 -->
      <div class="search-input-wrap">
        <span class="search-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="1.8"/>
            <line x1="15" y1="15" x2="19" y2="19" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </span>
        <input
          ref="kwInput"
          v-model="kw"
          class="search-input"
          placeholder="搜索帖子、作者、内容..."
          @keyup.enter="doSearch"
        />
        <button class="search-btn" @click="doSearch" :disabled="loading">
          <span v-if="loading">搜索中</span>
          <span v-else>搜 索</span>
        </button>
      </div>

      <!-- 热门快捷词（实时刷新） -->
      <div class="hot-keywords">
        <span class="hot-label">热门→</span>
        <span
          v-for="item in hotKeywords.slice(0, 6)"
          :key="item.label + '-' + hotVersion"
          class="hot-pill"
          :class="{ 'hot-pill-active': kw === item.label }"
          @click="quickSearch(item.label)"
        >
          {{ item.label }}
        </span>
      </div>
    </div>

    <!-- ===== 主体：左结果 + 右侧栏 ===== -->
    <div class="search-body">
      <div class="search-main">
        <!-- 工具栏 -->
        <div v-if="kw" class="result-toolbar">
          <div class="toolbar-meta">
            搜索结果 <span class="kw-highlight-inline">「{{ kw }}」</span> 共
            <span class="count-badge">{{ total }}</span> 条
          </div>
          <div class="toolbar-actions">
            <button class="sort-pill" :class="{ active: sortType === 'time' }" @click="setSort('time')">最新</button>
            <button class="sort-pill" :class="{ active: sortType === 'view' }" @click="setSort('view')">最多浏览量</button>
          </div>
        </div>

        <!-- 热门搜索大块（无搜索词时显示） -->
        <div v-if="!kw" class="hot-section">
          <div class="hot-section-header">
            <h3>🔥 热门搜索</h3>
            <button class="refresh-btn" @click="refreshHotKeywords">
              <svg viewBox="0 0 24 24" width="14" height="14"><path d="M17.65 6.35A7.95 7.95 0 0 0 12 4a8 8 0 1 0 7.45 11h-2.1A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/></svg>
              换一批
            </button>
          </div>
          <div class="hot-grid">
            <div v-for="(item, i) in hotKeywords" :key="item.label + '-grid-' + hotVersion" class="hot-card" @click="quickSearch(item.label)">
              <span class="hot-rank" :class="`rank-${i + 1}`">{{ i + 1 }}</span>
              <span class="hot-label">{{ item.label }}</span>
              <span class="hot-count">{{ item.count }} 条结果</span>
            </div>
          </div>
        </div>

        <!-- 搜索结果列表 -->
        <template v-else>
          <div v-loading="loading" class="result-list">
            <div v-if="!results.length && !loading" class="empty-state">
              <div class="empty-icon">
                <svg viewBox="0 0 80 80" width="68" height="68">
                  <circle cx="32" cy="32" r="20" fill="none" stroke="#D3D1C7" stroke-width="3"/>
                  <line x1="46" y1="46" x2="62" y2="62" stroke="#D3D1C7" stroke-width="4" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="empty-title">没有找到相关内容</div>
              <div class="empty-desc">换个关键词试试，或检查关键词是否拼写正确</div>
              <button class="empty-btn" @click="$router.push('/')">查看全部帖子</button>
            </div>

            <div
              v-for="p in results"
              :key="p.id"
              class="post-card"
              @click="$router.push(`/posts/${p.id}`)"
            >
              <div class="post-bar" :class="boardColorClass(p.board_id)"></div>
              <div class="post-avatar" :class="boardColorClass(p.board_id)">
                {{ (p.board_name || '匿').charAt(0) }}
              </div>
              <div class="post-body">
                <div class="post-title" v-html="highlightTitle(p.title)"></div>
                <div class="post-tags">
                  <span class="pill-board" :class="boardColorClass(p.board_id)">
                    {{ p.board_name || '默认板块' }}
                  </span>
                  <span v-if="p.is_pinned" class="pill-meta">置顶</span>
                  <span v-if="p.is_essence" class="pill-meta pill-essence">精华</span>
                </div>
                <div class="post-content" v-html="highlightContent(p.content_preview)"></div>
                <div class="post-meta">
                  <span class="meta-item">
                    <svg viewBox="0 0 24 24" width="11" height="11"><circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>
                    {{ p.anonymous_name }}
                  </span>
                  <span class="meta-item">📅 {{ p.created_at }}</span>
                  <span class="meta-item stat-blue">👍 {{ p.like_count || 0 }}</span>
                  <span class="meta-item">💬 {{ p.comment_count || 0 }}</span>
                  <span class="meta-item">👁 {{ p.view_count || 0 }}</span>
                  <span class="meta-item">⭐ {{ p.favorite_count || 0 }}</span>
                </div>
              </div>
              <div class="post-right">
                <button class="view-btn">查看 →</button>
              </div>
            </div>
          </div>

          <!-- 加载更多 / 分页 -->
          <div v-if="results.length" class="load-more-wrap">
            <button v-if="hasMore" class="load-more-btn" @click="loadMore">加载更多结果 ↓</button>
            <span v-else class="no-more">— 没有更多了 —</span>
          </div>
        </template>
      </div>

      <!-- 右侧栏：板块筛选 -->
      <div v-if="kw" class="search-side">
        <div class="side-card">
          <div class="side-title">板块筛选</div>
          <div class="board-filters">
            <button class="board-pill" :class="{ active: !boardFilter }" @click="setBoardFilter('')">全部板块</button>
            <button
              v-for="b in availableBoards"
              :key="b.id"
              class="board-pill"
              :class="['board-' + boardColorClass(b.id), { active: boardFilter === b.id }]"
              @click="setBoardFilter(b.id)"
            >
              {{ b.name }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { StarFilled, Right } from '@element-plus/icons-vue'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const kw = ref((route.query.kw as string) || '')
const sortType = ref<'time' | 'view'>('time')
const boardFilter = ref<number | ''>('')
const results = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = 10
const hasMore = ref(false)
const hotKeywords = ref<any[]>([])
const hotVersion = ref(0)              // 用于强制刷新组件
const availableBoards = ref<any[]>([])
const kwInput = ref<HTMLInputElement | null>(null)

// 颜色映射
const colors = ['blue', 'pink', 'green', 'amber', 'purple', 'coral']
function boardColorClass(id?: number | string) {
  if (id === undefined || id === null) return 'green'
  const n = typeof id === 'string' ? id.length : id
  return colors[n % colors.length]
}

async function loadHotKeywords() {
  try {
    const res = await api.get('/posts/hot-keywords')
    hotKeywords.value = res.data || []
  } catch {
    hotKeywords.value = [
      { label: '期末复习', count: 12 },
      { label: '表白墙投稿', count: 8 },
      { label: '二手书交易', count: 6 },
      { label: '食堂推荐', count: 3 },
      { label: '校园兼职', count: 5 },
      { label: '失物招领', count: 4 },
    ]
  }
  hotVersion.value++    // 触发 :key 变更 → 强制重新渲染
}

// 用户主动点 "换一批" / 刷新按钮
function refreshHotKeywords() {
  loadHotKeywords()
}

async function loadBoards() {
  try {
    const res = await api.get('/boards')
    availableBoards.value = res.data?.list || res.data || []
  } catch {
    availableBoards.value = []
  }
}

async function loadResults(resetPage = true) {
  if (!kw.value.trim()) return
  if (resetPage) page.value = 1
  loading.value = true
  try {
    const params: any = {
      kw: kw.value.trim(),
      sort: sortType.value,
      cursor: page.value > 1 ? (page.value - 1) * pageSize : undefined,
      limit: pageSize,
    }
    if (boardFilter.value !== '') params.board_id = boardFilter.value

    const res = await api.get('/posts', { params })
    const list = res.data?.list || []
    if (resetPage) {
      results.value = list
    } else {
      results.value = results.value.concat(list)
    }
    hasMore.value = !!res.data?.has_more
    total.value = hasMore.value
      ? (page.value * pageSize + 1)
      : (page.value - 1) * pageSize + list.length
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '搜索失败')
    results.value = []
    hasMore.value = false
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  page.value += 1
  await loadResults(false)
}

function doSearch() {
  const q = kw.value.trim()
  if (!q) { ElMessage.warning('请输入搜索内容'); return }
  page.value = 1
  router.replace({ query: { kw: q } })
  loadResults()
}

function quickSearch(label: string) {
  kw.value = label
  doSearch()
}

function setSort(s: 'time' | 'view') {
  sortType.value = s
  loadResults()
}

function setBoardFilter(id: number | '') {
  boardFilter.value = id
  loadResults()
}

function escapeHtml(s: string): string {
  if (!s) return ''
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function highlightTitle(title: string): string {
  const safe = escapeHtml(title)
  if (!kw.value) return safe
  const re = new RegExp(`(${escapeRegExp(kw.value)})`, 'gi')
  return safe.replace(re, '<span class="kw-highlight">$1</span>')
}

function highlightContent(text: string): string {
  const safe = escapeHtml(text)
  if (!kw.value) return safe
  const re = new RegExp(`(${escapeRegExp(kw.value)})`, 'gi')
  return safe.replace(re, '<span class="kw-content-highlight">$1</span>')
}

// 路由 kw 变化 → 自动重新拉热词（实时性）
watch(() => route.query.kw, (newKw) => {
  kw.value = (newKw as string) || ''
  // 每次进入搜索页都重新拉取热词，保证"实时"
  loadHotKeywords()
  if (kw.value) loadResults()
})

onMounted(() => {
  loadHotKeywords()
  loadBoards()
  if (kw.value) loadResults()
  kwInput.value?.focus()
})
</script>

<style scoped>
.search-page { max-width: 960px; margin: 0 auto; padding: 0 16px; }

/* ===== Hero 渐变区 ===== */
.search-hero {
  background: linear-gradient(90deg, #0C447C 0%, #1D9E75 100%);
  padding: 18px 24px 22px;
  border-radius: 14px;
  margin-bottom: 14px;
  color: #fff;
}

.search-input-wrap {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 22px;
  padding: 4px 4px 4px 18px;
  height: 44px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.search-icon { display: inline-flex; color: #1D9E75; margin-right: 8px; }
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: #2C2C2A;
  height: 100%;
  font-family: inherit;
}
.search-input::placeholder { color: #B4B2A9; }
.search-btn {
  border: none;
  background: #1D9E75;
  color: #fff;
  border-radius: 18px;
  height: 36px;
  padding: 0 22px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}
.search-btn:hover { background: #0F6E56; }
.search-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.hot-keywords {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 14px;
}

/* 热门标签 —— 迷你胶囊（与 pill 同高，比 pill 略小） */
.hot-label {
  display: inline-block !important;
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  width: auto !important;
  height: 22px;
  line-height: 22px;
  padding: 0 8px;
  margin-right: auto !important;             /* 把后面的 pills 推到右侧 */
  border-radius: 11px;
  background: linear-gradient(135deg, #FFD580 0%, #FFE9C2 100%);
  color: #8B5A00;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2px;
  box-shadow: 0 1px 2px rgba(255, 211, 128, 0.5);
  border: 0.5px solid rgba(255, 211, 128, 0.6);
  vertical-align: middle;
  white-space: nowrap;
}
.hot-label :deep(svg) { display: none !important; }
.hot-label .hot-arrow { display: none !important; }

.hot-pill {
  display: inline-flex; align-items: center;
  flex: 0 0 auto !important;             /* 禁止拉伸 */
  padding: 4px 12px;
  background: rgba(255,255,255,0.18);
  color: #fff;
  border-radius: 12px;
  font-size: 11px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}
.hot-pill:hover { background: rgba(255,255,255,0.32); }
.hot-pill.hot-pill-active { background: #fff; color: #1D9E75; font-weight: 500; }

/* ===== 主体两栏 ===== */
.search-body { display: flex; gap: 16px; align-items: flex-start; }
.search-main { flex: 1; min-width: 0; }
.search-side { width: 196px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px; }

/* ===== 工具栏 ===== */
.result-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff;
  border: 0.5px solid #D3D1C7;
  border-radius: 10px;
  padding: 12px 18px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 10px;
}
.toolbar-meta { font-size: 13px; color: #5F5E5A; }
.kw-highlight-inline { color: #1D9E75; font-weight: 500; margin: 0 4px; }
.count-badge {
  display: inline-block; padding: 1px 8px;
  background: #E1F5EE; color: #1D9E75;
  border-radius: 10px; font-size: 12px; font-weight: 500;
  margin: 0 4px;
}
.toolbar-actions { display: flex; gap: 6px; }
.sort-pill {
  border: 0.5px solid #D3D1C7;
  background: #fff;
  color: #5F5E5A;
  padding: 4px 14px;
  border-radius: 14px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}
.sort-pill:hover { background: #F1EFE8; }
.sort-pill.active { background: #1D9E75; color: #fff; border-color: #1D9E75; font-weight: 500; }

/* ===== 热门搜索（无搜索词时） ===== */
.hot-section {
  background: #fff;
  border: 0.5px solid #D3D1C7;
  border-radius: 10px;
  padding: 18px 22px;
}
.hot-section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.hot-section-header h3 { margin: 0; font-size: 14px; font-weight: 500; color: #2C2C2A; }
.refresh-btn {
  background: transparent; border: none; color: #888780; font-size: 11px;
  cursor: pointer; display: inline-flex; align-items: center; gap: 3px;
}
.refresh-btn:hover { color: #1D9E75; }

.hot-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.hot-card {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px;
  background: #FAFDFC;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.hot-card:hover { background: #E1F5EE; transform: translateY(-1px); }
.hot-rank {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: 5px;
  background: #F1EFE8; color: #888780;
  font-size: 10px; font-weight: 500; flex-shrink: 0;
}
.hot-card .rank-1 { background: #E24B4A; color: #fff; }
.hot-card .rank-2 { background: #D85A30; color: #fff; }
.hot-card .rank-3 { background: #BA7517; color: #fff; }
.hot-label { flex: 1; font-size: 13px; color: #2C2C2A; font-weight: 500; }
.hot-count { font-size: 11px; color: #B4B2A9; }

/* ===== 结果列表 ===== */
.result-list { display: flex; flex-direction: column; gap: 10px; }
.post-card {
  display: flex; align-items: flex-start; gap: 12px;
  background: #fff;
  border: 0.5px solid #D3D1C7;
  border-radius: 10px;
  padding: 14px 18px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}
.post-card:hover { background: #FAFDFC; border-color: #1D9E75; }

.post-bar {
  position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
}
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
.post-title {
  font-size: 14px; font-weight: 500; color: #2C2C2A;
  margin-bottom: 8px; line-height: 1.5;
  overflow: hidden; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical;
}
.post-title :deep(.kw-highlight) {
  color: #1D9E75;
  background: #E1F5EE;
  padding: 0 4px;
  border-radius: 3px;
  font-weight: 600;
}

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

.post-content {
  font-size: 12px; color: #888780;
  line-height: 1.6;
  margin-bottom: 8px;
  overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}
.post-content :deep(.kw-content-highlight) {
  color: #1D9E75;
  background: #E1F5EE;
  padding: 0 2px;
  border-radius: 2px;
  font-weight: 500;
}

.post-meta { display: flex; gap: 12px; flex-wrap: wrap; font-size: 11px; color: #888780; }
.meta-item { display: inline-flex; align-items: center; gap: 3px; }
.stat-blue { color: #378ADD; font-weight: 500; }

.post-right { display: flex; align-items: flex-start; flex-shrink: 0; }
.view-btn {
  background: transparent;
  border: 0.5px solid #D3D1C7;
  color: #5F5E5A;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}
.view-btn:hover { background: #1D9E75; color: #fff; border-color: #1D9E75; }

/* ===== 空状态 ===== */
.empty-state {
  background: #fff;
  border: 0.5px solid #D3D1C7;
  border-radius: 10px;
  padding: 48px 20px;
  text-align: center;
}
.empty-icon { margin-bottom: 14px; }
.empty-title { font-size: 14px; font-weight: 500; color: #5F5E5A; margin-bottom: 6px; }
.empty-desc { font-size: 12px; color: #B4B2A9; margin-bottom: 16px; }
.empty-btn {
  background: #E1F5EE;
  color: #1D9E75;
  border: none;
  border-radius: 14px;
  padding: 6px 20px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.empty-btn:hover { background: #9FE1CB; }

/* ===== 加载更多 ===== */
.load-more-wrap { text-align: center; padding: 16px 0; }
.load-more-btn {
  background: #1D9E75; color: #fff;
  border: none; border-radius: 16px;
  padding: 8px 28px; font-size: 12px; font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.load-more-btn:hover { background: #0F6E56; }
.no-more { color: #B4B2A9; font-size: 11px; }

/* ===== 右侧栏 ===== */
.side-card {
  background: #fff;
  border: 0.5px solid #D3D1C7;
  border-radius: 10px;
  padding: 14px 16px;
}
.side-title {
  font-size: 12px; font-weight: 500; color: #2C2C2A;
  margin-bottom: 10px;
}

.board-filters { display: flex; flex-wrap: wrap; gap: 6px; }
.board-pill {
  display: inline-flex; align-items: center;
  padding: 3px 10px;
  background: #F1EFE8;
  color: #5F5E5A;
  border: 0.5px solid transparent;
  border-radius: 10px;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.board-pill:hover { background: #E1F5EE; color: #1D9E75; }
.board-pill.active { background: #1D9E75; color: #fff; border-color: #1D9E75; }
.board-pill.board-blue.active { background: #378ADD; border-color: #378ADD; }
.board-pill.board-pink.active { background: #D4537E; border-color: #D4537E; }
.board-pill.board-green.active { background: #1D9E75; border-color: #1D9E75; }
.board-pill.board-amber.active { background: #BA7517; border-color: #BA7517; }
.board-pill.board-purple.active { background: #7F77DD; border-color: #7F77DD; }
.board-pill.board-coral.active { background: #D85A30; border-color: #D85A30; }

/* ===== 响应式 ===== */
@media (max-width: 880px) {
  .search-body { flex-direction: column; }
  .search-side { width: 100%; }
  .side-card { flex: 1; }
}
</style>
