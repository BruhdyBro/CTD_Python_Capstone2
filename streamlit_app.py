import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import sqlite3

try:
    with sqlite3.connect("weather_db.db") as conn:
        print("Database connected sucessfully.")

        sql_query = "SELECT location, temperature, time, raw_temp FROM weather_data"
        all_data = pd.read_sql_query(sql_query, conn)
        all_data = all_data.sort_values(by='location')

        sql_query = "SELECT location FROM weather_data"
        locations = all_data['location'].tolist()
        locations.sort()
         

        


except Exception as e:
    print("Unable to complete: ", e)

all_data["raw_time"] = pd.to_datetime(
    all_data["time"],
    format="%a %I:%M %p"
)

print(all_data.head(10))
all_data.info()


st.title("Location Comparator")
col1, col2 = st.columns(2)
with col1:
    loc1 = st.selectbox("Select a location:", locations)
    loc1_df = all_data.loc[all_data['location'] == loc1]

with col2:
    loc2 = st.selectbox("Select another location:", locations, index=1)
    loc2_df = all_data.loc[all_data['location'] == loc2]

if (loc1 == loc2):
    st.warning("Same location selected in both")
else:

    loc1_temp_diff = (loc1_df.iloc[0]['raw_temp']- loc2_df.iloc[0]['raw_temp'])
    loc2_temp_diff = (loc2_df.iloc[0]['raw_temp']- loc1_df.iloc[0]['raw_temp'])

    with col1:
        st.markdown(f"# {loc1}")
        st.metric(
                label="Temperature", 
                value=loc1_df.iloc[0]['temperature'], 
                delta=f"{loc1_temp_diff} °F"
            )
        st.text(f"Time: {loc1_df.iloc[0]['time']}")

    with col2:
        st.markdown(f"# {loc2}")
        st.metric(
            label="Temperature", 
            value=loc2_df.iloc[0]['temperature'], 
            delta=f"{loc2_temp_diff} °F"
        )
        st.text(f"Time: {loc2_df.iloc[0]['time']}")

all_data = all_data.sort_values(by=['raw_time', 'raw_temp'])
fig = px.scatter(all_data, x='temperature', y='time',
                hover_name='location', title="Temperature vs. Time")
st.plotly_chart(fig)