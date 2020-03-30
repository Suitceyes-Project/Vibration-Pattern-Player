from abc import ABC, abstractmethod

class VestDevice(ABC):
    
    @abstractmethod
    def set_pin(self, index, intensity):
        pass

    @abstractmethod
    def set_pins_batched(self, values = dict):
        pass
    
    @abstractmethod
    def set_frequency(self, frequency):
        pass
    
    @abstractmethod
    def mute(self):
        pass
    
class DummyVestDevice(VestDevice):
    def set_pin(self, index, intensity):
        pass
    
    def set_frequency(self, frequency):
        pass
    
    def mute(self):
        pass

    def set_pins_batched(self, values = dict):
        pass