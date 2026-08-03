import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/types/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/types/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
        silenceDeprecations: ['legacy-js-api', 'import', 'global-builtin'],
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    // 允许内网穿透 / 隧道访问的公网域名（Vite 5+ 安全机制）
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '.frp-ski.com',       // skfrp 内网穿透域名
      '.frp.com',
      '.cpolar.cn',          // cpolar 域名
      '.cpolar.io',
      '.frp.run',
      '.natfrp.com',
      '.nps.local',
      '.ngrok-free.app',   // ngrok 域名
      '.ngrok.io',
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          element: ['element-plus', '@element-plus/icons-vue'],
        },
      },
    },
  },
})
