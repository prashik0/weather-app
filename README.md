# Weather API Project

## Overview

The objective of this project is to develop an API that provides historical weather data based on user input for location (Latitude & Longitude) and the number of days in the past. The API will return detailed hourly information on temperature, precipitation, and cloud cover for the specified duration.

## Getting Started

1. **Update Python to the latest version (>= 3.10)**

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```

1. **Create a Virtual Environment:**

   ```bash
   virtualenv env
   ```

1. **Activate the Virtual Environment:**
   
   Mac users
   ```bash
   source env/bin/activate
   ```
   Windows users
   ```bash
   env\Scripts\activate
   ```

1. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt

1. **Create Database Tables:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate

1. **Run the Development Server:**

   ```bash
   python manage.py runserver


<img width="1440" alt="Screenshot 2024-01-18 at 7 28 10 PM" src="https://github.com/prashik0/weather-app/assets/88423828/e49fe184-4007-42a4-95ea-31bb7a6b4e31">
