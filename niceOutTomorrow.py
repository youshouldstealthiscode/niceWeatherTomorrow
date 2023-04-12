import os
import requests  # Import the requests library to make HTTP requests
from datetime import datetime, timedelta  # Import datetime and timedelta classes from the datetime module
from twilio.rest import Client  # Import the Twilio Client class from the twilio.rest module

# Replace the placeholders with your actual API keys, Twilio phone number, location, and phone numbers for recipients
OPENWEATHER_API_KEY = "your_openweathermap_api_key"
TWILIO_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
LOCATION = "your_city,your_country_code"
recipients = ["phone_number_1", "phone_number_2"]

def get_weather_data():  # Define a function to fetch weather data from the OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={LOCATION}&appid={OPENWEATHER_API_KEY}&units=metric"  # Create the URL to fetch weather data with location and API key
    response = requests.get(url)  # Send an HTTP GET request to the URL and store the response
    data = response.json()  # Convert the response JSON data to a Python dictionary
    return data  # Return the weather data dictionary

def check_conditions(data):  # Define a function to check the specified weather conditions in the data
    today = datetime.now()  # Get the current date and time
    tomorrow = today + timedelta(days=1)  # Calculate the date for tomorrow by adding 1 day to today
    tomorrow_date = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)  # Create a datetime object for tomorrow with the same date but no time information
    today_rain = False  # Initialize a variable to track whether it rained today
    tomorrow_sunny = False  # Initialize a variable to track whether tomorrow will be sunny
    tomorrow_temp = None  # Initialize a variable to store the minimum temperature for tomorrow

    for entry in data["list"]:  # Loop through each entry in the weather data's list of forecasts
        entry_time = datetime.fromtimestamp(entry["dt"])  # Convert the forecast's timestamp to a datetime object
        if entry_time.date() == today.date() and "rain" in entry["weather"][0]["description"]:  # If the forecast is for today and has rain in its description
            today_rain = True  # Set today_rain to True, indicating that it rained today
        if entry_time.date() == tomorrow.date() and entry_time.hour >= 6 and entry_time.hour <= 18:  # If the forecast is for tomorrow and is within sunlight hours (6 AM to 6 PM)
            if entry["weather"][0]["main"].lower() == "clear":  # If the forecast's main weather condition is "clear"
                tomorrow_sunny = True  # Set tomorrow_sunny to True, indicating that tomorrow will be sunny
            if not tomorrow_temp or entry["main"]["temp_min"] < tomorrow_temp:  # If there's no minimum temperature set yet, or the current forecast's minimum temperature is lower than the existing one
                tomorrow_temp = entry["main"]["temp_min"]  # Update the minimum temperature for tomorrow with the current forecast's minimum temperature

    return today_rain, tomorrow_sunny, tomorrow_temp  # Return the values for today_rain, tomorrow_sunny, and tomorrow_temp

def send_text_message(temperature_celsius):  # Define a function to send a text message using the Twilio API
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32  # Convert the temperature from Celsius to Fahrenheit

    # Create the message body, including the temperature in both Celsius and Fahrenheit
    message_body = f"Tomorrow will be sunny! Temperatures: {temperature_celsius}°C / {temperature_fahrenheit}°F."

    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)  # Initialize a Twilio Client instance with the given credentials

    for phone_number in recipients:  # Loop through each phone number in the recipients list
        message = client.messages.create(  # Create and send a text message
            body=message_body,  # Set the message body with the temperature information
            from_=TWILIO_PHONE_NUMBER,  # Set the sender's phone number (your Twilio phone number)
            to=phone_number  # Set the recipient's phone number (the current phone number in the loop)
        )

def main():  # Define the main function to execute the program
    data = get_weather_data()  # Call the get_weather_data function to fetch weather data
    today_rain, tomorrow_sunny, tomorrow_temp = check_conditions(data)  # Call the check_conditions function to check the weather conditions

    # If all conditions are met (rained today, sunny tomorrow, and minimum temperature >= 19.4 Celsius)
    if today_rain and tomorrow_sunny and tomorrow_temp and tomorrow_temp >= 19.4:
        send_text_message(tomorrow_temp)  # Call the send_text_message function with the minimum temperature for tomorrow

if __name__ == "__main__":
    main()  # Call the main function to run the program when the script is executed

