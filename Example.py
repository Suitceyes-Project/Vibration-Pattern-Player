from VestDeviceBase import DummyVestDevice
from I2CVibrationDevice import I2CVestDevice
import json
import time
from VibrationPatternPlayer import VibrationPatternPlayer
    
with I2CVestDevice(0x40) as vest_controller: #replace with real implementation
    vbp = VibrationPatternPlayer(vest_controller)
    with open("Examples/heartbeat.json") as file:
        clip = json.load(file)
        vbp.play_clip(clip)
        delta_time = 0.0
        time.sleep(2)
        prev_frame = time.time()
        while vbp.is_playing:
            current_time = time.time()
            delta_time = (current_time - prev_frame)
            vbp.update(delta_time)
            prev_frame = current_time
            time.sleep(0.01)