import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

def fetch_cocoa_prices():
    print("Step 1: Fetching cocoa market prices...")
    cocoa_ticker = "CC=F"
    
    # Fetch price history from 2020 to today
    cocoa_df = yf.download(cocoa_ticker, start="2020-01-01")
    cocoa_df.reset_index(inplace=True)
    
    # Some yfinance results use an unnamed index column after reset_index()
    if 'Date' not in cocoa_df.columns and 'index' in cocoa_df.columns:
        cocoa_df.rename(columns={'index': 'Date'}, inplace=True)

    # FIX: Flatten multi-index headers if yfinance returns them
    if isinstance(cocoa_df.columns, pd.MultiIndex):
        cocoa_df.columns = cocoa_df.columns.get_level_values(0)

    # Validate the expected columns exist before selecting them
    expected_columns = ['Date', 'Close', 'Volume']
    if not all(col in cocoa_df.columns for col in expected_columns):
        raise ValueError(
            f"Unexpected yfinance output columns: {list(cocoa_df.columns)}. "
            "Expected at least Date, Close, and Volume."
        )

    cocoa_df = cocoa_df[['Date', 'Close', 'Volume']]
    cocoa_df.columns = ['Date', 'Cocoa_Price_USD', 'Trading_Volume']
    return cocoa_df

def fetch_ivoire_rainfall():
    print("Step 2: Fetching historical rainfall data for Côte d'Ivoire (Yamoussoukro)...")
    
    # Coordinates for Yamoussoukro, the heart of Côte d'Ivoire's cocoa region
    latitude = 6.82
    longitude = -5.28
    end_date = datetime.today().strftime('%Y-%m-%d')
    
    # Query the free Open-Meteo Archive API
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date=2020-01-01&end_date={end_date}&daily=precipitation_sum&timezone=auto"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        daily_data = data['daily']
        
        # Create weather dataframe
        weather_df = pd.DataFrame({
            'Date': pd.to_datetime(daily_data['time']),
            'Rainfall_mm': daily_data['precipitation_sum']
        })
        print("Rainfall data successfully retrieved!")
        return weather_df
    else:
        print(f"Failed to fetch weather data. Status code: {response.status_code}")
        return None

def merge_and_clean():
    # Run both data extractions
    prices_df = fetch_cocoa_prices()
    weather_df = fetch_ivoire_rainfall()
    
    if weather_df is not None:
        print("Step 3: Merging datasets on Date...")
        
        # Make sure dates are formatted identically
        prices_df['Date'] = pd.to_datetime(prices_df['Date'])
        weather_df['Date'] = pd.to_datetime(weather_df['Date'])
        
        # Merge using an inner join (matches market days with weather records)
        merged_df = pd.merge(prices_df, weather_df, on='Date', how='inner')
        
        # Save to a clean, final CSV for your dashboard
        output_file = "clean_cocoa_weather_data.csv"
        merged_df.to_csv(output_file, index=False)
        
        print(f"\nSuccess! Final portfolio dataset saved as '{output_file}'")
        print("\nPreview of your live data:")
        print(merged_df.head())
    else:
        print("Process aborted due to weather API failure.")

if __name__ == "__main__":
    merge_and_clean()