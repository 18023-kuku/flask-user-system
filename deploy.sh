#!/bin/bash

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 运行测试
echo "Running tests..."
pytest test_app.py

# 构建 Docker 镜像
echo "Building Docker image..."
docker-compose build

# 启动容器
echo "Starting container..."
docker-compose up -d

echo "Deployment completed!"
