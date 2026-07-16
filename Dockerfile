# ===== 阶段 1：构建 Uni-app H5 产物 =====
FROM node:22-alpine AS builder

WORKDIR /src
COPY diabetes-tracker-uniapp/package.json .
RUN npm install --registry https://registry.npmmirror.com

COPY diabetes-tracker-uniapp/ .
RUN npm run build:h5

# ===== 阶段 2：Python Flask 生产镜像 =====
FROM python:3.11-slim

WORKDIR /app

# 后端依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY page.html .

# Uni-app 前端产物（从构建阶段复制）
COPY --from=builder /src/dist/build/h5 /app/static/spa

# 创建非 root 用户 + 安装 gosu
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

# entrypoint
RUN printf '#!/bin/sh\nmkdir -p /app/data\nchown -R appuser:appuser /app/data\nexec gosu appuser "$@"\n' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

ENV DB_PATH=/app/data/diabetes.db
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_WORKERS=2
ENV GUNICORN_TIMEOUT=120

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD sh -c 'W=${GUNICORN_WORKERS:-$(( $(nproc 2>/dev/null || echo 1) * 2 + 1 ))}; [ "$W" -gt 8 ] && W=8; exec gunicorn --workers "$W" --timeout "${GUNICORN_TIMEOUT:-120}" -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app'
