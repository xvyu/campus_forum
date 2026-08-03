# 校园树洞 · 后端（Flask）

> Flask 3.0 + Blueprint 模块化 + 工厂模式

## 快速开始

```bash
# 1. 激活你的 Python 3.10.10 虚拟环境
venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. 配置环境变量
copy .env.example .env
# 编辑 .env，填入：
# - DB_PASSWORD（MySQL 密码）
# - SMTP_ACCOUNTS（QQ 邮箱）
# - AES_KEY_BASE64（32 字节 base64 编码）

# 4. 初始化数据库
python scripts/init_db.py
# 输出：✅ 15 tables created, 1 school, 8 boards, 2 admins, 10 sensitive words

# 5. 启动开发服务器
python run.py
```

访问 http://localhost:5000/api/health 验证。

## 目录结构

```
backend/
├── app/
│   ├── __init__.py          ← 工厂函数 create_app()
│   ├── config.py            ← Dev/Prod/Test 配置类
│   ├── extensions.py        ← db/redis/cors/session 实例
│   ├── errors.py            ← 统一错误处理 + 业务异常
│   ├── response.py          ← 统一响应构造器 + ErrorCode 常量
│   ├── blueprints/          ← 7 个业务蓝图
│   ├── services/            ← 业务服务层
│   ├── repositories/        ← 数据访问层
│   ├── models/              ← SQLAlchemy 模型
│   ├── utils/               ← 工具层
│   └── middleware/          ← 中间件
├── tests/
│   ├── conftest.py
│   └── test_smoke.py        ← 6 个烟雾测试
├── scripts/
│   ├── init_db.sql          ← 15 张表 DDL + 种子
│   └── init_db.py           ← 一键执行脚本
├── static/
│   └── uploads/             ← V0.1 本地文件存储
├── venv/                    ← 虚拟环境（不提交）
├── requirements.txt         ← 主依赖
├── requirements-dev.txt     ← 开发依赖
├── .env.example             ← 环境变量模板
├── run.py                   ← 启动入口
└── wsgi.py                  ← Gunicorn 入口
```

## API 端点（V0.1 Day1 已就位）

| 路径 | 方法 | 说明 |
|---|---|---|
| `/api/health` | GET | 健康检查 |
| `/api/version` | GET | 版本信息 |
| `/api/auth/`、`/api/posts/`、`/api/comments/`、`/api/boards/`、`/api/users/`、`/api/notifications/` | GET | 蓝图占位 |

业务接口将在 V01-T04 ~ T14 实现。

## 测试

```bash
pytest tests/ -v
```

## 错误码体系（4 位）

| 段 | 含义 |
|---|---|
| 1xxx | 通用错误（参数/404/500） |
| 2xxx | 认证错误（未登录/Token/权限） |
| 3xxx | 业务错误（敏感词/限流/重复） |
| 4xxx | 后台错误 |
| 5xxx | 第三方错误（邮件/Redis/OSS） |

## 部署

- 开发：`python run.py`
- 生产：`gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app`
- 容器化：Docker Compose（V0.1 T32 引入）
