import os
from dotenv import load_dotenv

load_dotenv()

# AWS RDS PostgreSQL配置
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', '5432')
}

# AI服务URL（在AWS上运行）
AI_SERVER_URL = os.getenv('AI_SERVER_URL', 'http://localhost:8001')

# Redis配置（用于Celery）
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')



