import sqlite3
import uvicorn
import json
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
from fastapi import HTTPException
from typing import List
# Other imports
from sklearn.model_selection import train_test_split
from surprise import KNNBasic
from sklearn.metrics import pairwise_distances
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import numpy as np

modelo = load('modelo_algo_cosine.joblib')


def generar_recomendaciones( user_id, item_id, rating):
    recomendaciones = modelo.predict(user_id, item_id, rating)
    return recomendaciones

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/generaterecommendation/{user_id}", response_model=models.Recomendacion)
def obtener_recomendaciones(
    user_id: str,
    item_id: str = Body(..., embed=True),
    rating: float = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    user = db.query(models.UserDB).filter(models.UserDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recomendaciones = generar_recomendaciones(user.id, item_id, rating)

    details_str = json.dumps(recomendaciones.details)

    db_recomendation = models.RecomendacionDB(
        uid=recomendaciones.uid,
        iid=recomendaciones.iid,
        r_ui=recomendaciones.r_ui,
        est=recomendaciones.est,
        details=details_str
    )
    db.add(db_recomendation)
    db.commit()

    return models.Recomendacion(
        uid=db_recomendation.uid,
        iid=db_recomendation.iid,
        r_ui=db_recomendation.r_ui,
        est=db_recomendation.est,
        details=json.loads(db_recomendation.details)
    )

@app.get("/")
def root():
    return {"message": "Fast API in Python"}

@app.post("/signup/")
def create_user(
    user_data: models.User,
    db: Session = Depends(get_db)
):
    user_db = models.UserDB(username=user_data.username, password=user_data.password)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@app.post("/login/")
def login_user(
    username: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username, models.User.password == password).first()
    if user:
        return {"message": "Login Successful"}
    else:
        return {"message": "Invalid Credentials"}

@app.get("/user/")
def get_user(db: Session = Depends(get_db)):
    users = db.query(models.UserDB).all()
    return users

@app.get("/user/{user_id}")
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user

# Logout
@app.get("/logout/")
def logout_user():
    return {"message": "Logout Successful"}

@app.get("/user/{user_id}/recommendations", response_model=List[models.Recomendacion])
def get_user_recommendations(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(models.UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.recommendations

@app.get("/recommendations/", response_model=List[models.Recomendacion])
def get_all_recommendations(db: Session = Depends(get_db)):
    recommendations = db.query(models.RecomendacionDB).all()
    return recommendations


@app.get("/recommendations/{recommendation_id}", response_model=models.Recomendacion)
def get_recommendation_by_id(recommendation_id: int, db: Session = Depends(get_db)):
    recommendation = db.query(models.RecomendacionDB).filter(models.RecomendacionDB.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)