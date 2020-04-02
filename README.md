# Vibration Pattern Player
The vibration pattern player can be used to play a sequence of vibrations. Vibration patterns are encoded as JSON files (see below for more details).

## Requirements
- For USB: PyCmdMessenger (https://pypi.org/project/PyCmdMessenger/)
- For BLE: bluepy (https://pypi.org/project/bluepy/)
- For I2C: https://github.com/Suitceyes-Project-Code/PCA9685-Controller. (Copy `suitceyes.py` over to the root.)

## Json Format
The following JSON format is used:
```json
{
    "isLooped": true,
    "duration" : 1.26,
    "interpolation" : 0,
    "frames": [
      {
        "time": 0.0,
        "actuators": [
          {
            "pin": 0,
            "value": 255
          }
        ]
      },
      ...
    ]
  }
```
- `isLooped`: a flag stating whether the vibration pattern should be looped
- `duration`: length of entire pattern in seconds
- `interpolation`: alters how/if frames are interpolated. 0 = 0ff, 1 = Linear, 2 = Quadratic Ease In Ease Out. 
- `frames`: contains an array of the actual frames used in the vibration pattern.
- `time`: the time in seconds of that frame.
- `actuators`: contains an array of actuators whose values should be changed for the current frame.
- `pin`: the index of the motor to be changed.
- `value`: a value between 0 - 255 which corresponds to the vibration motor intensity.

## Example

```python
from VestDeviceBase import DummyVestDevice
import json
import time
from VibrationPatternPlayer import VibrationPatternPlayer
    
vest_controller = DummyVestDevice() #replace with real implementation
vbp = VibrationPatternPlayer(vest_controller, 32) # 32: the number of actuators being updated.
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
```
Updates of the vibration pattern player require a call to `update(delta_time)` every frame. `delta_time` is the time in seconds that have elapsed since the last call. 

## Authors
- James Gay (james.gay@hs-offenburg.de)