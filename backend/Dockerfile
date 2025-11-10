# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/

# 注意：CMD 命令已移至 docker-compose.yml 中，以方便在开发和生产环境中使用不同命令。
# 这里保留 EXPOSE 仅作为文档说明。
EXPOSE 8000