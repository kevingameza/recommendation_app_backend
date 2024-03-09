from pathlib import Path
import joblib

def cargar_modelo():
    modelo = joblib.load('modelo_algo_cosine.joblib')
    return modelo

def generar_recomendaciones( datos_usuario):
    # Implementa la lógica necesaria para generar recomendaciones
    # Esto dependerá de la naturaleza de tu modelo y de tus datos
    modelo = cargar_modelo()
    recomendaciones = modelo.predict(datos_usuario)  # Ajusta esto según tu modelo
    return recomendaciones
