import serial
import time
# Define the serial port and baud rate for communication
ser = serial.Serial('/dev/tty8', 9600)
# Adjust the port as needed
try:
  while True:         
  # Read a line from the serial port         
    line = ser.readline().decode().strip()
    # Check if the line contains distance data
    if line.startswith("Distance"):
      print(line)
      # Add a short delay to avoid overwhelming the serial buffer
    time.sleep(0.1)
except KeyboardInterrupt:     # Close the serial port on keyboard interrupt     
  ser.close()
print("Serial port closed.")