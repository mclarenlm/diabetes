FROM python:3.11-slim

WORKDIR /app

# 依赖管理：从 requirements.txt 安装，便于版本锁定与 CI/CD
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY page.html .

# 创建非 root 用户 + 安装 gosu（用于 entrypoint 降权）
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

# entrypoint：以 root 修复挂载目录权限，再降权到 appuser 运行
RUN printf '#!/bin/sh\nmkdir -p /app/data\nchown -R appuser:appuser /app/data\nexec gosu appuser "$@"\n' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

ENV DB_PATH=/app/data/diabetes.db
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_WORKERS=1
ENV GUNICORN_TIMEOUT=120

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
# 注意：SQLite 不支持多进程并发写入，强制单 worker + 多线程模式
# 多 worker 会产生 "database is locked" 错误
# --threads 2 处理并发请求时互不阻塞
CMD exec gunicorn --workers 1 --threads 2 --timeout "${GUNICORN_TIMEOUT:-120}" -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
