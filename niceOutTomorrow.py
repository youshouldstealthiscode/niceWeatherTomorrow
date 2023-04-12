import os
import requests
from datetime import datetime, timedelta
from twilio.rest import Client

OPENWEATHER_API_KEY = "your_openweathermap_api_key"
TWILIO_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
LOCATION = "your_city,your_country_code"
recipients = ["phone_number_1", "phone_number_2"]

def get_weather_data():
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={LOCATION}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

def check_conditions(data):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    tomorrow_date = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
    today_rain = False
    tomorrow_sunny = False
    tomorrow_temp = None

    for entry in data["list"]:
        entry_time = datetime.fromtimestamp(entry["dt"])
        if entry_time.date() == today.date() and "rain" in entry["weather"][0]["description"]:
            today_rain = True
        if entry_time.date() == tomorrow.date() and entry_time.hour >= 6 and entry_time.hour <= 18:
            if entry["weather"][0]["main"].lower() == "clear":
                tomorrow_sunny = True
            if not tomorrow_temp or entry["main"]["temp_min"] < tomorrow_temp:
                tomorrow_temp = entry["main"]["temp_min"]

    return today_rain, tomorrow_sunny, tomorrow_temp

def send_text_message(temperature_celsius):
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32
    message_body = f"Tomorrow will be sunny! Temperatures: {temperature_celsius}°C / {temperature_fahrenheit}°F."

    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    for phone_number in recipients:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )

def main():
    data = get_weather_data()
    today_rain, tomorrow_sunny, tomorrow_temp = check_conditions(data)

    if today_rain and tomorrow_sunny and tomorrow_temp and tomorrow_temp >= 19.4:
        send_text_message(tomorrow_temp)

if __name__ == "__main__":
    main()
