<template>
  <!-- 模板样式：胶囊形按钮 + 图标 + 数字 + 文字（与 PostDetail.vue 完全一致） -->
  <div class="post-actions">
    <span class="action-btn" :class="['is-liked']" v-if="interactive && !readonly">
      <svg viewBox="0 0 24 24" class="action-icon"><path d="M7 11v8m0-8l4.5-6.5a1.5 1.5 0 0 1 2.7 1V9h4.4a1.8 1.8 0 0 1 1.8 2.1l-.9 5a1.8 1.8 0 0 1-1.8 1.6H7M7 11H4v8h3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
      <span class="action-count">{{ like_count || 0 }}</span>
      <span class="action-text">点赞</span>
    </span>
    <span class="action-btn no-hover" v-else>
      <svg viewBox="0 0 24 24" class="action-icon"><path d="M7 11v8m0-8l4.5-6.5a1.5 1.5 0 0 1 2.7 1V9h4.4a1.8 1.8 0 0 1 1.8 2.1l-.9 5a1.8 1.8 0 0 1-1.8 1.6H7M7 11H4v8h3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
      <span class="action-count">{{ like_count || 0 }}</span>
      <span class="action-text">点赞</span>
    </span>

    <span class="action-btn no-hover">
      <svg viewBox="0 0 24 24" class="action-icon"><path d="M20 11a8 8 0 0 1-8 8c-1.2 0-2.3-.3-3.3-.7L4 20l1.7-4.7A7.9 7.9 0 0 1 4 11a8 8 0 0 1 16 0z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
      <span class="action-count">{{ comment_count || 0 }}</span>
      <span class="action-text">评论</span>
    </span>

    <span class="action-btn no-hover">
      <svg viewBox="0 0 24 24" class="action-icon"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>
      <span class="action-count">{{ view_count || 0 }}</span>
      <span class="action-text">浏览</span>
    </span>

    <span class="action-btn no-hover" v-if="show_favorite">
      <svg viewBox="0 0 24 24" class="action-icon"><path d="M12 4l2.1 4.6 5 .6-3.7 3.5 1 5L12 15.4 7.6 17.7l1-5L4.9 9.2l5-.6L12 4z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>
      <span class="action-count">{{ favorite_count || 0 }}</span>
      <span class="action-text">收藏</span>
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  like_count?: number
  comment_count?: number
  view_count?: number
  favorite_count?: number
  show_favorite?: boolean       // 是否显示"收藏"按钮（弹窗里可隐藏）
  interactive?: boolean         // 是否可交互（未来扩展用）
  readonly?: boolean            // 只读模式
}>()
</script>

<style scoped>
/* ===== 完全对齐 PostDetail.vue 模板样式 ===== */
.post-actions { display: flex; gap: 6px; padding: 6px 0; flex-wrap: wrap; align-items: center; }
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 28px;
  min-width: 60px;
  padding: 0 10px;
  background: #F1EFE8;
  border: 0.5px solid #D3D1C7;
  border-radius: 14px;
  font-size: 11px;
  color: #5F5E5A;
  transition: all 0.2s ease;
  font-family: inherit;
  line-height: 1;
  white-space: nowrap;
}
.action-icon { width: 13px; height: 13px; flex-shrink: 0; display: block; }
.action-count { font-weight: 500; }
.action-text { color: inherit; }

/* 弹窗中无 hover，但保留激活态的颜色（已点赞等场景）*/
.action-btn.no-hover { cursor: default; color: #888780; }
.action-btn.no-hover:hover { background: #F1EFE8; color: #888780; border-color: #D3D1C7; border-width: 0.5px; }

/* 激活态：实色填充（保留与 PostDetail 一致）*/
.action-btn.is-liked { background: #1D9E75; border-color: #1D9E75; color: #fff; font-weight: 500; }
</style>