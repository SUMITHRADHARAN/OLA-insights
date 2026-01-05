import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from sqlalchemy import create_engine, text
import pymysql
import urllib.parse

# Initial Page Config
st.set_page_config(layout="wide", page_title="Ola Analytics 2026")
st.title("OLA DATA ANALYTICS DASHBOARD")

# --- STEP 1: DATABASE INITIALIZATION ---
# Using standard engine to handle DDL (Create DB/Tables/Views)
def initialize_db():
    # Update credentials as per your 2026 MySQL setup
    # Using 127.0.0.1 to avoid hostname parsing errors with the @ symbol in the password
    # Ensure this password exactly matches your MySQL root password
    engine = create_engine("mysql+pymysql://root:dm3879%40D@127.0.0.1")
    
    setup_commands = [
        "CREATE DATABASE IF NOT EXISTS Ola",
        "USE Ola",
        """CREATE TABLE IF NOT EXISTS bookings (
            Booking_ID VARCHAR(50) PRIMARY KEY,
            Booking_Status VARCHAR(50),
            Vehicle_Type VARCHAR(50),
            Ride_Distance DECIMAL(10,2),
            Customer_ID VARCHAR(50),
            Canceled_Rides_by_Driver VARCHAR(100),
            Driver_Ratings DECIMAL(3,1),
            Customer_Rating DECIMAL(3,1),
            Payment_Method VARCHAR(50),
            Booking_Value INT,
            Incomplete_Rides VARCHAR(5),
            Incomplete_Rides_Reason VARCHAR(255)
        )""",
        # ...
        "CREATE OR REPLACE VIEW Success_Booking AS SELECT * FROM book WHERE Booking_Status = 'Success'",
        "CREATE OR REPLACE VIEW average_ride_distance_for_each_vehicle AS SELECT Vehicle_Type, AVG(Ride_Distance) AS avg_distance FROM book GROUP BY Vehicle_Type;",
        # ADD A COMMA ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        "CREATE OR REPLACE VIEW number_of_cancelled_rides AS SELECT COUNT(*) AS total_cancelled FROM book WHERE Booking_Status = 'Canceled by Customer'",
        "CREATE OR REPLACE VIEW top_5_customers AS SELECT Customer_ID, COUNT(Booking_ID) AS total_rides FROM book GROUP BY Customer_ID ORDER BY total_rides DESC LIMIT 5;",
        "CREATE OR REPLACE VIEW rides_cancelled_by_drivers AS SELECT COUNT(*) AS cancelled_count FROM book WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';", # Check this comma
        "CREATE OR REPLACE VIEW Max_Min_Driver_Rating AS SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating FROM book WHERE Vehicle_Type = 'Prime Sedan';", # Check this comma
        "CREATE OR REPLACE VIEW UPI_payments AS SELECT * FROM book WHERE Payment_Method = 'UPI';", # Check this comma
        "CREATE OR REPLACE VIEW avg_rating_for_v_type AS SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 1) AS avg_rating FROM book GROUP BY Vehicle_Type;", # Check this comma
        "CREATE OR REPLACE VIEW total_booking_value_rides_completed AS SELECT SUM(Booking_Value) AS total_successful_value FROM book WHERE Booking_Status = 'Success';", # Check this comma
        "CREATE OR REPLACE VIEW Incomplete_Rides_Reason_View AS SELECT Booking_ID, Incomplete_Rides_Reason FROM book WHERE Incomplete_Rides = 'Yes';" # Check final comma
    ]
    try:
        with engine.connect() as conn:
            for cmd in setup_commands:
                conn.execute(text(cmd))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        st.info("Check if your MySQL server is running and the connection string is accurate.")
        return False

# --- STEP 2: LOAD DATA ---
if initialize_db():
    try:
        # st.connection uses settings from .streamlit/secrets.toml
        # This uses the connection settings from the TOML file for the rest of the dashboard interactions
        conn = st.connection("mysql", type="sql")

        # Sidebar Filters
        st.sidebar.header("Dashboard Filters")
        vehicle_filter = st.sidebar.multiselect(
            "Select Vehicle Type", 
            options=["Prime Sedan", "Prime SUV", "Prime plus", "Mini","Auto", "Bike","E-Bike"],
            default=["Auto", "Prime Sedan"]
        )

        # Main Query Execution
        query = "SELECT * FROM Success_Booking"
        if vehicle_filter:
            # Safely format the list of vehicle types for the SQL IN clause
            filter_tuple = tuple(vehicle_filter)
            if len(filter_tuple) == 1:
                 # Handle single item tuple formatting for SQL IN clause
                query += f" WHERE Vehicle_Type IN ('{filter_tuple[0]}')"
            else:
                query += f" WHERE Vehicle_Type IN {filter_tuple}"

        df = conn.query(query, ttl="10m")

        # --- STEP 3: DISPLAY RESULTS ---
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Booking Data Overview")
            st.dataframe(df, use_container_width=True)

        with col2:
            st.subheader("Key Metrics")
            if not df.empty:
                st.metric("Total Revenue", f"₹{df['Booking_Value'].sum():,}")
                st.metric("Avg Ride Distance", f"{round(df['Ride_Distance'].mean(), 2)} km")

                # --- STEP 4: EMBED POWER BI ---
        st.divider()
        st.subheader("Power BI Deep Dive")
       # Base URL
        pbi_url = "https://app.powerbi.com/reportEmbed?reportId=05950598-9e8b-4e9e-9a57-57cf1e7cbe0e&autoAuth=true&ctid=f3c9ebc3-0543-43d8-9cac-9db513a7c000"
        # Syntax: &$filter=TableName/ColumnName in ('Val1', 'Val2')
        if vehicle_filter:
            # Safely format the list of vehicle types for the SQL IN clause
            filter_values = ", ".join([f"'{v}'" for v in vehicle_filter])
            pbi_filter = f"&$filter=book/Vehicle_Type in ({filter_values})"
            
            # CRITICAL: Encode only the *filter* part of the URL
            encoded_filter = urllib.parse.quote(pbi_filter, safe="&$=")
            pbi_url += encoded_filter # Append the safe, encoded string

        # Embed the final, filtered URL
        components.iframe(pbi_url, height=800, scrolling=True) 
    except Exception as e:
        st.error(f"Dashboard Load Error: {e}")
