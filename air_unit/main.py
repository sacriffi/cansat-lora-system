# CanSat Air Unit - BMP280 + LoRa Transmitter
# Raspberry Pi Pico 2 with MicroPython
# Reads BMP280 sensor and transmits data via LoRa

import machine
import utime
from bmp280 import BMP280
from sx127x import SX127x
import sys

# I2C and SPI configuration
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=400000)
spi = machine.SPI(0, baudrate=10000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))

# BMP280 initialization
bmp280 = BMP280(i2c=i2c, addr=0x77)

# LoRa module initialization
cs_pin = machine.Pin(5, machine.Pin.OUT)
reset_pin = machine.Pin(8, machine.Pin.OUT)
di0_pin = machine.Pin(9, machine.Pin.IN)

lora = SX127x(spi, cs_pin, reset_pin, di0_pin)
lora.init()
lora.set_frequency(433e6)  # 433 MHz frequency, it is the same as the ground unit
lora.set_tx_power(20)  # 20 dBm
lora.set_spreading_factor(7)
lora.set_bandwidth(125000)

print("Air Unit Initialized")
print("BMP280 Sensor Ready")
print("LoRa Transmitter Ready (433 MHz)")

def read_sensors():
    """Read BMP280 sensor data"""
    try:
        temperature = bmp280.temperature
        pressure = bmp280.pressure
        altitude = bmp280.altitude
        return {
            'temp': temperature,
            'pressure': pressure,
            'altitude': altitude
        }
    except Exception as e:
        print(f"Error reading BMP280: {e}")
        return None

def format_data(sensor_data, packet_num):
    """Format sensor data for transmission"""
    if sensor_data is None:
        return None
    
    data = f"{packet_num},{sensor_data['temp']:.2f},{sensor_data['pressure']:.2f},{sensor_data['altitude']:.2f}"
    return data

def transmit_data(data):
    """Transmit data via LoRa"""
    try:
        lora.send(data.encode())
        print(f"Transmitted: {data}")
        return True
    except Exception as e:
        print(f"Error transmitting: {e}")
        return False

# Main loop
packet_count = 0
while True:
    try:
        # Read sensor data
        sensor_data = read_sensors()
        
        # Format and transmit
        if sensor_data:
            packet_count += 1
            formatted_data = format_data(sensor_data, packet_count)
            transmit_data(formatted_data)
        
        # Wait 5 seconds before next transmission
        utime.sleep(5)
        
    except KeyboardInterrupt:
        print("Air Unit Stopped")
        break
    except Exception as e:
        print(f"Error in main loop: {e}")
        utime.sleep(1)
