import os
import joblib
import pandas as pd
import numpy as np
import xgboost
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Bengaluru House Price Predictor")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SMART PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "bengaluru_house_price_final.pkl")
DATA_PATH = os.path.join(BASE_DIR, "Bengaluru_House_Data.csv")

print(f"DEBUG: Model should be at -> {MODEL_PATH}")

# Load Model
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ SUCCESS: Model loaded!")
else:
    print("❌ ERROR: Model file not found!")

# Load Data for Dropdowns
unique_locations = []
unique_area_types = []
if os.path.exists(DATA_PATH):
    try:
        df_raw = pd.read_csv(DATA_PATH)
        df_raw['location'] = df_raw['location'].astype(str).apply(lambda x: x.strip())
        unique_locations = sorted(df_raw['location'].unique().tolist())
        unique_area_types = sorted(df_raw['area_type'].unique().tolist())
    except:
        pass

# Input Schema
class HouseInput(BaseModel):
    location: str
    area_type: str
    size: str
    total_sqft: float
    bath: int
    balcony: float | None = 0

# Routes
@app.get("/")
def read_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/api/options")
def get_options():
    return {"locations": unique_locations, "area_types": unique_area_types}

@app.post("/predict")
def predict_price(data: HouseInput):
    if not model:
        return {"error": "Model not loaded"}

    try:
        # BHK Logic
        try:
            bhk = int(str(data.size).split(" ")[0])
        except:
            bhk = 2

        # Create DataFrame
        input_data = pd.DataFrame([{
            "area_type": data.area_type,
            "location": data.location,
            "total_sqft": data.total_sqft,
            "bath": data.bath,
            "balcony": data.balcony,
            "bhk": bhk
        }])

        # Predict
        prediction_log = model.predict(input_data)[0]
        
        # --- FIX IS HERE: Convert numpy float to python float ---
        prediction = float(np.exp(prediction_log))

        return {
            "estimated_price_lakh": round(prediction, 2),
            "price_range_lakh": [
                round(prediction - 10, 2),
                round(prediction + 10, 2)
            ]
        }
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}