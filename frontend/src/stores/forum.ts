/** 板块 + 帖子状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useForumStore = defineStore('forum', () => {
  const boards = ref<any[]>([])
  const posts = ref<any[]>([])
  const currentPost = ref<any>(null)
  const trendingBoards = ref<any[]>([])
  const trendingSummary = ref<any>(null)
  const rankingList = ref<any[]>([])

  async function fetchBoards() {
    const res = await api.get('/boards')
    boards.value = res.data || []
  }

  async function fetchPosts(params?: any) {
    const res = await api.get('/posts', { params })
    posts.value = res.data?.list || []
    return res.data
  }

  async function fetchPostDetail(id: number) {
    const res = await api.get(`/posts/${id}`)
    currentPost.value = res.data
    return res.data
  }

  async function createPost(data: any) {
    return await api.post('/posts', data)
  }

  async function fetchTrending(range: 'week' | 'month' = 'week') {
    const res = await api.get('/posts/trending', { params: { range } })
    trendingBoards.value = res.data?.boards || []
    trendingSummary.value = res.data?.summary || null
    return res.data
  }

  async function fetchRanking(sort: 'view' | 'comment' | 'time' | 'favorite' = 'view', limit = 10) {
    const res = await api.get('/posts/ranking', { params: { sort, limit } })
    rankingList.value = res.data?.list || []
    return res.data
  }

  return {
    boards, posts, currentPost,
    trendingBoards, trendingSummary, rankingList,
    fetchBoards, fetchPosts, fetchPostDetail, createPost,
    fetchTrending, fetchRanking,
  }
})
