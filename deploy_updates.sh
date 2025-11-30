#!/bin/bash
# Deploy updated files to Linux server

SERVER_USER="root"
SERVER_HOST="your-server-ip"  # แก้เป็น IP ของ server
SERVER_PATH="/opt/thai-news-scraper/thai-news-scraper"

echo "🚀 Deploying updates to server..."

# Upload updated files
echo "📤 Uploading app/api/sources.py..."
scp app/api/sources.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/app/api/

echo "📤 Uploading app/api/__init__.py..."
scp app/api/__init__.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/app/api/

echo "📤 Uploading app/api/articles.py..."
scp app/api/articles.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/app/api/

echo "📤 Uploading app/main.py..."
scp app/main.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/app/

echo "📤 Uploading sources.yaml..."
scp sources.yaml ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/

echo "✅ Files uploaded successfully!"

# Restart Docker container
echo "🔄 Restarting Docker container..."
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${SERVER_PATH} && docker-compose restart api"

echo "✅ Deployment complete!"
echo "📊 Check logs: ssh ${SERVER_USER}@${SERVER_HOST} 'docker logs -f thai-news-api'"
