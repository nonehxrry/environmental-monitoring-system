from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processor import load_and_preprocess_data
from src.ml_forecaster import get_forecasts, detect_anomalies
from src.genai_chatbot import generate_alert, chat_with_ai

try:
    df = load_and_preprocess_data()
except FileNotFoundError:
    raise RuntimeError("Data file not found. Please run `data_processor.py` first.")

app = FastAPI(
    title="Environmental Monitoring & Alert System",
    description="An API for real-time environmental data, ML forecasting, and GenAI alerts.",
    version="1.0.0"
)

class ChatQuery(BaseModel):
    query: str
    location: str

class AlertRequest(BaseModel):
    aqi_level: int
    location: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Environmental Monitoring API. Access docs at /docs."}

@app.get("/status")
def get_status():
    """Returns the status of the system components."""
    return {
        "data_loaded": not df.empty,
        "aqi_model_exists": os.path.exists('models/aqi_model.pkl'),
        "temp_model_exists": os.path.exists('models/temp_model.pkl')
    }

@app.get("/forecasts")
def get_forecasts_and_anomalies():
    """Returns 24-hour forecasts and detects recent anomalies."""
    try:
        aqi_forecasts, temp_forecasts = get_forecasts(df)
        anomalies = detect_anomalies(df)
        
        anomaly_list = anomalies[['aqi', 'temperature']].reset_index().to_dict('records')

        return {
            "status": "success",
            "current_aqi": df['aqi'].iloc[-1],
            "current_temperature": df['temperature'].iloc[-1],
            "aqi_forecast_24h": aqi_forecasts,
            "temperature_forecast_24h": temp_forecasts,
            "anomalies": anomaly_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alert")
def create_alert(request: AlertRequest):
    """Generates a GenAI-powered alert."""
    if request.aqi_level > 150:
        alert = generate_alert(request.aqi_level, request.location)
        return {"alert": alert}
    else:
        return {"alert": "AQI is within a safe range, no alert needed."}

@app.post("/chatbot")
def chatbot_endpoint(request: ChatQuery):
    """Responds to user queries via a GenAI chatbot."""
    current_aqi = df['aqi'].iloc[-1]
    response = chat_with_ai(request.query, current_aqi, request.location)
    return {"response": response}