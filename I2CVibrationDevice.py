from suitceyes import VibrationMotorDriver
import VestDeviceBase

class I2CVestDevice(VestDevice):
    def __init__(self, *addresses):
        self._board_count = len(addresses)
        self._driver = VibrationMotorDriver(*addresses)
    
    def __enter__(self):
        self._driver.start()
        return self

    def __exit__(self, type, value, traceback):
        # Make sure the vest is muted and that the connection is closed.
        self._driver.stop()
    
    def set_pin(self, index, intensity):
        # map 0 - 255 value to 0 - 1 range
        intensity = intensity / 255        
        self._driver.set_vibration(index, intensity)
    
    def set_frequency(self, frequency):
        for i in range(self._board_count):
            self._driver.set_frequency(i, frequency)
    
    def mute(self):
        self._driver.mute_all()

    def set_pins_batched(self, values = dict):
        for key in values:
            values[key] = values[key]/255     
        self._driver.set_vibration_batched(values)