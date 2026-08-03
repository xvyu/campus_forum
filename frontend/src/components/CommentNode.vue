<template>
  <div class="reply-item" :style="indentStyle">
    <div class="reply-top">
      <div>
        <span class="reply-anon">{{ node.anonymous_name }}</span>
        <span v-if="node.reply_to_name" class="reply-to-inline">回复 @{{ node.reply_to_name }}</span>
      </div>
      <span class="reply-time">{{ node.created_at }}</span>
    </div>
    <div class="reply-text">{{ node.content }}</div>
    <div class="comment-actions">
      <el-button size="small" text :class="['heart-btn', node.like_count > 0 ? 'liked' : 'unliked']" @click="$emit('like', node, node.like_count > 0 ? 'cancel' : 'like')">
        <el-icon><component :is="node.like_count > 0 ? StarFilled : Star" /></el-icon>
        <span v-if="node.like_count > 0" class="heart-num">{{ node.like_count }}</span>
      </el-button>
      <el-button v-if="userStore.isLoggedIn" size="small" text @click="$emit('toggle-reply', node.id, node.anonymous_name)">
        <el-icon><ChatLineRound /></el-icon> 回复
      </el-button>
      <el-button v-if="canDelete(node)" size="small" type="danger" text @click="$emit('delete', node.id)">
        <el-icon><Delete /></el-icon> 删除
      </el-button>
    </div>
    <!-- 该层的回复输入框 -->
    <div v-if="replyBoxId === node.id" class="reply-input">
      <el-input :model-value="replyText" @update:model-value="(v) => $emit('update:replyText', v)" type="textarea" :rows="2" :placeholder="'回复 ' + replyToName + '...'" maxlength="1000" show-word-limit />
      <div style="display:flex;gap:8px;margin-top:6px;justify-content:flex-end">
        <el-button size="small" @click="$emit('cancel-reply')">取消</el-button>
        <el-button type="primary" size="small" @click="$emit('submit-reply', node.id)">提交回复</el-button>
      </div>
    </div>
    <!-- 递归：任意层级子评论 -->
    <div v-if="node.replies && node.replies.length" class="sub-replies">
      <CommentNode
        v-for="child in node.replies"
        :key="child.id"
        :node="child"
        :depth="depth + 1"
        :reply-box-id="replyBoxId"
        :reply-text="replyText"
        :reply-to-name="replyToName"
        @toggle-reply="(id, name) => $emit('toggle-reply', id, name)"
        @like="(n) => $emit('like', n, 'like')"
        @delete="(id) => $emit('delete', id)"
        @cancel-reply="$emit('cancel-reply')"
        @submit-reply="(pid) => $emit('submit-reply', pid)"
        @update:reply-text="(v) => $emit('update:replyText', v)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Delete, ChatLineRound, Star, StarFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const props = defineProps<{
  node: any
  depth: number
  replyBoxId: number | null
  replyText: string
  replyToName: string
}>()
defineEmits<{
  'toggle-reply': [id: number, name: string]
  'like': [n: any, action: string]
  'delete': [id: number]
  'cancel-reply': []
  'submit-reply': [parentId: number]
  'update:replyText': [v: string]
}>()

const userStore = useUserStore()
const indentStyle = computed(() => ({ marginLeft: props.depth * 16 + 'px' }))

function canDelete(c: any) {
  if (!userStore.isLoggedIn) return false
  return c.is_author || c.is_post_author || c.is_admin
}
</script>

<style scoped>
.reply-item { padding: 8px 0; border-radius: 4px; }
.reply-top { display: flex; justify-content: space-between; align-items: center; }
.reply-anon { color: #67c23a; font-weight: 500; font-size: 13px; }
.reply-time { font-size: 12px; color: #909399; }
.reply-text { margin: 4px 0; font-size: 13px; line-height: 1.6; }
.comment-actions { display: flex; gap: 4px; align-items: center; margin-top: 4px; flex-wrap: wrap; }

/* 爱心点赞按钮 */
.heart-btn { display: inline-flex; align-items: center; gap: 2px; padding: 0 8px; transition: all 0.2s; }
.heart-btn.unliked :deep(svg) { color: rgba(0, 0, 0, 0.15); transition: color 0.2s; }
.heart-btn.liked :deep(svg) { color: #f56c6c; transition: color 0.2s; }
.heart-btn:hover :deep(svg) { color: #f56c6c; }
.heart-num { font-size: 12px; color: #f56c6c; font-weight: 500; }
.heart-btn.unliked .heart-num { color: #909399; }
.reply-input { margin: 8px 0 4px; padding: 10px; background: #f9f9f9; border-radius: 6px; }
.floor-tag { margin-left: 6px; font-size: 11px; color: #909399; background: #f5f7fa; border: none; }
.reply-to-inline { margin-left: 8px; font-size: 12px; color: #909399; background: #f5f7fa; padding: 1px 6px; border-radius: 8px; }
.sub-replies { margin-top: 4px; }
</style>
