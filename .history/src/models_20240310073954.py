# SQLAlchemy models
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserDB(Base):  # Rename the SQLAlchemy model to differentiate from Pydantic model
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
        recommendations = relationship('RecomendacionDB', back_populates='user')

class RecomendacionDB(Base):  # Rename for clarity
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String)
    iid = Column(String)
    r_ui = Column(Float)
    est = Column(Float)
    details = Column(String)

# Pydantic models for request and response data validation
from pydantic import BaseModel

class User(BaseModel):  # This is for FastAPI interaction, not for database
    email: str
    password: str

class Recomendacion(BaseModel):
    uid: str
    iid: str
    r_ui: float
    est: float
    details: dict