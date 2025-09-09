import pandas as pd
import numpy as np

def generate_mock_data():
    """Generates and saves mock environmental data."""
    dates = pd.date_range('2025-01-01', periods=200, freq='H')
    aqi = np.random.randint(10, 150, size=200) + np.sin(np.arange(200)/10) * 20
    temperature = np.random.randint(20, 35, size=200) + np.cos(np.arange(200)/15) * 5

    aqi[50:55] = np.nan
    aqi[180] = 400
    temperature[190] = 50

    df = pd.DataFrame({
        'timestamp': dates,
        'aqi': aqi,
        'temperature': temperature
    }).set_index('timestamp')

    df.to_csv('data/raw_data.csv')
    print("Mock data generated and saved to 'data/raw_data.csv'.")
    return df

def load_and_preprocess_data(file_path='data/raw_data.csv'):
    """Loads historical data, handles missing values, and returns a clean DataFrame."""
    if not pd.to_datetime:
        generate_mock_data()
    
    df = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
    df.ffill(inplace=True)
    
    print("Historical data loaded and preprocessed.")
    return df

if __name__ == "__main__":
    generate_mock_data()
    processed_data = load_and_preprocess_data()
    print("\nProcessed Data Head:")
    print(processed_data.head())