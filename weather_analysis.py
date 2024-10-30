import requests
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean

API_KEY = "3365a8548520afaebde066bc0379f39e"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city):
    """
    Fetch weather data for a given city
    Returns: Dictionary with weather data or None if request fails
    """
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'imperial'  # Using imperial for US temperature format
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data for {city}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching data for {city}: {str(e)}")
        return None

def analyze_cities(cities):
    """
    Analyze weather data for a list of cities
    Returns: DataFrame with analysis results
    """
    weather_data = []
    
    for city in cities:
        data = get_weather_data(city)
        if data:
            weather_info = {
                'city': city,
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'description': data['weather'][0]['description'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            weather_data.append(weather_info)
    
    return pd.DataFrame(weather_data)

def generate_report(df):
    """
    Generate a detailed weather report from the DataFrame
    Writes both a text summary and CSV file
    """
    # Create summary report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    report_file = f'weather_report_{timestamp}.txt'
    csv_file = f'weather_data_{timestamp}.csv'
    
    with open(report_file, 'w') as f:
        f.write("Weather Analysis Report\n")
        f.write("======================\n\n")
        f.write(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Temperature statistics
        f.write("Temperature Summary:\n")
        f.write(f"Highest temperature: {df['temperature'].max()}°F in {df.loc[df['temperature'].idxmax(), 'city']}\n")
        f.write(f"Lowest temperature: {df['temperature'].min()}°F in {df.loc[df['temperature'].idxmin(), 'city']}\n")
        f.write(f"Average temperature across cities: {df['temperature'].mean():.1f}°F\n\n")
        
        # Wind conditions
        f.write("Wind Conditions:\n")
        f.write(f"Highest wind speed: {df['wind_speed'].max()} mph in {df.loc[df['wind_speed'].idxmax(), 'city']}\n")
        f.write(f"Average wind speed: {df['wind_speed'].mean():.1f} mph\n\n")
        
        # City-by-city breakdown
        f.write("City-by-City Breakdown:\n")
        for _, row in df.iterrows():
            f.write(f"\n{row['city']}:\n")
            f.write(f"  Temperature: {row['temperature']}°F (Feels like: {row['feels_like']}°F)\n")
            f.write(f"  Humidity: {row['humidity']}%\n")
            f.write(f"  Wind Speed: {row['wind_speed']} mph\n")
            f.write(f"  Conditions: {row['description']}\n")
    
    # Save raw data to CSV
    df.to_csv(csv_file, index=False)
    
    return report_file, csv_file

def main():
    # List of cities to analyze - you can modify this list
    cities = [
        'Gainesville,FL,US',
        'Miami,FL,US',
        'Orlando,FL,US',
        'Tampa,FL,US',
        'Jacksonville,FL,US'
    ]
    
    print("Fetching weather data...")
    weather_df = analyze_cities(cities)
    
    if not weather_df.empty:
        report_file, csv_file = generate_report(weather_df)
        print(f"\nAnalysis complete!")
        print(f"Detailed report saved to: {report_file}")
        print(f"Raw data saved to: {csv_file}")
        
        # Print quick summary to console
        print("\nQuick Summary:")
        print(f"Warmest city: {weather_df.loc[weather_df['temperature'].idxmax(), 'city']} "
              f"({weather_df['temperature'].max()}°F)")
        print(f"Coolest city: {weather_df.loc[weather_df['temperature'].idxmin(), 'city']} "
              f"({weather_df['temperature'].min()}°F)")

if __name__ == "__main__":
    main()
