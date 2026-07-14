FROM python:3.11-slim

WORKDIR /app

# 依赖管理：从 requirements.txt 安装，便于版本锁定与 CI/CD
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY page.html .

# 创建非 root 用户，避免容器以 root 权限运行（降低容器逃逸风险）
RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

ENV DB_PATH=/app/data/diabetes.db
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_WORKERS=2
ENV GUNICORN_TIMEOUT=120

EXPOSE 5000

# 以非 root 用户运行
USER appuser

# worker 数按 CPU 核心数自适应（默认 2*核数+1，上限 8），--timeout 防止备份/恢复大数据量时请求卡死
CMD sh -c 'W=${GUNICORN_WORKERS:-$(( $(nproc 2>/dev/null || echo 1) * 2 + 1 ))}; [ "$W" -gt 8 ] && W=8; exec gunicorn --workers "$W" --timeout "${GUNICORN_TIMEOUT:-120}" -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app'
