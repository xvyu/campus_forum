import { ElMessageBox } from 'element-plus'

/**
 * @param message - 弹窗提示文本
 * @param title - 弹窗标题
 * @param type - 'confirm' (绿) | 'danger' (红) | 'info' (蓝)
 * @param detail - 底部附加信息卡文本（可选，仅 danger 类型时显示效果最佳）
 */
export function showConfirm(
  message: string,
  title: string,
  type: 'confirm' | 'danger' | 'info' = 'confirm',
  detail?: string,
): Promise<any> {
  const iconMap: Record<string, string> = {
    confirm: '?',
    danger: '!',
    info: 'i',
  }
  const icon = iconMap[type] || '?'

  // 构建自定义 message HTML
  let html = `<div class="campus-confirm-body">
    <div class="campus-confirm-icon campus-confirm-icon--${type}">${icon}</div>
    <div class="campus-confirm-text">
      <div class="campus-confirm-title">${escapeHtml(title)}</div>
      <div class="campus-confirm-msg">${escapeHtml(message)}</div>
    </div>
  </div>`

  // 附加信息卡（有 detail 参数时显示）
  if (detail) {
    html += `<div class="campus-confirm-detail">${escapeHtml(detail)}</div>`
  }

  return ElMessageBox.confirm(html, '', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: type === 'danger' ? '删除' : '确定',
    cancelButtonText: '取消',
    type: null as any,
    customClass: `campus-confirm-dialog campus-confirm--${type}`,
    showClose: false,
    closeOnClickModal: false,
    distinguishCancelAndClose: true,
  })
}

function escapeHtml(s: string): string {
  if (!s) return ''
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}
