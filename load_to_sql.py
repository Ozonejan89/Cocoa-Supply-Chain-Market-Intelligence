import pandas as pd
import sqlite3

from update_regional_production import inject_regional_production

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

    print("\nStep 5: Updating regional production table...")
    inject_regional_production()

if __name__ == "__main__":
    load_csv_to_sqlite()