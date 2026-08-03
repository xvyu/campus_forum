<template>
  <div class="board-detail">
    <div v-if="board" class="board-header-card">
      <div class="board-icon-large" :class="'board-icon-' + boardColor">{{ board.icon || '📁' }}</div>
      <div class="board-header-info">
        <h2 class="board-name">{{ board.name }}</h2>
        <p class="board-desc">{{ board.description }}</p>
        <div class="board-stats-row">
          <span>帖子 {{ (forumStore.posts || []).length || 0 }}</span>
        </div>
      </div>
    </div>

    <div v-if="forumStore.posts.length === 0" class="empty-state">该板块暂无帖子</div>
    <div
      v-for="(p, idx) in forumStore.posts"
      :key="p.id"
      class="post-item-modern"
      @click="$router.push(`/posts/${p.id}`)"
    >
      <div class="accent-bar" :class="'accent-' + barColors[idx % barColors.length]"></div>
      <div class="avatar-anon" :class="'avatar-' + barColors[idx % barColors.length]">匿</div>
      <div class="post-content">
        <div class="post-title">{{ p.title }}</div>
        <div class="post-meta">
          <span>{{ p.anonymous_name }}</span>
          <span>·</span>
          <span>{{ p.created_at }}</span>
          <span>·</span>
          <span>♥ {{ p.like_count }} 💬 {{ p.comment_count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useForumStore } from '@/stores/forum'

const route = useRoute()
const forumStore = useForumStore()
const board = ref<any>(null)
const boardColor = ref('blue')
const barColors = ['blue', 'pink', 'green', 'amber', 'purple', 'coral']

onMounted(async () => {
  await forumStore.fetchBoards()
  board.value = forumStore.boards.find(b => b.id === Number(route.params.id))
  if (board.value) {
    const colorMap: Record<string, string> = {
      '学习': 'blue', '情感': 'pink', '生活': 'green', '二手': 'amber',
      '吐槽': 'coral', '表白': 'purple', '失物': 'pink', '兼职': 'gray'
    }
    boardColor.value = colorMap[board.value.name?.charAt(0)] || 'blue'
  }
  await forumStore.fetchPosts({ board_id: Number(route.params.id) })
})
</script>

<style scoped>
.board-header-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: #fff;
  border: 0.5px solid #d3d1c7;
  border-radius: 12px;
  margin-bottom: 16px;
}
.board-icon-large {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}
.board-icon-blue { background: #378ADD; }
.board-icon-pink { background: #D4537E; }
.board-icon-green { background: #639922; }
.board-icon-amber { background: #BA7517; }
.board-icon-coral { background: #D85A30; }
.board-icon-purple { background: #7F77DD; }
.board-icon-gray { background: #888780; }
.board-header-info { flex: 1; }
.board-name { margin: 0 0 4px; font-size: 18px; font-weight: 600; }
.board-desc { margin: 0 0 8px; font-size: 13px; color: #888780; }
.board-stats-row { font-size: 11px; color: #b4b2a9; display: flex; gap: 12px; }

.post-item-modern {
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
}
.post-item-modern:hover {
  border-color: #1D9E75;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(29, 158, 117, 0.06);
}
.post-content { flex: 1; min-width: 0; }
.post-title { font-size: 14px; font-weight: 500; color: #1a1a1a; margin-bottom: 4px; }
.post-meta { font-size: 11px; color: #b4b2a9; display: flex; gap: 6px; }

.empty-state { text-align: center; padding: 60px 0; color: #b4b2a9; font-size: 14px; }

.avatar-anon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}
.avatar-blue { background: #E6F1FB; color: #185FA5; border: 0.5px solid #378ADD; }
.avatar-pink { background: #FBEAF0; color: #993556; border: 0.5px solid #D4537E; }
.avatar-green { background: #EAF3DE; color: #27500A; border: 0.5px solid #639922; }
.avatar-amber { background: #FAEEDA; color: #633806; border: 0.5px solid #BA7517; }
.avatar-purple { background: #EEEDFE; color: #3C3489; border: 0.5px solid #7F77DD; }
.avatar-coral { background: #FAECE7; color: #712B13; border: 0.5px solid #D85A30; }
.avatar-gray { background: #F1EFE8; color: #5f5e5a; }

.accent-bar { width: 6px; border-radius: 3px; flex-shrink: 0; height: 48px; }
.accent-blue { background: #378ADD; }
.accent-pink { background: #D4537E; }
.accent-green { background: #639922; }
.accent-amber { background: #BA7517; }
.accent-purple { background: #7F77DD; }
.accent-coral { background: #D85A30; }
</style>
