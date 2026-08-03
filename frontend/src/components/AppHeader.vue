<template>
  <header class="app-header">
    <div class="header-content">
      <!-- 左侧 Logo -->
      <div class="header-left">
        <router-link to="/" class="logo">
          <span class="logo-text">Campus Forum</span>
          <span class="logo-sub">· 校园论坛</span>
        </router-link>
      </div>

      <!-- 中部搜索栏 -->
      <div class="header-search">
        <div class="search-box" :class="{ focused: searchFocused }">
          <span class="search-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <circle cx="10.5" cy="10.5" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/>
              <line x1="15" y1="15" x2="19" y2="19" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
          </span>
          <input
            ref="searchInput"
            v-model="searchKeyword"
            class="search-input"
            placeholder="搜索帖子标题..."
            @focus="onFocus"
            @blur="onBlur"
            @keyup.enter="handleSearch"
          />
          <button v-if="searchFocused" class="search-enter-btn" type="button" @mousedown.prevent="handleSearch">
            Enter 搜索
          </button>

          <!-- 下拉建议面板 -->
          <transition name="dropdown">
            <div v-if="searchFocused && showSuggestions" class="search-dropdown">
              <!-- 输入框为空：显示热门搜索 -->
              <template v-if="!searchKeyword.trim()">
                <div class="dropdown-section">
                  <div class="section-title">🔥 热门搜索</div>
                  <ul class="hot-list">
                    <li
                      v-for="(item, i) in hotKeywords"
                      :key="item.label + i"
                      class="hot-item"
                      :class="{ active: hoveredHot === i }"
                      @mouseenter="hoveredHot = i"
                      @mouseleave="hoveredHot = -1"
                      @mousedown.prevent="selectHot(item.label)"
                    >
                      <span class="hot-rank" :class="`rank-${i + 1}`">{{ i + 1 }}</span>
                      <span class="hot-label">{{ item.label }}</span>
                      <span class="hot-count">{{ item.count }} 条结果</span>
                    </li>
                    <li v-if="!hotKeywords.length" class="hot-empty">暂无热门搜索</li>
                  </ul>
                </div>
              </template>

              <!-- 输入框有内容：显示相关建议 -->
              <template v-else>
                <div v-if="suggestions.length" class="dropdown-section">
                  <div class="section-title">📚 相关搜索</div>
                  <ul class="hot-list">
                    <li
                      v-for="(item, i) in suggestions"
                      :key="item.title + i"
                      class="hot-item"
                      :class="{ active: hoveredHot === i }"
                      @mouseenter="hoveredHot = i"
                      @mouseleave="hoveredHot = -1"
                      @mousedown.prevent="selectHot(item.title)"
                    >
                      <el-icon style="color:#B4B2A9"><Document /></el-icon>
                      <span class="hot-label">{{ item.title }}</span>
                    </li>
                  </ul>
                </div>
              </template>

              <div class="dropdown-footer">
                <span class="footer-tip">按 Enter 直接搜索「{{ searchKeyword || '热门话题' }}」</span>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- 右侧导航 -->
      <div class="header-right">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          首页
        </router-link>
        <template v-if="userStore.isLoggedIn">
          <router-link v-if="userStore.user?.role === 3" to="/admin" class="nav-item" :class="{ active: $route.path === '/admin' }">
            <el-icon><Monitor /></el-icon> 管理
          </router-link>
          <router-link to="/posts/create" class="nav-item" :class="{ active: $route.path === '/posts/create' }">
            写新帖子
          </router-link>
          <router-link to="/profile" class="nav-item profile-nav" :class="{ active: $route.path === '/profile' }">
            <span class="nav-avatar">{{ (userStore.user?.nickname || '我').charAt(0) }}</span>
            {{ userStore.user?.nickname || '我的' }}
          </router-link>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-item" :class="{ active: $route.path === '/login' }">
            登录
          </router-link>
          <router-link to="/register" class="nav-item" :class="{ active: $route.path === '/register' }">
            注册
          </router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Document } from '@element-plus/icons-vue'
import { Monitor } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()
const searchKeyword = ref('')
const searchFocused = ref(false)
const showSuggestions = ref(false)
const hoveredHot = ref(-1)
const searchInput = ref<HTMLInputElement | null>(null)
const hotKeywords = ref<{ label: string; count: number }[]>([])
const suggestions = ref<{ title: string; id?: number }[]>([])
let suggestTimer: any = null

// 加载热门关键词（每次聚焦都重新拉取）
async function loadHotKeywords() {
  try {
    const res = await api.get('/posts/hot-keywords')
    hotKeywords.value = (res.data || []).slice(0, 5)
  } catch {
    hotKeywords.value = [
      { label: '期末复习', count: 12 },
      { label: '表白墙投稿', count: 8 },
      { label: '二手书交易', count: 6 },
      { label: '食堂推荐', count: 3 },
      { label: '校园兼职', count: 5 },
    ]
  }
}

// 加载相关搜索建议（输入时调用）
async function loadSuggestions(prefix: string) {
  if (!prefix.trim()) {
    suggestions.value = []
    return
  }
  try {
    const res = await api.get('/posts/search-suggest', { params: { prefix: prefix.trim() } })
    suggestions.value = (res.data || []).slice(0, 6)
  } catch {
    suggestions.value = []
  }
}

function onFocus() {
  searchFocused.value = true
  showSuggestions.value = true
  // 每次聚焦都拉一次最新热门
  loadHotKeywords()
}

function onBlur() {
  searchFocused.value = false
  // 延迟关闭面板，避免点击建议项时瞬间关闭
  setTimeout(() => { showSuggestions.value = false }, 150)
}

// 监听输入：300ms 防抖后拉相关搜索
watch(searchKeyword, (val) => {
  if (suggestTimer) clearTimeout(suggestTimer)
  suggestTimer = setTimeout(() => loadSuggestions(val), 300)
})

function selectHot(label: string) {
  searchKeyword.value = label
  handleSearch()
}

function handleSearch() {
  const kw = searchKeyword.value.trim()
  if (!kw) return
  // 跳转到新的搜索结果页
  router.push({ path: '/search', query: { kw } })
  showSuggestions.value = false
  searchFocused.value = false
  searchInput.value?.blur()
}

onMounted(async () => {
  loadHotKeywords()
  if (!userStore.user) {
    const restored = await userStore.initFromToken()
    if (!restored) {
      await userStore.fetchMe()
    }
  }
})
</script>

<style scoped>
.app-header {
  background: linear-gradient(90deg, #0C447C 0%, #1D9E75 100%);
  color: #fff;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 60px;
}

/* ===== Logo ===== */
.header-left .logo {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  color: #fff;
  height: 60px;
  flex-shrink: 0;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
}
.logo-sub {
  font-size: 12px;
  color: #9FE1CB;
  font-weight: 400;
}

/* ===== 搜索栏 ===== */
.header-search {
  flex: 1;
  max-width: 460px;
  margin: 0 20px;
  position: relative;
}
.search-box {
  position: relative;
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  display: flex;
  align-items: center;
  height: 36px;
  padding: 0 6px 0 14px;
  box-shadow: none;
  transition: all 0.2s;
}
.search-box.focused {
  background: #fff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.search-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #888780;
  flex-shrink: 0;
  margin-right: 6px;
}
.search-box.focused .search-icon {
  color: #1D9E75;
}
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  height: 100%;
  font-size: 13px;
  color: #2C2C2A;
  font-family: inherit;
  min-width: 0;
}
.search-input::placeholder {
  color: #B4B2A9;
}
.search-enter-btn {
  flex-shrink: 0;
  height: 28px;
  padding: 0 14px;
  background: #1D9E75;
  color: #fff;
  border: none;
  border-radius: 14px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  letter-spacing: 0.3px;
  transition: background 0.2s;
}
.search-enter-btn:hover {
  background: #0F6E56;
}

/* ===== 下拉建议面板 ===== */
.search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 12px 32px rgba(12, 68, 124, 0.16), 0 2px 6px rgba(0, 0, 0, 0.06);
  z-index: 200;
  overflow: hidden;
  padding: 8px 0;
}
.dropdown-section {
  padding: 4px 0;
}
.section-title {
  padding: 8px 16px 4px;
  font-size: 11px;
  font-weight: 500;
  color: #888780;
  text-transform: none;
  letter-spacing: 0.4px;
}
.hot-list {
  margin: 0;
  padding: 0;
  list-style: none;
}
.hot-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 13px;
  color: #2C2C2A;
  gap: 10px;
}
.hot-item.active,
.hot-item:hover {
  background: #F1EFE8;
}
.hot-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  background: #F1EFE8;
  color: #888780;
  font-size: 11px;
  font-weight: 500;
  flex-shrink: 0;
}
.hot-item.active .hot-rank {
  color: #fff;
  background: #1D9E75;
}
.rank-1 { background: #E24B4A !important; color: #fff !important; }
.rank-2 { background: #D85A30 !important; color: #fff !important; }
.rank-3 { background: #BA7517 !important; color: #fff !important; }
.hot-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hot-count {
  color: #B4B2A9;
  font-size: 12px;
  flex-shrink: 0;
}
.hot-empty {
  padding: 12px 16px;
  font-size: 12px;
  color: #B4B2A9;
  text-align: center;
}
.dropdown-footer {
  border-top: 0.5px solid #F1EFE8;
  margin-top: 4px;
  padding: 10px 16px;
  background: #FAFDFC;
}
.footer-tip {
  font-size: 11px;
  color: #888780;
}

/* ===== 下拉过渡 ===== */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.18s ease;
  transform-origin: top center;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px) scaleY(0.96);
}

/* ===== 右侧导航 ===== */
.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 60px;
  flex-shrink: 0;
}
.nav-item {
  color: #9FE1CB;
  text-decoration: none;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 14px;
  border-radius: 16px;
  transition: all 0.2s;
  line-height: 32px;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}
.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 500;
}
.nav-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #0F6E56;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
}

/* ===== 响应式 ===== */
@media (max-width: 720px) {
  .logo-sub { display: none; }
  .header-search { max-width: 220px; margin: 0 8px; }
}
</style>
