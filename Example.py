from VestDeviceBase import DummyVestDevice
import json
import time
from VibrationPatternPlayer import VibrationPatternPlayer
    
vest_controller = DummyVestDevice() #replace with real implementation
vbp = VibrationPatternPlayer(vest_controller, 32)
with open("Examples/25_percent.json") as file:
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