"""Generate the local CSV inputs used by the dashboard."""

from merge_weather_prices import merge_and_clean
from update_regional_production import inject_regional_production


def main():
    print("Preparing dashboard data files...")
    merge_and_clean()
    inject_regional_production()
    print("\nDashboard data is ready in the local project folder.")


if __name__ == "__main__":
    main()
