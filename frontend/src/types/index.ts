/**
 * 全局 TypeScript 类型定义
 */

// 统一 API 响应格式
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

// 通用分页
export interface Pagination {
  page: number
  page_size: number
  total: number
  has_more: boolean
}

// 用户
export interface User {
  id: number
  school_id: number
  student_id: string
  email: string
  nickname: string
  avatar: string
  role: 1 | 2 | 3 // 1用户 2审核员 3管理员
  status: 1 | 2 | 3 | 4
  created_at: string
}

// 板块
export interface Board {
  id: number
  slug: string
  name: string
  description: string
  icon: string
  post_count: number
}

// 帖子
export interface Post {
  id: number
  user_id: number
  board_id: number
  title: string
  content: string
  anonymous_name: string
  anonymous_avatar: string
  view_count: number
  like_count: number
  comment_count: number
  is_top: boolean
  is_essence: boolean
  created_at: string
}
