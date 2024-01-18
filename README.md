# Weather API Project

## Overview

The objective of this project is to develop an API that provides historical weather data based on user input for location (Latitude & Longitude) and the number of days in the past. The API will return detailed hourly information on temperature, precipitation, and cloud cover for the specified duration.

## Getting Started

1. **Update Python to the latest version**

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
   
