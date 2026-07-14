# 🩸 糖尿病记录工具 (Diabetes Tracker)

一个为糖尿病患者设计的个人健康记录 Web 应用，支持在极空间 NAS 等设备上通过 Docker 部署，全家多设备访问，数据集中存储。

## ✨ 核心功能

| 模块 | 功能 |
|------|------|
| 🍽️ 饮食记录 | 记录每餐食物、热量、进食顺序、餐后血糖 |
| 🏃 运动记录 | 记录运动类型/时长/强度、运动前后血糖、防低血糖措施 |
| 📊 血糖记录 | 空腹/餐后1h/餐后2h/睡前血糖追踪 |
| 💊 用药记录 | 药品快捷选择、自定义快捷按钮、CSV 导出、用药汇总统计 |
| 🏥 随访记录 | 体重、腰围、糖化血红蛋白(HbA1c) 定期追踪 |
| 🎯 目标管理 | 个性化体重和血糖目标设定 |
| 🌓 主题切换 | 亮色/暗色模式，自动记忆偏好 |
| 📱 移动端优化 | 响应式布局，手机端完美显示 |
| ↕️ 标签拖拽 | 标签页支持拖拽排序，偏好自动保存 |

## 🚀 快速部署（Docker Compose）

```bash
# 1. 克隆仓库
git clone https://github.com/mclarenlm/diabetes-tracker-nas-app.git
cd diabetes-tracker-nas-app

# 2. 启动服务
docker compose up -d

# 3. 访问
# 浏览器打开 http://你的NAS_IP:5088
```

## 📦 文件说明

```
diabetes/
├── app.py              # Flask 后端，SQLite 数据库 + REST API
├── page.html           # 单页前端（内嵌 CSS + JS）
├── Dockerfile          # Docker 镜像构建文件
├── docker-compose.yml  # Docker Compose 编排配置
└── data/               # SQLite 数据目录（Docker volume 挂载，自动创建）
    └── diabetes.db
```

## ⚙️ 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `DB_PATH` | `/app/data/diabetes.db` | SQLite 数据库路径 |
| `TZ` | `Asia/Shanghai` | 时区设置 |

修改 `docker-compose.yml` 中的端口映射（默认 `5088:5000`）和数据卷路径即可自定义。

## 🔧 技术栈

- **后端**：Python 3.11 + Flask + Gunicorn
- **数据库**：SQLite 3
- **前端**：纯 HTML/CSS/JS（无框架依赖）
- **部署**：Docker + Docker Compose

## 🔄 更新部署

```bash
git pull
docker compose down
docker compose up -d --build
```

## 🔒 部署安全加固

- **非 root 运行**：Dockerfile 已创建 `appuser` 并 `USER appuser`，容器不再以 root 权限运行。
- **健康检查**：`docker-compose.yml` 配置了 `healthcheck`，定期访问 `/api/profile`，Flask 假死时 Docker 可自动重启。
- **依赖锁定**：依赖集中在 `requirements.txt`，版本可复现，便于 CI/CD。
- **Gunicorn 调优**：worker 数按 CPU 核心数自适应（上限 8），并设 `--timeout 120` 防止备份/恢复大数据量时请求超时。
- **备份防注入**：备份/恢复仅允许 `ALLOWED_TABLES` 白名单内的表，杜绝 SQL 注入。

## 📝 License

MIT
