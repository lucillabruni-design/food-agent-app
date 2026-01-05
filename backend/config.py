import os
from typing import Optional

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# AWS Services Configuration
# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "food-agent-app")
S3_UPLOADS_PREFIX = os.getenv("S3_UPLOADS_PREFIX", "uploads/")

# DynamoDB Configuration
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "food-agent-app")

# Lambda Configuration
LAMBDA_FUNCTION_NAME = os.getenv("LAMBDA_FUNCTION_NAME", "food-agent-processor")

# SQS Configuration
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "food-agent-queue")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./food_agent.db")
DATABASE_ECHO = DEBUG

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Authentication
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

# Food Agent Configuration
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4")
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", 300))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# External APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Cache Configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 3600))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Feature Flags
FEATURE_IMAGE_PROCESSING = os.getenv("FEATURE_IMAGE_PROCESSING", "true").lower() == "true"
FEATURE_RECIPE_GENERATION = os.getenv("FEATURE_RECIPE_GENERATION", "true").lower() == "true"
FEATURE_NUTRITIONAL_ANALYSIS = os.getenv("FEATURE_NUTRITIONAL_ANALYSIS", "true").lower() == "true"

def validate_aws_credentials() -> bool:
    """Validate that AWS credentials are configured."""
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        if ENVIRONMENT == "production":
            raise ValueError("AWS credentials are required in production environment")
        return False
    return True

def get_aws_config() -> dict:
    """Get AWS configuration dictionary for boto3."""
    return {
        "region_name": AWS_REGION,
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    }
