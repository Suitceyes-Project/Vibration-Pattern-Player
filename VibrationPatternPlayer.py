import Interpolation

class VibrationPatternPlayer:    

    def __init__(self, vest_controller):
        self._vest_controller = vest_controller
        self._get_frames_list = []
        self.speed = 1
        self._current_time = 0
        self._actuators = {} # dictionary mapping index to vibration intensity
        self._is_playing = False
        self._clip = None
        
        actuators = vest_controller.get_actuator_indices()
        for i in range(0, len(actuators)):
            self._actuators[actuators[i]] = 0
        

    def _get_frames_until(self, time):
        self._get_frames_list.clear()
        frames = self._clip["frames"]
        for frame in frames:
            if frame["time"] <= time:
                self._get_frames_list.append(frame)
            else:
                break

        return self._get_frames_list

    def _get_previous_frame(self, time, pin):
        frames = self._clip["frames"]
        returned_frame = { }
        returned_frame["time"] = 0
        returned_frame["value"] = 0
        # go through every frame
        for frame in frames:
            # check if actuator is in frame
            for actuator in frame["actuators"]:
                # if pin is found then...
                if actuator["pin"] == pin:
                    # check if the frame is smaller or equal
                    if frame["time"] <= time:
                        if returned_frame["time"] <= frame["time"]:
                            returned_frame["value"] = actuator["value"]
                            returned_frame["time"] = frame["time"]

        return returned_frame
    
    def _get_next_frame(self, time, pin):
        frames = self._clip["frames"]
        returned_frame = { }
        returned_frame["time"] = self._clip["duration"]
        returned_frame["value"] = 0
        # go through every frame
        for frame in frames:
            # check if actuator is in frame
            for actuator in frame["actuators"]:
                # if pin is found then...
                if actuator["pin"] == pin:
                    # check if the frame is larger
                    if frame["time"] > time:
                        if returned_frame["time"] >= frame["time"]:
                            returned_frame["value"] = actuator["value"]
                            returned_frame["time"] = frame["time"]
            
        return returned_frame

    def _reset_actuator_values(self):
        for key in self._actuators:
            self._actuators[key] = 0

    def sample(self, time):
        self._reset_actuator_values()

        for key in self._actuators:
            prev = self._get_previous_frame(time, key)
            next = self._get_next_frame(time, key)
            if prev["value"] == 0 and next["value"] == 0:
                continue         
            self._actuators[key] = int(round(self._interpolate(prev["value"], next["value"], prev["time"], next["time"], time)))
            #print(str(time) + ": [" + str(key) +"] : [" + str(self._actuators[key]) + "]")
        
        self._vest_controller.vibrate_batched(self._actuators)
            

    def _interpolate(self, start_value, end_value, start_time, end_time, current_time):
        if ("interpolation" in self._clip.keys()) == False:
            return start_time

        method = self._clip["interpolation"]
        t = (current_time - start_time) / (end_time - start_time)
        switcher = {            
            1 : Interpolation.LinearInterpolation,
            2 : Interpolation.QuadraticEaseInOut
        }
        func = switcher.get(method, lambda t: 0.0)
        t = func(t)
        return (1-t) * start_value + t * end_value

    def play_clip(self, clip):
        self._current_time = 0
        self._vest_controller.set_frequency(0)
        self.speed = 1
        self.is_playing = True
        self._clip = clip

    def update(self, deltaTime):

        if self.is_playing == False:
            return

        if self._clip == None:
            return

        self._current_time += deltaTime * self.speed        
        duration = self._clip["duration"]
        
        if self._current_time > duration:
            if self._clip["isLooped"] == True:
                self._current_time = self._current_time - duration
            else:
                self._vest_controller.mute()
                self.is_playing = False
                return            
        
        self.sample(self._current_time)


if __name__ == "__main__":
    from VibrationController import VestController
    from VestDeviceBase import DummyVestDevice
    import json
    import time
    vest_controller = VestController(DummyVestDevice(), range(0,32))
    vbp = VibrationPatternPlayer(vest_controller)
    with open("vibration_patterns/25_percent.json") as file:
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