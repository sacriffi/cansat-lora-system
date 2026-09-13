# BMP280 Driver for MicroPython
# Pressure and Temperature Sensor

import ustruct
import utime

# BMP280 Register addresses
BMP280_I2CADDR = 0x77
BMP280_CHIPID = 0x58

REG_ID = 0xD0
REG_RESET = 0xE0
REG_STATUS = 0xF3
REG_CONTROL = 0xF4
REG_CONFIG = 0xF5
REG_PRESSURE = 0xF7
REG_TEMPERATURE = 0xFA
REG_HUMIDITY = 0xFD
REG_CALIB_START = 0x88

class BMP280:
    def __init__(self, i2c, addr=BMP280_I2CADDR):
        self.i2c = i2c
        self.addr = addr
        self.calib_temp = None
        self.calib_press = None
        self.t_fine = 0
        
        # Check device ID
        chip_id = self.i2c.readfrom_mem(self.addr, REG_ID, 1)[0]
        if chip_id != BMP280_CHIPID:
            raise ValueError(f"BMP280 not found. ID: {chip_id}")
        
        # Reset device
        self.i2c.writeto_mem(self.addr, REG_RESET, b'\xB6')
        utime.sleep_ms(10)
        
        # Read calibration data
        self._read_calib()
        
        # Configure sensor
        # Standby time: 1000 ms
        # Filter coefficient: 16
        self.i2c.writeto_mem(self.addr, REG_CONFIG, b'\xA0')
        
        # Control register: Temperature x2, Pressure x4, Normal mode
        self.i2c.writeto_mem(self.addr, REG_CONTROL, b'\x57')
        
        utime.sleep_ms(10)
    
    def _read_calib(self):
        """Read calibration coefficients"""
        calib = self.i2c.readfrom_mem(self.addr, REG_CALIB_START, 26)
        
        # Temperature calibration
        self.calib_temp = [
            ustruct.unpack('<H', calib[0:2])[0],
            ustruct.unpack('<h', calib[2:4])[0],
            ustruct.unpack('<h', calib[4:6])[0]
        ]
        
        # Pressure calibration
        self.calib_press = [
            ustruct.unpack('<H', calib[6:8])[0],
            ustruct.unpack('<h', calib[8:10])[0],
            ustruct.unpack('<h', calib[10:12])[0],
            ustruct.unpack('<h', calib[12:14])[0],
            ustruct.unpack('<h', calib[14:16])[0],
            ustruct.unpack('<h', calib[16:18])[0],
            ustruct.unpack('<h', calib[18:20])[0],
            ustruct.unpack('<h', calib[20:22])[0],
            ustruct.unpack('<h', calib[22:24])[0]
        ]
    
    def _read_raw(self):
        """Read raw ADC values"""
        data = self.i2c.readfrom_mem(self.addr, REG_PRESSURE, 6)
        
        # Extract raw values
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        
        return adc_p, adc_t
    
    def _compensate_temp(self, adc_t):
        """Compensate temperature reading"""
        var1 = (adc_t >> 3) - (self.calib_temp[0] << 1)
        var2 = (var1 * self.calib_temp[1]) >> 11
        var3 = ((var1 >> 1) * (var1 >> 1)) >> 12
        var3 = ((var3) * (self.calib_temp[2])) >> 14
        
        self.t_fine = var2 + var3
        return (self.t_fine * 5 + 128) >> 8
    
    def _compensate_press(self, adc_p):
        """Compensate pressure reading"""
        var1 = (self.t_fine >> 1) - 64000
        var2 = (((var1 >> 2) * (var1 >> 2)) >> 11) * (self.calib_press[5])
        var2 = var2 + ((var1 * (self.calib_press[4])) << 1)
        var2 = (var2 >> 2) + ((self.calib_press[3]) << 16)
        var1 = (((self.calib_press[2] * (((var1 >> 2) * (var1 >> 2)) >> 13)) >> 3) +
                ((self.calib_press[1] * var1) >> 1)) >> 18
        var1 = ((32768 + var1) * (self.calib_press[0])) >> 15
        
        if var1 == 0:
            return 0
        
        pressure = (((1048576 - adc_p) - (var2 >> 12)) * 3125) // var1
        var1 = (((pressure >> 3) * (pressure >> 3)) >> 13)
        var2 = ((self.calib_press[6] * pressure) >> 13)
        pressure = pressure + (((var1 + var2 + self.calib_press[7]) >> 4))
        
        return pressure
    
    @property
    def temperature(self):
        """Get temperature in Celsius"""
        adc_p, adc_t = self._read_raw()
        temp_raw = self._compensate_temp(adc_t)
        return temp_raw / 100.0
    
    @property
    def pressure(self):
        """Get pressure in Pa"""
        adc_p, adc_t = self._read_raw()
        self._compensate_temp(adc_t)
        pressure = self._compensate_press(adc_p)
        return pressure / 100.0  # Return in Pa
    
    @property
    def altitude(self):
        """Get altitude in meters (sea level = 101325 Pa)"""
        pressure = self.pressure
        altitude = 44330 * (1.0 - ((pressure / 101325.0) ** (1.0 / 5.255)))
        return altitude
