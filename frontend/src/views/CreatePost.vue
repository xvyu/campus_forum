<template>
  <div class="create-post-page">
    <!-- Hero 区 -->
    <div class="hero-section">
      <div class="hero-icon">✍️</div>
      <div class="hero-text">
        <h2 class="hero-title">分享你的想法</h2>
        <p class="hero-desc">匿名发帖，畅所欲言</p>
      </div>
    </div>

    <!-- 发帖表单卡片 -->
    <div class="post-card">
      <div class="card-header">
        <div class="accent-bar accent-green"></div>
        <span class="card-title">📝 发表新帖</span>
      </div>

      <form @submit.prevent="handleSubmit" class="post-form">
        <!-- 板块选择 -->
        <div class="form-group">
          <label class="form-label">📂 板块 <span class="required-star">*</span></label>
          <div class="select-wrap" @click="showBoardPicker = !showBoardPicker">
            <div class="select-placeholder" v-if="!form.board_id">
              <span class="select-text">请选择板块</span>
            </div>
            <div class="select-value" v-else>
              <span class="board-tag" :class="'board-tag-' + getBoardColor(selectedBoard)">{{ selectedBoard?.icon || '📁' }}</span>
              <span class="select-text">{{ selectedBoard?.name }} · {{ selectedBoard?.description }}</span>
            </div>
            <span class="select-arrow">▾</span>
          </div>
          <div class="board-picker" v-if="showBoardPicker">
            <div
              v-for="b in forumStore.boards"
              :key="b.id"
              class="board-option"
              :class="{ selected: form.board_id === b.id }"
              @click="selectBoard(b)"
            >
              <span class="board-tag" :class="'board-tag-' + getBoardColor(b)">{{ b.icon || '📁' }}</span>
              <div class="board-option-info">
                <div class="board-option-name">{{ b.name }}</div>
                <div class="board-option-desc">{{ b.description }}</div>
              </div>
              <span v-if="form.board_id === b.id" class="check-mark">✓</span>
            </div>
          </div>
        </div>

        <!-- 标题输入 -->
        <div class="form-group">
          <label class="form-label">✏️ 标题 <span class="required-star">*</span></label>
          <input
            v-model="form.title"
            class="form-input"
            :class="{ 'input-limit': form.title.length >= TITLE_MAX }"
            placeholder="输入帖子标题"
            :maxlength="TITLE_MAX"
            @keydown="handleTitleKeydown"
            @paste="handleTitlePaste"
          />
          <span class="char-count">{{ form.title.length }} / 50</span>
        </div>

        <!-- 内容输入（富文本 contenteditable 编辑器） -->
        <div class="form-group">
          <label class="form-label">📄 内容 <span class="required-star">*</span></label>

          <!-- 格式工具栏 -->
          <div class="editor-toolbar">
            <button type="button" class="toolbar-btn" :class="{ active: activeFormats.bold }" @mousedown.prevent @click="exec('bold')" title="加粗 (Ctrl+B)"><b>B</b></button>
            <button type="button" class="toolbar-btn" :class="{ active: activeFormats.italic }" @mousedown.prevent @click="exec('italic')" title="斜体 (Ctrl+I)"><i>I</i></button>
            <button type="button" class="toolbar-btn" :class="{ active: activeFormats.underline }" @mousedown.prevent @click="exec('underline')" title="下划线 (Ctrl+U)"><u>U</u></button>
            <button type="button" class="toolbar-btn" :class="{ active: activeFormats.strikeThrough }" @mousedown.prevent @click="exec('strikeThrough')" title="删除线"><s>S</s></button>
            <span class="toolbar-divider"></span>

            <button type="button" class="toolbar-btn toolbar-btn-text" @mousedown.prevent @click="execBlock('formatBlock', 'H2')" title="标题">标</button>
            <button type="button" class="toolbar-btn toolbar-btn-text" @mousedown.prevent @click="execBlock('formatBlock', 'P')" title="正文">正</button>
            <span class="toolbar-divider"></span>

            <button type="button" class="toolbar-btn" @mousedown.prevent @click="execBlock('insertUnorderedList')" title="无序列表">•</button>
            <button type="button" class="toolbar-btn" @mousedown.prevent @click="execBlock('insertOrderedList')" title="有序列表">1.</button>
            <button type="button" class="toolbar-btn" :class="{ active: activeFormats.blockquote }" @mousedown.prevent @click="execBlock('formatBlock', 'BLOCKQUOTE')" title="引用">❝</button>
            <span class="toolbar-divider"></span>

            <button type="button" class="toolbar-btn" :class="{ active: activeFormats.justifyLeft }" @mousedown.prevent @click="exec('justifyLeft')" title="左对齐">⇤</button>
            <button type="button" class="toolbar-btn" :class="{ active: activeFormats.justifyCenter }" @mousedown.prevent @click="exec('justifyCenter')" title="居中">↔</button>
            <button type="button" class="toolbar-btn" :class="{ active: activeFormats.justifyRight }" @mousedown.prevent @click="exec('justifyRight')" title="右对齐">⇥</button>
            <span class="toolbar-divider"></span>

            <button type="button" class="toolbar-btn" @mousedown.prevent @click="insertLink" title="插入本地文件/图片">📎</button>
            <button type="button" class="toolbar-btn toolbar-btn-text" @mousedown.prevent @click="exec('removeFormat')" title="清除格式">清</button>
            <span class="toolbar-divider"></span>

            <button type="button" class="toolbar-btn" @mousedown.prevent @click="exec('undo')" title="撤销 (Ctrl+Z)">↩</button>
            <button type="button" class="toolbar-btn" @mousedown.prevent @click="exec('redo')" title="重做 (Ctrl+Y)">↪</button>
          </div>

          <div
            ref="contentEditor"
            class="form-content-editor"
            :class="{ 'input-limit': plainTextLength >= CONTENT_MAX }"
            contenteditable="true"
            data-placeholder="写下你想分享的内容..."
            @input="syncContent"
            @keydown="handleEditorKeydown"
            @mouseup="updateActiveFormats"
            @keyup="updateActiveFormats"
            @focus="updateActiveFormats"
            @paste="handlePaste"
            @beforeinput="handleContentBeforeInput"
          ></div>
          <div class="editor-status">
            <span class="char-count">{{ plainTextLength }} / 5000</span>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="form-actions">
          <button type="button" class="pill-btn" @click="saveDraft">📋 保存草稿</button>
          <button type="submit" class="pill-btn pill-btn-primary" :disabled="loading">
            {{ loading ? '发布中...' : '发布 →' }}
          </button>
        </div>
      </form>
    </div>

    <div class="footer-tip">系统将使用你的匿名马甲发布</div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showConfirm } from '@/utils/confirm'
import { useForumStore } from '@/stores/forum'

const router = useRouter()
const forumStore = useForumStore()
const loading = ref(false)
const showBoardPicker = ref(false)
const contentEditor = ref<HTMLDivElement | null>(null)
const form = reactive({ board_id: null as number | null, title: '', content: '', anonymous_id: undefined })
const plainTextLength = ref(0)
const activeFormats = reactive({
  bold: false, italic: false, underline: false, strikeThrough: false,
  justifyLeft: false, justifyCenter: false, justifyRight: false,
  blockquote: false,
})

const selectedBoard = computed(() => {
  return forumStore.boards.find(b => b.id === form.board_id) || null
})

const boardColors: Record<string, string> = {
  '学习': 'blue', '情感': 'pink', '生活': 'green', '二手': 'amber',
  '吐槽': 'coral', '表白': 'purple', '失物': 'pink', '兼职': 'gray'
}

function getBoardColor(board: any): string {
  if (!board) return 'blue'
  const key = Object.keys(boardColors).find(k => board.name?.includes(k))
  return boardColors[key || ''] || 'blue'
}

function selectBoard(board: any) {
  form.board_id = board.id
  showBoardPicker.value = false
}

/** 富文本格式化核心 */
function exec(command: string, value: string | null = null) {
  if (!contentEditor.value) return
  contentEditor.value.focus()
  document.execCommand(command, false, value || undefined)
  syncContent()
  updateActiveFormats()
}

function execBlock(command: string, value: string | null = null) {
  if (!contentEditor.value) return
  contentEditor.value.focus()
  document.execCommand(command, false, value || undefined)
  syncContent()
  updateActiveFormats()
}

function insertLink() {
  // 创建隐藏的文件选择 input
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*,.pdf,.doc,.docx,.txt,.zip,.rar'
  input.multiple = true
  input.style.display = 'none'
  document.body.appendChild(input)

  input.addEventListener('change', async (e) => {
    const files = (e.target as HTMLInputElement).files
    if (!files || files.length === 0) {
      document.body.removeChild(input)
      return
    }

    if (!contentEditor.value) {
      document.body.removeChild(input)
      return
    }
    contentEditor.value.focus()

    const maxSize = 5 * 1024 * 1024 // 5MB
    const errors: string[] = []
    let successCount = 0

    for (const file of Array.from(files)) {
      if (file.size > maxSize) {
        errors.push(`${file.name} 超过 5MB`)
        continue
      }
      try {
        // 所有文件统一转 base64
        const dataUrl = await fileToDataURL(file)
        const sizeText = formatFileSize(file.size)
        const color = getFileTypeColor(file.name)

        if (file.type.startsWith('image/')) {
          // 图片卡片：仅显示缩略图，不显示文件名（避免占用编辑区空间）
          // contenteditable="false" 防止光标误入造成文件信息被修改
          const html = `<span class="editor-image" data-file-name="${escapeAttr(file.name)}" data-base64="${escapeAttr(dataUrl)}" data-size="${file.size}" contenteditable="false">` +
            `<img src="${dataUrl}" alt="${escapeAttr(file.name)}" class="editor-image-thumb" draggable="false" />` +
          `</span>`
          document.execCommand('insertHTML', false, html)
          successCount++
        } else {
          // 文件卡片：色条 + icon + 名称 + 类型·大小，contenteditable="false" 防止误删
          const html = `<span class="editor-file-card" data-filename="${escapeAttr(file.name)}" data-size="${file.size}" data-base64="${escapeAttr(dataUrl)}" contenteditable="false">` +
            `<span class="editor-file-bar" style="background:${color};"></span>` +
            `<span class="editor-file-icon" style="background:${color}22;color:${color}">${getFileIcon(file.name)}</span>` +
            `<span class="editor-file-body">` +
              `<span class="editor-file-name">${escapeHtml(file.name)}</span>` +
              `<span class="editor-file-meta">${getFileType(file.name)} · ${sizeText}</span>` +
            `</span></span>`
          document.execCommand('insertHTML', false, html)
          successCount++
        }
      } catch (err) {
        errors.push(`${file.name} 读取失败`)
      }
    }

    // 立即手动同步字数（execCommand 不一定触发 input 事件）
    syncContent()
    updateActiveFormats()

    if (successCount > 0) {
      ElMessage.success(`已插入 ${successCount} 个文件`)
    }
    if (errors.length > 0) {
      ElMessage.warning(`部分文件失败：${errors.join('；')}`)
    }

    document.body.removeChild(input)
  })

  // 取消选择时清理
  input.addEventListener('cancel', () => {
    if (input.parentNode) document.body.removeChild(input)
  })

  input.click()
}

function fileToDataURL(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function escapeAttr(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}
function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

/** 根据文件后缀返回颜色 */
function getFileTypeColor(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  if (['doc','docx','txt','pdf'].includes(ext)) return '#378ADD'
  if (['xls','xlsx','csv'].includes(ext)) return '#639922'
  if (['ppt','pptx'].includes(ext)) return '#D85A30'
  if (['zip','rar','7z','gz','tar'].includes(ext)) return '#BA7517'
  if (['py','js','ts','html','css','json','xml','java','cpp','go'].includes(ext)) return '#7F77DD'
  if (['png','jpg','jpeg','gif','svg','webp','ico'].includes(ext)) return '#D4537E'
  return '#888780'
}
function getFileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  if (['doc','docx'].includes(ext)) return '📄'
  if (['xls','xlsx','csv'].includes(ext)) return '📊'
  if (['ppt','pptx'].includes(ext)) return '📽'
  if (['pdf'].includes(ext)) return '📕'
  if (['zip','rar','7z','gz','tar'].includes(ext)) return '📦'
  if (['py','js','ts','html','css','json','xml','java','cpp','go'].includes(ext)) return '💻'
  if (['png','jpg','jpeg','gif','svg','webp'].includes(ext)) return '🖼'
  if (['txt','md'].includes(ext)) return '📝'
  return '📎'
}
function getFileType(filename: string): string {
  const ext = filename.split('.').pop()?.toUpperCase() || 'FILE'
  return ext
}

/** 字数限制常量 */
const TITLE_MAX = 50
const CONTENT_MAX = 5000
/** 提示去重：同一位置同一提示只显示一次 */
let lastLimitMsgShown: { target: 'title' | 'content'; at: number } | null = null
const LIMIT_MSG_INTERVAL = 1500 // ms

function showLimitReached(target: 'title' | 'content') {
  const now = Date.now()
  if (lastLimitMsgShown && lastLimitMsgShown.target === target && now - lastLimitMsgShown.at < LIMIT_MSG_INTERVAL) {
    return
  }
  lastLimitMsgShown = { target, at: now }
  if (target === 'title') {
    ElMessage.warning(`标题已达 ${TITLE_MAX} 字上限`)
  } else {
    ElMessage.warning(`内容已达 ${CONTENT_MAX} 字上限`)
  }
}

/** 标题输入超限检测：在用户已输入 50 字时再敲键 → 提示 */
function handleTitleKeydown(e: KeyboardEvent) {
  if (form.title.length >= TITLE_MAX) {
    // 允许功能键（退格、删除、方向键、Ctrl/Command 组合键等）
    const isControl = e.ctrlKey || e.metaKey || e.altKey
    const isFunctional = [
      'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight',
      'ArrowUp', 'ArrowDown', 'Home', 'End', 'Tab', 'Escape',
    ].includes(e.key)
    if (!isControl && !isFunctional) {
      e.preventDefault()
      showLimitReached('title')
    }
  }
}

/** 标题粘贴超长内容时截断 */
function handleTitlePaste(e: ClipboardEvent) {
  e.preventDefault()
  const text = e.clipboardData?.getData('text/plain') || ''
  const allowed = TITLE_MAX - form.title.length
  if (allowed <= 0) {
    showLimitReached('title')
    return
  }
  const inserted = text.slice(0, allowed)
  form.title = form.title + inserted
  if (text.length > allowed) {
    setTimeout(() => showLimitReached('title'), 0)
  }
}

function handlePaste(e: ClipboardEvent) {
  e.preventDefault()
  const text = e.clipboardData?.getData('text/plain') || ''
  const current = plainTextLength.value
  const allowed = CONTENT_MAX - current
  if (allowed <= 0) {
    showLimitReached('content')
    return
  }
  const inserted = text.slice(0, allowed)
  document.execCommand('insertText', false, inserted)
  if (text.length > allowed) {
    setTimeout(() => showLimitReached('content'), 0)
  }
}

/** 内容编辑区主键盘处理器：Ctrl 快捷键 + 字数限制拦截 */
function handleEditorKeydown(e: KeyboardEvent) {
  // 功能键一律放行
  if (['Backspace','Delete','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End','Tab','Escape','Shift'].includes(e.key)) return

  // Ctrl 快捷键处理
  if (e.ctrlKey || e.metaKey) {
    const key = e.key.toLowerCase()
    if (key === 'b') { e.preventDefault(); exec('bold') }
    else if (key === 'i') { e.preventDefault(); exec('italic') }
    else if (key === 'u') { e.preventDefault(); exec('underline') }
    else if (key === 'z' && !e.shiftKey) { e.preventDefault(); exec('undo') }
    else if ((key === 'y') || (key === 'z' && e.shiftKey)) { e.preventDefault(); exec('redo') }
    return
  }

  // 达到字数上限时拦截普通字符输入
  if (plainTextLength.value >= CONTENT_MAX) {
    e.preventDefault()
    showLimitReached('content')
  }
}

/** 拦截中文/富文本输入：达到上限时禁止 input event 生效 */
function handleContentBeforeInput(e: InputEvent) {
  if (plainTextLength.value >= CONTENT_MAX) {
    const insertLen = (e.data?.length || 0)
    // 删除操作不放行（inputType 为 deleteContent*）
    if (e.inputType && e.inputType.startsWith('delete')) return
    // 只阻止"插入"行为
    if (insertLen > 0) {
      e.preventDefault()
      showLimitReached('content')
    }
  }
}

function syncContent() {
  if (!contentEditor.value) return
  form.content = contentEditor.value.innerHTML
  plainTextLength.value = computePlainTextLength(contentEditor.value)
}

/** 计算纯文本字数，排除图片和文件占位符 */
function computePlainTextLength(root: HTMLElement): number {
  let len = 0
  // TreeWalker 遍历文本节点，跳过在 <img> 和 .editor-file 内部的文本
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      let p: HTMLElement | null = node.parentElement
      while (p) {
        // 跳过图片元素（整个 <img> 区域）
        if (p.tagName === 'IMG') {
          return NodeFilter.FILTER_REJECT
        }
        if (p.classList && (p.classList.contains('editor-file-card') || p.classList.contains('editor-image') || p.classList.contains('editor-file'))) {
          return NodeFilter.FILTER_REJECT
        }
        p = p.parentElement
      }
      return NodeFilter.FILTER_ACCEPT
    }
  })
  let node = walker.nextNode() as Text | null
  while (node) {
    const text = node.nodeValue || ''
    if (text.trim()) len += text.length
    node = walker.nextNode() as Text | null
  }
  return len
}

/** 实时同步工具栏高亮状态 */
function updateActiveFormats() {
  if (!contentEditor.value) return
  activeFormats.bold = document.queryCommandState('bold')
  activeFormats.italic = document.queryCommandState('italic')
  activeFormats.underline = document.queryCommandState('underline')
  activeFormats.strikeThrough = document.queryCommandState('strikeThrough')
  activeFormats.justifyLeft = document.queryCommandState('justifyLeft')
  activeFormats.justifyCenter = document.queryCommandState('justifyCenter')
  activeFormats.justifyRight = document.queryCommandState('justifyRight')
  try { activeFormats.blockquote = document.queryCommandValue('formatBlock')?.toLowerCase() === 'blockquote' } catch { /* ignore */ }
}

function saveDraft() {
  if (!form.title && plainTextLength.value === 0) {
    ElMessage.warning('暂无内容可保存')
    return
  }
  localStorage.setItem('post_draft', JSON.stringify({ ...form, plainTextLength: plainTextLength.value }))
  ElMessage.success('草稿已保存')
}

function loadDraft() {
  try {
    const draft = localStorage.getItem('post_draft')
    if (!draft) return
    const data = JSON.parse(draft)
    if (data.title || (data.content && data.content !== '<br>' && data.content.length > 0)) {
      // 显示确认弹窗，避免自动恢复大草稿导致用户困惑
      showConfirm('检测到上次未发布的草稿，是否恢复？', '恢复草稿', 'info').then(() => {
        form.board_id = data.board_id
        form.title = data.title || ''
        form.content = data.content || ''
        nextTick(() => {
          if (contentEditor.value) {
            contentEditor.value.innerHTML = data.content || ''
            syncContent()
          }
        })
        ElMessage.success('已恢复草稿')
      }).catch(() => {
        localStorage.removeItem('post_draft')
      })
    }
  } catch { /* ignore */ }
}

onMounted(async () => {
  await forumStore.fetchBoards()
  loadDraft()
  // 点击外部关闭板块选择器
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    if (!target.closest('.form-group') || !target.closest('.select-wrap')) {
      showBoardPicker.value = false
    }
  })
})

async function handleSubmit() {
  if (!form.board_id) { ElMessage.warning('请选择板块'); return }
  if (!form.title.trim()) { ElMessage.warning('请输入标题'); return }
  if (plainTextLength.value === 0) { ElMessage.warning('请输入内容'); return }
  if (plainTextLength.value > CONTENT_MAX) {
    ElMessage.warning(`正文字数 ${plainTextLength.value} 超过 ${CONTENT_MAX} 字上限，请删除部分内容`)
    return
  }
  // 提交前再同步一次，确保内容是最新
  syncContent()
  if (plainTextLength.value > CONTENT_MAX) {
    ElMessage.warning(`正文字数 ${plainTextLength.value} 超过 ${CONTENT_MAX} 字上限，请删除部分内容`)
    return
  }
  loading.value = true
  try {
    await forumStore.createPost(form)
    localStorage.removeItem('post_draft')
    ElMessage.success('发帖成功')
    router.push('/')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '发帖失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
.create-post-page {
  max-width: 720px;
  margin: 0 auto;
}

/* Hero */
.hero-section {
  background: #E1F5EE;
  border-radius: 14px;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.hero-icon {
  width: 44px;
  height: 44px;
  background: #1D9E75;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}
.hero-text { flex: 1; }
.hero-title { margin: 0 0 2px; font-size: 16px; font-weight: 600; color: #085041; }
.hero-desc { margin: 0; font-size: 12px; color: #0F6E56; }

/* Form Card */
.post-card {
  background: #fff;
  border: 0.5px solid #d3d1c7;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 12px;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: #F1EFE8;
  position: relative;
}
.accent-bar { width: 6px; height: 20px; border-radius: 3px; flex-shrink: 0; }
.accent-green { background: #1D9E75; }
.card-title { font-size: 14px; font-weight: 600; color: #085041; flex: 1; }
.card-required { font-size: 10px; color: #b4b2a9; }

.post-form { padding: 20px 24px 16px; display: flex; flex-direction: column; gap: 18px; }
.form-group { display: flex; flex-direction: column; gap: 6px; position: relative; }
.form-label { font-size: 12px; font-weight: 500; color: #5f5e5a; }
.required-star { color: #D85A30; }

/* Select */
.select-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: #F1EFE8;
  border: 0.5px solid #d3d1c7;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}
.select-wrap:hover { border-color: #1D9E75; }
.select-value, .select-placeholder { flex: 1; display: flex; align-items: center; gap: 8px; }
.select-text { font-size: 13px; color: #1a1a1a; }
.select-arrow { font-size: 11px; color: #888780; }

.board-tag {
  width: 22px; height: 22px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px; flex-shrink: 0;
}
.board-tag-blue { background: #378ADD; color: #fff; }
.board-tag-pink { background: #D4537E; color: #fff; }
.board-tag-green { background: #639922; color: #fff; }
.board-tag-amber { background: #BA7517; color: #fff; }
.board-tag-coral { background: #D85A30; color: #fff; }
.board-tag-purple { background: #7F77DD; color: #fff; }
.board-tag-gray { background: #888780; color: #fff; }

.board-picker {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 50;
  background: #fff; border: 0.5px solid #d3d1c7; border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  padding: 6px; margin-top: 2px;
}
.board-option {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 8px;
  cursor: pointer; transition: background 0.15s;
}
.board-option:hover { background: #F1EFE8; }
.board-option.selected { background: #E1F5EE; }
.board-option-info { flex: 1; }
.board-option-name { font-size: 13px; font-weight: 500; color: #1a1a1a; }
.board-option-desc { font-size: 11px; color: #888780; }
.check-mark { color: #1D9E75; font-weight: 600; font-size: 14px; }

/* Form Inputs */
.form-input {
  width: 100%;
  padding: 10px 14px;
  background: #F1EFE8;
  border: 0.5px solid #d3d1c7;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  font-family: inherit;
}
.form-input:focus { border-color: #1D9E75; background: #fff; }

.char-count {
  position: absolute; right: 10px; bottom: 8px;
  font-size: 10px; color: #b4b2a9; pointer-events: none;
}

/* Editor Toolbar */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 6px 8px;
  background: #F1EFE8;
  border: 0.5px solid #d3d1c7;
  border-radius: 8px 8px 0 0;
  flex-wrap: wrap;
}
.toolbar-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 30px; height: 26px;
  border: none; background: transparent;
  border-radius: 4px; cursor: pointer;
  font-size: 12px; color: #5f5e5a;
  transition: all 0.15s; font-family: inherit;
}
.toolbar-btn:hover { background: #fff; color: #1a1a1a; }
.toolbar-btn.active { background: #fff; color: #1D9E75; border: 0.5px solid #1D9E75; }
.toolbar-btn b { font-weight: 700; }
.toolbar-btn i { font-style: italic; }
.toolbar-btn u, .toolbar-btn s { text-decoration: underline; }
.toolbar-btn s { text-decoration: line-through; }
.toolbar-divider {
  width: 0.5px; height: 18px; background: #d3d1c7; margin: 0 4px; flex-shrink: 0;
}

/* 富文本编辑区 */
.form-content-editor {
  width: 100%;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  padding: 14px 16px;
  background: #F1EFE8;
  border: 0.5px solid #d3d1c7;
  border-top: none;
  border-radius: 0 0 8px 8px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  font-family: inherit;
  line-height: 1.7;
}
.form-content-editor:focus { border-color: #1D9E75; background: #fff; }
.form-content-editor:empty::before {
  content: attr(data-placeholder);
  color: #b4b2a9;
  pointer-events: none;
}
.form-content-editor :deep(b), .form-content-editor :deep(strong) { font-weight: 700; }
.form-content-editor :deep(i), .form-content-editor :deep(em) { font-style: italic; }
.form-content-editor :deep(u) { text-decoration: underline; }
.form-content-editor :deep(s), .form-content-editor :deep(strike) { text-decoration: line-through; }
.form-content-editor :deep(h2) { font-size: 18px; font-weight: 600; margin: 8px 0; }
.form-content-editor :deep(p) { margin: 4px 0; }
.form-content-editor :deep(blockquote) {
  border-left: 3px solid #1D9E75;
  padding: 4px 12px;
  margin: 8px 0;
  color: #5f5e5a;
  background: #fff;
}
.form-content-editor :deep(ul), .form-content-editor :deep(ol) {
  padding-left: 24px; margin: 6px 0;
}
.form-content-editor :deep(a) { color: #1D9E75; text-decoration: underline; }

/* 图片卡片 */
.form-content-editor :deep(.editor-image) {
  display: inline-flex; align-items: center; justify-content: center;
  border: 0.5px solid #d3d1c7; border-radius: 10px;
  padding: 0; margin: 6px 4px;
  background: #F1EFE8;
  vertical-align: top;
  width: 180px; height: 130px;
  overflow: hidden;
  user-select: none;
  cursor: default;
}
.form-content-editor :deep(.editor-image-thumb) {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
  background: #fff;
  pointer-events: none;
}
.form-content-editor :deep(.editor-image-info) {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px 2px 0;
}
.form-content-editor :deep(.editor-image-name) {
  font-size: 10px; color: #5f5e5a;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  max-width: 130px;
}
.form-content-editor :deep(.editor-image-size) {
  font-size: 9px; color: #b4b2a9;
  flex-shrink: 0;
}
/* 文件卡片 */
.form-content-editor :deep(.editor-file-card) {
  display: inline-flex; align-items: center; gap: 8px;
  border: 0.5px solid #d3d1c7; border-radius: 10px;
  padding: 6px 10px 6px 14px; margin: 4px;
  background: #F1EFE8;
  vertical-align: middle;
  position: relative;
  overflow: hidden;
  user-select: none;
  cursor: default;
}
.form-content-editor :deep(.editor-file-bar) {
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 4px;
  border-radius: 10px 0 0 10px;
}
.form-content-editor :deep(.editor-file-icon) {
  width: 32px; height: 32px;
  border-radius: 6px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}
.form-content-editor :deep(.editor-file-body) {
  display: flex; flex-direction: column;
  min-width: 0;
}
.form-content-editor :deep(.editor-file-name) {
  font-size: 12px; font-weight: 500; color: #1a1a1a;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  max-width: 140px;
}
.form-content-editor :deep(.editor-file-meta) {
  font-size: 10px; color: #888780;
  margin-top: 1px;
}

.toolbar-btn-text {
  font-size: 13px !important;
  font-weight: 500;
  width: 32px;
}

.input-limit {
  border-color: #D85A30 !important;
  background: #FAF3F0 !important;
}

.input-limit:focus {
  border-color: #D85A30 !important;
}

.editor-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}
.editor-hint { font-size: 10px; color: #b4b2a9; }

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 4px;
}
.pill-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 8px 20px; border-radius: 20px;
  font-size: 13px; border: 0.5px solid #d3d1c7;
  cursor: pointer; transition: all 0.15s ease;
  background: #fff; color: #5f5e5a; font-family: inherit;
}
.pill-btn:hover { border-color: #1D9E75; color: #1D9E75; }
.pill-btn-primary { background: #1D9E75; color: #fff; border-color: #1D9E75; }
.pill-btn-primary:hover { background: #0F6E56; border-color: #0F6E56; color: #fff; }
.pill-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.footer-tip {
  text-align: center; font-size: 11px; color: #b4b2a9;
  padding: 8px 0 20px;
}
</style>
