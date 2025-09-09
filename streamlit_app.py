import streamlit as st
import requests
import pandas as pd
import os

# Set the URL of your deployed FastAPI backend
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.set_page_config(layout="wide")
st.title("🌍 Environmental Monitoring Dashboard")

with st.sidebar:
    st.header("GenAI Chatbot 💬")
    user_query = st.text_input("Ask a question:")
    if st.button("Get Advice"):
        if user_query:
            try:
                # Note: You need a location for the chatbot to work
                response = requests.post(f"{FASTAPI_URL}/chatbot", json={"query": user_query, "location": "Your Location"})
                st.write(response.json()["response"])
            except Exception as e:
                st.error(f"Error: Could not connect to the API. {e}")
        else:
            st.warning("Please enter a query.")

st.header("Real-time Data & Forecasts")

if st.button("Refresh Dashboard"):
    try:
        with st.spinner('Fetching data...'):
            response = requests.get(f"{FASTAPI_URL}/forecasts")
            data = response.json()

        # Display current metrics
        col1, col2 = st.columns(2)
        col1.metric("Current AQI", f"{data['current_aqi']:.0f}")
        col2.metric("Current Temp", f"{data['current_temperature']:.1f} °C")

        # Display forecast graph
        st.subheader("24-Hour Forecasts 📈")
        aqi_forecast_df = pd.DataFrame(data['aqi_forecast_24h'].items(), columns=['Timestamp', 'AQI'])
        aqi_forecast_df['Timestamp'] = pd.to_datetime(aqi_forecast_df['Timestamp'])
        st.line_chart(aqi_forecast_df.set_index('Timestamp'))

        # Display alerts
        st.subheader("Alerts 🚨")
        if data['anomalies']:
            st.warning("Potential Anomalies Detected!")
            for anomaly in data['anomalies']:
                if anomaly.get('aqi', 0) > 150:
                    alert_response = requests.post(f"{FASTAPI_URL}/alert", json={"aqi_level": anomaly['aqi'], "location": "Your Location"})
                    st.info(f"**High AQI Alert:** {alert_response.json()['alert']}")
        else:
            st.info("No anomalies detected.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error: Could not connect to the backend API. Please check your FASTAPI_URL. {e}")