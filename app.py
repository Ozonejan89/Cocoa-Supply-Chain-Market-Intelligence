import pandas as pd
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


@st.cache_data
def load_clean_market_data():
    data_file = BASE_DIR / "clean_cocoa_weather_data.csv"
    try:
        df = pd.read_csv(data_file)
    except FileNotFoundError:
        st.warning("The dashboard data is not ready yet. Run: py -3 prepare_dashboard_data.py")
        return None

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


@st.cache_data
def load_regional_production():
    data_file = BASE_DIR / "regional_production.csv"
    try:
        df = pd.read_csv(data_file)
    except FileNotFoundError:
        st.warning("Regional production data is missing. Run: py -3 prepare_dashboard_data.py")
        return None

    return df


def main():
    st.set_page_config(page_title="Cocoa Supply Chain Market Intelligence", layout="wide")
    st.title("Cocoa Supply Chain Market Intelligence")
    st.caption("Clean market data, weather data, and regional production insights")

    market_df = load_clean_market_data()
    regional_df = load_regional_production()

    if market_df is None or regional_df is None:
        st.stop()

    latest_date = market_df["Date"].max()
    latest_price = market_df.loc[market_df["Date"] == latest_date, "Cocoa_Price_USD"].iloc[0]
    avg_rainfall = market_df["Rainfall_mm"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest cocoa price (USD)", f"{latest_price:,.0f}")
    col2.metric("Average rainfall (mm)", f"{avg_rainfall:.2f}")
    col3.metric("Regional data rows", f"{len(regional_df)}")

    st.subheader("Cocoa price trend")
    st.line_chart(market_df.set_index("Date")["Cocoa_Price_USD"])

    st.subheader("Rainfall trend")
    st.line_chart(market_df.set_index("Date")["Rainfall_mm"])

    st.subheader("Regional production by year")
    regional_chart = regional_df.set_index("Year")
    st.bar_chart(regional_chart)

    st.subheader("Clean market data preview")
    st.dataframe(market_df.head(10), use_container_width=True)


if __name__ == "__main__":
    main()
