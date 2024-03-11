# SQLAlchemy models
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional, List
import enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import VARCHAR  # Import specific to PostgreSQL

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))
    recommendations = relationship('RecomendacionDB', back_populates='user')
    interacciones = relationship('InteraccionDB', back_populates='user')

class RecommendationStatus(enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    UNDEFINED = None

class RecomendacionDB(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(VARCHAR(50))
    iid = Column(VARCHAR(50))
    r_ui = Column(Float)
    est = Column(Float)
    details = Column(VARCHAR(50))
    user_id = Column(Integer, ForeignKey('users.id'))
    cancion_id = Column(Integer, ForeignKey('songs.id'))

    user = relationship('UserDB', back_populates='recommendations')
    cancion = relationship('CancionDB', back_populates='recomendaciones')
    rating = Column(Float, default=None)
class CancionDB(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    titulo = Column(VARCHAR(400))
    recomendaciones = relationship('RecomendacionDB', back_populates='cancion', )
    interacciones = relationship('InteraccionDB', back_populates='cancion')


class InteraccionDB(Base):
    __tablename__ = 'interactions'

    RecomendacionID = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Ensure this is a foreign key
    cancion_id = Column(Integer, ForeignKey('songs.id'))  # Ensure this is a foreign key
    rating = Column(Float, nullable=True)

    # Update these relationship lines
    user = relationship('UserDB', back_populates='interacciones')
    cancion = relationship('CancionDB', back_populates='interacciones')


class User(BaseModel):
    username: str
    password: str

class Recomendacion(BaseModel):
    id: int
    uid: str
    iid: str
    r_ui: float
    est: float
    details: dict
    rating: Optional[str] = Field(default=None, enum=["positive", "negative", None])


class CancionBase(BaseModel):
    id: int
    titulo: str

class Cancion(CancionBase):
    recomendaciones: List['Recomendacion'] = []

class CancionCreate(BaseModel):
    titulo: str


class Interaccion(BaseModel):
    user_id: int
    cancion_id: int
    rating: float

class InteraccionCreate(BaseModel):
    user_id: int
    cancion_id: int
    rating: float