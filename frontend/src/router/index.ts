import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'Home', component: () => import('@/views/Home.vue'), meta: { title: '首页' } },
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue'), meta: { title: '注册' } },
  { path: '/posts/create', name: 'CreatePost', component: () => import('@/views/CreatePost.vue'), meta: { title: '发帖' } },
  { path: '/posts/:id', name: 'PostDetail', component: () => import('@/views/PostDetail.vue'), meta: { title: '帖子详情' } },
  { path: '/profile', name: 'Profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心' } },
  { path: '/admin', name: 'Admin', component: () => import('@/views/Admin.vue'), meta: { title: '管理后台' } },
  { path: '/board/:id', name: 'Board', component: () => import('@/views/BoardDetail.vue'), meta: { title: '板块' } },
  { path: '/search', name: 'Search', component: () => import('@/views/Search.vue'), meta: { title: '搜索' } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFound.vue'), meta: { title: '页面不存在' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _from, next) => {
  document.title = ((to.meta.title as string) || '') ? `${to.meta.title} - Campus Forum` : 'Campus Forum'
  next()
})

export default router
