import sqlite3
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

def fetch_cocoa_prices():
    print("Step 1: Fetching cocoa market prices...")
    cocoa_ticker = "CC=F"
    
    # Fetch price history from 2020 to today
    cocoa_df = yf.download(cocoa_ticker, start="2020-01-01")
    cocoa_df.reset_index(inplace=True)

    # Some yfinance versions return the date as an unnamed 'index' column after reset_index.
    if 'Date' not in cocoa_df.columns and 'index' in cocoa_df.columns:
        cocoa_df.rename(columns={'index': 'Date'}, inplace=True)

    # FIX: Flatten multi-index headers if yfinance returns them
    if isinstance(cocoa_df.columns, pd.MultiIndex):
        cocoa_df.columns = cocoa_df.columns.get_level_values(0)

    expected_columns = ['Date', 'Close', 'Volume']
    if not all(col in cocoa_df.columns for col in expected_columns):
        raise ValueError(
            f"Unexpected yfinance output columns: {list(cocoa_df.columns)}. "
            "Expected at least Date, Close, and Volume."
        )

    # Keep only the essential columns and rename them cleanly
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

def load_csv_to_sqlite():
    csv_file = "clean_cocoa_weather_data.csv"
    db_name = "cocoa_data.db"
    table_name = "cocoa_weather_metrics"
    
    print(f"Step 1: Reading clean data from '{csv_file}'...")
    try:
        # Load the CSV data we created in the last step
        df = pd.read_csv(csv_file)
        # Ensure the Date column is properly recognized as a string/datetime format
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    except FileNotFoundError:
        print(f"Error: '{csv_file}' not found. Please run merge_weather_prices.py first.")
        return

    print(f"Step 2: Connecting to SQLite Database ('{db_name}')...")
    # This automatically creates the database file if it doesn't exist yet
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    print(f"Step 3: Defining SQL table schema and rules...")
    # Explicitly creating the table with strict relational database rules
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Date TEXT PRIMARY KEY,
            Cocoa_Price_USD REAL,
            Trading_Volume REAL,
            Rainfall_mm REAL
        );
    """)

    print(f"Step 4: Writing records into table '{table_name}'...")
    # append/replace data into the SQL table
    # if_exists='replace' ensures that if you re-run it with updated data, it builds cleanly
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"\nSuccess! Database pipeline complete.")
    print(f"Your relational database file '{db_name}' is loaded and ready for queries!")

def export_regional_production_csv(db_name="cocoa_data.db", output_file="regional_production.csv"):
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("SELECT * FROM regional_production", conn)
    conn.close()
    df.to_csv(output_file, index=False)
    print(f"Saved regional production data to '{output_file}'")
    return df


def inject_regional_production():
    db_name = "cocoa_data.db"
    table_name = "regional_production"
    
    print("Step 1: Preparing historical country production data (Metric Tons)...")
    
    # Clean historical production data for the three West African majors
    data = {
        "Year": [2020, 2021, 2022, 2023, 2024, 2025],
        "Cote_d_Ivoire": [2200000, 2250000, 2400000, 2280000, 1800000, 1900000],
        "Ghana": [800000, 1040000, 680000, 650000, 450000, 500000],
        "Nigeria": [270000, 290000, 280000, 275000, 240000, 250000]
    }
    
    df = pd.DataFrame(data)
    
    print(f"Step 2: Loading regional production data into SQLite database '{db_name}'...")
    conn = sqlite3.connect(db_name)
    
    # Save to a new table inside your existing database
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    print("Step 3: Verifying the new table schema...")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
    print("Sample SQL Rows:", cursor.fetchall())
    
    conn.commit()
    conn.close()

    export_regional_production_csv()
    print("\nSuccess! Regional production table created and populated.")

if __name__ == "__main__":
    inject_regional_production()