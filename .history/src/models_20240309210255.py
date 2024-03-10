from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel
from typing import List

class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Recomendacion(BaseModel):
    __tablename__ = "recomendaciones"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String)
    iid = Column(String)
    r_ui = Column(Float)
    est = Column(Float)
    details = Column(String)

