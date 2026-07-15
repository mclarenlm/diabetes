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
| `ACCESS_PASSWORD` | 空（关闭） | 设置后开启**访问密码保护**，未登录无法查看/录入任何数据 |
| `SECRET_KEY` | 随机生成 | 用于签名 session；生产环境务必固定，否则容器重启后需重新登录 |
| `SESSION_TIMEOUT` | `86400`（24h） | 登录会话有效期（秒） |

修改 `docker-compose.yml` 中的端口映射（默认 `5088:5000`）和数据卷路径即可自定义。

### 🔐 开启访问密码（强烈建议）

在 `docker-compose.yml` 的 `environment` 中增加：

```yaml
environment:
  - DB_PATH=/app/data/diabetes.db
  - TZ=Asia/Shanghai
  - ACCESS_PASSWORD=你的强密码
  - SECRET_KEY=一段随机字符串（可用 openssl rand -hex 24 生成）
```

开启后：
- 未登录访问页面会显示登录页；所有 API 返回 `401`。
- 登录后浏览器记住会话，可正常使用；右上角出现「🔓 退出」按钮。
- 会话过期时页面会自动弹出登录层，无需刷新。
- 若 NAS 仅局域网使用且已信任网络，可不设；一旦端口暴露到公网，务必设置。

## 🔧 技术栈

- **后端**：Python 3.11 + Flask + Gunicorn
- **数据库**：SQLite 3（WAL 模式 + 性能索引 + 连接池）
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
- **数据库优化**：SQLite WAL 模式 + `busy_timeout=5000` 避免写入锁死；按请求缓存连接，无需手动关闭；7 个性能索引加速常用查询。SQLite 是单写者模型，Gunicorn 强制 `--workers 1 --threads 2`，多并发请求由线程处理。
- **备份防注入**：备份/恢复仅允许 `ALLOWED_TABLES` 白名单内的表，杜绝 SQL 注入。

## 📝 License

MIT
