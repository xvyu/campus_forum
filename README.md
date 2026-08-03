# 校园匿名社交论坛（树洞）

> 校园树洞 - 让每个学生都能匿名说出心声

![V0.1](https://img.shields.io/badge/version-0.1.0-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Python](https://img.shields.io/badge/python-3.10-blue) ![Vue](https://img.shields.io/badge/vue-3.4-brightgreen) ![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen)

## 项目简介

校园匿名社交论坛（树洞）是一个**强隐私、高互动、多租户可扩展**的 Web 应用，专为高校学生设计。

**核心特性**：
- 🔒 **完全匿名**：学号↔匿名 ID 完全解耦，每次发帖使用随机马甲（如"风旁345"），AES-256 字段加密
- 🏫 **校园白名单**：仅限 QQ 邮箱 + 学号注册（试点校 bjtu.edu.cn）
- 💬 **8 大板块**：学习/情感/生活/吐槽/表白/兼职/失物/二手
- 👍 **互动丰富**：点赞/评论/无限层楼中楼/收藏/马甲刷新/马甲切换
- 🔍 **智能搜索**：标题搜索 + 关键词高亮 + 热门词实时统计 + 板块筛选 + 排序
- 🛡️ **安全合规**：敏感词 DFA + 图形/邮箱双验证码 + 限流 + 密码重置

## 技术栈

| 层级 | 技术 | 版本 |
|---|---|---|
| 前端 | Vue 3 + Vite 5 + Element Plus + Pinia | 3.4 / 5 / 2.7 / 2 |
| 后端 | Flask + SQLAlchemy + PyMySQL + Redis | 3.0 / 3.1 / 1.1 / 7 |
| 数据库 | MySQL | 8.0 |
| 认证 | Flask-Session + JWT 双通道 | - |
| 部署 | Docker Compose（占位） | - |

## 目录结构

```
campus_forum/
├── backend/                     ← Flask 后端
│   ├── app/
│   │   ├── blueprints/          ← 9 个蓝图
│   │   │   ├── auth.py          # 注册/登录/登出/验证码/忘记密码
│   │   │   ├── post.py          # 发帖/列表/详情/点赞/搜索/排行/热词
│   │   │   ├── comment.py       # 评论 + 无限层楼中楼 + 评论点赞
│   │   │   ├── board.py         # 板块列表/详情
│   │   │   ├── user.py          # 个人中心/马甲管理/我的记录
│   │   │   ├── favorite.py      # 收藏/取消收藏/收藏状态/我的收藏
│   │   │   ├── admin.py         # 管理后台（帖子/评论/用户/统计/快照）
│   │   │   ├── notification.py  # 通知（预留）
│   │   │   └── common.py        # 健康检查/版本
│   │   ├── models/              # ORM 模型
│   │   │   ├── user.py          # School / User / AnonymousIdMapping / Favorite
│   │   │   └── post.py          # Board / Post / Comment / PostDeleteSnapshot
│   │   ├── utils/               # crypto/bcrypt/captcha/email/ratelimit/sensitive/auth_token
│   │   ├── middleware/          # 中间件（预留）
│   │   ├── config.py            # 环境配置（开发/测试/生产）
│   │   ├── extensions.py        # db/cors/session/redis 单例
│   │   ├── errors.py            # 统一错误码 + 业务异常
│   │   └── response.py          # 统一响应格式
│   ├── tests/                   # pytest（19 个用例）
│   ├── scripts/                 # init_db.py + SQL 分片
│   ├── requirements.txt
│   ├── .env.example             # 环境变量模板
│   ├── run.py                   # 启动入口
│   └── README.md
├── frontend/                    ← Vue 3 前端
│   ├── src/
│   │   ├── views/               # 10 个页面
│   │   ├── components/          # AppHeader / CommentNode
│   │   ├── stores/              # user / forum / index
│   │   ├── api/                 # axios 拦截器
│   │   └── router/              # 路由 + 标题
│   ├── package.json
│   ├── vite.config.ts           # 代理 + allowedHosts
│   └── .env.development
├── docs/                        ← 项目文档
├── docker-compose.yml           # 占位
└── README.md                    ← 本文件
```

## 前端页面功能

| 页面 | 功能 |
|---|---|
| **首页** `Home.vue` | 热门板块 / 3 Tab 榜单（最新热帖·⭐收藏·👁最多浏览）/ 热词 / 搜索入口 |
| **登录** `Login.vue` | 学号+密码+图形验证码 / 忘记密码 |
| **注册** `Register.vue` | 学号+QQ邮箱+图形码+邮箱码 |
| **帖子详情** `PostDetail.vue` | 内容 / 爱心点赞 / 收藏 / 无限层楼中楼评论 |
| **发帖** `CreatePost.vue` | 选板块 / 标题 / 内容 |
| **搜索** `Search.vue` | 结果列表 / 最新·最多浏览量排序 / 板块筛选 / 热词实时刷新 |
| **个人中心** `Profile.vue` | 4 统计卡 / 6 Tab（帖子/评论/收藏/马甲/数据）/ 活跃度图 |
| **板块详情** `BoardDetail.vue` | 板块内帖子列表 |
| **管理后台** `Admin.vue` | 帖子审核 / 恢复 / 硬删 / 用户列表 / 统计 |
| **404** `NotFound.vue` | 页面不存在 |

## 后端数据模型（9 张表）

| 表 | 说明 | 关键字段 |
|---|---|---|
| `pf_schools` | 学校 | code/name/email_suffix |
| `pf_users` | 用户 | student_id/email/nickname/role/comment_count/liked_* |
| `pf_anonymous_id_mapping` | 匿名马甲 | anonymous_name/is_default/is_active |
| `pf_boards` | 板块 | slug/name/description/icon/post_count |
| `pf_posts` | 帖子 | view/like/dislike/comment/favorite_count、is_top/is_essence |
| `pf_comments` | 评论 | parent_id（无限层）/reply_to_user_id/like_count |
| `pf_favorites` | 收藏 | user_id/post_id |
| `pf_post_delete_snapshots` | 删除快照 | 管理后台恢复用 |

## 快速开始

### 1. 后端启动

```bash
# 1) 激活虚拟环境（必须用项目 venv）
cd backend
..\.venv\Scripts\activate

# 2) 安装依赖
pip install -r requirements.txt

# 3) 复制环境变量模板
copy .env.example .env
# 编辑 .env：MySQL / Redis / SMTP_ACCOUNTS（qq1:pwd1,qq2:pwd2 轮发）

# 4) 初始化数据库（MySQL 建库后）
python scripts/init_db.py

# 5) 启动 Flask
python run.py
# 访问 http://localhost:5000/api/health
```

### 2. 前端启动

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 3. 测试

```bash
cd backend
..\.venv\Scripts\activate
pytest tests/ -v
# 19 passed（含 23 步 E2E：注册→登录→发帖→评论→楼中楼→点赞→删除→登出）
```

### 4. 内网穿透（公网访问）

前端已适配穿透场景：
1. `vite.config.ts` 已配置 `allowedHosts`（frp/cpolar/ngrok 等域名）
2. 后端 CORS 已加隧道域名白名单（`extensions.py`）
3. 前端 `VITE_API_BASE_URL=/api` 走 Vite 代理

**操作**：穿透工具将**本地端口 5173** 映射到公网即可。
**注意**：关闭前后端进程后，穿透地址将无法访问（穿透≠托管）。

## API 概览

### 认证 `auth.py`
| 方法 | 端点 | 说明 |
|---|---|---|
| GET | `/api/auth/captcha` | 图形验证码（base64） |
| POST | `/api/auth/send-code` | 发送邮箱验证码 |
| POST | `/api/auth/register` | 注册（学号+QQ邮箱+双验证码） |
| POST | `/api/auth/login` | 登录（返回 JWT） |
| POST | `/api/auth/logout` | 登出 |
| GET | `/api/auth/me` | 当前用户信息 |
| POST | `/api/auth/reset-password/send-code` | 忘记密码 - 发重置码 |
| POST | `/api/auth/reset-password` | 重置密码 |

### 帖子 `post.py`
| 方法 | 端点 | 说明 |
|---|---|---|
| GET | `/api/posts?kw=&sort=&board_id=` | 列表（kw 标题搜索 / sort: latest·hot·view·time） |
| POST | `/api/posts` | 发帖 |
| GET | `/api/posts/ranking` | 排行榜（favorite/view 等） |
| GET | `/api/posts/hot-keywords` | 热门搜索词（实时统计） |
| GET | `/api/posts/search-suggest?prefix=` | 搜索建议（自动补全） |
| GET | `/api/posts/trending` | 首页 trending |
| GET | `/api/posts/<id>` | 详情 |
| POST | `/api/posts/<id>/like` | 点赞/取消点赞 |
| DELETE | `/api/posts/<id>` | 删除 |

### 评论 `comment.py`
| 方法 | 端点 | 说明 |
|---|---|---|
| POST | `/api/comments` | 评论（parent_id → 楼中楼） |
| DELETE | `/api/comments/<id>` | 删除 |
| POST | `/api/comments/<id>/like` | 点赞评论 |

### 用户 `user.py`
| 方法 | 端点 | 说明 |
|---|---|---|
| GET | `/api/users/me` | 个人中心（全维度统计） |
| GET | `/api/users/me/activity` | 本周活跃度（7 天） |
| GET | `/api/users/me/likes` | 收到的点赞 |
| PUT | `/api/users/me/nickname` | 修改昵称 |
| POST | `/api/users/me/refresh-masquerade` | 刷新马甲 |
| POST | `/api/users/me/set-default-masquerade` | 切换马甲 |
| GET | `/api/users/my-posts` | 我的帖子 |
| GET | `/api/users/my-comments` | 我的评论 |
| POST | `/api/users/my-posts/batch-hide` | 批量隐藏记录 |

### 收藏 `favorite.py`
| 方法 | 端点 | 说明 |
|---|---|---|
| POST | `/api/favorites/posts/<id>` | 收藏/取消收藏（toggle） |
| GET | `/api/favorites/posts/<id>/status` | 收藏状态 |
| GET | `/api/favorites/my` | 我的收藏列表 |

### 管理后台 `admin.py`
| 方法 | 端点 | 说明 |
|---|---|---|
| GET | `/api/admin/posts` | 帖子列表（状态筛选） |
| GET | `/api/admin/posts/<id>` | 详情（含快照） |
| POST | `/api/admin/posts/<id>/restore` | 恢复删除 |
| DELETE | `/api/admin/posts/<id>/hard-delete` | 彻底删除 |
| DELETE | `/api/admin/posts/<id>` | 软删除 |
| GET | `/api/admin/posts/<id>/snapshot` | 删除快照 |
| DELETE | `/api/admin/comments/<id>` | 删除评论 |
| GET | `/api/admin/users` | 用户列表 |
| GET | `/api/admin/stats` | 全站统计 |

## 统一响应格式

```json
{ "code": 0, "message": "ok", "data": null }
```

错误码规则：`1xxx` 通用 / `2xxx` 认证 / `3xxx` 业务 / `4xxx` 后台 / `5xxx` 第三方

## 当前进度（V0.1）

### ✅ 已完成
- 后端：9 蓝图 + 19/19 测试 + 9 张表
- 前端：10 页面 + 递归评论组件 + 搜索页
- 功能：认证/发帖/评论/楼中楼/点赞/收藏/搜索/个人中心/马甲/管理后台/忘记密码
- 内网穿透适配

### ⏳ 待办
- V01-T32 Docker Compose 部署（占位文件已建）
- V0.3 WebSocket 实时推送
- V0.4 对象存储 + 学校切换

## 文档

- [PRD-产品需求文档.md](docs/PRD-产品需求文档.md)
- [Roadmap-产品路线图.md](docs/Roadmap-产品路线图.md)
- [Architecture-系统架构设计文档.md](docs/Architecture-系统架构设计文档.md)
- [ER-Diagram-数据库设计文档.md](docs/ER-Diagram-数据库设计文档.md)
- [TaskList-任务分解清单.md](docs/TaskList-任务分解清单.md)

## 许可

MIT License - 详见 [LICENSE](LICENSE)
