<template>
  <div class="post-detail-page">
    <div v-if="post" class="post-card">
      <!-- 作者信息 -->
      <div class="post-author">
        <div class="author-avatar">{{ (post.anonymous_name || '匿').charAt(0) }}</div>
        <div class="author-info">
          <div class="author-name">{{ post.anonymous_name }}</div>
          <div class="author-meta">
            <span>{{ post.board_name }}</span> · <span>{{ post.created_at }}</span>
            <span v-if="post.is_top" class="tag-pill tag-blue" style="margin-left:6px">置顶</span>
          </div>
        </div>
      </div>

      <!-- 标题与内容 -->
      <h1 class="detail-title">{{ post.title }}</h1>
      <div class="detail-content" v-html="post.content" @click="handleContentClick"
        @mouseover="handleImageHover" @mouseleave="hidePreview">
      </div>

      <!-- 互动栏 -->
      <div class="post-actions">
        <button class="action-btn" :class="{ 'is-liked': liked }" @click="handleLike('like')" :disabled="liking">
          <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M7 11v8m0-8l4.5-6.5a1.5 1.5 0 0 1 2.7 1V9h4.4a1.8 1.8 0 0 1 1.8 2.1l-.9 5a1.8 1.8 0 0 1-1.8 1.6H7M7 11H4v8h3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
          <span class="action-count">{{ post.like_count || 0 }}</span>
          <span class="action-text">{{ liked ? '已赞' : '点赞' }}</span>
        </button>
        <button class="action-btn" :class="{ 'is-disliked': disliked }" @click="handleLike('dislike')" :disabled="liking">
          <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M17 13V5m0 8l-4.5 6.5a1.5 1.5 0 0 1-2.7-1V15H5.4a1.8 1.8 0 0 1-1.8-2.1l.9-5a1.8 1.8 0 0 1 1.8-1.6H17M17 13h3V5h-3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
          <span class="action-count">{{ post.dislike_count || 0 }}</span>
          <span class="action-text">{{ disliked ? '已踩' : '点踩' }}</span>
        </button>
        <span class="action-btn no-hover">
          <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M20 11a8 8 0 0 1-8 8c-1.2 0-2.3-.3-3.3-.7L4 20l1.7-4.7A7.9 7.9 0 0 1 4 11a8 8 0 0 1 16 0z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
          <span class="action-count">{{ post.comment_count || 0 }}</span>
          <span class="action-text">评论</span>
        </span>
        <span class="action-btn no-hover">
          <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>
          <span class="action-count">{{ post.view_count || 0 }}</span>
          <span class="action-text">浏览</span>
        </span>
        <span v-if="post.is_admin" class="action-btn admin-btn" @click="deletePost(post.id)">
          <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
          <span class="action-text">删除</span>
        </span>
        <span style="flex: 1;"></span>
        <button class="action-btn" :class="{ 'is-favorited': favorited }" @click="toggleFavorite" :disabled="favoriting">
          <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M12 4l2.1 4.6 5 .6-3.7 3.5 1 5L12 15.4 7.6 17.7l1-5L4.9 9.2l5-.6L12 4z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
          <span class="action-count" v-if="post.favorite_count">{{ post.favorite_count }}</span>
          <span class="action-text">{{ favorited ? '已收藏' : '收藏' }}</span>
        </button>
        <button class="action-btn share-btn" @click="sharePost">
          <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><circle cx="5" cy="12" r="2.5" fill="none" stroke="currentColor" stroke-width="1.7"/><circle cx="19" cy="6" r="2.5" fill="none" stroke="currentColor" stroke-width="1.7"/><circle cx="19" cy="18" r="2.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M7.2 10.8l9.6-3.6M7.2 13.2l9.6 3.6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          <span class="action-text">分享</span>
        </button>
      </div>

      <div class="comments-separator"></div>

      <!-- 评论输入框 -->
      <div class="comment-input-area">
        <div class="comment-input-row">
          <div class="input-avatar">{{ (userStore.user?.nickname || '我').charAt(0) }}</div>
          <textarea v-model="commentText" class="comment-input" placeholder="写下你的评论..." rows="2" />
          <button class="submit-comment-btn" @click="submitComment(null)" :disabled="submitting">评论</button>
        </div>
      </div>

      <div class="comments-header">
        💬 全部评论 · {{ post.comment_count || 0 }} 条
      </div>

      <!-- 评论列表 - 线程分组 -->
      <div v-if="!post.comments?.length" class="empty-state">暂无评论，快来抢沙发吧～</div>
      <div v-else>
        <template v-for="(cg, idx) in commentGroups" :key="cg.main.id">
        <div
          :id="'comment-'+cg.main.id"
          class="comment-thread"
          :class="'thread-'+threadColors[idx % threadColors.length]"
        >
          <!-- 通栏色条 -->
          <div class="thread-bar" :style="{ background: getColor(idx).bar }"></div>

          <!-- 主评论 -->
          <div class="thread-main">
            <div class="thread-avatar" :class="'avatar-'+threadColors[idx % threadColors.length]">
              {{ (cg.main.anonymous_name || '匿').charAt(0) }}
            </div>
            <div class="thread-body">
              <div class="thread-header">
                <span class="thread-author">{{ cg.main.anonymous_name }}</span>
                <span class="thread-time">{{ cg.main.created_at }}</span>
              </div>
              <div class="thread-text">{{ cg.main.content }}</div>
              <div class="thread-actions">
                <button class="action-link" :class="getColor(idx).linkCls" @click="likeComment(cg.main.id, 1)" :disabled="cg.main._liking">
                  <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M7 11v8m0-8l4.5-6.5a1.5 1.5 0 0 1 2.7 1V9h4.4a1.8 1.8 0 0 1 1.8 2.1l-.9 5a1.8 1.8 0 0 1-1.8 1.6H7M7 11H4v8h3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                  <span>{{ cg.main.like_count || 0 }}</span>
                </button>
                <button v-if="userStore.isLoggedIn" class="action-link" :class="getColor(idx).linkCls" @click="toggleReplyBox(cg.main.id, cg.main.anonymous_name)">
                  <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M20 11a8 8 0 0 1-8 8c-1.2 0-2.3-.3-3.3-.7L4 20l1.7-4.7A7.9 7.9 0 0 1 4 11a8 8 0 0 1 16 0z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                  <span>回复</span>
                </button>
                <button v-if="canDelete(cg.main)" class="action-link danger-link" @click="deleteComment(cg.main.id)">
                  <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                  <span>删除</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 在线框内的回复输入框（回复主评论） -->
          <div v-if="replyBoxId === cg.main.id" class="thread-reply-input">
            <div style="display: flex; gap: 8px; align-items: flex-start;">
              <div class="reply-input-avatar">{{ (userStore.user?.nickname || '我').charAt(0) }}</div>
              <textarea v-model="replyText" :placeholder="'回复 ' + (replyToName || cg.main.anonymous_name) + '...'" class="comment-input" rows="2" />
            </div>
            <div class="reply-actions-bar">
              <button class="cancel-btn" @click="cancelReply">取消</button>
              <button class="submit-comment-btn" @click="submitComment(cg.main.id)" :disabled="submitting">回复</button>
            </div>
          </div>

          <!-- 分隔线 -->
          <div v-if="cg.replies.length" class="thread-divider"></div>

          <!-- 回复列表（缩进在线框内） + 各自独立的回复框 -->
          <div v-for="r in cg.replies" :key="'r'+r.id" class="thread-reply" style="display: block;">
            <div class="thread-reply-row" style="display: flex; gap: 10px; padding: 8px 14px;">
              <div class="reply-avatar" :class="'avatar-'+threadColors[idx % threadColors.length]">
                {{ (r.anonymous_name || '匿').charAt(0) }}
              </div>
              <div class="reply-body" style="flex: 1; min-width: 0;">
                <div class="reply-header">
                  <span class="reply-author">{{ r.anonymous_name }}</span>
                  <span v-if="r.reply_to_name" class="reply-mention">回复 @{{ r.reply_to_name }}</span>
                  <span class="reply-time">{{ r.created_at }}</span>
                </div>
                <div class="reply-text">{{ r.content }}</div>
                <div class="thread-actions">
                  <button class="action-link" :class="getColor(idx).linkCls" @click="likeComment(r.id, 1)" :disabled="r._liking">
                    <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M7 11v8m0-8l4.5-6.5a1.5 1.5 0 0 1 2.7 1V9h4.4a1.8 1.8 0 0 1 1.8 2.1l-.9 5a1.8 1.8 0 0 1-1.8 1.6H7M7 11H4v8h3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                    <span>{{ r.like_count || 0 }}</span>
                  </button>
                  <button v-if="userStore.isLoggedIn" class="action-link" :class="getColor(idx).linkCls" @click="toggleReplyBox(r.id, r.anonymous_name)">
                    <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M20 11a8 8 0 0 1-8 8c-1.2 0-2.3-.3-3.3-.7L4 20l1.7-4.7A7.9 7.9 0 0 1 4 11a8 8 0 0 1 16 0z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                    <span>回复</span>
                  </button>
                  <button v-if="canDelete(r)" class="action-link danger-link" @click="deleteComment(r.id)">
                    <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                    <span>删除</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 楼中楼：子评论下的直接子评论（缩进 +22px） -->
            <div v-if="r.replies && r.replies.length" class="thread-sub-replies" style="padding-left: 22px; background: #fafbfc;">
              <div v-for="rr in r.replies" :key="'sr-'+rr.id" class="thread-sub-reply" style="display: flex; gap: 8px; padding: 6px 14px; border-left: 2px solid #d3d1c7;">
                <div class="sub-reply-avatar" style="width: 22px; height: 22px; font-size: 10px; line-height: 22px; text-align: center; border-radius: 50%; background: #F1EFE8; color: #5f5e5a; flex-shrink: 0;">
                  {{ (rr.anonymous_name || '匿').charAt(0) }}
                </div>
                <div class="sub-reply-body" style="flex: 1; min-width: 0;">
                  <div class="sub-reply-header" style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                    <span class="sub-reply-author" style="font-size: 12px; font-weight: 500; color: #5f5e5a;">{{ rr.anonymous_name }}</span>
                    <span v-if="rr.reply_to_name" class="sub-reply-mention" style="font-size: 11px; color: #909399;">回复 @{{ rr.reply_to_name }}</span>
                    <span class="sub-reply-time" style="font-size: 10px; color: #c0c4cc;">{{ rr.created_at }}</span>
                  </div>
                  <div class="sub-reply-text" style="font-size: 12px; color: #606266; margin: 2px 0;">{{ rr.content }}</div>
                  <div class="thread-actions" style="display: flex; gap: 8px;">
                    <button class="action-link" :class="getColor(idx).linkCls" @click="likeComment(rr.id, 1)" :disabled="rr._liking">
                      <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M7 11v8m0-8l4.5-6.5a1.5 1.5 0 0 1 2.7 1V9h4.4a1.8 1.8 0 0 1 1.8 2.1l-.9 5a1.8 1.8 0 0 1-1.8 1.6H7M7 11H4v8h3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                      <span>{{ rr.like_count || 0 }}</span>
                    </button>
                    <button v-if="userStore.isLoggedIn" class="action-link" :class="getColor(idx).linkCls" @click="toggleReplyBox(rr.id, rr.anonymous_name)">
                      <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M20 11a8 8 0 0 1-8 8c-1.2 0-2.3-.3-3.3-.7L4 20l1.7-4.7A7.9 7.9 0 0 1 4 11a8 8 0 0 1 16 0z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                      <span>回复</span>
                    </button>
                    <button v-if="canDelete(rr)" class="action-link danger-link" @click="deleteComment(rr.id)">
                      <svg viewBox="0 0 24 24" class="action-icon" aria-hidden="true"><path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m3 0v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7h12z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
                      <span>删除</span>
                    </button>
                  </div>
                  <!-- 楼中楼自己的回复框 -->
                  <div v-if="replyBoxId === rr.id" class="thread-reply-input nested" style="margin: 4px 0;">
                    <div style="display: flex; gap: 8px; align-items: flex-start;">
                      <div class="reply-input-avatar small">{{ (userStore.user?.nickname || '我').charAt(0) }}</div>
                      <textarea v-model="replyText" :placeholder="'回复 ' + replyToName + '...'" class="comment-input" rows="2" />
                    </div>
                    <div class="reply-actions-bar">
                      <button class="cancel-btn" @click="cancelReply">取消</button>
                      <button class="submit-comment-btn" @click="submitComment(rr.id)" :disabled="submitting">回复</button>
                    </div>
                  </div>
                </div>
                <!-- 楼中楼的楼中楼：子评论的子评论 -->
                <div v-if="rr.replies && rr.replies.length" class="thread-sub-sub-replies" style="padding-left: 22px; background: #f5f5f5;">
                  <div v-for="rrr in rr.replies" :key="'ssr-'+rrr.id" class="thread-sub-sub-reply" style="display: flex; gap: 6px; padding: 4px 12px; border-left: 2px solid #b4b2a9;">
                    <div class="sub-sub-reply-avatar" style="width: 18px; height: 18px; font-size: 9px; line-height: 18px; text-align: center; border-radius: 50%; background: #F1EFE8; color: #5f5e5a; flex-shrink: 0;">
                      {{ (rrr.anonymous_name || '匿').charAt(0) }}
                    </div>
                    <div class="sub-sub-reply-body" style="flex: 1; min-width: 0;">
                      <div class="sub-sub-reply-header" style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap;">
                        <span class="sub-sub-reply-author" style="font-size: 11px; font-weight: 500; color: #5f5e5a;">{{ rrr.anonymous_name }}</span>
                        <span v-if="rrr.reply_to_name" class="sub-sub-reply-mention" style="font-size: 10px; color: #909399;">回复 @{{ rrr.reply_to_name }}</span>
                        <span class="sub-sub-reply-time" style="font-size: 9px; color: #c0c4cc;">{{ rrr.created_at }}</span>
                      </div>
                      <div class="sub-sub-reply-text" style="font-size: 11px; color: #606266; margin: 1px 0;">{{ rrr.content }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- 子评论自己的回复框 -->
            <div v-if="replyBoxId === r.id" class="thread-reply-input nested" style="padding: 8px 14px 8px 56px;">
              <div style="display: flex; gap: 8px; align-items: flex-start;">
                <div class="reply-input-avatar small">{{ (userStore.user?.nickname || '我').charAt(0) }}</div>
                <textarea v-model="replyText" :placeholder="'回复 ' + replyToName + '...'" class="comment-input" rows="2" />
              </div>
              <div class="reply-actions-bar">
                <button class="cancel-btn" @click="cancelReply">取消</button>
                <button class="submit-comment-btn" @click="submitComment(r.id)" :disabled="submitting">回复</button>
              </div>
            </div>
          </div>
        </div>
      </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showConfirm } from '@/utils/confirm'
import { useForumStore } from '@/stores/forum'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const forumStore = useForumStore()
const userStore = useUserStore()
const post = ref<any>(null)
const loading = ref(false)
const commentText = ref('')
const replyText = ref('')
const replyBoxId = ref<number | null>(null)
const replyToName = ref('')
const submitting = ref(false)
const liking = ref(false)
const liked = ref(false)
const disliked = ref(false)
const favorited = ref(false)
const favoriting = ref(false)

const threadColors = ['green', 'pink', 'blue', 'amber', 'purple', 'coral']

const colorPalette: Record<string, { bar: string; border: string; bg: string; text: string; linkCls: string }> = {
  green:  { bar: '#1D9E75', border: '#1D9E75', bg: '#E1F5EE', text: '#085041', linkCls: 'link-green' },
  pink:   { bar: '#D4537E', border: '#D4537E', bg: '#FBEAF0', text: '#993556', linkCls: 'link-pink' },
  blue:   { bar: '#378ADD', border: '#378ADD', bg: '#E6F1FB', text: '#185FA5', linkCls: 'link-blue' },
  amber:  { bar: '#BA7517', border: '#BA7517', bg: '#FAEEDA', text: '#633806', linkCls: 'link-amber' },
  purple: { bar: '#7F77DD', border: '#7F77DD', bg: '#EEEDFE', text: '#3C3489', linkCls: 'link-purple' },
  coral:  { bar: '#D85A30', border: '#D85A30', bg: '#FAECE7', text: '#712B13', linkCls: 'link-coral' },
}

function getColor(idx: number) {
  return colorPalette[threadColors[idx % threadColors.length]]
}

/** 将 post.comments 按主评论 + replies 分组为扁平数组 */
const commentGroups = computed(() => {
  if (!post.value?.comments) return []
  return post.value.comments.map((c: any) => ({
    main: c,
    // 过滤掉错误的子评论（parent_id 不是自己 ID 的）
    replies: (c.replies || []).filter((r: any) => r.parent_id === c.id),
  }))
})

function canDelete(c: any) {
  if (!userStore.isLoggedIn) return false
  return c.is_author || c.is_post_author || c.is_admin
}

async function loadPost() {
  loading.value = true
  try {
    const res = await api.get(`/posts/${route.params.id}`)
    post.value = res.data
    liked.value = res.data?.user_liked === 1
    disliked.value = res.data?.user_disliked === 1
    // 加载收藏状态
    if (userStore.isLoggedIn) {
      try {
        const favRes = await api.get(`/favorites/posts/${route.params.id}/status`)
        favorited.value = favRes.data?.favorited === true
        if (res.data) res.data.favorite_count = favRes.data?.favorite_count ?? 0
      } catch {}
    }
    await nextTick()
    if (route.hash) {
      const el = document.getElementById(route.hash.replace('#', ''))
      if (el) setTimeout(() => { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); el.classList.add('comment-highlight'); setTimeout(() => el.classList.remove('comment-highlight'), 2400) }, 300)
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '加载失败')
  } finally { loading.value = false }
}

onMounted(loadPost)

async function handleLike(action: string) {
  if (!userStore.isLoggedIn) { ElMessage.warning('请先登录'); return }
  liking.value = true
  try {
    await api.post('/posts/' + route.params.id + '/like', { action })
    if (action === 'like') liked.value = !liked.value
    else disliked.value = !disliked.value
    await loadPost()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally { liking.value = false }
}

async function toggleFavorite() {
  if (!userStore.isLoggedIn) { ElMessage.warning('请先登录'); return }
  favoriting.value = true
  try {
    const res = await api.post(`/favorites/posts/${route.params.id}`)
    favorited.value = res.data?.favorited === true
    if (post.value) {
      post.value.favorite_count = res.data?.favorite_count ?? post.value.favorite_count
    }
    ElMessage.success(res.data?.favorited ? '已收藏' : '取消收藏')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally { favoriting.value = false }
}

/** 分享：复制当前页面链接 */
async function sharePost() {
  try {
    const url = window.location.href
    await navigator.clipboard.writeText(url)
    ElMessage.success('链接已复制，快去分享吧！')
  } catch {
    // 降级：直接展示链接
    ElMessage.info(`分享链接：${window.location.href}`)
  }
}

async function submitComment(parentId: number | null) {
  const text = parentId === null ? commentText.value : replyText.value
  if (!text || !text.trim()) { ElMessage.warning('请输入评论内容'); return }
  submitting.value = true
  try {
    await api.post('/comments', { post_id: Number(route.params.id), content: text.trim(), parent_id: parentId || undefined })
    ElMessage.success(parentId === null ? '评论成功' : '回复成功')
    commentText.value = ''; replyText.value = ''; replyBoxId.value = null; replyToName.value = ''
    await loadPost()
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '操作失败') }
  finally { submitting.value = false }
}

function toggleReplyBox(id: number, name: string) {
  if (replyBoxId.value === id) { cancelReply() }
  else { replyBoxId.value = id; replyToName.value = name; replyText.value = '' }
}

function cancelReply() { replyBoxId.value = null; replyText.value = ''; replyToName.value = '' }

async function likeComment(commentId: number, action: number) {
  if (!userStore.isLoggedIn) { ElMessage.warning('请先登录'); return }
  try {
    await api.post(`/comments/${commentId}/like`, { action })
    await loadPost()
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '操作失败') }
}

async function deletePost(postId: number) {
  try {
    await showConfirm('确定删除该帖子吗？此操作不可撤销。', '删除帖子', 'danger', '帖子关联的评论也会一并移除。')
  } catch { return }
  try {
    await api.delete(`/posts/${postId}`)
    ElMessage.success('已删除')
    router.push('/')
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '删除失败') }
}

async function deleteComment(commentId: number) {
  try {
    await showConfirm('确定要删除这条评论吗？删除后无法恢复。', '删除评论', 'danger')
  } catch { return }
  try {
    await api.delete(`/comments/${commentId}`)
    ElMessage.success('已删除')
    await loadPost()
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '删除失败') }
}

// ==== 内容区交互 ====
let previewPopover: HTMLDivElement | null = null
let previewTimer: any = null

function handleContentClick(e: MouseEvent) {
  const el = e.target as HTMLElement
  const img = el.closest('img')
  if (img && img.classList.contains('editor-image')) {
    downloadFile(img.src, img.getAttribute('data-file-name') || img.getAttribute('alt') || '图片')
    return
  }
  const fileCard = el.closest('.editor-file-card')
  if (fileCard) {
    const base64 = fileCard.getAttribute('data-base64') || ''
    const filename = fileCard.getAttribute('data-filename') || '文件'
    if (base64 && base64.startsWith('data:')) {
      downloadFile(base64, filename)
    } else {
      ElMessage.warning('该文件数据未嵌入，无法下载')
    }
    return
  }
}

function downloadFile(href: string, filename: string) {
  const a = document.createElement('a')
  a.href = href; a.download = filename
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
}

function handleImageHover(e: MouseEvent) {
  const el = e.target as HTMLElement
  const img = el.closest('img.editor-image') as HTMLImageElement | null
  if (!img) { delayedHidePreview(); return }
  if (previewTimer) clearTimeout(previewTimer)
  showPreview(img.src, e.clientX, e.clientY)
}

function showPreview(src: string, x: number, y: number) {
  hidePreviewNow()
  const el = document.createElement('div')
  el.className = 'image-preview-popover'
  el.innerHTML = `<img src="${src}" alt="preview">`
  el.style.left = (x + 20) + 'px'; el.style.top = (y + 20) + 'px'
  document.body.appendChild(el)
  const rect = el.getBoundingClientRect()
  if (rect.right > window.innerWidth) el.style.left = (x - rect.width - 20) + 'px'
  if (rect.bottom > window.innerHeight) el.style.top = (y - rect.height - 20) + 'px'
  previewPopover = el
}

function delayedHidePreview() {
  if (previewTimer) clearTimeout(previewTimer)
  previewTimer = setTimeout(() => hidePreviewNow(), 200)
}
function hidePreview() { delayedHidePreview() }
function hidePreviewNow() {
  if (previewPopover) {
    if (previewPopover.parentNode) previewPopover.parentNode.removeChild(previewPopover)
    previewPopover = null
  }
}
</script>

<style scoped>
.post-detail-page { max-width: 720px; margin: 0 auto; }
.post-card { background: #fff; border: 0.5px solid #d3d1c7; border-radius: 14px; overflow: hidden; }
.loading-card { background: #fff; border: 0.5px solid #d3d1c7; border-radius: 14px; padding: 40px; text-align: center; }

/* 作者 */
.post-author { display: flex; align-items: center; gap: 12px; padding: 16px 20px; }
.author-avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #409EFF, #67C23A); color: #fff; font-size: 16px; font-weight: 600; display: flex; align-items: center; justify-content: center; }
.author-info { flex: 1; }
.author-name { font-size: 14px; font-weight: 500; color: #303133; }
.author-meta { font-size: 11px; color: #b4b2a9; display: flex; gap: 6px; margin-top: 2px; }

.detail-title { font-size: 22px; font-weight: 700; color: #1a1a1a; margin: 0; padding: 0 20px; line-height: 1.3; }
.detail-content { padding: 12px 20px; white-space: pre-wrap; line-height: 1.8; font-size: 14px; color: #5f5e5a; }

/* 图片卡片样式 */
.detail-content :deep(span.editor-image) { display: inline-flex; align-items: center; justify-content: center; border: 0.5px solid #d3d1c7; border-radius: 10px; margin: 6px 4px; padding: 0; background: #F1EFE8; overflow: hidden; width: 180px; height: 130px; vertical-align: top; cursor: pointer; transition: all 0.2s; }
.detail-content :deep(span.editor-image:hover) { box-shadow: 0 4px 16px rgba(0,0,0,0.12); transform: translateY(-2px); }
.detail-content :deep(.editor-image-thumb) { width: 100%; height: 100%; object-fit: cover; display: block; background: #fff; }
.detail-content :deep(.editor-file-card) { display: inline-flex; align-items: center; gap: 8px; border: 0.5px solid #d3d1c7; border-radius: 10px; padding: 6px 14px; margin: 4px; background: #F1EFE8; cursor: pointer; position: relative; overflow: hidden; vertical-align: middle; max-width: 280px; transition: all 0.2s; }
.detail-content :deep(.editor-file-card:hover) { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(29,158,117,0.12); border-color: #1D9E75; }
.detail-content :deep(.editor-file-bar) { position: absolute; left: 0; top: 0; bottom: 0; width: 4px; border-radius: 10px 0 0 10px; }
.detail-content :deep(.editor-file-icon) { width: 32px; height: 32px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }
.detail-content :deep(.editor-file-body) { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.detail-content :deep(.editor-file-name) { font-size: 12px; font-weight: 500; color: #1a1a1a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.detail-content :deep(.editor-file-meta) { font-size: 10px; color: #888780; margin-top: 1px; }

/* 互动栏 - 第一版设计：默认灰底 / hover 彩边 / 激活实色填充 */
.post-actions { display: flex; gap: 8px; padding: 0 20px 12px; flex-wrap: wrap; align-items: center; }
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 36px;
  min-width: 68px;
  padding: 0 14px;
  background: #F1EFE8;
  border: 0.5px solid #D3D1C7;
  border-radius: 18px;
  font-size: 12px;
  color: #5F5E5A;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  line-height: 1;
  white-space: nowrap;
}
.action-icon { width: 15px; height: 15px; flex-shrink: 0; display: block; }
.action-count { font-weight: 500; }
.action-text { color: inherit; }

/* 悬浮态：白底 + 彩色描边 */
.action-btn:hover { background: #fff; border-width: 1px; }
.action-btn:not(.no-hover):hover,
.action-btn:not(.admin-btn):hover { color: #1D9E75; border-color: #1D9E75; }
.action-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.action-btn:disabled:hover { background: #F1EFE8; color: #5F5E5A; border-color: #D3D1C7; }

/* 无交互态（评论/浏览计数） */
.action-btn.no-hover { cursor: default; color: #888780; }
.action-btn.no-hover:hover { background: #F1EFE8; color: #888780; border-color: #D3D1C7; border-width: 0.5px; }

/* 激活态：实色填充 */
.action-btn.is-liked { background: #1D9E75; border-color: #1D9E75; color: #fff; font-weight: 500; }
.action-btn.is-liked:hover { background: #0F6E56; color: #fff; border-color: #0F6E56; }
.action-btn.is-disliked { background: #D85A30; border-color: #D85A30; color: #fff; font-weight: 500; }
.action-btn.is-disliked:hover { background: #993C1D; color: #fff; border-color: #993C1D; }
.action-btn.is-favorited { background: #BA7517; border-color: #BA7517; color: #fff; font-weight: 500; }
.action-btn.is-favorited:hover { background: #854F0B; color: #fff; border-color: #854F0B; }

/* 管理员删除按钮（红色系） */
.action-btn.admin-btn { color: #E24B4A; }
.action-btn.admin-btn:hover { background: #fff; border-color: #E24B4A; color: #E24B4A; }

/* 分享按钮（紫色 hover） */
.action-btn.share-btn:hover { color: #7F77DD; border-color: #7F77DD; }

/* 分割 */
.comments-separator { height: 0.5px; background: #e0e0e0; margin: 0 20px; }

/* 评论输入框 */
.comment-input-area { padding: 14px 20px; background: linear-gradient(180deg, #fafbfc 0%, #ffffff 100%); border-bottom: 0.5px solid #ebeef5; }
.comment-input-row { display: flex; gap: 12px; align-items: flex-start; }
.input-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #1D9E75, #0F6E56); color: #fff; font-size: 14px; font-weight: 600; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; box-shadow: 0 2px 6px rgba(29,158,117,0.2); }
.comment-input { flex: 1; padding: 10px 14px; border: 1px solid #e4e7ed; border-radius: 10px; font-size: 13px; outline: none; resize: none; font-family: inherit; transition: all 0.2s; background: #fff; line-height: 1.6; min-height: 60px; }
.comment-input:hover { border-color: #c0c4cc; }
.comment-input:focus { border-color: #1D9E75; box-shadow: 0 0 0 3px rgba(29,158,117,0.1); }
.submit-comment-btn { padding: 8px 22px; background: linear-gradient(135deg, #1D9E75, #0F6E56); color: #fff; border: none; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; font-family: inherit; transition: all 0.2s; flex-shrink: 0; box-shadow: 0 2px 4px rgba(29,158,117,0.2); }
.submit-comment-btn:hover { background: linear-gradient(135deg, #0F6E56, #085041); box-shadow: 0 4px 8px rgba(29,158,117,0.3); transform: translateY(-1px); }
.submit-comment-btn:active { transform: translateY(0); box-shadow: 0 1px 2px rgba(29,158,117,0.2); }
.submit-comment-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }

/* 评论标题 */
.comments-header { padding: 12px 20px; font-size: 14px; font-weight: 600; color: #1a1a1a; }

/* 线程容器 */
.comment-thread {
  position: relative;
  margin: 0 20px 8px;
  padding: 0;
  border: 0.5px solid #d3d1c7;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}
.thread-bar {
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 4px;
}

/* 线程颜色边框 */
.thread-green  { border-color: #1D9E75; }
.thread-pink   { border-color: #D4537E; }
.thread-blue   { border-color: #378ADD; }
.thread-amber  { border-color: #BA7517; }
.thread-purple { border-color: #7F77DD; }
.thread-coral  { border-color: #D85A30; }

/* 主评论 */
.thread-main { display: flex; gap: 10px; padding: 12px 14px 8px; }
.thread-avatar { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; flex-shrink: 0; margin-top: 2px; }
.avatar-green  { background: #E1F5EE; color: #085041; border: 0.5px solid #1D9E75; }
.avatar-pink   { background: #FBEAF0; color: #993556; border: 0.5px solid #D4537E; }
.avatar-blue   { background: #E6F1FB; color: #185FA5; border: 0.5px solid #378ADD; }
.avatar-amber  { background: #FAEEDA; color: #633806; border: 0.5px solid #BA7517; }
.avatar-purple { background: #EEEDFE; color: #3C3489; border: 0.5px solid #7F77DD; }
.avatar-coral  { background: #FAECE7; color: #712B13; border: 0.5px solid #D85A30; }

.thread-body { flex: 1; min-width: 0; }
.thread-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap; }
.thread-author { font-size: 13px; font-weight: 600; color: #1a1a1a; }
.thread-time { font-size: 11px; color: #b4b2a9; }
.thread-text { font-size: 13px; color: #5f5e5a; line-height: 1.6; margin-bottom: 6px; word-break: break-word; }
.thread-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.thread-actions .action-link {
  display: inline-flex; align-items: center; justify-content: center;
  gap: 4px;
  height: 24px;
  padding: 0 10px;
  background: #F1EFE8;
  border: 0.5px solid #D3D1C7;
  border-radius: 12px;
  font-size: 11px;
  color: #5F5E5A;
  cursor: pointer;
  transition: all 0.18s ease;
  font-family: inherit;
  line-height: 1;
  white-space: nowrap;
}
.thread-actions .action-link .action-icon { width: 11px; height: 11px; flex-shrink: 0; }
.thread-actions .action-link:hover { background: #fff; border-width: 1px; }
.thread-actions .action-link:disabled { opacity: 0.5; cursor: not-allowed; }
.thread-actions .action-link:disabled:hover { background: #F1EFE8; border-color: #D3D1C7; }

/* 颜色主题 hover（继承每条评论的语义色） */
.link-green:hover  { color: #1D9E75; border-color: #1D9E75; }
.link-pink:hover   { color: #D4537E; border-color: #D4537E; }
.link-blue:hover   { color: #378ADD; border-color: #378ADD; }
.link-amber:hover  { color: #BA7517; border-color: #BA7517; }
.link-purple:hover { color: #7F77DD; border-color: #7F77DD; }
.link-coral:hover  { color: #D85A30; border-color: #D85A30; }
.danger-link:hover { color: #E24B4A; border-color: #E24B4A; opacity: 1; }

/* 分隔线 */
.thread-divider { height: 0.5px; background: #e0e0e0; margin: 0 14px; }

/* 回复输入框（在线框内） */
.thread-reply-input { padding: 10px 14px; background: #fafbfc; border-radius: 8px; margin: 6px 0; }
.thread-reply-input .comment-input { border-radius: 8px; min-height: 50px; font-size: 12px; }
.reply-input-avatar { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #1D9E75, #0F6E56); color: #fff; font-size: 11px; font-weight: 600; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 4px; }
.reply-input-avatar.small { width: 24px; height: 24px; font-size: 10px; margin-top: 6px; }
.reply-actions-bar { display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px; }
.cancel-btn { padding: 6px 16px; background: #fff; color: #606266; border: 1px solid #dcdfe6; border-radius: 6px; cursor: pointer; font-size: 12px; font-family: inherit; transition: all 0.2s; }
.cancel-btn:hover { background: #f5f7fa; color: #1D9E75; border-color: #1D9E75; }

/* 回复列表 */
.thread-reply { display: flex; gap: 10px; padding: 8px 14px 8px 14px; }
.reply-avatar { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 600; flex-shrink: 0; margin-top: 2px; }
.reply-body { flex: 1; min-width: 0; }
.reply-header { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 2px; }
.reply-author { font-size: 12px; font-weight: 600; color: #1a1a1a; }
.reply-mention { font-size: 11px; color: #1D9E75; font-weight: 500; }
.reply-time { font-size: 10px; color: #b4b2a9; }
.reply-text { font-size: 12px; color: #5f5e5a; line-height: 1.6; margin-bottom: 4px; word-break: break-word; }

.tag-pill { display: inline-flex; align-items: center; padding: 1px 8px; border-radius: 8px; font-size: 10px; font-weight: 500; line-height: 1.6; }
.tag-blue { background: #E6F1FB; color: #185FA5; }

.empty-state { text-align: center; padding: 30px 0; color: #b4b2a9; font-size: 13px; }

.comment-highlight { animation: highlightFade 2.4s ease-out; border-radius: 10px; }
@keyframes highlightFade { 0% { background: #E1F5EE; } 100% { background: transparent; } }

/* 鼠标悬停图片预览弹层 */
.image-preview-popover { position: fixed; z-index: 9999; max-width: 320px; max-height: 320px; padding: 6px; background: #fff; border: 1px solid #409EFF; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.18); pointer-events: none; animation: fadeIn 0.15s ease-out; }
.image-preview-popover img { max-width: 320px; max-height: 320px; display: block; border-radius: 4px; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
</style>
