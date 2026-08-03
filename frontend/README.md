# 校园树洞 · 前端（Vue 3）

## 技术栈

- Vue 3.4 + Composition API + `<script setup>`
- Vite 5 + TypeScript 5
- Element Plus 2.7（按需自动引入）
- Pinia 2 状态管理
- Vue Router 4 路由
- Sass 样式预处理
- Axios HTTP 客户端

## 目录结构

```
frontend/
├── src/
│   ├── api/           # API 客户端封装
│   ├── components/    # 公共组件
│   ├── router/        # 路由
│   ├── stores/        # Pinia stores
│   ├── styles/        # 全局样式
│   ├── types/         # TypeScript 类型
│   ├── views/         # 页面
│   ├── App.vue
│   └── main.ts
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## 启动方式

```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
# 访问 http://localhost:5173

# 3. 构建生产版本
npm run build

# 4. 类型检查
npm run type-check
```

## API 代理

开发环境 Vite 自动代理 `/api` → `http://localhost:5000`，无需配置 CORS。
