import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import IsolationForest
import joblib
import os

def train_models(data: pd.DataFrame):
    """Trains and saves ARIMA and Isolation Forest models."""
    print("Training models...")
    os.makedirs('models', exist_ok=True) # Ensure models directory exists
    try:
        aqi_model = ARIMA(data['aqi'], order=(5, 1, 0))
        aqi_model_fit = aqi_model.fit()
        joblib.dump(aqi_model_fit, 'models/aqi_model.pkl')
        print("AQI ARIMA model trained and saved.")

        temp_model = ARIMA(data['temperature'], order=(5, 1, 0))
        temp_model_fit = temp_model.fit()
        joblib.dump(temp_model_fit, 'models/temp_model.pkl')
        print("Temperature ARIMA model trained and saved.")

        iso_forest = IsolationForest(random_state=42)
        iso_forest.fit(data[['aqi', 'temperature']])
        joblib.dump(iso_forest, 'models/iso_forest.pkl')
        print("Isolation Forest model trained and saved.")

    except Exception as e:
        print(f"Error during model training: {e}")

def get_forecasts(data: pd.DataFrame, steps=24):
    """Loads models and generates forecasts."""
    try:
        aqi_model = joblib.load('models/aqi_model.pkl')
        aqi_forecast = aqi_model.forecast(steps=steps)

        temp_model = joblib.load('models/temp_model.pkl')
        temp_forecast = temp_model.forecast(steps=steps)

        return aqi_forecast.to_dict(), temp_forecast.to_dict()

    except FileNotFoundError:
        print("Models not found. Please run 'train_models' first.")
        return None, None

def detect_anomalies(data: pd.DataFrame):
    """Loads model and detects anomalies."""
    try:
        iso_forest = joblib.load('models/iso_forest.pkl')
        predictions = iso_forest.fit_predict(data[['aqi', 'temperature']])
        anomalies = data[predictions == -1]
        
        return anomalies

    except FileNotFoundError:
        print("Anomaly detection model not found. Please run 'train_models' first.")
        return pd.DataFrame()

if __name__ == "__main__":
    from data_processor import load_and_preprocess_data
    df = load_and_preprocess_data()
    train_models(df)
    
    aqi_f, temp_f = get_forecasts(df)
    anomalies = detect_anomalies(df)
    print("\nAnomalies Detected:")
    print(anomalies)