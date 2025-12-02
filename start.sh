#!/bin/bash

# Pokemon GO Tracker - Quick Start Script
# 포켓몬GO 트래커 빠른 시작 스크립트

echo "🎮 Pokemon GO Tracker - Starting..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사합니다..."
    cp .env.example .env
    echo "✅ .env 파일이 생성되었습니다. SendGrid API 키를 입력하세요!"
    echo ""
    echo "편집: nano .env"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker가 실행되지 않았습니다. Docker를 시작하세요."
    exit 1
fi

echo "🐳 Docker Compose로 서비스 시작 중..."
docker-compose up -d

echo ""
echo "⏳ 서비스가 시작될 때까지 기다리는 중..."
sleep 10

echo ""
echo "🗄  데이터베이스 마이그레이션 실행 중..."
docker-compose exec -T backend alembic upgrade head

echo ""
echo "✅ 모든 서비스가 시작되었습니다!"
echo ""
echo "📱 접속 주소:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 로그 확인: docker-compose logs -f"
echo "🛑 중지: docker-compose down"
echo ""
echo "즐거운 포켓몬GO 하세요! ⚡️"
