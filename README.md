# 糖尿病记录工具 (Diabetes Tracker)

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
git clone https://github.com/mclarenlm/diabetes.git
cd diabetes
mkdir -p data
docker compose up -d
```

访问 `http://你的NAS_IP:5088`

## 📦 文件说明

```
diabetes/
├── app.py              # Flask 后端，SQLite + REST API
├── page.html           # 单页前端
├── Dockerfile          # Docker 镜像构建
├── docker-compose.yml  # 编排配置
└── data/               # 数据库持久化目录
```

## ⚙️ 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_PATH` | `/app/data/diabetes.db` | 数据库路径 |
| `TZ` | `Asia/Shanghai` | 时区 |

## 🔧 技术栈

Python 3.11 + Flask + Gunicorn / SQLite / 纯 HTML/CSS/JS / Docker

## 🔄 更新部署

```bash
git pull && docker compose down && docker compose up -d --build
```

## ⚠️ 健康声明

本工具仅用于个人健康数据记录，**不能替代专业医疗建议**。所有用药、饮食、运动方案请遵医嘱。

## 📝 License

MIT
