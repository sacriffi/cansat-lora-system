# Detailed Wiring Guide

## Raspberry Pi Pico 2 Pin Layout

```
   USB Port
     ||
   -----
  |     |
  | RPI |
  | 2   |
  |     |
  |     |
   -----

GPIO Pins (left side):  GPIO Pins (right side):
GP0  (Pin 1)           GP1  (Pin 2)
GP2  (Pin 4)           GP3  (Pin 5)  
GP4  (Pin 6)           GP5  (Pin 7)
GP6  (Pin 9)           GP7  (Pin 10)
GP8  (Pin 11)          GP9  (Pin 12)
GP10 (Pin 14)          GP11 (Pin 15)
GP12 (Pin 16)          GP13 (Pin 17)
GP14 (Pin 19)          GP15 (Pin 20)
GP16 (Pin 21)          GP17 (Pin 22)
GP18 (Pin 24)          GP19 (Pin 25)
GP20 (Pin 26)          GP21 (Pin 27)
GP22 (Pin 29)          GND  (Pin 28/30)
3.3V (Pin 36)          GND  (Pin 38)
VBUS (Pin 40)          GND  (Pin 39)
```

## BMP280 I2C Connection

### I2C Bus Mapping (Pico 2)
- **I2C0**: SDA=GP0, SCL=GP1
- **I2C1**: SDA=GP2, SCL=GP3

### Recommended Configuration (I2C0)

| BMP280 Pin | Pico 2 Pin | Description |
|-----------|-----------|-------------|
| VCC       | 3V3(OUT)  | Power (3.3V) |
| GND       | GND       | Ground |
| SCL       | GP1       | I2C Clock |
| SDA       | GP0       | I2C Data |
| SDO       | GND       | I2C Address Select (0x77 when GND) |
| CSB       | NC        | SPI Chip Select (not used in I2C mode) |

### Alternate Configuration (I2C1)
If you need to use I2C1:
```python
i2c = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
```

### I2C Pull-up Resistors
- BMP280 breakout boards usually have built-in pull-ups (4.7k ohm)
- If not included, add 4.7k resistors between SCL/SDA and 3.3V

## SX127x LoRa Module SPI Connection

### SPI Bus Mapping (Pico 2)
- **SPI0**: SCK=GP2, MOSI=GP3, MISO=GP4
- **SPI1**: SCK=GP10, MOSI=GP11, MISO=GP12

### Recommended Configuration (SPI0)

| SX127x Pin | Pico 2 Pin | Description |
|-----------|-----------|-------------|
| VCC       | 3V3(OUT)  | Power (3.3V) |
| GND       | GND       | Ground |
| SCK       | GP2       | SPI Clock |
| MOSI      | GP3       | SPI Master Out |
| MISO      | GP4       | SPI Master In |
| CS/NSS    | GP5       | Chip Select |
| RST       | GP8       | Reset (active low) |
| DIO0      | GP9       | Interrupt (RX Done/TX Done) |
| DIO1      | NC        | Not required for basic operation |
| DIO2      | NC        | Not required for basic operation |
| DIO3      | NC        | Not required for basic operation |
| DIO4      | NC        | Not required for basic operation |
| DIO5      | NC        | Not required for basic operation |
| GND       | GND       | Ground |

### Alternate Configuration (SPI1)
If you need to use SPI1:
```python
spi = machine.SPI(1, baudrate=10000000, sck=machine.Pin(10), 
                  mosi=machine.Pin(11), miso=machine.Pin(12))
```

## Power Supply Considerations

### Current Requirements
- **Pico 2**: ~50-100 mA (normal operation)
- **BMP280**: ~0.7-2 mA (very low power)
- **SX127x LoRa**:
  - RX Mode: ~80-90 mA
  - TX Mode: 25-250 mA (depending on power setting)
  - Sleep Mode: ~1-10 µA

### Total Current
- **Idle**: ~50-100 mA
- **Receiving**: ~130-200 mA
- **Transmitting**: ~150-350 mA (with 20 dBm power)

### Power Supply Recommendations
- Use a 3.3V power supply rated for **at least 500 mA**
- Add **100 µF capacitor** between VCC and GND near LoRa module
- Add **10 µF capacitor** between VCC and GND near BMP280
- Use short, thick wires for power distribution
- Consider **LiPo battery** (3.7V with 5V USB boost converter) for field deployment

## Antenna Connection

### Antenna Requirements
- **Frequency**: 915 MHz (for ISM band, may vary by region)
- **Impedance**: 50 Ω
- **Length**: ~82 mm quarter-wave monopole OR 165 mm half-wave dipole
- **Type**: Recommended - flexible wire antenna or commercial 915 MHz antenna

### Simple Dipole Antenna Construction
```
Frequency: 915 MHz
Wavelength: ~327 mm
Half-wave dipole: 327/2 = ~165 mm
Quarter-wave monopole: 327/4 = ~82 mm

Simple construction:
- Solid copper wire 1-2 mm diameter
- Insulated with PVC or Teflon
- Solder to module antenna connector
```

## Complete Wiring Table

| Component | Pin | Pico 2 Pin | Function |
|-----------|-----|-----------|----------|
| **BMP280** |
| VCC | - | 3V3(OUT) | Power |
| GND | - | GND | Ground |
| SCL | - | GP1 | I2C Clock |
| SDA | - | GP0 | I2C Data |
| SDO | - | GND | Address Select |
| **SX127x** |
| VCC | - | 3V3(OUT) | Power |
| GND | - | GND | Ground |
| SCK | - | GP2 | SPI Clock |
| MOSI | - | GP3 | SPI MOSI |
| MISO | - | GP4 | SPI MISO |
| CS | - | GP5 | Chip Select |
| RST | - | GP8 | Reset |
| DIO0 | - | GP9 | IRQ |

## Troubleshooting Connections

### I2C Issues
```python
# Check if BMP280 is detected
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))
devices = i2c.scan()
print(devices)  # Should show [119] for 0x77 or [118] for 0x76
```

### SPI Issues
```python
# Test SPI communication
spi = machine.SPI(0, baudrate=10000000, sck=machine.Pin(2), 
                  mosi=machine.Pin(3), miso=machine.Pin(4))
cs = machine.Pin(5, machine.Pin.OUT)
cs.value(0)
spi.write(b'\x42')  # Read version register
version = spi.read(1)
cs.value(1)
print(version)  # Should read LoRa module version
```

## Cable Length Guidelines

- **I2C**: Keep under 1 meter (use twisted pair if longer)
- **SPI**: Keep under 1 meter (use shielded cable for noisy environments)
- **Antenna**: Can be at distance, use SMA/N-type connector

## Board Layout Tips

1. **Separation**: Keep LoRa module away from CPU if possible
2. **Shielding**: Use Faraday cage around LoRa module if experiencing interference
3. **Heat**: Ensure adequate cooling for long TX transmissions
4. **Mounting**: Use non-conductive standoffs to prevent shorts
5. **Cable Routing**: Keep signal wires away from power wires
