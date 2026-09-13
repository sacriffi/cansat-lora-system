# CanSat LoRa System

A complete CanSat system for Raspberry Pi Pico 2 that reads environmental sensor data and transmits it wirelessly via LoRa to a ground station.

## System Overview

This project consists of two main components:

### Air Unit
- **Sensor**: BMP280 (Barometric Pressure, Temperature)
- **Communication**: SX127x LoRa Transmitter
- **Data**: Temperature, Pressure, Altitude
- **Location**: `air_unit/main.py`

### Ground Station
- **Communication**: SX127x LoRa Receiver
- **Data Storage**: CSV file logging
- **Output**: `cansat_data.csv`
- **Location**: `ground_station/main.py`

## Hardware Requirements

### Air Unit
- Raspberry Pi Pico 2
- BMP280 Breakout Board
- SX127x LoRa Module (915 MHz)
- Antenna

### Ground Station
- Raspberry Pi Pico 2 (or any computer with serial access)
- SX127x LoRa Module (915 MHz)
- Antenna

## Wiring Diagram

### BMP280 to Pico 2 (I2C)
```
BMP280   ->  Pico 2
VCC      ->  3.3V
GND      ->  GND
SCL      ->  GPIO 1
SDA      ->  GPIO 0
SDO      ->  GND (sets address to 0x77)
```

### SX127x LoRa Module to Pico 2 (SPI)
```
SX127x   ->  Pico 2
VCC      ->  3.3V
GND      ->  GND
SCK      ->  GPIO 2  (SPI0 SCK)
MOSI     ->  GPIO 3  (SPI0 MOSI)
MISO     ->  GPIO 4  (SPI0 MISO)
CS       ->  GPIO 5
RST      ->  GPIO 8
DIO0     ->  GPIO 9
```

## Installation

1. **Install MicroPython** on Raspberry Pi Pico 2
   - Download from: https://micropython.org/download/rp2-pico2/
   - Flash using `rshell` or `mpremote`

2. **Upload Files**
   ```bash
   # Using mpremote
   mpremote cp bmp280.py :/bmp280.py
   mpremote cp sx127x.py :/sx127x.py
   
   # For air unit
   mpremote cp air_unit/main.py :/main.py
   
   # For ground station
   mpremote cp ground_station/main.py :/main.py
   ```

3. **Run the Code**
   - The code will start automatically on boot
   - Or run manually: `mpremote run main.py`

## Configuration

### Air Unit Settings (air_unit/main.py)
```python
lora.set_frequency(915e6)      # LoRa frequency (Hz)
lora.set_tx_power(20)          # TX power (2-20 dBm)
lora.set_spreading_factor(7)   # SF (6-12, higher = longer range)
lora.set_bandwidth(125000)     # Bandwidth (125k, 250k, 500k)
utime.sleep(5)                 # Transmission interval (seconds)
```

### Ground Station Settings (ground_station/main.py)
```python
lora.set_frequency(915e6)      # Must match air unit
lora.set_spreading_factor(7)   # Must match air unit
lora.set_bandwidth(125000)     # Must match air unit
```

## Data Format

### LoRa Transmission Format
```
Packet_Number,Temperature(C),Pressure(Pa),Altitude(m)
Example: 1,25.45,101325.50,10.23
```

### CSV Output Format
```csv
Packet_Number,Temperature(C),Pressure(Pa),Altitude(m),Timestamp(s),RSSI,SNR
1,25.45,101325.50,10.23,1234567890,-85,-2.5
```

- **Packet_Number**: Sequential packet count
- **Temperature(C)**: Temperature in Celsius
- **Pressure(Pa)**: Pressure in Pascals
- **Altitude(m)**: Altitude above sea level in meters
- **Timestamp(s)**: Unix timestamp when received
- **RSSI**: Received Signal Strength Indicator (dBm)
- **SNR**: Signal to Noise Ratio (dB)

## Troubleshooting

### BMP280 Not Found
- Check I2C wiring
- Verify address: 0x77 (SDO to GND) or 0x76 (SDO to VCC)
- Use `i2c.scan()` to verify device is detected

### LoRa Module Not Communicating
- Verify SPI wiring
- Check frequency matches between air and ground units
- Ensure antennas are properly connected
- Check power supply (LoRa modules draw significant current)

### CSV Not Being Created
- Check filesystem permissions
- Ensure ground station has write access
- Verify file path is correct

### No Data Reception
- Verify spreading factor and bandwidth match
- Check transmit power setting
- Ensure both modules are on same frequency
- Verify antenna connections and orientation

## Performance

- **Range**: Up to 15+ km (line of sight with good antennas)
- **Data Rate**: Depends on spreading factor (SF7: ~5.5 kbps)
- **Transmission Interval**: Default 5 seconds (adjustable)
- **Packet Size**: ~40 bytes per transmission

## Power Consumption

- **Air Unit**: ~100-200 mA during transmission, 5-10 mA standby
- **Ground Station**: ~50-100 mA during reception
- **Battery Life**: Depends on capacity and transmission interval

## Future Enhancements

- [ ] Add GPS module support
- [ ] Add accelerometer/gyroscope data
- [ ] Implement error correction (Reed-Solomon)
- [ ] Add data compression
- [ ] Implement acknowledgment system
- [ ] Add web dashboard for real-time monitoring
- [ ] SD card data logging for ground station

## References

- [BMP280 Datasheet](https://www.bosch-sensortec.com/media/boschsensortec_content/documents/bstsensortec_content/datasheets/bst-bmp280-ds002.pdf)
- [SX127x Datasheet](https://www.semtech.com/uploads/documents/DS_SX1276-7-8-9_W_APP_V5.pdf)
- [MicroPython Documentation](https://docs.micropython.org/)
- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)

## License

MIT License - See LICENSE file for details
