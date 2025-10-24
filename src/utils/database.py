from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("sqlite:///sqlite.db")

SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    pass



async def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

