import os

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/postgres")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Seoul")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
