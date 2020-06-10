import Interpolation

"""
Used to play vibration patterns from a json file.
"""
class VibrationPatternPlayer:    

    def __init__(self, vest_device):
        """Initializes the Vibration Pattern Player.
        Args:
            vest_device: An implementation of the VestDeviceBase
            motor_count: The total number of vibration motors. Vibration motors will be addressed via an index 0 - (motor_count -1).
        """
        self._vest_controller = vest_device
        self._get_frames_list = []
        self.speed = 1
        self._current_time = 0
        self._actuators = {} # dictionary mapping index to vibration intensity
        self.is_playing = False
        self._clip = None

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
        """
        Samples the current clip at the given time.
        Args:
            time: a float value between 0 - clip duration.
        """
        self._reset_actuator_values()

        for key in self._actuators:
            prev = self._get_previous_frame(time, key)
            next = self._get_next_frame(time, key)
            if prev["value"] == 0 and next["value"] == 0:
                continue            
            self._actuators[key] = int(round(self._interpolate(prev["value"], next["value"], prev["time"], next["time"], time)))
            #print(str(time) + ": [" + str(key) +"] : [" + str(self._actuators[key]) + "]")
        
        self._vest_controller.set_pins_batched(self._actuators)
            

    def _interpolate(self, start_value, end_value, start_time, end_time, current_time):
        if ("interpolation" in self._clip.keys()) == False:
            return start_value

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
        """
        Plays a given json clip.
        Args:
            clip: the json loaded clip.
        """
        self._current_time = 0
        self._vest_controller.set_frequency(0)
        self.speed = 1
        self.is_playing = True
        self._clip = clip
        self._actuators.clear()
        for frame in clip["frames"]:
            for actuator in frame["actuators"]:
                self._actuators.setdefault(actuator["pin"], 0)

    def update(self, deltaTime):
        """
        Updates the vibration pattern player.
        Args:
            deltaTime: A float that represents the time that has elapsed since the last frame in seconds.
        """
        if self.is_playing == False:
            return

        if self._clip == None:
            return

        self._current_time += deltaTime * self.speed
        #print(str(self._current_time))        
        duration = self._clip["duration"]
        
        if self._current_time > duration:
            if self._clip["isLooped"] == True:
                self._current_time = self._current_time - duration
            else:
                self._vest_controller.mute()
                self.is_playing = False
                return            
        
        self.sample(self._current_time)           