<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-logo">
          <span class="auth-logo-icon">🌳</span>
          <h2 class="auth-title">欢迎来到Campus Forum</h2>
          <p class="auth-subtitle">匿名分享，畅所欲言</p>
        </div>
        <h3 class="auth-form-title">登 录</h3>
        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label class="form-label">学号</label>
            <input v-model="form.student_id" class="form-input" placeholder="请输入学号" />
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <div class="password-wrap">
              <input v-model="form.password" :type="showPassword ? 'text' : 'password'" class="form-input" placeholder="请输入密码" />
              <button type="button" class="password-toggle" @click="showPassword = !showPassword">
                {{ showPassword ? '👁' : '👁‍🗨' }}
              </button>
            </div>
          </div>
          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" /> 记住我
            </label>
            <a href="javascript:;" class="forgot-link" @click="openForgotDialog">忘记密码？</a>
          </div>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
        <div class="auth-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="register-link">立即注册</router-link>
        </div>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <el-dialog v-model="forgotVisible" title="重置密码" width="460px" :close-on-click-modal="false">
      <el-steps :active="forgotStep" align-center finish-status="success" class="forgot-steps">
        <el-step title="验证邮箱" />
        <el-step title="输入验证码" />
        <el-step title="设置新密码" />
      </el-steps>
      <div v-if="forgotStep === 0" class="forgot-form">
        <p class="forgot-tip">请输入您注册时使用的邮箱，我们会向该邮箱发送验证码</p>
        <div class="form-group">
          <label class="form-label">注册邮箱</label>
          <input v-model="forgotForm.email" class="form-input" placeholder="例如：123456@qq.com" />
        </div>
        <button class="submit-btn" :disabled="sendingCode" @click="sendResetCode">
          {{ sendingCode ? '发送中...' : '发送验证码' }}
        </button>
      </div>
      <div v-if="forgotStep === 1" class="forgot-form">
        <p class="forgot-tip">验证码已发送至 <b>{{ forgotForm.email }}</b>，有效期 5 分钟</p>
        <div class="form-group">
          <label class="form-label">6 位验证码</label>
          <input v-model="forgotForm.email_code" class="form-input" maxlength="6" placeholder="请输入 6 位数字" style="letter-spacing: 8px; text-align: center; font-size: 18px;" />
        </div>
        <div class="forgot-actions">
          <button class="submit-btn submit-btn-secondary" @click="forgotStep = 0">上一步</button>
          <button class="submit-btn" @click="forgotStep = 2">下一步</button>
        </div>
        <div class="resend-row">
          没收到？
          <a href="javascript:;" :class="{ disabled: resendCooldown > 0 }" @click="resendCode">
            {{ resendCooldown > 0 ? `${resendCooldown}s 后重发` : '重新发送' }}
          </a>
        </div>
      </div>
      <div v-if="forgotStep === 2" class="forgot-form">
        <p class="forgot-tip">请输入新密码，<b>8 位以上</b>且<b>同时包含字母和数字</b></p>
        <div class="form-group">
          <label class="form-label">新密码</label>
          <div class="password-wrap">
            <input v-model="forgotForm.new_password" :type="showNewPwd ? 'text' : 'password'" class="form-input" placeholder="新密码" />
            <button type="button" class="password-toggle" @click="showNewPwd = !showNewPwd">
              {{ showNewPwd ? '👁' : '👁‍🗨' }}
            </button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">确认新密码</label>
          <div class="password-wrap">
            <input v-model="forgotForm.confirm_password" :type="showConfirmPwd ? 'text' : 'password'" class="form-input" placeholder="再次输入新密码" />
            <button type="button" class="password-toggle" @click="showConfirmPwd = !showConfirmPwd">
              {{ showConfirmPwd ? '👁' : '👁‍🗨' }}
            </button>
          </div>
        </div>
        <div class="forgot-actions">
          <button class="submit-btn submit-btn-secondary" @click="forgotStep = 1">上一步</button>
          <button class="submit-btn" :disabled="resetting" @click="doResetPassword">
            {{ resetting ? '重置中...' : '确认重置' }}
          </button>
        </div>
      </div>
      <div v-if="forgotStep === 3" class="forgot-form forgot-success">
        <el-result icon="success" title="密码已重置" sub-title="请使用新密码登录">
          <template #extra>
            <el-button type="primary" @click="goBackToLogin">返回登录</el-button>
          </template>
        </el-result>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const showPassword = ref(false)
const form = reactive({ student_id: '', password: '' })
const REMEMBER_KEY = 'campus_forum_remember'
const rememberMe = ref(localStorage.getItem(REMEMBER_KEY) !== null)
if (rememberMe.value) {
  const saved = JSON.parse(localStorage.getItem(REMEMBER_KEY) || '{}')
  form.student_id = saved.student_id || ''
  form.password = saved.password || ''
}
function syncRemember() {
  if (rememberMe.value && form.student_id.trim()) {
    localStorage.setItem(REMEMBER_KEY, JSON.stringify({
      student_id: form.student_id.trim(),
      password: form.password,
    }))
  } else {
    localStorage.removeItem(REMEMBER_KEY)
  }
}
async function handleLogin() {
  if (!form.student_id.trim() || !form.password.trim()) {
    ElMessage.warning('请填写学号和密码'); return
  }
  syncRemember()
  loading.value = true
  try {
    await userStore.login(form.student_id, form.password)
    await new Promise(r => setTimeout(r, 200))
    await userStore.fetchMe()
    ElMessage.success('登录成功')
    router.push('/')
    setTimeout(async () => { await userStore.fetchMe() }, 300)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '登录失败')
  } finally { loading.value = false }
}
const forgotVisible = ref(false)
const forgotStep = ref(0)
const sendingCode = ref(false)
const resetting = ref(false)
const resendCooldown = ref(0)
const showNewPwd = ref(false)
const showConfirmPwd = ref(false)
const forgotForm = reactive({
  email: '',
  email_code: '',
  new_password: '',
  confirm_password: '',
})
let cooldownTimer: any = null
function openForgotDialog() {
  forgotVisible.value = true
  forgotStep.value = 0
  forgotForm.email = ''
  forgotForm.email_code = ''
  forgotForm.new_password = ''
  forgotForm.confirm_password = ''
  resendCooldown.value = 0
  showNewPwd.value = false
  showConfirmPwd.value = false
}
watch(forgotVisible, (v) => {
  if (!v) {
    showNewPwd.value = false
    showConfirmPwd.value = false
    showPassword.value = false
  }
})
watch(forgotStep, (v) => {
  if (v === 2) {
    showNewPwd.value = false
    showConfirmPwd.value = false
  }
})
function startCooldown() {
  resendCooldown.value = 60
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    resendCooldown.value -= 1
    if (resendCooldown.value <= 0) {
      clearInterval(cooldownTimer); cooldownTimer = null
    }
  }, 1000)
}
async function sendResetCode() {
  const email = forgotForm.email.trim().toLowerCase()
  if (!email) { ElMessage.warning('请输入邮箱'); return }
  if (!email.endsWith('@qq.com')) { ElMessage.warning('请使用 QQ 邮箱（@qq.com）'); return }
  sendingCode.value = true
  try {
    await api.post('/auth/reset-password/send-code', { email })
    ElMessage.success('验证码已发送，请查收邮箱')
    startCooldown()
    forgotStep.value = 1
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '发送失败')
  } finally { sendingCode.value = false }
}
async function resendCode() {
  if (resendCooldown.value > 0) return
  await sendResetCode()
}
async function doResetPassword() {
  if (!forgotForm.email_code || forgotForm.email_code.length !== 6) {
    ElMessage.warning('请输入 6 位验证码'); return
  }
  if (!forgotForm.new_password || forgotForm.new_password.length < 8) {
    ElMessage.warning('新密码至少 8 位'); return
  }
  if (!/[a-zA-Z]/.test(forgotForm.new_password) || !/\d/.test(forgotForm.new_password)) {
    ElMessage.warning('新密码必须同时包含字母和数字'); return
  }
  if (forgotForm.new_password !== forgotForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致'); return
  }
  if (form.password && form.password === forgotForm.new_password) {
    ElMessage.warning('新密码不能与当前登录密码相同'); return
  }
  resetting.value = true
  try {
    await api.post('/auth/reset-password', {
      email: forgotForm.email.trim().toLowerCase(),
      email_code: forgotForm.email_code,
      new_password: forgotForm.new_password,
    })
    ElMessage.success('密码已重置')
    forgotStep.value = 3
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '重置失败')
  } finally { resetting.value = false }
}
function goBackToLogin() {
  forgotVisible.value = false
  form.password = ''
}
onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
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
.auth-form { display: flex; flex-direction: column; gap: 18px; }
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
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}
.remember-me { display: flex; align-items: center; gap: 6px; color: #888780; cursor: pointer; }
.remember-me input { accent-color: #1D9E75; }
.forgot-link { color: #1D9E75; text-decoration: none; cursor: pointer; }
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
}
.submit-btn:hover { background: #0F6E56; }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.submit-btn-secondary { background: #f5f7fa; color: #606266; }
.submit-btn-secondary:hover { background: #ebeef5; }
.auth-footer { text-align: center; margin-top: 16px; font-size: 12px; color: #888780; }
.register-link { color: #1D9E75; font-weight: 500; text-decoration: none; margin-left: 4px; }
.forgot-steps { margin-bottom: 24px; }
.forgot-form { display: flex; flex-direction: column; gap: 14px; }
.forgot-tip { font-size: 13px; color: #5f5e5a; margin: 0 0 4px; line-height: 1.6; }
.forgot-tip b { color: #1D9E75; }
.forgot-actions { display: flex; gap: 10px; }
.forgot-actions .submit-btn { flex: 1; }
.resend-row { text-align: center; font-size: 12px; color: #888780; }
.resend-row a { color: #1D9E75; text-decoration: none; margin-left: 4px; }
.resend-row a.disabled { color: #c0c4cc; pointer-events: none; }
.forgot-success { padding: 12px 0; }
</style>
