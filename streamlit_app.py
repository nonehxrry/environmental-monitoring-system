import streamlit as st
import requests
import pandas as pd
import os

# Set the URL of your deployed FastAPI backend.
# The `FASTAPI_URL` must be set as a secret on Streamlit Community Cloud.
# This code will now crash if the environment variable is not found,
# which prevents silent failures during deployment.
FASTAPI_URL = os.getenv("FASTAPI_URL")

# --- Page Configuration ---
st.set_page_config(
    page_title="Environmental Monitoring & Alert System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Error Handling for Missing Environment Variable ---
if not FASTAPI_URL:
    st.error("FASTAPI_URL environment variable is not set. Please add it to your Streamlit Cloud secrets.")
    st.info("For local testing, set FASTAPI_URL='http://127.0.0.1:8000' in your local .env file.")
    st.stop()

# --- Title and Description ---
st.title("🌍 Environmental Monitoring Dashboard")
st.markdown("""
This app monitors environmental data, predicts future conditions, and provides
intelligent alerts and recommendations powered by a machine learning model and GenAI.
""")

# --- Sidebar for Chatbot ---
with st.sidebar:
    st.header("GenAI Chatbot 💬")
    user_query = st.text_input("Ask a question:", placeholder="What should I do if the AQI is high?")
    location = st.text_input("Your location:", placeholder="New Delhi")
    
    if st.button("Get Advice"):
        if user_query and location:
            payload = {"query": user_query, "location": location}
            try:
                response = requests.post(f"{FASTAPI_URL}/chatbot", json=payload)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                st.write(response.json()["response"])
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the backend API: {e}")
        else:
            st.warning("Please enter both a query and your location.")

# --- Main Dashboard ---
st.header("Real-time Data & Forecasts")

if st.button("Refresh Dashboard"):
    try:
        with st.spinner('Fetching data from the backend...'):
            response = requests.get(f"{FASTAPI_URL}/forecasts")
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
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
                aqi_level = anomaly.get('aqi', 0)
                if aqi_level > 150:
                    # Pass the location from the user input to the alert endpoint
                    alert_response = requests.post(f"{FASTAPI_URL}/alert", json={"aqi_level": aqi_level, "location": location})
                    alert_response.raise_for_status()
                    st.info(f"**High AQI Alert:** {alert_response.json()['alert']}")
        else:
            st.info("No anomalies detected.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error: Could not connect to the backend API. Please check your FASTAPI_URL. {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
