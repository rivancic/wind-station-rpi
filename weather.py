from gpiozero import Button
from signal import pause
import requests
from datetime import datetime
import time
from threading import Timer
import os

# Initialize GPIO pin 5 as a Button (input pin)
interruption_pin = Button(5)

# Constants
ROTATIONS_PER_SECOND_TO_MPS = 40 / 50  # Conversion factor based on specification 50 rotations per second translates to 40 meter per second wind speed
MPS_TO_MPH = 2.23694  # Conversion from m/s to mph
  
# Global variables
rotation_count = 0
wind_speed_mph = 0

# WU credentials
STATION_ID = os.getenv("STATION_ID")
STATION_KEY = os.getenv("STATION_KEY")


###################################
#   Will upload wind data to WU   #
###################################
def upload_to_wu():

  # WU credentials
  global STATION_ID, STATION_KEY

  # Format the URL
  upload_url = (
    f"https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?"
    f"ID={STATION_ID}&PASSWORD={STATION_KEY}&dateutc=now"
    f"&windspeedmph={wind_speed_mph}&action=updateraw"
  )

  try:
    # Send the data
    response = requests.get(upload_url)

    if response.status_code == 200:
      print("Data uploaded successfully!")
    else:
      print(f"Failed to upload data. Status code: {response.status_code}")
  
  except requests.exceptions.ConnectionError as e:
    print("Can't connect and upload wind speed to WU:", e)


#########################################################################################
#         Calculate the wind speed from the number of rotations in the last minute.     #       
#########################################################################################   
def calculate_wind_speed():
    global rotation_count, wind_speed_mph

    # Calculate wind speed in m/s
    rotations_per_second = rotation_count / 60.0  # Count per minute to per second
    wind_speed_mps = rotations_per_second * ROTATIONS_PER_SECOND_TO_MPS

    # Convert to mph
    wind_speed_mph = wind_speed_mps * MPS_TO_MPH

    # Reset the rotation count for the next minute
    rotation_count = 0

    # Send wind speed data
    # TODO send_wind_speed_to_wunderstation(wind_speed_mph)
    print("Average wind speed 1min : " + str(wind_speed_mph) + "mps")
    upload_to_wu()

    # Schedule the next calculation
    Timer(60.0, calculate_wind_speed).start()


#################################################################################
#       Callback functions to handle interruption/anemometer rotation state     #
#################################################################################
def anemometer_rotation():
    global rotation_count
    rotation_count += 1
    # debugging print 
    # print("GPIO 5 is HIGH (anemometer rotated), count is: " + str(rotation_count))
    
###################################
#         Main program            #
###################################
print("Wind speed measurement started for station: " + STATION_ID)

# Assign the callback functions to the button
interruption_pin.when_pressed = anemometer_rotation

# Start wind speed measurement
Timer(60.0, calculate_wind_speed).start()

print("Listening to GPIO 5...")
# Keep the program running to listen for button state changes
pause()




