from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "mysql+pymysql://sql12804543:q7nEDGs7uA@sql12.freesqldatabase.com/sql12804543?charset=utf8mb4"), pool_size=10, max_overflow=20, pool_recycle=1800)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass



async def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

