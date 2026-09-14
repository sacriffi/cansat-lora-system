# CanSat Ground Station - LoRa Receiver + CSV Logger
# Raspberry Pi Pico 2 with MicroPython
# Receives LoRa data and logs to CSV file

import machine
import utime
from sx127x import SX127x
import os

# SPI configuration for LoRa module
spi = machine.SPI(0, baudrate=10000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))

# LoRa module initialization
cs_pin = machine.Pin(5, machine.Pin.OUT)
reset_pin = machine.Pin(8, machine.Pin.OUT)
di0_pin = machine.Pin(9, machine.Pin.IN)

lora = SX127x(spi, cs_pin, reset_pin, di0_pin)
lora.init()
lora.set_frequency(433e6)  # Our Lora is 433MHz it should match the air unit
lora.set_spreading_factor(7)
lora.set_bandwidth(125000)
lora.enable_crc()

print("Ground Station Initialized")
print("LoRa Receiver Ready")

# CSV file setup
CSV_FILENAME = "cansat_data.csv"
CSV_HEADER = "Packet_Number,Temperature(C),Pressure(Pa),Altitude(m),Timestamp(s),RSSI,SNR\n"

def init_csv_file():
    """Initialize CSV file with headers"""
    try:
        # Check if file exists
        files = os.listdir()
        if CSV_FILENAME not in files:
            with open(CSV_FILENAME, 'w') as f:
                f.write(CSV_HEADER)
            print(f"Created {CSV_FILENAME}")
        else:
            print(f"{CSV_FILENAME} already exists")
    except Exception as e:
        print(f"Error initializing CSV: {e}")

def log_to_csv(packet_num, temperature, pressure, altitude, rssi, snr):
    """Log sensor data to CSV file"""
    try:
        timestamp = utime.time()
        data_line = f"{packet_num},{temperature},{pressure},{altitude},{timestamp},{rssi},{snr}\n"
        
        with open(CSV_FILENAME, 'a') as f:
            f.write(data_line)
        
        print(f"Logged to CSV: P{packet_num} | T:{temperature}C | P:{pressure}Pa | A:{altitude}m")
        return True
    except Exception as e:
        print(f"Error logging to CSV: {e}")
        return False

def receive_and_log():
    """Receive LoRa data and log to CSV"""
    try:
        # Check if data is available
        if lora.receive_irq():
            # Get received data
            payload = lora.recv()
            
            if payload:
                # Decode data
                data_str = payload.decode('utf-8').strip()
                print(f"Received: {data_str}")
                
                # Parse data: packet_num,temp,pressure,altitude
                parts = data_str.split(',')
                
                if len(parts) == 4:
                    packet_num = parts[0]
                    temperature = parts[1]
                    pressure = parts[2]
                    altitude = parts[3]
                    
                    # Get signal strength
                    rssi = lora.get_rssi()
                    snr = lora.get_snr() if hasattr(lora, 'get_snr') else 'N/A'
                    
                    # Log to CSV
                    log_to_csv(packet_num, temperature, pressure, altitude, rssi, snr)
                else:
                    print(f"Invalid data format: {data_str}")
    except Exception as e:
        print(f"Error receiving data: {e}")

# Initialize CSV file
init_csv_file()

print("Waiting for LoRa transmissions...")
start_time = utime.time()

# Main reception loop
try:
    while True:
        receive_and_log()
        utime.sleep(0.1)  # Small delay to prevent CPU overload
except KeyboardInterrupt:
    print("\nGround Station Stopped")
    print(f"Data logged to {CSV_FILENAME}")
