#!/bin/bash

IMAGE_NAME="aligenie:latest"
CONTAINER_NAME="tmallgenie"
ENV_FILE="../.env"
HOST_PORT=8000
CONTAINER_PORT=8000

# =========================
# 从 .env 文件安全读取 WEATHER_API_KEY
# =========================
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env 文件不存在: $ENV_FILE"
    exit 1
fi

# 忽略空行和注释
WEATHER_API_KEY=$(grep -E '^\s*WEATHER_API_KEY\s*=' "$ENV_FILE" | tail -n1 | cut -d '=' -f2- | xargs | tr -d '"')

if [ -z "$WEATHER_API_KEY" ]; then
    echo "ERROR: WEATHER_API_KEY 没有在 $ENV_FILE 中正确配置"
    exit 1
fi

echo "✅ 找到 WEATHER_API_KEY: ${WEATHER_API_KEY:0:4}****（已隐藏）"

# =========================
# 停止旧容器（如果存在）
# =========================
OLD_CONTAINER=$(docker ps -aq -f name=$CONTAINER_NAME || true)
if [ -n "$OLD_CONTAINER" ]; then
    echo "🚨 停止旧容器: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME || true
    echo "🗑 删除旧容器: $CONTAINER_NAME"
    docker rm $CONTAINER_NAME || true
fi

# =========================
# 构建 Docker 镜像
# =========================
echo "📦 构建 Docker 镜像: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

# =========================
# 启动新容器，只传 WEATHER_API_KEY
# =========================
echo "🚀 启动新容器: $CONTAINER_NAME"
docker run -d \
    --name $CONTAINER_NAME \
    -e WEATHER_API_KEY="$WEATHER_API_KEY" \
    -p $HOST_PORT:$CONTAINER_PORT \
    $IMAGE_NAME

echo "✅ 容器启动完成，访问 http://localhost:$HOST_PORT"
