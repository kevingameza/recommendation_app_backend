import sqlite3
import uvicorn
from fastapi import Depends, FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import hashlib
from datetime import datetime
import models 
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List
app = FastAPI()
import uvicorn
models.Base.metadata.create_all(bind=engine)
from joblib import load
import pandas as pd

def cargar_modelo():
    modelo = load('modelo_algo_cosine.joblib')
    return modelo

def generar_recomendaciones( user_id, item_id):
    modelo = cargar_modelo()
    recomendaciones = modelo.predict(user_id, item_id)
    return recomendaciones

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/recomendaciones/{user_id}", response_model=List[models.Recomendacion])
def obtener_recomendaciones(user_id: int, db: Session = Depends(get_db)):
    user_id='user_000370'
    item_id= 'Bad Ischl'
    recomendaciones = generar_recomendaciones(user_id, item_id)
    recomendation = models.Recomendacion(uid=recomendaciones.uid, iid=recomendaciones.iid, r_ui=recomendaciones.r_ui, est=recomendaciones.est, details=recomendaciones.details)
    print(recomendaciones)
    return recomendation

@app.get("/")
def root():
    return {"message": "Fast API in Python"}

@app.post("/signUp/")
def create_user(
    username: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    password = hashlib.sha256(password.encode()).hexdigest()
    user = models.User( username=username, password=password)
    db.add(user)
    db.commit()
    return user

@app.post("/login/")
def login_user(
    username: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    password = hashlib.sha256(password.encode()).hexdigest()
    user = db.query(models.User).filter(models.User.username == username, models.User.password == password).first()
    if user:
        return {"message": "Login Successful"}
    else:
        return {"message": "Invalid Credentials"}

@app.get("/user/")
def get_user(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.get("/user/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user

# Logout
@app.get("/logout/")
def logout_user():
    return {"message": "Logout Successful"}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)