<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-logo">
          <span class="auth-logo-icon">🌳</span>
          <h2 class="auth-title">欢迎来到Campus Forum</h2>
          <p class="auth-subtitle">匿名分享，畅所欲言</p>
        </div>
        <h3 class="auth-form-title">注 册</h3>
        <form @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label class="form-label">学号</label>
            <input v-model="form.student_id" class="form-input" placeholder="请输入学号" />
          </div>
          <div class="form-group">
            <label class="form-label">QQ 邮箱</label>
            <input v-model="form.email" class="form-input" placeholder="xxx@qq.com" />
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <div class="password-wrap">
              <input v-model="form.password" :type="showPassword ? 'text' : 'password'" class="form-input" placeholder="至少8位，需含字母和数字" />
              <button type="button" class="password-toggle" @click="showPassword = !showPassword">
                {{ showPassword ? '👁' : '👁‍🗨' }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">图形验证码</label>
            <div class="captcha-row">
              <input v-model="form.captcha_answer" class="form-input captcha-input" placeholder="请输入图形验证码" />
              <div class="captcha-img-box" @click="loadCaptcha" title="点击刷新">
                <img v-if="captchaImg" :src="captchaImg" alt="验证码" class="captcha-img" />
                <span v-else class="captcha-placeholder">加载中...</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">邮箱验证码</label>
            <div class="captcha-row">
              <input v-model="form.email_code" class="form-input captcha-input" placeholder="6 位数字" />
              <button type="button" class="send-btn" @click="sendCode" :disabled="cooldown">
                {{ cooldown ? `${cooldownSec}s 后重发` : '发送验证码' }}
              </button>
            </div>
          </div>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>
        <div class="auth-footer">
          <span>已有账号？</span>
          <router-link to="/login" class="register-link">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const showPassword = ref(false)
const captchaUuid = ref('')
const captchaImg = ref('')
const cooldown = ref(false)
const cooldownSec = ref(0)
const LAST_CLICK_KEY = 'last_send_code_click'
let cooldownTimer: number | null = null

const form = reactive({
  student_id: '', email: '', password: '',
  captcha_uuid: '', captcha_answer: '', email_code: '',
})

async function loadCaptcha() {
  captchaImg.value = ''   // 显示加载中占位
  try {
    const res: any = await api.get('/auth/captcha', { timeout: 30000 })
    // axios 拦截器已解包，res = {code, message, data: {uuid, image}}
    const payload = res?.data || res   // 兼容两层 / 三层结构
    const uuid = payload?.uuid ?? payload?.data?.uuid
    const image = payload?.image ?? payload?.data?.image
    if (!uuid || !image) {
      throw new Error('验证码响应字段缺失')
    }
    captchaUuid.value = uuid
    captchaImg.value = image
    form.captcha_uuid = uuid
  } catch (e: any) {
    console.error('[captcha] 加载失败:', e?.message || e)
    ElMessage.error('图形验证码加载失败：' + (e?.message || '请检查后端 / 网络'))
    // 5 秒后自动重试一次
    setTimeout(() => loadCaptcha(), 5000)
  }
}
loadCaptcha()

function startCooldown(sec: number) {
  cooldown.value = true
  cooldownSec.value = sec
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = window.setInterval(() => {
    cooldownSec.value--
    if (cooldownSec.value <= 0) {
      if (cooldownTimer) { clearInterval(cooldownTimer); cooldownTimer = null }
      cooldown.value = false
      cooldownSec.value = 0
    }
  }, 1000)
}

onBeforeUnmount(() => { if (cooldownTimer) clearInterval(cooldownTimer) })

async function sendCode() {
  const now = Date.now()
  const last = Number(localStorage.getItem(LAST_CLICK_KEY) || 0)
  if (now - last < 2000) {
    ElMessage.warning('请勿连续点击')
    return
  }
  localStorage.setItem(LAST_CLICK_KEY, String(now))

  if (!form.email) { ElMessage.warning('请先输入 QQ 邮箱'); return }
  if (!form.email.endsWith('@qq.com')) { ElMessage.warning('请使用 QQ 邮箱（@qq.com）'); return }

  try {
    await api.post('/auth/send-code', { email: form.email })
    ElMessage.success('验证码已发送，请查收邮箱')
    startCooldown(20)
  } catch (e: any) {
    const code = e?.code
    const msg = e?.response?.data?.message || e.message || '发送失败'
    if (code === 5001 || /SMTP|配置|授权码/i.test(msg)) {
      ElMessage.error('邮件发送失败：' + msg)
    } else if (code === 3003) {
      ElMessage.warning(msg || '操作过于频繁，请稍后再试')
      startCooldown(20)
    } else {
      ElMessage.error(msg)
    }
  }
}

async function handleRegister() {
  if (!form.student_id.trim() || !form.email.trim() || !form.password.trim() || !form.captcha_answer.trim() || !form.email_code.trim()) {
    ElMessage.warning('请填写完整的注册信息'); return
  }
  loading.value = true
  try {
    const payload = { ...form, captcha_uuid: captchaUuid.value }
    await userStore.register(payload)
    ElMessage.success('注册成功，欢迎加入Campus Forum！')
    router.push('/')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '注册失败')
    await loadCaptcha()
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.auth-container { width: 400px; }
.auth-card {
  background: #fff;
  border: 0.5px solid #d3d1c7;
  border-radius: 16px;
  padding: 32px 40px;
}
.auth-logo { text-align: center; margin-bottom: 16px; }
.auth-logo-icon { font-size: 32px; }
.auth-title { margin: 8px 0 4px; font-size: 20px; font-weight: 600; color: #0C447C; }
.auth-subtitle { margin: 0; font-size: 12px; color: #888780; }

.auth-form-title { margin: 0 0 20px; text-align: center; font-size: 18px; font-weight: 600; color: #1a1a1a; letter-spacing: 5px; }

.auth-form { display: flex; flex-direction: column; gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 12px; font-weight: 500; color: #5f5e5a; }
.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 0.5px solid #d3d1c7;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  font-family: inherit;
}
.form-input:focus { border-color: #1D9E75; }
.password-wrap { position: relative; }
.password-toggle {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: #F1EFE8;
  border: none;
  border-radius: 4px;
  padding: 2px 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}
.password-toggle:hover {
  background: #1D9E75;
  color: #fff;
  box-shadow: 0 0 0 3px rgba(29, 158, 117, 0.25);
}

.captcha-row { display: flex; gap: 8px; align-items: center; }
.captcha-input { flex: 1; }
.captcha-img-box {
  width: 100px;
  height: 36px;
  border: 0.5px solid #d3d1c7;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.captcha-img { width: 100%; height: 100%; object-fit: contain; }
.captcha-placeholder { font-size: 11px; color: #909399; }
.send-btn {
  padding: 10px 14px;
  background: #E1F5EE;
  color: #1D9E75;
  border: 0.5px solid #1D9E75;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s;
  font-family: inherit;
}
.send-btn:hover { background: #1D9E75; color: #fff; }
.send-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #1D9E75;
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  font-family: inherit;
  margin-top: 4px;
}
.submit-btn:hover { background: #0F6E56; }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.auth-footer { text-align: center; margin-top: 16px; font-size: 12px; color: #888780; }
.register-link { color: #1D9E75; font-weight: 500; text-decoration: none; margin-left: 4px; }
</style>
