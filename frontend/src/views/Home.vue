<template>
  <div class="home-page">
    <div class="home-main">
      <!-- 左侧主内容 -->
      <div class="home-left">
        <!-- Hero 区域 -->
        <div class="hero-section">
          <div class="hero-icon">🌳</div>
          <div class="hero-text">
            <h2 class="hero-title">今天有什么想说的？</h2>
            <p class="hero-desc">匿名分享，畅所欲言</p>
          </div>
          <router-link v-if="userStore.isLoggedIn" to="/posts/create" class="hero-btn">写新帖子 →</router-link>
          <router-link v-else to="/login" class="hero-btn">登录参与 →</router-link>
        </div>

        <!-- 热门板块 -->
        <div class="section-header">
          <h3 class="section-title">热门板块</h3>
        </div>
        <div class="board-grid">
          <div
            v-for="(b, idx) in forumStore.boards.slice(0, 8)"
            :key="b.id"
            class="board-card"
            :class="'board-card-' + boardColors[idx % boardColors.length]"
            @click="$router.push(`/board/${b.id}`)"
          >
            <div class="board-icon-wrap" :class="'board-icon-' + boardColors[idx % boardColors.length]">
              <span>{{ b.icon || boardIcons[idx % boardIcons.length] }}</span>
            </div>
            <div class="board-info">
              <div class="board-name">{{ b.name }}</div>
              <div class="board-stats">{{ b.post_count || 0 }} 帖子</div>
            </div>
          </div>
        </div>

        <!-- Tab 切换 -->
        <div class="tabs-row">
          <div class="tab" :class="{ 'tab-active': activeTab === 'latest' }" @click="switchTab('latest')">🔥 最新热帖</div>
          <div class="tab" :class="{ 'tab-active': activeTab === 'favorite' }" @click="switchTab('favorite')">⭐ 收藏</div>
          <div class="tab" :class="{ 'tab-active': activeTab === 'view' }" @click="switchTab('view')">👁 最多浏览</div>
        </div>

        <!-- 搜索结果提示 -->
        <div v-if="(route.query.kw as string)" class="search-banner">
          <el-icon><Search /></el-icon>
          <span>搜索 "<b>{{ route.query.kw }}</b>" 的结果 ({{ currentPosts.length }})</span>
          <el-button size="small" plain @click="clearSearch">清除</el-button>
        </div>

        <!-- 帖子列表 -->
        <div v-if="currentPosts.length === 0" class="empty-state">暂无帖子，快去发帖吧</div>
        <div
          v-for="(p, idx) in displayPosts"
          :key="p.id"
          class="post-card-modern"
          @click="$router.push(`/posts/${p.id}`)"
        >
          <div class="accent-bar" :class="'accent-' + barColors[idx % barColors.length]"></div>
          <div class="avatar-anon" :class="'avatar-' + avatarColors[idx % avatarColors.length]">匿</div>
          <div class="post-content">
            <div class="post-title-row">
              <span v-if="p.is_top" class="tag-pill tag-blue" style="margin-right:6px;">置顶</span>
              <span class="tag-pill" :class="'tag-' + tagColors[idx % tagColors.length]">{{ p.board_name || '默认' }}</span>
              <span class="post-title">{{ p.title }}</span>
            </div>
            <div class="post-meta">
              <span>{{ p.anonymous_name }}</span>
              <span>·</span>
              <span>{{ p.created_at }}</span>
            </div>
          </div>
          <div class="post-stats">
            <template v-if="activeTab === 'favorite'">
              <span class="stat-item">⭐ {{ p.favorite_count }}</span>
            </template>
            <template v-else-if="activeTab === 'view'">
              <span class="stat-item">👁 {{ p.view_count }}</span>
            </template>
            <template v-else>
              <span class="stat-item" :class="{ 'stat-hot': p.like_count > 50 }">♥ {{ p.like_count }}</span>
              <span class="stat-item">💬 {{ p.comment_count }}</span>
              <span class="stat-item">👁 {{ p.view_count }}</span>
              <span class="stat-item stat-fav">⭐ {{ p.favorite_count }}</span>
            </template>
          </div>
        </div>

        <div class="load-more" v-if="currentPosts.length > PREVIEW_LIMIT" @click="toggleLoadMore">
          <span v-if="!expanded">展开加载更多帖子 ↓ ({{ currentPosts.length - PREVIEW_LIMIT }} 条)</span>
          <span v-else>收起 ↑</span>
        </div>
      </div>

      <!-- 右侧 trending 栏 -->
      <div class="home-right">
        <div class="trending-card">
          <div class="trending-header">
            <span class="trending-icon">📈</span>
            <span class="trending-title">板块热度</span>
            <div class="trending-tabs">
              <span :class="{ 'trending-tab-active': trendingRange === 'week' }" @click="trendingRange = 'week'">本周</span>
              <span :class="{ 'trending-tab-active': trendingRange === 'month' }" @click="trendingRange = 'month'">本月</span>
            </div>
          </div>

          <div v-if="forumStore.trendingSummary" class="trending-summary">
            <div class="summary-item">
              <div class="summary-num">{{ forumStore.trendingSummary.total_recent_view }}</div>
              <div class="summary-label">总浏览</div>
            </div>
            <div class="summary-item">
              <div class="summary-num">{{ forumStore.trendingSummary.total_recent_posts }}</div>
              <div class="summary-label">新帖</div>
            </div>
            <div class="summary-item">
              <div class="summary-num">{{ forumStore.trendingSummary.active_boards }}</div>
              <div class="summary-label">活跃</div>
            </div>
          </div>

          <div v-if="forumStore.trendingBoards.length === 0" class="trending-empty">暂无数据</div>
          <div
            v-for="(b, idx) in forumStore.trendingBoards.slice(0, 6)"
            :key="b.board_id"
            class="trending-board-item"
            @click="$router.push(`/board/${b.board_id}`)"
          >
            <div class="trending-board-rank" :class="'trending-rank-' + Math.min(idx + 1, 3)">{{ idx + 1 }}</div>
            <span class="trending-board-icon">{{ b.board_icon || '💬' }}</span>
            <div class="trending-board-info">
              <div class="trending-board-name">{{ b.board_name }}</div>
              <div class="trending-board-bar-wrap">
                <div class="trending-board-bar" :style="{ width: b.percent + '%' }" :class="'bar-color-' + (idx % 6)"></div>
              </div>
            </div>
            <div class="trending-board-stat">
              <div class="trending-board-num">{{ b.recent_view }}</div>
              <div class="trending-board-label">浏览</div>
            </div>
          </div>
        </div>

        <!-- 收藏榜 - 任何 tab 都显示（按收藏数排序） -->
        <div class="rank-card">
          <div class="rank-header">
            <span class="rank-icon">⭐</span>
            <span class="rank-title">收藏榜 TOP3（按收藏数）</span>
          </div>
          <div v-if="favoriteTop3.length === 0" class="rank-empty">暂无数据</div>
          <div v-for="(p, idx) in favoriteTop3" :key="p.id" class="rank-item" @click="$router.push(`/posts/${p.id}`)">
            <div class="rank-num" :class="'rank-num-' + (idx + 1)">{{ idx + 1 }}</div>
            <div class="rank-content">
              <div class="rank-title-text">{{ p.title }}</div>
            </div>
            <div class="rank-stat">⭐ {{ p.favorite_count }}</div>
          </div>
        </div>

        <!-- 浏览榜 - 任何 tab 都显示（按浏览量排序） -->
        <div class="rank-card">
          <div class="rank-header">
            <span class="rank-icon">👁</span>
            <span class="rank-title">浏览榜 TOP3（按浏览量）</span>
          </div>
          <div v-if="viewTop3.length === 0" class="rank-empty">暂无数据</div>
          <div v-for="(p, idx) in viewTop3" :key="p.id" class="rank-item" @click="$router.push(`/posts/${p.id}`)">
            <div class="rank-num" :class="'rank-num-' + (idx + 1)">{{ idx + 1 }}</div>
            <div class="rank-content">
              <div class="rank-title-text">{{ p.title }}</div>
            </div>
            <div class="rank-stat">👁 {{ p.view_count }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { useForumStore } from '@/stores/forum'
import { useUserStore } from '@/stores/user'

const forumStore = useForumStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const boardColors = ['blue', 'pink', 'green', 'amber', 'purple', 'coral', 'teal', 'gray']
const boardIcons = ['📚', '💕', '☀️', '🛒', '💭', '💌', '🔍', '💼']
const barColors = ['blue', 'pink', 'green', 'amber', 'purple', 'coral']
const avatarColors = ['blue', 'pink', 'green', 'amber', 'purple', 'coral']
const tagColors = ['green', 'pink', 'green', 'amber', 'blue', 'coral']

const activeTab = ref<'latest' | 'favorite' | 'view'>('latest')
const trendingRange = ref<'week' | 'month'>('week')
const PREVIEW_LIMIT = 5
const expanded = ref(false)

const currentPosts = computed(() => {
  if (activeTab.value === 'latest') return forumStore.posts
  return forumStore.rankingList
})

const displayPosts = computed(() => {
  if (expanded.value) return currentPosts.value
  return currentPosts.value.slice(0, PREVIEW_LIMIT)
})

function toggleLoadMore() {
  expanded.value = !expanded.value
}

function clearSearch() {
  router.replace({ query: {} })
}

// 独立 fetch 缓存
const favRanking = ref<any[]>([])
const viewRanking = ref<any[]>([])

const favoriteTop3 = computed(() => {
  return favRanking.value.slice(0, 3)
})

const viewTop3 = computed(() => {
  return viewRanking.value.slice(0, 3)
})

async function switchTab(tab: 'latest' | 'favorite' | 'view') {
  activeTab.value = tab
  expanded.value = false
  if (tab === 'latest') {
    const params: any = { sort: 'time' }
    const kw = (route.query.kw as string) || ''
    if (kw) params.kw = kw
    await forumStore.fetchPosts(params)
  } else if (tab === 'favorite') {
    const res = await forumStore.fetchRanking('favorite', 10)
    favRanking.value = res?.list || []
  } else if (tab === 'view') {
    const res = await forumStore.fetchRanking('view', 10)
    viewRanking.value = res?.list || []
  }
}

async function loadBothRankings() {
  // 两个榜单都加载（按各自正确的排序）
  const favRes = await forumStore.fetchRanking('favorite', 10)
  favRanking.value = favRes?.list || []
  const viewRes = await forumStore.fetchRanking('view', 10)
  viewRanking.value = viewRes?.list || []
}

watch(trendingRange, async (val) => {
  await forumStore.fetchTrending(val)
})

onMounted(async () => {
  // 如果 URL 带 ?kw=，自动跳转到 /search 页
  const kw = (route.query.kw as string) || ''
  if (kw) {
    router.replace({ path: '/search', query: { kw } })
    return
  }
  await forumStore.fetchBoards()
  await forumStore.fetchPosts({ sort: 'time' })
  await forumStore.fetchTrending('week')
  await loadBothRankings()
})

// 监听 URL ?kw= 参数变化，自动跳转到 /search
watch(() => route.query.kw, (kw) => {
  if (kw) router.replace({ path: '/search', query: { kw: kw as string } })
})
</script>

<style scoped>
.home-page {
  max-width: 1280px;
  margin: 0 auto;
}
.home-main {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}
.home-left { min-width: 0; }
.home-right { display: flex; flex-direction: column; gap: 16px; }

/* Hero */
.hero-section {
  background: #E1F5EE;
  border-radius: 14px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.hero-icon {
  width: 48px;
  height: 48px;
  background: #1D9E75;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}
.hero-text { flex: 1; }
.hero-title { margin: 0 0 4px; font-size: 16px; font-weight: 600; color: #085041; }
.hero-desc { margin: 0; font-size: 12px; color: #0F6E56; }
.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 18px;
  background: #1D9E75;
  color: #fff;
  border-radius: 20px;
  font-size: 13px;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.2s;
  flex-shrink: 0;
}
.hero-btn:hover { background: #0F6E56; color: #fff; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-title { font-size: 15px; font-weight: 600; color: #1a1a1a; margin: 0; }

.board-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 24px;
}
.board-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.board-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.board-card-blue { background: #E6F1FB; }
.board-card-pink { background: #FBEAF0; }
.board-card-green { background: #EAF3DE; }
.board-card-amber { background: #FAEEDA; }
.board-card-purple { background: #EEEDFE; }
.board-card-coral { background: #FAECE7; }
.board-card-teal { background: #E1F5EE; }
.board-card-gray { background: #F1EFE8; }

.board-icon-wrap {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.board-icon-blue { background: #378ADD; }
.board-icon-pink { background: #D4537E; }
.board-icon-green { background: #639922; }
.board-icon-amber { background: #BA7517; }
.board-icon-purple { background: #7F77DD; }
.board-icon-coral { background: #D85A30; }
.board-icon-teal { background: #1D9E75; }
.board-icon-gray { background: #888780; }
.board-icon-wrap span { color: #fff; }
.board-info { flex: 1; min-width: 0; }
.board-name { font-size: 13px; font-weight: 600; color: #1a1a1a; }
.board-stats { font-size: 11px; color: #888780; margin-top: 2px; }

/* Tabs */
.tabs-row {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  background: #F1EFE8;
  padding: 4px;
  border-radius: 10px;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #5f5e5a;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.tab:hover { color: #1D9E75; }
.tab-active {
  background: linear-gradient(135deg, #1D9E75, #0F6E56);
  color: #fff;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(29,158,117,0.3);
}

/* Search banner */
.search-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #FFFBE6;
  border: 1px solid #FFE58F;
  border-radius: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #874D00;
}
.search-banner b { color: #D4380D; margin: 0 4px; }
.search-banner .el-icon { color: #D4380D; }

/* Post card */
.post-card-modern {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: #fff;
  border: 0.5px solid #d3d1c7;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 8px;
  position: relative;
}
.post-card-modern:hover {
  border-color: #1D9E75;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(29, 158, 117, 0.06);
}
.accent-bar { width: 3px; height: 36px; border-radius: 2px; flex-shrink: 0; margin-top: 4px; }
.accent-blue { background: #378ADD; }
.accent-pink { background: #D4537E; }
.accent-green { background: #639922; }
.accent-amber { background: #BA7517; }
.accent-purple { background: #7F77DD; }
.accent-coral { background: #D85A30; }

.avatar-anon {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600; flex-shrink: 0;
}
.avatar-blue { background: #E6F1FB; color: #185FA5; border: 0.5px solid #378ADD; }
.avatar-pink { background: #FBEAF0; color: #993556; border: 0.5px solid #D4537E; }
.avatar-green { background: #EAF3DE; color: #27500A; border: 0.5px solid #639922; }
.avatar-amber { background: #FAEEDA; color: #633806; border: 0.5px solid #BA7517; }
.avatar-purple { background: #EEEDFE; color: #3C3489; border: 0.5px solid #7F77DD; }
.avatar-coral { background: #FAECE7; color: #712B13; border: 0.5px solid #D85A30; }

.post-content { flex: 1; min-width: 0; }
.post-title-row { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
.post-title { font-size: 14px; font-weight: 500; color: #1a1a1a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.post-meta { display: flex; gap: 6px; font-size: 11px; color: #b4b2a9; }
.post-stats { display: flex; gap: 6px; flex-shrink: 0; align-items: center; padding-top: 4px; flex-wrap: wrap; }
.stat-item {
  font-size: 10px;
  color: #888780;
  background: #F1EFE8;
  padding: 2px 7px;
  border-radius: 10px;
  line-height: 1.6;
}
.stat-hot { background: #FCEBEB; color: #A32D2D; font-weight: 500; }
.stat-fav { background: #FFF7E6; color: #BA7517; }
.stat-fav-only { background: linear-gradient(135deg, #FFE9C2 0%, #FFD580 100%); color: #8B5A00; font-weight: 600; font-size: 14px; padding: 4px 12px; }

.tag-pill { display: inline-flex; align-items: center; padding: 1px 6px; border-radius: 6px; font-size: 10px; font-weight: 500; line-height: 1.6; }
.tag-blue { background: #E6F1FB; color: #185FA5; }
.tag-green { background: #EAF3DE; color: #27500A; }
.tag-pink { background: #FBEAF0; color: #993556; }
.tag-amber { background: #FAEEDA; color: #633806; }
.tag-coral { background: #FAECE7; color: #712B13; }

.load-more {
  text-align: center;
  padding: 12px;
  font-size: 12px;
  color: #1D9E75;
  cursor: pointer;
  border-radius: 8px;
  background: #E1F5EE;
  margin-top: 8px;
}
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #b4b2a9;
  font-size: 14px;
}

/* Trending Card (右侧) */
.trending-card {
  background: #fff;
  border: 0.5px solid #d3d1c7;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.trending-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #ebeef5;
}
.trending-icon { font-size: 16px; }
.trending-title { font-size: 14px; font-weight: 600; color: #1a1a1a; flex: 1; }
.trending-tabs { display: flex; gap: 4px; background: #F1EFE8; padding: 2px; border-radius: 6px; }
.trending-tabs span {
  font-size: 10px; padding: 2px 8px; border-radius: 4px; color: #888780; cursor: pointer;
}
.trending-tab-active { background: #1D9E75 !important; color: #fff !important; }

.trending-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 14px;
  padding: 10px 8px;
  background: linear-gradient(135deg, #E1F5EE 0%, #F1EFE8 100%);
  border-radius: 8px;
}
.summary-item { text-align: center; }
.summary-num { font-size: 18px; font-weight: 700; color: #0F6E56; line-height: 1.2; }
.summary-label { font-size: 10px; color: #888780; margin-top: 2px; }

.trending-empty, .rank-empty {
  text-align: center;
  padding: 20px 0;
  color: #b4b2a9;
  font-size: 12px;
}

.trending-board-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}
.trending-board-item:hover { background: #F8FAFC; }
.trending-board-item:last-child { margin-bottom: 0; }

.trending-board-rank {
  width: 18px; height: 18px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; color: #fff;
  flex-shrink: 0;
}
.trending-rank-1 { background: linear-gradient(135deg, #FF8E53, #FE6B8B); }
.trending-rank-2 { background: linear-gradient(135deg, #A8B7FF, #8E9EFF); }
.trending-rank-3 { background: linear-gradient(135deg, #F5C27B, #E89E58); }
.trending-rank-4, .trending-rank-5, .trending-rank-6 { background: #d3d1c7; }

.trending-board-icon { font-size: 16px; flex-shrink: 0; }
.trending-board-info { flex: 1; min-width: 0; }
.trending-board-name { font-size: 12px; font-weight: 500; color: #1a1a1a; margin-bottom: 3px; }
.trending-board-bar-wrap {
  height: 4px; background: #F1EFE8; border-radius: 2px; overflow: hidden;
}
.trending-board-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s ease;
  background: linear-gradient(90deg, #1D9E75, #85E5BC);
}
.bar-color-1 { background: linear-gradient(90deg, #378ADD, #6FBCFF); }
.bar-color-2 { background: linear-gradient(90deg, #D4537E, #FF8DA8); }
.bar-color-3 { background: linear-gradient(90deg, #BA7517, #F5C27B); }
.bar-color-4 { background: linear-gradient(90deg, #7F77DD, #B5B0F5); }
.bar-color-5 { background: linear-gradient(90deg, #D85A30, #FF9776); }
.bar-color-0 { background: linear-gradient(90deg, #1D9E75, #85E5BC); }

.trending-board-stat { text-align: right; flex-shrink: 0; }
.trending-board-num { font-size: 13px; font-weight: 700; color: #1D9E75; line-height: 1.2; }
.trending-board-label { font-size: 9px; color: #888780; }

/* Rank Card */
.rank-card {
  background: #fff;
  border: 0.5px solid #d3d1c7;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.rank-header { display: flex; align-items: center; gap: 6px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px dashed #ebeef5; }
.rank-icon { font-size: 14px; }
.rank-title { font-size: 13px; font-weight: 600; color: #1a1a1a; }

.rank-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
  margin-bottom: 2px;
}
.rank-item:hover { background: #F8FAFC; }
.rank-num {
  width: 20px; height: 20px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #fff;
  flex-shrink: 0;
  background: #b4b2a9;
}
.rank-num-1 { background: linear-gradient(135deg, #FF8E53, #FE6B8B); }
.rank-num-2 { background: linear-gradient(135deg, #A8B7FF, #8E9EFF); }
.rank-num-3 { background: linear-gradient(135deg, #F5C27B, #E89E58); }

.rank-content { flex: 1; min-width: 0; }
.rank-title-text {
  font-size: 12px; font-weight: 500; color: #1a1a1a;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.rank-meta { font-size: 10px; color: #b4b2a9; margin-top: 1px; }
.rank-stat { font-size: 10px; color: #888780; font-weight: 600; flex-shrink: 0; }

@media (max-width: 1024px) {
  .home-main { grid-template-columns: 1fr; }
  .home-right { order: -1; flex-direction: row; overflow-x: auto; }
  .trending-card, .rank-card { min-width: 280px; }
  .board-grid { grid-template-columns: repeat(4, 1fr); }
}
@media (max-width: 768px) {
  .board-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
