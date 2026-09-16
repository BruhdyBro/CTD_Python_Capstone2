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
main_table = driver.find_element(By.CSS_SELECTOR, 'table.zebra.fw.tb-theme')

table_body = main_table.find_element(By.CSS_SELECTOR, 'tbody')

table_rows = table_body.find_elements(By.CSS_SELECTOR, 'tr')

with open('weather.csv', mode='w', newline='', encoding='utf-8') as file:

    writer = csv.writer(file)
    headers = ["location", "temperature", "time"]
    writer.writerow(headers)

        
    for row in table_rows:
        table_data = row.find_elements(By.CSS_SELECTOR, 'td')
                
        for i in range(0, len(table_data), 4):
            loc_name = table_data[i].text
            loc_time = table_data[i + 1].text
            loc_temp = table_data[i + 3].text

            writer.writerow([loc_name, loc_temp, loc_time])

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


# Might parse time into date Pandas format, but would require checking today's date compared to tmr for each day
# E.g. if today = mon, then (mon = day) and (tues = day+1), if today = tues, then (tues = day) and (wed = day+1), etc.
# This is because the website uses text to show the date.


# Creates connection to weather_db.db file
try:
    with sqlite3.connect("weather_db.db") as conn:

        cursor = conn.cursor()

        # Create the base table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data(
        weather_id INTEGER PRIMARY KEY,
        location TEXT NOT NULL,
        temperature TEXT NOT NULL,
        time TEXT NOT NULL
        )
        """)

        # Send cleaned df to sql weather_data table
        weather_df.to_sql("weather_data", conn, if_exists="append", index=False)

        conn.commit()

except Exception as e:
    print("Error doing the request: " + e)