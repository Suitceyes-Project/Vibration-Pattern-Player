from bluepy.btle import UUID, Peripheral
import VestDeviceBase

class BleVestDevice(VestDevice):
    def __init__(self, deviceAddr):
        try:
            self._peripheral = Peripheral(deviceAddr)
            serviceUUID = UUID("713d0000-503e-4c75-ba94-3148f18d941e")
            characteristicUUID = UUID("713d0003-503e-4c75-ba94-3148f18d941e")
            s = self._peripheral.getServiceByUUID(serviceUUID)
            self._characteristic = s.getCharacteristics(characteristicUUID)[0]
        except Exception as e:
            print("Error: " + str(e))
            
    def __isValidState(self):        
        return self._peripheral.getState() == "conn"
    
    def __write(self, byteArr):
        self._peripheral.writeCharacteristic(self._characteristic.getHandle(), byteArr)
            
    def set_pin(self, index, intensity):
        """Sets a pin to a given intensity.
        index: an integer from 0 - 6
        intensity: an integer from 0 - 255
        """
        if self.__isValidState():
            rList=[0,index,intensity]
            self.__write(bytes(rList))
            
    def set_frequency(self,frequency):
        """Sets the frequency of the entire vest.
        frequency.
        """
        if self.__isValidState():
            rList=[4, frequency & (255), (frequency & (255 << 8)) >> 8, (frequency & (255 << 16)) >> 16, (frequency & (255 << 24)) >> 24]
            b = bytes(rList)
            self.__write(b)
    
    def mute(self):
        """Stops all motors on the vest from vibrating"""
        if self.__isValidState():
            rList=[3]
            self.__write(bytes(rList))
    
    def set_motor(self,index,rotation):
        """
        Sets a given motor index to a given target rotation.
        """
        if self.__isValidState():
            rList = [11,index,rotation]
            self.__write(bytes(rList))
            
    def set_motor_speed(self,speed):
        """
        Changes how long it takes to move 1 degree per millisecond.
        """
        if speed <= 0:
            raise ValueError("speed must be greater than 0.")
        rList = [12,speed]
        self.__write(bytes(rList))

    def set_pins_batched(self, values = dict):
        for pin in values:
            self.set_pin(pin, values[pin])