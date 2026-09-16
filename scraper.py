from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import csv

import pandas as pd
import numpy as np

import sqlite3


driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

driver.get("https://www.timeanddate.com/weather/")


# Getting table elements down to table data
main_table = driver.find_element(By.CSS_SELECTOR, 'table')

table_body = main_table.find_element(By.CSS_SELECTOR, 'tbody')

table_rows = table_body.find_elements(By.CSS_SELECTOR, 'tr')

with open('weather.csv', mode='w', newline='', encoding='utf-8') as file:

    writer = csv.writer(file)
    headers = ["location", "country", "temperature", "time"]
    writer.writerow(headers)

        
    for row in table_rows:
        

        loc_name = row.find_element(By.CSS_SELECTOR, 'a.tad-link').text
        loc_country = row.find_element(By.CSS_SELECTOR, 'td.tad-weather-table__country-cell').text
        loc_temp = row.find_element(By.CSS_SELECTOR, 'td.tad-weather-table__temperature-cell').text
        loc_time = row.find_element(By.CSS_SELECTOR, 'span.tad-weather-table__row-time-value').text

        writer.writerow([loc_name, loc_country, loc_temp, loc_time])

driver.quit()



#
#   Creating the dataframe from the CSV file
#

weather_df = pd.read_csv("weather.csv")

print("-=-=-=- Base DF -=-=-=-")
print(weather_df)
print()
weather_df.info()
print()



#
#   Initial cleaning of the dataframe
#

print("-=-=-=- Initial Cleaning -=-=-=-")
# Cleaning location column
weather_df['location'] = weather_df['location'].str.strip("*")
weather_df['location'] = weather_df['location'].str.strip()

# Cleaning temperature column
weather_df['temperature'] = weather_df['temperature'].str.strip()

# Cleaning Time column
weather_df['temperature'] = weather_df['temperature'].str.strip()

print(weather_df)
print()
weather_df.info()
print()

#
#   Final cleaning of the dataframe
#
print("-=-=-=- Final DF Clean -=-=-=-")
weather_df = weather_df.dropna()
weather_df = weather_df.drop_duplicates()

weather_df.info()
print()
print(weather_df)
print()


#
#   Creating raw temperature column for numeric comparison
#

weather_df['raw_temp'] = weather_df['temperature'].str.replace(" °F","")
weather_df['raw_temp'] = pd.to_numeric(weather_df['raw_temp'], errors="coerce")
weather_df.info()
print()
print(weather_df)
print()


# Creates connection to weather_db.db file
try:
    with sqlite3.connect("weather_db.db") as conn:

        cursor = conn.cursor()

        # Create the base table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data(
        weather_id INTEGER PRIMARY KEY,
        location TEXT NOT NULL,
        country TEXT NOT NULL,
        temperature TEXT NOT NULL,
        time TEXT NOT NULL,
        raw_temp INTEGER
        )
        """)

        # Send cleaned df to sql weather_data table
        weather_df.to_sql("weather_data", conn, if_exists="append", index=False)

        conn.commit()

except Exception as e:
    print("Error doing the request: " + e)