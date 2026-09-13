# SX127x LoRa Driver for MicroPython
# LoRa Transceiver Module

import ustruct
import utime

# Register addresses
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_FRF_MSB = 0x06
REG_FRF_MID = 0x07
REG_FRF_LSB = 0x08
REG_PA_CONFIG = 0x09
REG_PA_RAMP = 0x0A
REG_OCP = 0x0B
REG_LNA = 0x0C
REG_FIFO_ADDR_PTR = 0x0D
REG_FIFO_TX_BASE_ADDR = 0x0E
REG_FIFO_RX_BASE_ADDR = 0x0F
REG_FIFO_RX_CURRENT_ADDR = 0x10
REG_IRQ_FLAGS_MASK = 0x11
REG_IRQ_FLAGS = 0x12
REG_RX_NB_BYTES = 0x13
REG_RX_HEADER_CNT_VALUE_MSB = 0x14
REG_RX_HEADER_CNT_VALUE_LSB = 0x15
REG_RX_PACKET_CNT_VALUE_MSB = 0x16
REG_RX_PACKET_CNT_VALUE_LSB = 0x17
REG_MODEM_STAT = 0x18
REG_PKT_SNR_VALUE = 0x19
REG_PKT_RSSI_VALUE = 0x1A
REG_RSSI_VALUE = 0x1B
REG_HOP_CHANNEL = 0x1C
REG_MODEM_CONFIG_1 = 0x1D
REG_MODEM_CONFIG_2 = 0x1E
REG_SYMB_TIMEOUT = 0x1F
REG_PREAMBLE_MSB = 0x20
REG_PREAMBLE_LSB = 0x21
REG_PAYLOAD_LENGTH = 0x22
REG_MAX_PAYLOAD_LENGTH = 0x23
REG_HOP_PERIOD = 0x24
REG_FIFO_RX_BYTE_ADDR = 0x25
REG_MODEM_CONFIG_3 = 0x26
REG_FREQ_ERROR_MSB = 0x28
REG_FREQ_ERROR_MID = 0x29
REG_FREQ_ERROR_LSB = 0x2A
REG_WAVEFORM_DETECTION = 0x2B
REG_WAVEFORM_THRESHOLD = 0x2C
REG_SYNC_WORD = 0x39
REG_VERSION = 0x42
REG_AGCREF = 0x43
REG_AGCTHRESH1 = 0x44
REG_AGCTHRESH2 = 0x45
REG_AGCTHRESH3 = 0x46
REG_PLL_HOP = 0x4B
REG_TCXO = 0x4B
REG_PA_DAC = 0x4D
REG_FORMER_TEMP = 0x5B
REG_BIT_RATE_FRAC = 0x5D
REG_AGCREF_THRESH3 = 0x46

# Modes
MODE_SLEEP = 0x80
MODE_STANDBY = 0x81
MODE_TX = 0x83
MODE_RX = 0x82
MODE_RX_CONTINUOUS = 0x85

# DIO mappings
DIO0_RX_DONE = 0x00
DIO0_TX_DONE = 0x40

class SX127x:
    def __init__(self, spi, cs, reset, di0):
        self.spi = spi
        self.cs = cs
        self.reset = reset
        self.di0 = di0
        self.freq = 915e6
        self.tx_power = 20
        self.spreading_factor = 7
        self.bandwidth = 125000
    
    def init(self):
        """Initialize LoRa module"""
        # Reset module
        self.reset.value(0)
        utime.sleep_ms(10)
        self.reset.value(1)
        utime.sleep_ms(10)
        
        # Check version
        version = self.read_reg(REG_VERSION)
        print(f"SX127x Version: {version:02x}")
        
        # Set sleep mode
        self.write_reg(REG_OP_MODE, MODE_SLEEP)
        utime.sleep_ms(10)
        
        # Set LoRa mode
        self.write_reg(REG_OP_MODE, MODE_SLEEP | 0x80)
        utime.sleep_ms(10)
        
        # Configure frequency, power, and other settings
        self.set_frequency(self.freq)
        self.set_tx_power(self.tx_power)
        self.set_spreading_factor(self.spreading_factor)
        self.set_bandwidth(self.bandwidth)
        
        # Set sync word
        self.write_reg(REG_SYNC_WORD, 0x34)
        
        # Go to standby
        self.write_reg(REG_OP_MODE, MODE_STANDBY)
        utime.sleep_ms(10)
    
    def read_reg(self, addr):
        """Read register"""
        self.cs.value(0)
        self.spi.write(bytes([addr & 0x7F]))
        value = self.spi.read(1)[0]
        self.cs.value(1)
        return value
    
    def write_reg(self, addr, value):
        """Write register"""
        self.cs.value(0)
        self.spi.write(bytes([addr | 0x80, value]))
        self.cs.value(1)
    
    def set_frequency(self, freq):
        """Set transmission frequency"""
        self.freq = freq
        frf = int(freq / 32e6 * (1 << 19))
        self.write_reg(REG_FRF_MSB, (frf >> 16) & 0xFF)
        self.write_reg(REG_FRF_MID, (frf >> 8) & 0xFF)
        self.write_reg(REG_FRF_LSB, frf & 0xFF)
    
    def set_tx_power(self, power):
        """Set transmission power (2-20 dBm)"""
        self.tx_power = power
        if power > 17:
            self.write_reg(REG_PA_DAC, 0x87)
            power = power - 3
        else:
            self.write_reg(REG_PA_DAC, 0x84)
        
        self.write_reg(REG_PA_CONFIG, 0x80 | (power - 2))
    
    def set_spreading_factor(self, sf):
        """Set spreading factor (6-12)"""
        self.spreading_factor = sf
        modem_config_2 = self.read_reg(REG_MODEM_CONFIG_2)
        modem_config_2 = (modem_config_2 & 0x0F) | ((sf << 4) & 0xF0)
        self.write_reg(REG_MODEM_CONFIG_2, modem_config_2)
    
    def set_bandwidth(self, bandwidth):
        """Set bandwidth (125000, 250000, 500000)"""
        self.bandwidth = bandwidth
        modem_config_1 = self.read_reg(REG_MODEM_CONFIG_1)
        
        if bandwidth == 125000:
            bw = 0x70
        elif bandwidth == 250000:
            bw = 0x80
        elif bandwidth == 500000:
            bw = 0x90
        else:
            bw = 0x70
        
        modem_config_1 = (modem_config_1 & 0x0F) | bw
        self.write_reg(REG_MODEM_CONFIG_1, modem_config_1)
    
    def enable_crc(self):
        """Enable CRC"""
        modem_config_2 = self.read_reg(REG_MODEM_CONFIG_2)
        modem_config_2 |= 0x04
        self.write_reg(REG_MODEM_CONFIG_2, modem_config_2)
    
    def send(self, data):
        """Send data"""
        # Go to standby
        self.write_reg(REG_OP_MODE, MODE_STANDBY)
        utime.sleep_ms(1)
        
        # Clear TX done flag
        self.write_reg(REG_IRQ_FLAGS, 0x08)
        
        # Set FIFO pointer to TX base
        self.write_reg(REG_FIFO_ADDR_PTR, self.read_reg(REG_FIFO_TX_BASE_ADDR))
        
        # Write data to FIFO
        if isinstance(data, str):
            data = data.encode()
        
        self.cs.value(0)
        self.spi.write(bytes([REG_FIFO | 0x80]))
        self.spi.write(data)
        self.cs.value(1)
        
        # Set payload length
        self.write_reg(REG_PAYLOAD_LENGTH, len(data))
        
        # Go to TX mode
        self.write_reg(REG_OP_MODE, MODE_TX)
        
        # Wait for TX done
        while not self.di0.value():
            utime.sleep_ms(1)
        
        # Go back to standby
        self.write_reg(REG_OP_MODE, MODE_STANDBY)
    
    def receive_irq(self):
        """Check if data received (IRQ method)"""
        # Go to RX mode
        self.write_reg(REG_OP_MODE, MODE_RX_CONTINUOUS)
        
        # Check DIO0 pin for RX done
        return self.di0.value()
    
    def recv(self):
        """Receive data"""
        # Clear RX done flag
        self.write_reg(REG_IRQ_FLAGS, 0x40)
        
        # Get number of bytes received
        nb_bytes = self.read_reg(REG_RX_NB_BYTES)
        
        # Get FIFO RX current address
        fifo_addr = self.read_reg(REG_RX_CURRENT_ADDR)
        self.write_reg(REG_FIFO_ADDR_PTR, fifo_addr)
        
        # Read data from FIFO
        self.cs.value(0)
        self.spi.write(bytes([REG_FIFO & 0x7F]))
        payload = self.spi.read(nb_bytes)
        self.cs.value(1)
        
        return payload
    
    def get_rssi(self):
        """Get RSSI (Received Signal Strength Indicator)"""
        return -(self.read_reg(REG_PKT_RSSI_VALUE))
    
    def get_snr(self):
        """Get SNR (Signal to Noise Ratio)"""
        snr_value = self.read_reg(REG_PKT_SNR_VALUE)
        return snr_value / 4.0
