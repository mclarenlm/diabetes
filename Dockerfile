FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask==3.0.0 gunicorn==21.2.0

COPY app.py .
COPY page.html .

RUN mkdir -p /app/data

ENV DB_PATH=/app/data/diabetes.db
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
