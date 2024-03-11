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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    cancion = db.query(models.CancionDB).filter(models.CancionDB.titulo == item_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recomendaciones = generar_recomendaciones(user.id, item_id, rating)


    if isinstance(recomendaciones.details, str):
        details_dict = json.loads(recomendaciones.details)
    else:
        details_dict = recomendaciones.details


    details_json = json.dumps(details_dict)  # Convert dict to JSON string

    db_recomendation = models.RecomendacionDB(
        uid=recomendaciones.uid,
        iid=recomendaciones.iid,
        r_ui=recomendaciones.r_ui,
        est=recomendaciones.est,
        details=details_json,  # Use the JSON string here
        user_id=user.id,
        rating=None,
        cancion_id=cancion.id
    )

    db.add(db_recomendation)
    db.commit()

    return models.Recomendacion(
        id=db_recomendation.id,
        uid=db_recomendation.uid,
        iid=db_recomendation.iid,
        r_ui=db_recomendation.r_ui,
        est=db_recomendation.est,
        details=json.loads(db_recomendation.details),
        cancion_id=db_recomendation.cancion_id
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
    recommendations_db = db.query(models.RecomendacionDB).filter(models.RecomendacionDB.user_id == user_id).all()
    
    recommendations = [
        models.Recomendacion(
            id=recomendacion.id,
            uid=recomendacion.uid,
            iid=recomendacion.iid,
            r_ui=recomendacion.r_ui,
            est=recomendacion.est,
            details=json.loads(recomendacion.details) if recomendacion.details else {},
            rating=recomendacion.rating if isinstance(recomendacion.rating, str) else None  # Asegurar que rating sea una cadena o None
        )
        for recomendacion in recommendations_db
    ]
    return recommendations

@app.get("/recommendations/", response_model=List[models.Recomendacion])
def get_all_recommendations(db: Session = Depends(get_db)):
    recommendations_db = db.query(models.RecomendacionDB).all()
    recommendations = [
        models.Recomendacion(
            id=recomendacion.id,
            uid=recomendacion.uid,
            iid=recomendacion.iid,
            r_ui=recomendacion.r_ui,
            est=recomendacion.est,
            details=json.loads(recomendacion.details) if recomendacion.details else {},
            rating=recomendacion.rating if isinstance(recomendacion.rating, str) else None
        )
        for recomendacion in recommendations_db
    ]
    return recommendations


@app.get("/recommendations/{recommendation_id}", response_model=models.Recomendacion)
def get_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    recomendacion = db.query(models.RecomendacionDB).filter(models.RecomendacionDB.id == recommendation_id).first()
    if not recomendacion:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return models.Recomendacion(
        id=recomendacion.id,
        uid=recomendacion.uid,
        iid=recomendacion.iid,
        r_ui=recomendacion.r_ui,
        est=recomendacion.est,
        details=json.loads(recomendacion.details) if recomendacion.details else {},
        rating=recomendacion.rating if isinstance(recomendacion.rating, str) else None
    )


@app.post("/songs/", response_model=models.CancionCreate)
def create_cancion(cancion: models.CancionCreate, db: Session = Depends(get_db)):
    db_cancion = models.CancionDB(titulo=cancion.titulo)
    db.add(db_cancion)
    db.commit()
    db.refresh(db_cancion)
    return db_cancion

@app.get("/songs/", response_model=List[models.Cancion])
def get_canciones(db: Session = Depends(get_db)):
    canciones_db = db.query(models.CancionDB).all()
    canciones_response = []
    for cancion in canciones_db:
        recomendaciones = []  # Inicializamos una lista vacía de recomendaciones
        if cancion.recomendaciones:  # Verificamos si hay recomendaciones asociadas
            # Si hay recomendaciones, las serializamos adecuadamente
            recomendaciones = [
                models.Recomendacion(
                    id=recomendacion.id,
                    uid=recomendacion.uid,
                    iid=recomendacion.iid,
                    r_ui=recomendacion.r_ui,
                    est=recomendacion.est,
                    details=json.loads(recomendacion.details) if recomendacion.details else {},
                    rating=recomendacion.rating if isinstance(recomendacion.rating, str) else None
                )
                for recomendacion in cancion.recomendaciones
            ]
        # Creamos una instancia de Cancion con las recomendaciones adecuadas
        cancion_response = models.Cancion(
            id=cancion.id,
            titulo=cancion.titulo,
            recomendaciones=recomendaciones
        )
        canciones_response.append(cancion_response)

    return canciones_response



@app.get("/user/{user_id}/interactions", response_model=List[models.Interaccion])
def get_interacciones_usuario(user_id: int, db: Session = Depends(get_db)):
    interacciones_db = db.query(models.InteraccionDB).filter(models.InteraccionDB.user_id == user_id).all()
    return interacciones_db


@app.get("/songs/{cancion_id}", response_model=models.Cancion)
def get_cancion(cancion_id: int, db: Session = Depends(get_db)):
    cancion_db = db.query(models.CancionDB).filter(models.CancionDB.id == cancion_id).first()
    if cancion_db is None:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return cancion_db

@app.get("/interactions/{interaccion_id}", response_model=models.Interaccion)
def get_interaccion(interaccion_id: int, db: Session = Depends(get_db)):
    interaccion_db = db.query(models.InteraccionDB).filter(models.InteraccionDB.RecomendacionID == interaccion_id).first()
    if interaccion_db is None:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return interaccion_db

@app.post("/interactions/", response_model=models.Interaccion)  # Adjust the response model as needed
def create_interaction(interaction: models.InteraccionCreate, db: Session = Depends(get_db)):
    new_interaction = models.InteraccionDB(
        user_id=interaction.user_id,
        cancion_id=interaction.cancion_id,
        rating=interaction.rating
    )
    db.add(new_interaction)
    db.commit()
    return new_interaction



if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)