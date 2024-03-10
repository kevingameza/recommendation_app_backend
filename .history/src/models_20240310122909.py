# SQLAlchemy models
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional
import enum

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    recommendations = relationship('RecomendacionDB', back_populates='user')


class RecommendationStatus(enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    UNDEFINED = None

class RecomendacionDB(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String)
    iid = Column(String)
    r_ui = Column(Float)
    est = Column(Float)
    details = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('UserDB', back_populates='recommendations')
    rating: Optional[str] = Field(default=None, example="positive", enum=["positive", "negative", None])


class User(BaseModel):  # This is for FastAPI interaction, not for database
    username: str
    password: str

class Recomendacion(BaseModel):
    uid: str
    iid: str
    r_ui: float
    est: float
    details: str
    rating: Optional[str] = Field(default=None, example="positive", enum=["positive", "negative", None])

