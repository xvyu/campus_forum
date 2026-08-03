<template>
  <div class="profile-page">
    <!-- 未登录 -->
    <div v-if="!userStore.isLoggedIn" class="not-logged-in">
      请先 <router-link to="/login">登录</router-link>
    </div>

    <template v-if="userStore.isLoggedIn">
      <!-- 用户信息卡 -->
      <div class="profile-card">
        <div class="profile-banner">
          <span class="banner-text">Campus Forum · 个人主页</span>
        </div>
        <div class="profile-body">
          <div class="avatar-circle">{{ profile?.nickname?.charAt(0) || '匿' }}</div>
          <div class="profile-info">
            <div class="profile-name-row">
              <span class="profile-name">{{ profile?.nickname || '匿名用户' }}</span>
            </div>
            <div class="profile-dept">
              {{ profile?.department || '人工智能学院' }} · {{ profile?.class_name || '软件工程 2023-2 班' }}
            </div>
            <div class="profile-meta">
              学号: {{ profile?.student_id || '未填写' }} · 已加入 {{ profile?.days_joined || 0 }} 天
            </div>
          </div>
        </div>
      </div>

      <!-- 4 个统计卡片 -->
      <div class="stat-grid">
        <div class="stat-card" @click="openMyPosts">
          <div class="stat-bar bar-blue"></div>
          <div class="stat-count blue">{{ profile?.post_count ?? 0 }}</div>
          <div class="stat-label">发布帖子</div>
        </div>
        <div class="stat-card" @click="openMyComments">
          <div class="stat-bar bar-green"></div>
          <div class="stat-count green">{{ profile?.comment_count ?? 0 }}</div>
          <div class="stat-label">发布评论</div>
        </div>
        <div class="stat-card" @click="openLikedDialog">
          <div class="stat-bar bar-pink"></div>
          <div class="stat-count pink">{{ (profile?.liked_post_count || 0) + (profile?.liked_comment_count || 0) }}</div>
          <div class="stat-label">点赞互动</div>
        </div>
        <div class="stat-card" @click="openFavorites">
          <div class="stat-bar bar-amber"></div>
          <div class="stat-count amber">{{ profile?.favorite_count ?? 0 }}</div>
          <div class="stat-label">收藏互动</div>
        </div>
      </div>

      <!-- Tab 栏 -->
      <div class="tab-bar">
        <button :class="['tab-btn', activeTab === 'posts' ? 'active' : '']" @click="activeTab = 'posts'">📝 我的帖子 {{ myNormalPostsCount || '' }}</button>
        <button :class="['tab-btn', activeTab === 'comments' ? 'active' : '']" @click="activeTab = 'comments'">💬 我的评论 {{ myNormalCommentsCount || '' }}</button>
        <button :class="['tab-btn', activeTab === 'favorites' ? 'active' : '']" @click="activeTab = 'favorites'">⭐ 我的收藏 {{ favoritesList.length || '' }}</button>
        <button :class="['tab-btn', activeTab === 'masquerade' ? 'active' : '']" @click="activeTab = 'masquerade'">🎭 匿名马甲 {{ profile?.anonymous_count || '' }}</button>
        <button :class="['tab-btn', activeTab === 'activity' ? 'active' : '']" @click="activeTab = 'activity'">📊 数据</button>
      </div>

      <!-- ===== 我的帖子 Tab ===== -->
      <template v-if="activeTab === 'posts'">
        <!-- 本周活跃度 -->
        <div class="activity-card">
          <div class="activity-header">
            <span class="activity-title">📊 本周活跃度</span>
            <span class="activity-sub">· 7 天内发帖 + 评论</span>
          </div>
          <div class="activity-body">
            <div class="activity-chart">
              <div v-for="(d, i) in activity.days" :key="i" class="chart-bar-col">
                <div :class="['chart-bar', { 'bar-peak': d.total === maxWeek }]" :style="{ height: maxWeek ? (d.total / maxWeek) * 32 + 4 + 'px' : '4px' }"></div>
                <span :class="['chart-label', { 'label-peak': d.total === maxWeek }]">{{ d.day }}</span>
              </div>
            </div>
            <div class="activity-stats">
              <div class="a-stat">
                <span class="a-stat-label">本周活跃</span>
                <span class="a-stat-num">{{ activity.week_total }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 我的帖子列表 -->
        <div class="post-list" v-loading="loadingMyPosts">
          <div v-if="!displayPosts.length" class="empty-state">暂无帖子</div>
          <div v-for="p in displayPosts" :key="p.id" class="post-card">
            <div :class="['post-bar', boardColor(p.board_name)]"></div>
            <div :class="['post-avatar', boardColor(p.board_name)]">{{ (p.anonymous_name || '匿').charAt(0) }}</div>
            <div class="post-body">
              <div class="post-title">{{ p.title }}</div>
              <div class="post-tags">
                <span :class="['pill', boardColor(p.board_name)]">📚 {{ p.board_name || '默认' }}</span>
                <span v-if="p.is_top" class="pill-meta">置顶</span>
                <span v-if="p.like_count + p.comment_count + p.view_count > 50" class="pill-hot">🔥 热门</span>
              </div>
              <div class="post-meta">
                {{ p.created_at }} · ❤ {{ p.like_count }} · 💬 {{ p.comment_count }} · 👁 {{ p.view_count }} · ⭐ {{ p.favorite_count }}
              </div>
            </div>
            <div class="post-right">
              <span class="status-tag">正常</span>
              <button class="post-edit-btn" @click="goToPost(p.id)">查看</button>
            </div>
          </div>
        </div>
      </template>

      <!-- ===== 我的评论 Tab ===== -->
      <template v-if="activeTab === 'comments'">
        <div class="post-list" v-loading="loadingMyComments">
          <div v-if="!displayComments.length" class="empty-state">暂无评论</div>
          <div v-for="c in displayComments" :key="'c' + c.id" class="post-card">
            <div class="post-bar bar-green"></div>
            <div class="post-avatar bar-green">💬</div>
            <div class="post-body">
              <div class="post-title">来自：{{ c.post_title }}</div>
              <div class="post-content">"{{ c.content_preview }}"</div>
              <div class="post-meta">{{ c.created_at }} · ❤ {{ c.like_count }} 条点赞</div>
            </div>
            <div class="post-right">
              <span class="status-tag">正常</span>
              <button v-if="!c.is_deleted_post" class="post-edit-btn" @click="goToMyComment(c)">查看</button>
            </div>
          </div>
        </div>
      </template>

      <!-- ===== 我的收藏 Tab ===== -->
      <template v-if="activeTab === 'favorites'">
        <div class="post-list" v-loading="loadingFavorites">
          <div v-if="!displayFavorites.length" class="empty-state">暂无收藏</div>
          <div v-for="p in displayFavorites" :key="'fav' + p.favorite_id" class="post-card">
            <div class="post-bar bar-amber"></div>
            <div class="post-avatar bar-amber">⭐</div>
            <div class="post-body">
              <div class="post-title">{{ p.title }}</div>
              <div class="post-meta">{{ p.favorited_at }} · 👁 {{ p.view_count }} · 💬 {{ p.comment_count }} · ❤ {{ p.like_count }}</div>
            </div>
            <div class="post-right">
              <button class="post-edit-btn danger" @click="removeFavorite(p)">取消收藏</button>
            </div>
          </div>
        </div>
      </template>

      <!-- ===== 匿名马甲 Tab ===== -->
      <template v-if="activeTab === 'masquerade'">
        <div class="masquerade-card">
          <h3 class="section-title">🎭 当前马甲</h3>
          <div class="masquerade-row">
            <span class="masquerade-tag">{{ profile?.anonymous_name || '加载中...' }}</span>
            <button class="btn-refresh" @click="refreshMasquerade" :disabled="refreshingMasquerade">🔄 换一个马甲</button>
          </div>
        </div>

        <div class="masquerade-card">
          <h3 class="section-title">✏️ 修改昵称</h3>
          <div class="action-row">
            <el-input v-model="newNickname" placeholder="输入新昵称" maxlength="20" show-word-limit clearable style="max-width: 360px;" />
            <button class="btn-save" @click="updateNickname" :disabled="updatingNickname">保存</button>
          </div>
        </div>
      </template>

      <!-- ===== 数据 Tab ===== -->
      <template v-if="activeTab === 'activity'">
        <div class="data-card">
          <h3 class="section-title">📊 我的数据</h3>
          <el-row :gutter="12">
            <el-col :span="8"><div class="data-item"><div class="data-num blue">{{ profile?.post_count ?? 0 }}</div><div class="data-label">发布帖子</div></div></el-col>
            <el-col :span="8"><div class="data-item"><div class="data-num green">{{ profile?.comment_count ?? 0 }}</div><div class="data-label">发布评论</div></div></el-col>
            <el-col :span="8"><div class="data-item"><div class="data-num pink">{{ (profile?.liked_post_count || 0) + (profile?.liked_comment_count || 0) }}</div><div class="data-label">点赞互动</div></div></el-col>
            <el-col :span="8"><div class="data-item"><div class="data-num purple">{{ profile?.total_likes_received ?? 0 }}</div><div class="data-label">被点赞数</div></div></el-col>
            <el-col :span="8"><div class="data-item"><div class="data-num coral">{{ profile?.favorite_count ?? 0 }}</div><div class="data-label">收藏互动</div></div></el-col>
            <el-col :span="8"><div class="data-item"><div class="data-num amber">{{ profile?.view_count ?? 0 }}</div><div class="data-label">浏览总量</div></div></el-col>
          </el-row>
        </div>
      </template>

      <!-- ===== 弹窗：我发布的帖子 ===== -->
      <el-dialog v-model="showMyPostsDialog" width="660px" :show-close="false" class="profile-dialog dialog-green">
        <div class="dialog-shell">
          <div class="dialog-topbar"></div>
          <div class="dialog-header">
            <span class="dialog-title">📝 我发布的帖子</span>
            <span class="dialog-underline"></span>
            <button class="dialog-close" @click="showMyPostsDialog = false">✕</button>
          </div>
          <div class="dialog-body" v-loading="loadingMyPosts">
            <!-- 工具栏 -->
            <div v-if="myItems.posts?.length" class="dialog-toolbar">
              <div class="filter-tabs">
                <button class="filter-tab" :class="{ active: myPostsFilter === 'all' }" @click="myPostsFilter = 'all'; onMyPostsFilterChange()">全部 ({{ myItems.posts.length }})</button>
                <button class="filter-tab" :class="{ active: myPostsFilter === 'active' }" @click="myPostsFilter = 'active'; onMyPostsFilterChange()">正常 ({{ filterCountMyPosts('active') }})</button>
                <button class="filter-tab" :class="{ active: myPostsFilter === 'deleted' }" @click="myPostsFilter = 'deleted'; onMyPostsFilterChange()">已删除 ({{ filterCountMyPosts('deleted') }})</button>
              </div>
              <div class="toolbar-right">
                <label class="cb-label">
                  <input type="checkbox" :checked="isAllSelectedMyPosts" @change="(e) => toggleSelectAllMyPosts(!!(e.target as HTMLInputElement).checked)" />
                  <span>全选 ({{ selectedMyPostIds.length }}/{{ filteredMyPosts.length }})</span>
                </label>
                <button class="batch-del-btn" :disabled="!selectedMyPostIds.length" @click="batchDeleteMyPosts">
                  <svg viewBox="0 0 24 24" class="batch-del-icon"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                  批量删除 ({{ selectedMyPostIds.length }})
                </button>
              </div>
            </div>

            <!-- 列表 -->
            <div v-if="!myItems.posts?.length" class="dialog-empty">暂无帖子</div>
            <div v-else-if="!filteredMyPosts.length" class="dialog-empty">没有{{ myPostsFilter === 'deleted' ? '已删除' : '正常' }}的帖子</div>
            <div v-for="p in filteredMyPosts" :key="'mp'+p.id" :class="['dialog-item', p.is_deleted ? 'dialog-item-deleted' : '']">
              <div :class="['item-bar', boardColor(p.board_name)]"></div>
              <label class="item-cb" @click.stop>
                <input type="checkbox" :checked="selectedMyPostIds.includes(p.id)" @change="(e) => toggleSelectMyPost(p.id, !!(e.target as HTMLInputElement).checked)" />
              </label>
              <div :class="['item-avatar', boardColor(p.board_name)]">{{ (p.board_name || '匿').charAt(0) }}</div>
              <div class="item-content" @click="goToPost(p.id)">
                <div class="item-title">
                  {{ p.title }}
                  <span :class="['item-status', p.is_deleted ? 'status-deleted' : 'status-ok']">{{ p.is_deleted ? '已删除' : '正常' }}</span>
                </div>
                <div class="item-actions"><PostActions :like_count="p.like_count" :comment_count="p.comment_count" :view_count="p.view_count" /></div>
              </div>
              <button v-if="!p.is_deleted" class="item-del-btn" @click.stop="deleteMyPost(p)">删除</button>
              <button v-else class="item-del-btn item-del-hard" @click.stop="hardDeleteMyPost(p)">彻底删除</button>
            </div>
          </div>
        </div>
      </el-dialog>

      <!-- ===== 弹窗：我发表的评论 ===== -->
      <el-dialog v-model="showMyCommentsDialog" width="660px" :show-close="false" class="profile-dialog dialog-blue">
        <div class="dialog-shell">
          <div class="dialog-topbar"></div>
          <div class="dialog-header">
            <span class="dialog-title">💬 我发表的评论</span>
            <span class="dialog-underline"></span>
            <button class="dialog-close" @click="showMyCommentsDialog = false">✕</button>
          </div>
          <div class="dialog-body" v-loading="loadingMyComments">
            <!-- 工具栏 -->
            <div v-if="myItems.comments?.length" class="dialog-toolbar">
              <div class="filter-tabs">
                <button class="filter-tab" :class="{ active: myCommentsFilter === 'all' }" @click="myCommentsFilter = 'all'; onMyCommentsFilterChange()">全部 ({{ myItems.comments.length }})</button>
                <button class="filter-tab" :class="{ active: myCommentsFilter === 'active' }" @click="myCommentsFilter = 'active'; onMyCommentsFilterChange()">正常 ({{ filterCountMyComments('active') }})</button>
                <button class="filter-tab" :class="{ active: myCommentsFilter === 'deleted' }" @click="myCommentsFilter = 'deleted'; onMyCommentsFilterChange()">已删除 ({{ filterCountMyComments('deleted') }})</button>
              </div>
              <div class="toolbar-right">
                <label class="cb-label">
                  <input type="checkbox" :checked="isAllSelectedMyComments" @change="(e) => toggleSelectAllMyComments(!!(e.target as HTMLInputElement).checked)" />
                  <span>全选 ({{ selectedMyCommentIds.length }}/{{ filteredMyComments.length }})</span>
                </label>
                <button class="batch-del-btn" :disabled="!selectedMyCommentIds.length" @click="batchDeleteMyComments">
                  <svg viewBox="0 0 24 24" class="batch-del-icon"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                  批量删除 ({{ selectedMyCommentIds.length }})
                </button>
              </div>
            </div>

            <!-- 列表 -->
            <div v-if="!myItems.comments?.length" class="dialog-empty">暂无评论</div>
            <div v-else-if="!filteredMyComments.length" class="dialog-empty">没有{{ myCommentsFilter === 'deleted' ? '已删除' : '正常' }}的评论</div>
            <div v-for="c in filteredMyComments" :key="'mc'+c.id" :class="['dialog-item', (c.is_deleted || c.is_deleted_post) ? 'dialog-item-deleted' : '']">
              <div class="item-bar bar-blue"></div>
              <label class="item-cb" @click.stop>
                <input type="checkbox" :checked="selectedMyCommentIds.includes(c.id)" @change="(e) => toggleSelectMyComment(c.id, !!(e.target as HTMLInputElement).checked)" />
              </label>
              <div class="item-avatar bar-blue">💬</div>
              <div class="item-content" @click="goToMyComment(c)">
                <div class="item-title">
                  来自：{{ c.post_title }}
                  <span v-if="c.is_deleted" class="item-status status-deleted">评论已删</span>
                  <span v-else-if="c.is_deleted_post" class="item-status status-pending">原帖已删</span>
                  <span v-else class="item-status status-ok">正常</span>
                </div>
                <div class="item-preview">"{{ c.content_preview }}"</div>
                <div class="item-actions"><PostActions :like_count="c.like_count" :show_favorite="false" /></div>
              </div>
              <button v-if="!c.is_deleted && !c.is_deleted_post" class="item-del-btn" @click.stop="deleteMyComment(c)">删除</button>
              <button v-else class="item-del-btn item-del-hard" @click.stop="hardDeleteMyComment(c)">彻底删除</button>
            </div>
          </div>
        </div>
      </el-dialog>

      <!-- ===== 弹窗：收到点赞 ===== -->
      <el-dialog v-model="showLikedDialog" width="600px" :show-close="false" class="profile-dialog dialog-amber">
        <div class="dialog-shell">
          <div class="dialog-topbar"></div>
          <div class="dialog-header">
            <span class="dialog-title">⭐ 被点赞的记录</span>
            <span class="dialog-underline"></span>
            <button class="dialog-close" @click="showLikedDialog = false">✕</button>
          </div>
          <div class="dialog-body" v-loading="loadingLikes">
            <div class="filter-tabs">
              <button class="filter-tab" :class="{ active: likedTab === 'posts' }" @click="likedTab = 'posts'">帖子</button>
              <button class="filter-tab" :class="{ active: likedTab === 'comments' }" @click="likedTab = 'comments'">评论</button>
            </div>
            <template v-if="likedTab === 'posts'">
              <div v-if="!likedItems.posts?.length" class="dialog-empty">暂无帖子被点赞</div>
              <div v-for="p in likedItems.posts" :key="'lp'+p.id" class="dialog-item" @click="goToPost(p.id)">
                <div :class="['item-bar', boardColor(p.board_name)]"></div>
                <div :class="['item-avatar', boardColor(p.board_name)]">{{ (p.board_name || '帖').charAt(0) }}</div>
                <div class="item-content">
                  <div class="item-title">{{ p.title }}</div>
                  <div class="item-actions"><PostActions :like_count="p.like_count" :comment_count="p.comment_count" :view_count="p.view_count" /></div>
                </div>
                <span class="like-badge">★ {{ p.like_count }}</span>
              </div>
            </template>
            <template v-else>
              <div v-if="!likedItems.comments?.length" class="dialog-empty">暂无评论被点赞</div>
              <div v-for="c in likedItems.comments" :key="'lc'+c.id" class="dialog-item" @click="goToComment(c)">
                <div class="item-bar bar-blue"></div>
                <div class="item-avatar bar-blue">💬</div>
                <div class="item-content">
                  <div class="item-title">来自：{{ c.post_title }}</div>
                  <div class="item-preview">"{{ c.content_preview }}"</div>
                  <div class="item-actions"><PostActions :like_count="c.like_count" :show_favorite="false" /></div>
                </div>
                <span class="like-badge">★ {{ c.like_count }}</span>
              </div>
            </template>
          </div>
        </div>
      </el-dialog>

      <!-- ===== 弹窗：我收藏的 ===== -->
      <el-dialog v-model="showFavoritesDialog" width="650px" :show-close="false" class="profile-dialog dialog-amber">
        <div class="dialog-shell">
          <div class="dialog-topbar"></div>
          <div class="dialog-header">
            <span class="dialog-title">⭐ 我收藏的帖子</span>
            <span class="dialog-underline"></span>
            <button class="dialog-close" @click="showFavoritesDialog = false">✕</button>
          </div>
          <div class="dialog-body" v-loading="loadingFavorites">
            <div v-if="!favoritesList?.length" class="dialog-empty">暂无收藏</div>
            <div v-for="p in favoritesList" :key="'fv'+p.id" class="dialog-item" @click="goToPost(p.id)">
              <div class="item-bar bar-amber"></div>
              <div class="item-avatar bar-amber">⭐</div>
              <div class="item-content">
                <div class="item-title">{{ p.title }}</div>
                <div class="item-actions"><PostActions :like_count="p.like_count" :comment_count="p.comment_count" :view_count="p.view_count" :favorite_count="p.favorite_count" /></div>
              </div>
              <span class="fav-badge">⭐ 已收藏</span>
            </div>
          </div>
        </div>
      </el-dialog>

      <!-- 退出登录 -->
      <div class="footer-actions">
        <button class="btn-logout" @click="handleLogout">退出登录</button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showConfirm } from '@/utils/confirm'
import PostActions from '@/components/PostActions.vue'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()
const profile = ref<any>(null)
const newNickname = ref('')
const updatingNickname = ref(false)
const refreshingMasquerade = ref(false)
const activeTab = ref('posts')
const activity = ref<any>({ days: [], week_total: 0 })

// 弹窗状态
const showMyPostsDialog = ref(false)
const showMyCommentsDialog = ref(false)
const showLikedDialog = ref(false)
const showFavoritesDialog = ref(false)
const likedTab = ref<'posts' | 'comments'>('posts')
const loadingMyPosts = ref(false)
const loadingMyComments = ref(false)
const loadingFavorites = ref(false)
const loadingLikes = ref(false)
const selectedMyPostIds = ref<number[]>([])
const selectedMyCommentIds = ref<number[]>([])
const myPostsFilter = ref<'all' | 'active' | 'deleted'>('all')
const myCommentsFilter = ref<'all' | 'active' | 'deleted'>('all')

// 筛选后的列表
const filteredMyPosts = computed(() => {
  const list = myItems.value.posts || []
  if (myPostsFilter.value === 'active') return list.filter((p: any) => !p.is_deleted)
  if (myPostsFilter.value === 'deleted') return list.filter((p: any) => p.is_deleted)
  return list
})
const filteredMyComments = computed(() => {
  const list = myItems.value.comments || []
  if (myCommentsFilter.value === 'active') return list.filter((c: any) => !c.is_deleted && !c.is_deleted_post)
  if (myCommentsFilter.value === 'deleted') return list.filter((c: any) => c.is_deleted || c.is_deleted_post)
  return list
})

function filterCountMyPosts(type: 'active' | 'deleted') {
  const list = myItems.value.posts || []
  if (type === 'active') return list.filter((p: any) => !p.is_deleted).length
  return list.filter((p: any) => p.is_deleted).length
}
function filterCountMyComments(type: 'active' | 'deleted') {
  const list = myItems.value.comments || []
  if (type === 'active') return list.filter((c: any) => !c.is_deleted && !c.is_deleted_post).length
  return list.filter((c: any) => c.is_deleted || c.is_deleted_post).length
}
function onMyPostsFilterChange() { selectedMyPostIds.value = [] }
function onMyCommentsFilterChange() { selectedMyCommentIds.value = [] }

// 只统计"正常"的帖子/评论（用于 Tab 右侧数量）
const myNormalPostsCount = computed(() => {
  const list = myItems.value.posts || []
  return list.filter((p: any) => !p.is_deleted).length
})
const myNormalCommentsCount = computed(() => {
  const list = myItems.value.comments || []
  return list.filter((c: any) => !c.is_deleted && !c.is_deleted_post).length
})
const myItems = ref<any>({ posts: [], comments: [] })
const likedItems = ref<any>({ posts: [], comments: [] })
const favoritesList = ref<any[]>([])

// 活跃度图表
const maxWeek = computed(() => {
  const days = activity.value?.days || []
  return Math.max(1, ...days.map((d: any) => d.total || 0))
})

// 过滤掉已彻底删除（hard-deleted）的帖子与评论
// 后端可能仍然返回带 is_deleted=true 的记录，这里在前端兜底过滤
const displayPosts = computed(() =>
  (myItems.value.posts || []).filter((p: any) => !p.is_deleted)
)
const displayComments = computed(() =>
  (myItems.value.comments || []).filter((c: any) => !c.is_deleted && !c.is_deleted_post)
)
const displayFavorites = computed(() =>
  (favoritesList.value || []).filter((p: any) => !p.is_deleted)
)

// 板块配色
const boardColors = ['blue', 'pink', 'green', 'amber', 'purple', 'coral']
function boardColor(name: string | undefined) {
  if (!name) return 'blue'
  const idx = (name.charCodeAt(0) || 0) % boardColors.length
  return boardColors[idx]
}

async function loadProfile() {
  if (!userStore.user) { try { await userStore.fetchMe() } catch {} }
  if (!userStore.isLoggedIn) return
  try {
    const res = await api.get('/users/me')
    profile.value = res.data
    newNickname.value = res.data.nickname || ''
  } catch (e: any) {
    ElMessage.warning('部分信息加载失败')
  }
}

async function loadActivity() {
  try {
    const res = await api.get('/users/me/activity')
    activity.value = res.data
  } catch {}
}

async function loadMyItems() {
  loadingMyPosts.value = true; loadingMyComments.value = true
  try {
    const [postsRes, commentsRes] = await Promise.all([
      api.get('/users/my-posts'),
      api.get('/users/my-comments'),
    ])
    myItems.value = { posts: postsRes.data || [], comments: commentsRes.data || [] }
  } catch {} finally {
    loadingMyPosts.value = false
    loadingMyComments.value = false
  }
}

async function loadFavorites() {
  loadingFavorites.value = true
  try {
    const res = await api.get('/favorites/my', { params: { page: 1, limit: 50 } })
    favoritesList.value = res.data?.list || []
  } catch {} finally { loadingFavorites.value = false }
}

async function loadLikes() {
  loadingLikes.value = true
  try {
    const res = await api.get('/users/me/likes')
    likedItems.value = res.data
  } catch {} finally { loadingLikes.value = false }
}

onMounted(async () => {
  await Promise.all([loadProfile(), loadActivity(), loadMyItems(), loadFavorites()])
})

async function updateNickname() {
  const name = newNickname.value.trim()
  if (!name) { ElMessage.warning('请输入新昵称'); return }
  if (name.length > 20) { ElMessage.warning('昵称不超过 20 字'); return }
  updatingNickname.value = true
  try {
    const res = await api.put('/users/me/nickname', { nickname: name })
    ElMessage.success('昵称已更新')
    if (res.data?.nickname) {
      userStore.user.nickname = res.data.nickname
      userStore.user.anonymous_name = res.data.anonymous_name || userStore.user.anonymous_name
    }
    await loadProfile()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '更新失败')
  } finally { updatingNickname.value = false }
}

async function refreshMasquerade() {
  refreshingMasquerade.value = true
  try {
    const res = await api.post('/users/me/refresh-masquerade')
    ElMessage.success('新马甲：' + res.data.anonymous_name)
    if (profile.value) profile.value.anonymous_name = res.data.anonymous_name
    if (userStore.user) userStore.user.anonymous_name = res.data.anonymous_name
    await loadProfile()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '刷新失败')
  } finally { refreshingMasquerade.value = false }
}

async function handleLogout() {
  await userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}

function openMyPosts() { showMyPostsDialog.value = true; selectedMyPostIds.value = []; loadMyItems() }
function openMyComments() { showMyCommentsDialog.value = true; selectedMyCommentIds.value = []; loadMyItems() }
function openFavorites() { showFavoritesDialog.value = true; loadFavorites() }
function openLikedDialog() { showLikedDialog.value = true; loadLikes() }

// ============ 我的帖子弹窗：批量选择 + 删除 ============
const isAllSelectedMyPosts = computed(() => {
  const list = myItems.value.posts || []
  return list.length > 0 && selectedMyPostIds.value.length === list.length
})
function toggleSelectMyPost(id: number, checked: boolean) {
  if (checked) {
    if (!selectedMyPostIds.value.includes(id)) selectedMyPostIds.value.push(id)
  } else {
    selectedMyPostIds.value = selectedMyPostIds.value.filter(x => x !== id)
  }
}
function toggleSelectAllMyPosts(checked: boolean) {
  const list = myItems.value.posts || []
  selectedMyPostIds.value = checked ? list.map((p: any) => p.id) : []
}

async function deleteMyPost(p: any) {
  try { await showConfirm('确定要删除这条帖子吗？删除后将进入"已删除"列表，可彻底删除。', '删除帖子'); } catch { return }
  try {
    await api.delete(`/posts/${p.id}`)
    ElMessage.success('帖子已删除')
    await loadMyItems()
    await loadProfile()
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '删除失败') }
}

async function hardDeleteMyPost(p: any) {
  try { await showConfirm('确定要彻底删除这条帖子吗？此操作不可恢复！', '彻底删除帖子'); } catch { return }
  try {
    await api.post(`/users/my-posts/${p.id}/hide`)
    ElMessage.success('已从记录中彻底移除')
    selectedMyPostIds.value = selectedMyPostIds.value.filter(x => x !== p.id)
    await loadMyItems()
    await loadProfile()
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '操作失败') }
}

async function batchDeleteMyPosts() {
  if (!selectedMyPostIds.value.length) return
  const list = filteredMyPosts.value.filter((p: any) => selectedMyPostIds.value.includes(p.id))
  const normalCount = list.filter((p: any) => !p.is_deleted).length
  const deletedCount = list.length - normalCount
  const msg = `确定要批量删除选中的 ${list.length} 条帖子吗？`
    + (normalCount ? `\n· ${normalCount} 条正常帖子 → 软删（可彻底删除）` : '')
    + (deletedCount ? `\n· ${deletedCount} 条已删除帖子 → 彻底从记录移除` : '')
  try { await showConfirm(msg, '批量删除'); } catch { return }
  loadingMyPosts.value = true
  try {
    // 1) 正常帖子：调用 DELETE /posts/{id}
    const normalIds = list.filter((p: any) => !p.is_deleted).map((p: any) => p.id)
    for (const id of normalIds) {
      await api.delete(`/posts/${id}`)
    }
    // 2) 已删除帖子：批量 hide
    const deletedIds = list.filter((p: any) => p.is_deleted).map((p: any) => p.id)
    if (deletedIds.length) {
      await api.post('/users/my-posts/batch-hide', { ids: deletedIds })
    }
    ElMessage.success(`已批量删除 ${list.length} 条`)
    selectedMyPostIds.value = []
    await loadMyItems()
    await loadProfile()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '批量删除失败')
  } finally { loadingMyPosts.value = false }
}

// ============ 我的评论弹窗：批量选择 + 删除 ============
const isAllSelectedMyComments = computed(() => {
  const list = myItems.value.comments || []
  return list.length > 0 && selectedMyCommentIds.value.length === list.length
})
function toggleSelectMyComment(id: number, checked: boolean) {
  if (checked) {
    if (!selectedMyCommentIds.value.includes(id)) selectedMyCommentIds.value.push(id)
  } else {
    selectedMyCommentIds.value = selectedMyCommentIds.value.filter(x => x !== id)
  }
}
function toggleSelectAllMyComments(checked: boolean) {
  const list = myItems.value.comments || []
  selectedMyCommentIds.value = checked ? list.map((c: any) => c.id) : []
}

async function deleteMyComment(c: any) {
  try { await showConfirm('确定要删除这条评论吗？删除后可彻底清除记录。', '删除评论'); } catch { return }
  try {
    await api.delete(`/comments/${c.id}`)
    ElMessage.success('评论已删除')
    await loadMyItems()
    await loadProfile()
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '删除失败') }
}

async function hardDeleteMyComment(c: any) {
  try { await showConfirm('确定要从记录中彻底移除这条评论吗？', '彻底移除'); } catch { return }
  try {
    await api.post(`/users/my-comments/${c.id}/hide`)
    ElMessage.success('已从记录中彻底移除')
    selectedMyCommentIds.value = selectedMyCommentIds.value.filter(x => x !== c.id)
    await loadMyItems()
    await loadProfile()
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '操作失败') }
}

async function batchDeleteMyComments() {
  if (!selectedMyCommentIds.value.length) return
  const list = filteredMyComments.value.filter((c: any) => selectedMyCommentIds.value.includes(c.id))
  const normalCount = list.filter((c: any) => !c.is_deleted && !c.is_deleted_post).length
  const deletedCount = list.length - normalCount
  const msg = `确定要批量删除选中的 ${list.length} 条评论吗？`
    + (normalCount ? `\n· ${normalCount} 条正常评论 → 软删（可彻底删除）` : '')
    + (deletedCount ? `\n· ${deletedCount} 条已删除评论 → 彻底从记录移除` : '')
  try { await showConfirm(msg, '批量删除'); } catch { return }
  loadingMyComments.value = true
  try {
    const normalIds = list.filter((c: any) => !c.is_deleted && !c.is_deleted_post).map((c: any) => c.id)
    for (const id of normalIds) {
      await api.delete(`/comments/${id}`)
    }
    const deletedIds = list.filter((c: any) => c.is_deleted || c.is_deleted_post).map((c: any) => c.id)
    if (deletedIds.length) {
      await api.post('/users/my-comments/batch-hide', { ids: deletedIds })
    }
    ElMessage.success(`已批量删除 ${list.length} 条`)
    selectedMyCommentIds.value = []
    await loadMyItems()
    await loadProfile()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '批量删除失败')
  } finally { loadingMyComments.value = false }
}

function goToPost(id: number) {
  showMyPostsDialog.value = false
  showMyCommentsDialog.value = false
  showFavoritesDialog.value = false
  showLikedDialog.value = false
  router.push(`/posts/${id}`)
}

function goToComment(c: any) {
  if (c.is_deleted_post) { ElMessage.warning('原帖已删除'); return }
  showLikedDialog.value = false
  router.push(`/posts/${c.post_id}#comment-${c.id}`)
}

function goToMyComment(c: any) {
  if (c.is_deleted_post) { ElMessage.warning('原帖已删除'); return }
  showMyCommentsDialog.value = false
  router.push(`/posts/${c.post_id}#comment-${c.id}`)
}

async function removeFavorite(p: any) {
  try {
    await showConfirm('确定要取消收藏这篇帖子吗？', '取消收藏')
  } catch { return }
  try {
    await api.post(`/favorites/posts/${p.id}`)
    ElMessage.success('已取消收藏')
    await loadFavorites()
    await loadProfile()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  }
}
</script>

<style scoped>
.profile-page { max-width: 720px; margin: 20px auto; padding: 0 16px; }
.not-logged-in { text-align: center; padding: 60px 0; font-size: 14px; color: #888780; }
.not-logged-in a { color: #1D9E75; text-decoration: none; font-weight: 500; }

/* ===== 用户信息卡 ===== */
.profile-card { background: #fff; border: 0.5px solid #D3D1C7; border-radius: 14px; overflow: hidden; margin-bottom: 16px; }
.profile-banner { background: linear-gradient(90deg, #0C447C 0%, #1D9E75 100%); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; height: 48px; }
.banner-text { font-size: 11px; color: rgba(255,255,255,0.85); }
.profile-body { display: flex; align-items: flex-start; gap: 20px; padding: 20px 24px; }
.avatar-circle { width: 76px; height: 76px; border-radius: 50%; background: #E1F5EE; color: #1D9E75; font-size: 32px; font-weight: 500; display: flex; align-items: center; justify-content: center; flex-shrink: 0; border: 2px solid #1D9E75; }
.profile-info { flex: 1; min-width: 0; }
.profile-name-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap; }
.profile-name { font-size: 18px; font-weight: 500; color: #2C2C2A; }
.profile-dept { font-size: 12px; color: #5F5E5A; margin-bottom: 2px; }
.profile-meta { font-size: 10px; color: #888780; margin-bottom: 10px; }

/* ===== 统计卡片 ===== */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 16px; }
.stat-card { background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px; padding: 16px 0; text-align: center; cursor: pointer; transition: all 0.2s; position: relative; overflow: hidden; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.stat-bar { position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.bar-blue { background: #378ADD; }
.bar-pink { background: #D4537E; }
.bar-green { background: #639922; }
.bar-amber { background: #BA7517; }
.stat-count { font-size: 28px; font-weight: 500; margin-bottom: 2px; }
.stat-count.blue { color: #378ADD; }
.stat-count.pink { color: #D4537E; }
.stat-count.green { color: #639922; }
.stat-count.amber { color: #BA7517; }
.stat-label { font-size: 11px; color: #888780; }

/* ===== Tab 栏 ===== */
.tab-bar { display: flex; flex-wrap: wrap; gap: 4px; background: #F1EFE8; border-radius: 10px; padding: 5px 6px; margin-bottom: 14px; }
.tab-btn { border: none; background: transparent; color: #5F5E5A; font-size: 12px; padding: 5px 14px; border-radius: 12px; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.tab-btn:hover { background: rgba(255,255,255,0.7); }
.tab-btn.active { background: #1D9E75; color: #fff; font-weight: 500; }

/* ===== 活跃度卡片 ===== */
.activity-card { background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px; padding: 16px 20px; margin-bottom: 14px; }
.activity-header { display: flex; align-items: center; gap: 4px; margin-bottom: 16px; }
.activity-title { font-size: 12px; font-weight: 500; color: #2C2C2A; }
.activity-sub { font-size: 10px; color: #B4B2A9; }
.activity-body { display: flex; align-items: flex-end; gap: 20px; }
.activity-chart { display: flex; align-items: flex-end; gap: 10px; flex: 1; }
.chart-bar-col { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.chart-bar { width: 100%; max-width: 24px; min-height: 4px; border-radius: 3px; background: #E1F5EE; transition: all 0.3s; }
.chart-bar.bar-peak { background: #1D9E75; }
.chart-label { font-size: 9px; color: #888780; }
.chart-label.label-peak { color: #1D9E75; font-weight: 500; }
.activity-stats { display: flex; gap: 16px; flex-shrink: 0; }
.a-stat { text-align: center; }
.a-stat-label { font-size: 10px; color: #888780; display: block; }
.a-stat-num { font-size: 18px; font-weight: 500; color: #1D9E75; display: block; }
.a-stat-num.green { color: #1D9E75; }

/* ===== 帖子卡片 ===== */
.post-list { display: flex; flex-direction: column; gap: 10px; }
.post-card { display: flex; align-items: flex-start; gap: 12px; background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px; padding: 12px 16px 12px 18px; position: relative; overflow: hidden; transition: all 0.2s; }
.post-card:hover { background: #FAFDFC; }
.post-bar {
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 5px;
  border-radius: 0 2px 2px 0;
  /* 双线效果：左侧主条 + 白色细缝 + 内侧副条 */
  box-shadow: 3px 0 0 0 rgba(255, 255, 255, 0.85),
              5px 0 0 0 currentColor;
}
.post-bar::after {
  content: '';
  position: absolute;
  right: -2px;
  top: 25%;
  bottom: 25%;
  width: 1px;
  background: rgba(255, 255, 255, 0.6);
}
.post-avatar { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 500; flex-shrink: 0; background: #E6F1FB; color: #378ADD; }
.post-avatar.bar-green { background: #EAF3DE; color: #639922; }
.post-avatar.bar-amber { background: #FAEEDA; color: #BA7517; }
.post-avatar.bar-pink { background: #FBEAF0; color: #D4537E; }
.post-avatar.bar-purple { background: #EEEDFE; color: #7F77DD; }
.post-avatar.bar-coral { background: #FAECE7; color: #D85A30; }
.post-body { flex: 1; min-width: 0; }
.post-title { font-size: 13px; font-weight: 500; color: #2C2C2A; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.post-content { font-size: 12px; color: #606266; background: #f5f7fa; padding: 6px 10px; border-radius: 4px; margin: 4px 0; border-left: 3px solid #409EFF; font-style: italic; }
.post-tags { display: flex; gap: 6px; margin-bottom: 4px; flex-wrap: wrap; }
.pill { display: inline-flex; align-items: center; padding: 0 8px; height: 16px; border-radius: 8px; font-size: 9px; background: #E6F1FB; color: #378ADD; }
.pill.bar-green { background: #EAF3DE; color: #639922; }
.pill.bar-amber { background: #FAEEDA; color: #BA7517; }
.pill.bar-pink { background: #FBEAF0; color: #D4537E; }
.pill.bar-purple { background: #EEEDFE; color: #7F77DD; }
.pill.bar-coral { background: #FAECE7; color: #D85A30; }
.pill-meta { background: #F1EFE8; color: #888780; display: inline-flex; align-items: center; padding: 0 8px; height: 16px; border-radius: 8px; font-size: 9px; }
.pill-hot { background: #FAECE7; color: #D85A30; display: inline-flex; align-items: center; padding: 0 8px; height: 16px; border-radius: 8px; font-size: 9px; }
.post-meta { font-size: 10px; color: #B4B2A9; }
.post-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.status-tag { display: inline-flex; align-items: center; padding: 0 10px; height: 20px; border-radius: 10px; background: #F1EFE8; color: #888780; font-size: 10px; }
.post-edit-btn { background: transparent; color: #5F5E5A; border: 0.5px solid #D3D1C7; border-radius: 12px; padding: 0 12px; height: 24px; font-size: 10px; cursor: pointer; transition: all 0.2s; }
.post-edit-btn:hover { background: #F1EFE8; }
.post-edit-btn.danger { color: #E24B4A; border-color: #E24B4A; }
.post-edit-btn.danger:hover { background: #FBECEC; }

/* ===== 数据卡片 ===== */
.data-card { background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px; padding: 20px; margin-bottom: 14px; }
.data-item { background: #FAFDFC; border-radius: 8px; padding: 16px 8px; text-align: center; margin-bottom: 12px; }
.data-num { font-size: 24px; font-weight: 500; margin-bottom: 4px; }
.data-num.blue { color: #378ADD; }
.data-num.pink { color: #D4537E; }
.data-num.green { color: #639922; }
.data-num.amber { color: #BA7517; }
.data-num.coral { color: #D85A30; }
.data-num.purple { color: #7F77DD; }
.data-label { font-size: 11px; color: #888780; }

/* ===== 马甲区 ===== */
.masquerade-card { background: #fff; border: 0.5px solid #D3D1C7; border-radius: 10px; padding: 16px 20px; margin-bottom: 14px; }
.section-title { font-size: 14px; font-weight: 500; margin: 0 0 12px; color: #2C2C2A; }
.masquerade-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.masquerade-tag { display: inline-flex; align-items: center; background: #E1F5EE; color: #1D9E75; padding: 6px 16px; border-radius: 18px; font-size: 14px; font-weight: 500; }
.btn-refresh { background: #FAEEDA; color: #854F0B; border: none; border-radius: 16px; padding: 6px 16px; font-size: 12px; cursor: pointer; }
.btn-refresh:hover { background: #FAC775; }
.btn-refresh:disabled { opacity: 0.6; cursor: not-allowed; }
.action-row { display: flex; gap: 12px; align-items: center; }
.btn-save { background: #1D9E75; color: #fff; border: none; border-radius: 16px; padding: 8px 24px; font-size: 13px; cursor: pointer; }
.btn-save:hover { background: #0F6E56; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

/* ===== 底部 ===== */
.footer-actions { text-align: center; margin: 24px 0; }
.btn-logout { background: transparent; color: #888780; border: 0.5px solid #D3D1C7; border-radius: 16px; padding: 6px 40px; font-size: 12px; cursor: pointer; }
.btn-logout:hover { color: #E24B4A; border-color: #E24B4A; }

/* ===== 弹窗 ===== */
.empty-state { text-align: center; padding: 32px; color: #888780; font-size: 13px; }

/* 覆盖 el-dialog 默认样式 */
.profile-dialog :deep(.el-dialog) { border-radius: 14px; overflow: hidden; padding: 0; }
.profile-dialog :deep(.el-dialog__header) { display: none; }
.profile-dialog :deep(.el-dialog__body) { padding: 0; }

/* 弹窗外壳 */
.dialog-shell { background: #fff; position: relative; }
.dialog-topbar { height: 4px; background: #1D9E75; }
.dialog-blue .dialog-topbar { background: #378ADD; }
.dialog-amber .dialog-topbar { background: #BA7517; }

.dialog-header { display: flex; align-items: center; gap: 10px; padding: 16px 22px 0; position: relative; }
.dialog-title { font-size: 14px; font-weight: 500; color: #2C2C2A; }
.dialog-underline { width: 16px; height: 3px; border-radius: 2px; background: #1D9E75; }
.dialog-blue .dialog-underline { background: #378ADD; }
.dialog-amber .dialog-underline { background: #BA7517; }
.dialog-close {
  position: absolute; right: 18px; top: 14px;
  width: 24px; height: 24px; border-radius: 50%;
  background: #F1EFE8; color: #5F5E5A;
  border: none; cursor: pointer; font-size: 12px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-family: inherit;
}
.dialog-close:hover { background: #E24B4A; color: #fff; }

.dialog-body { padding: 14px 22px 20px; max-height: 62vh; overflow-y: auto; }

/* 工具栏 */
.dialog-toolbar { display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; border-bottom: 0.5px dashed #D3D1C7; margin-bottom: 8px; flex-wrap: wrap; gap: 8px; }
.filter-tabs { display: flex; gap: 6px; flex-wrap: wrap; }
.filter-tab {
  display: inline-flex; align-items: center;
  padding: 0 14px; height: 26px;
  background: #F1EFE8; color: #5F5E5A;
  border: none; border-radius: 13px;
  font-size: 11px; cursor: pointer;
  transition: all 0.2s; font-family: inherit;
}
.filter-tab:hover { background: #E1F5EE; color: #1D9E75; }
.filter-tab.active { background: #1D9E75; color: #fff; font-weight: 500; }
.dialog-blue .filter-tab.active { background: #378ADD; }
.dialog-amber .filter-tab.active { background: #BA7517; }

.toolbar-right { display: flex; align-items: center; gap: 12px; }
.cb-label { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; color: #5F5E5A; cursor: pointer; }
.cb-label input[type="checkbox"], .item-cb input[type="checkbox"] { width: 14px; height: 14px; accent-color: #1D9E75; cursor: pointer; }
.batch-del-btn {
  display: inline-flex; align-items: center; gap: 4px;
  background: #E24B4A; color: #fff;
  border: none; border-radius: 13px;
  padding: 0 12px; height: 26px;
  font-size: 10px; font-weight: 500; cursor: pointer;
  transition: all 0.2s; font-family: inherit;
}
.batch-del-btn:hover:not(:disabled) { background: #A32D2D; }
.batch-del-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.batch-del-icon { width: 11px; height: 11px; }

/* 列表项 */
.dialog-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 8px;
  border-bottom: 0.5px solid #F1EFE8;
  border-radius: 6px;
  transition: all 0.15s;
  position: relative;
  overflow: hidden;
}
.dialog-item:hover { background: #FAFDFC; }
.dialog-item:last-child { border-bottom: none; }
.dialog-item-deleted { opacity: 0.65; background: #FAFAF8; }
.dialog-item-deleted:hover { opacity: 0.95; background: #FEF5F5; }
.item-bar { position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }
.item-bar.blue { background: #378ADD; }
.item-bar.pink { background: #D4537E; }
.item-bar.green { background: #639922; }
.item-bar.amber { background: #BA7517; }
.item-bar.purple { background: #7F77DD; }
.item-bar.coral { background: #D85A30; }
.item-cb { flex-shrink: 0; display: inline-flex; }
.item-avatar {
  width: 26px; height: 26px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 500; flex-shrink: 0;
}
.item-avatar.blue { background: #E6F1FB; color: #185FA5; }
.item-avatar.pink { background: #FBEAF0; color: #993556; }
.item-avatar.green { background: #EAF3DE; color: #27500A; }
.item-avatar.amber { background: #FAEEDA; color: #854F0B; }
.item-avatar.purple { background: #EEEDFE; color: #534AB7; }
.item-avatar.coral { background: #FAECE7; color: #993C1D; }
.item-content { flex: 1; min-width: 0; cursor: pointer; }
.item-title { font-size: 13px; font-weight: 500; color: #2C2C2A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 2px; display: flex; align-items: center; gap: 6px; }
.item-status { display: inline-flex; align-items: center; padding: 0 8px; height: 16px; border-radius: 8px; font-size: 9px; font-weight: 400; flex-shrink: 0; }
.item-status.status-ok { background: #EAF3DE; color: #27500A; }
.item-status.status-deleted { background: #FCEBEB; color: #791F1F; }
.item-status.status-pending { background: #FAEEDA; color: #854F0B; }
.item-preview {
  font-size: 11px; color: #5F5E5A;
  background: #FAFDFC; border-left: 2px solid #1D9E75;
  padding: 4px 10px; border-radius: 4px;
  margin: 4px 0; font-style: italic;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.item-actions { margin-top: 2px; }
.item-actions :deep(.post-actions) { padding: 0; gap: 4px; }
.item-actions :deep(.action-btn) { height: 22px; min-width: 0; padding: 0 8px; font-size: 10px; border-radius: 11px; }
.item-actions :deep(.action-icon) { width: 10px; height: 10px; }

/* 操作按钮 */
.item-del-btn {
  flex-shrink: 0;
  display: inline-flex; align-items: center; justify-content: center;
  padding: 0 12px; height: 24px;
  background: #fff; color: #E24B4A;
  border: 0.5px solid #E24B4A; border-radius: 12px;
  font-size: 10px; cursor: pointer;
  transition: all 0.2s; font-family: inherit;
}
.item-del-btn:hover { background: #FCEBEB; }
.item-del-hard { background: #E24B4A; color: #fff; }
.item-del-hard:hover { background: #A32D2D; }

/* 点赞徽章 / 收藏徽章 */
.like-badge {
  flex-shrink: 0;
  display: inline-flex; align-items: center;
  padding: 0 10px; height: 22px;
  background: #FAEEDA; color: #854F0B;
  border-radius: 11px; font-size: 10px; font-weight: 500;
}
.fav-badge {
  flex-shrink: 0;
  display: inline-flex; align-items: center;
  padding: 0 10px; height: 22px;
  background: #FAEEDA; color: #854F0B;
  border-radius: 11px; font-size: 10px; font-weight: 500;
}

/* 弹窗空状态 */
.dialog-empty { text-align: center; padding: 32px 0; color: #888780; font-size: 13px; }
</style>
