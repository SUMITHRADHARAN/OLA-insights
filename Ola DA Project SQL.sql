-- Block 1: Database Setup
CREATE DATABASE IF NOT EXISTS Ola;
USE Ola;

-- Block 2: Table Creation
CREATE TABLE IF NOT EXISTS bookings (
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
);

-- Block 3: View Creation (Execute these one by one in Python)

-- Note: You should import your CSV data here before proceeding.
-- Without data, the following SELECT and CREATE VIEW statements will return empty results.

-- 1. Retrieve all successful bookings
CREATE OR REPLACE VIEW Success_Booking AS 
SELECT * FROM book WHERE Booking_Status = 'Success';

-- 2. Find the average ride distance for each vehicle type
CREATE OR REPLACE VIEW average_ride_distance_for_each_vehicle AS 
SELECT Vehicle_Type, AVG(Ride_Distance) AS avg_distance FROM book GROUP BY Vehicle_Type;

-- 3. Get the total number of cancelled rides by customers
CREATE OR REPLACE VIEW number_of_cancelled_rides AS 
SELECT COUNT(*) AS total_cancelled FROM book WHERE Booking_Status = 'Canceled by Customer';

-- 4. List the top 5 customers who booked the highest number of rides
CREATE OR REPLACE VIEW top_5_customers AS 
SELECT Customer_ID, COUNT(Booking_ID) AS total_rides FROM book GROUP BY Customer_ID ORDER BY total_rides DESC LIMIT 5;

-- 5. Get the number of rides cancelled by drivers due to personal/car issues
CREATE OR REPLACE VIEW rides_cancelled_by_drivers AS 
SELECT COUNT(*) AS cancelled_count FROM book WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- 6. Find max and min driver ratings for Prime Sedan
CREATE OR REPLACE VIEW Max_Min_Driver_Rating AS 
SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating FROM book WHERE Vehicle_Type = 'Prime Sedan';

-- 7. Retrieve all rides using UPI
CREATE OR REPLACE VIEW UPI_payments AS 
SELECT * FROM book WHERE Payment_Method = 'UPI';

-- 8. Find average customer rating per vehicle type
CREATE OR REPLACE VIEW avg_rating_for_v_type AS 
SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 1) AS avg_rating FROM book GROUP BY Vehicle_Type;

-- 9. Calculate total booking value of successful rides
CREATE OR REPLACE VIEW total_booking_value_rides_completed AS 
SELECT SUM(Booking_Value) AS total_successful_value FROM book WHERE Booking_Status = 'Success';

-- 10. List all incomplete rides along with the reason
CREATE OR REPLACE VIEW Incomplete_Rides_Reason_View AS 
SELECT Booking_ID, Incomplete_Rides_Reason FROM book WHERE Incomplete_Rides = 'Yes';
