import requests
import openmeteo_requests
from datetime import datetime, timedelta

import requests_cache
import pandas as pd
from retry_requests import retry
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

@login_required(login_url="/login")
def index(request):
    
    forecast_url = "https://api.open-meteo.com/v1/forecast"
    location_url = "https://geocoding-api.open-meteo.com/v1/search?name={}&count={}&language=en&format=json"
    
    if request.method == "POST":
        
        city = request.POST.get("city")
        city_coord_response = requests.get(location_url.format(city, 5)).json()
        cities_coords = city_coord_response["results"]

        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)        
        
        n_past_days = int(request.POST.get("n_days"))
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=n_past_days)).strftime("%Y-%m-%d")
        
        final_list = []
        
        city_names = []
        
        for city in cities_coords:
            forecast_params = {
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "start_date": start_date,
                "end_date": end_date,
                "daily": ["temperature_2m_min", "temperature_2m_max", "precipitation_sum"],
                "hourly": ["temperature_2m", "cloud_cover", "precipitation"]
            }
            
            forecast_responses = openmeteo.weather_api(forecast_url, params=forecast_params)
            forecast_response = forecast_responses[0]

            city_info = {
                "city_name": city["name"],
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "country": city.get("country", "Somewhere on Earth"),
            }
            city_names.append(city_info)
            
            # Hourly
            hourly = forecast_response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
            hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()

            hourly_data = {"date": pd.date_range(
                start = pd.to_datetime(hourly.Time(), unit = "s"),
                end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
                freq = pd.Timedelta(seconds = hourly.Interval()),
                inclusive = "left"
            )}
            
            hourly_data["temperature_2m"] = hourly_temperature_2m
            hourly_data["cloud_cover"] = hourly_cloud_cover
            hourly_data["precipitation"] = hourly_precipitation
            

            hourly_dataframe = pd.DataFrame(data = hourly_data) 
            
            # Daily    
            daily = forecast_response.Daily()
            daily_temperature_2m_min = daily.Variables(0).ValuesAsNumpy()
            daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
            daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()

            daily_data = {"date": pd.date_range(
                start = pd.to_datetime(daily.Time(), unit = "s"),
                end = pd.to_datetime(daily.TimeEnd(), unit = "s"),
                freq = pd.Timedelta(seconds = daily.Interval()),
                inclusive = "left"
            )}
            
            daily_data["temperature_2m_min"] = daily_temperature_2m_min
            daily_data["temperature_2m_max"] = daily_temperature_2m_max
            daily_data["precipitation_sum"] = daily_precipitation_sum

            daily_dataframe = pd.DataFrame(data = daily_data)   
            
            # Creating dictionary    
            
            # Convert 'date' columns to datetime objects
            hourly_dataframe['date'] = pd.to_datetime(hourly_dataframe['date'])
            daily_dataframe['date'] = pd.to_datetime(daily_dataframe['date'])

            # Create a list of dictionaries
            result_list = []

            for index, row in daily_dataframe.iterrows():
                date_value = row['date']
                temperature_2m_max = row['temperature_2m_max']
                temperature_2m_min = row['temperature_2m_min']
                precipitation_sum = row['precipitation_sum']

                # Filter A DataFrame for the corresponding date and extract hourly temperatures
                hourly_temperatures = hourly_dataframe[hourly_dataframe['date'].dt.date == date_value.date()]['temperature_2m'].tolist()
                hourly_cloud_cover = hourly_dataframe[hourly_dataframe['date'].dt.date == date_value.date()]['cloud_cover'].tolist()   
                hourly_precipitation = hourly_dataframe[hourly_dataframe['date'].dt.date == date_value.date()]['precipitation'].tolist()
                

                # Create dictionary
                result_dict = {
                    'date': date_value.strftime("%Y-%m-%d"),
                    'temperature_2m_min': temperature_2m_min,
                    'temperature_2m_max': temperature_2m_max,
                    'precipitation_sum': precipitation_sum,
                    'hourly_temperature': hourly_temperatures,
                    'hourly_cloud_cover': hourly_cloud_cover,
                    'hourly_precipitation': hourly_precipitation
                }

                result_list.append(result_dict)    
            
            
            final_list.append(result_list)                
        final_list = zip(final_list, city_names)
        context = {
            "final_list": final_list,
            "page": "Index",
        }
        
        return render(request, "weather_app/index.html", context)
    return render(request, "weather_app/index.html", context={"page":"Index"})


def login_page(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        
        if not User.objects.filter(username = username).exists():
            messages.info(request, "Invalid username.")
            return redirect("/login")
        
        user = authenticate(username = username, password = password)
        
        if user is None:
            messages.info(request, "Invalid password.")
            return redirect("/login")
        else:
            login(request, user) # session
            return redirect("/")

    return render(request, "weather_app/login.html", context={"page": "Login"})

def logout_page(request):
    logout(request)
    return redirect("/login")

def register_page(request):
    if request.method == "POST":
        data = request.POST
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")
        password = data.get("password")
        
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already taken.")
            return redirect("/register")
        
        user = User.objects.create(first_name = first_name, last_name = last_name, username = username)
        user.set_password(password)
        user.save()
        
        messages.info(request, "Account created successfully.")
        return redirect("/register")    
    return render(request, "weather_app/register.html", context={"page":"Register"})
