#!/bin/bash

echo "🚀 Starting PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "✅ PostgreSQL started!"

echo "🚀 Activating virtual environment..."
source /home/ec2-user/my_project/.venv/bin/activate

echo "🚀 Starting Flask server..."
nohup python /home/ec2-user/my_project/app/server.py > flask.log 2>&1 &

echo "🚀 Starting Celery worker..."
nohup celery -A app.tasks worker --loglevel=info > celery.log 2>&1 &

echo "✅ All services started!"

chmod +x scripts/start_services.sh
./scripts/start_services.sh