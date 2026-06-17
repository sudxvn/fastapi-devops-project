from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

app = FastAPI(title="Мой DevOps проект")

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "FastAPI + PostgreSQL работает!", "status": "success"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "error"
    return {"db_status": db_status, "service": "running"}

@app.post("/log/{message}")
def add_log(message: str, db: Session = Depends(get_db)):
    log = Log(message=message)
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"id": log.id, "message": log.message, "created_at": log.created_at}

@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(Log).all()
    return logs