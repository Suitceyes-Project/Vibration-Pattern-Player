import time
import threading
import queue

class HaptogramService:
    def __init__(self, vibration_pattern_player, clip_interval = 0, delta_time = 0.01):
        self._queue = queue.Queue()
        self._should_run = False
        self._delta_time = delta_time
        self._clip_interval = clip_interval
        self._vpp = vibration_pattern_player

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, trackback):
        self.stop()

    def is_working(self):
        return (self._queue.empty() == False) or self._vpp.is_playing

    def start(self):
        self._should_run = True
        print("[HaptogramService]: Running on background thread...")
        threading.Thread(target=self._loop, args=()).start()

    def stop(self):
        print("[HaptogramService]: Shutting down service.")
        self._should_run = False

    def enqueue(self, vibration_pattern: str):
        if self.is_working() == False:
            #print("[HaptogramService]: Playing " + vibration_pattern)
            self._vpp.play_clip(vibration_pattern)
        else:
            self._queue.put(vibration_pattern)

    def _loop(self):        
        previous_time = time.time()
        while self._should_run:
            try:
                current_time = time.time()
                actual_delta_time = current_time - previous_time

                # Sleep if we're running faster than we should.
                if actual_delta_time < self._delta_time:
                    time.sleep(self._delta_time - actual_delta_time)

                previous_time = time.time()

                # Update current clip if we're playing.
                if self._vpp.is_playing:
                    self._vpp.update(self._delta_time)
                else:
                    # Otherwise get a new clip from the queue and play
                    if self._queue.empty() == False:
                        if self._clip_interval > 0.0:
                            #print("[HaptogramService]: Waiting " + str(self._clip_interval) + " seconds")
                            time.sleep(self._clip_interval)
                        new_clip = self._queue.get()                    
                        #print("[HaptogramService]: Playing " + new_clip)
                        self._vpp.play_clip(new_clip)
                        self._vpp.update(self._delta_time)
            except:
                print("[HaptogramService]: Caught an exception.")


class VibrationPatternPlayerMock:    
    def __init__(self):
        self.is_playing = False
        self._total_time = 0

    def play_clip(self, clip):
        self._total_time = 0
        self.is_playing = True
    
    def update(self, delta_time):
        self._total_time += delta_time
        if self._total_time > 5:
            self._total_time = 0
            self.is_playing = False 

if __name__ == "__main__":
    vpp = VibrationPatternPlayerMock()
    with HaptogramService(vpp, 0.0) as hs:
        hs.enqueue("Clip 1")
        hs.enqueue("Clip 2")
        hs.enqueue("Clip 3")
        while hs.is_working():
            time.sleep(1)
