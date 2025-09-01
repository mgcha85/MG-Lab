from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from .config import DB_URL

engine: Engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
