import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading
import queue
from faster_whisper import WhisperModel

class AudioHandler:
    def __init__(self):
        self.sample_rate = 16000
        self.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.audio_queue = queue.Queue()
        self.is_recording = False
        
    def record_audio(self):
        def callback(indata, _frames, _time, status):
            if status:
                print(f"Status: {status}")
            self.audio_queue.put(indata.copy())
            
        self.is_recording = True
        with sd.InputStream(callback=callback, channels=1, samplerate=self.sample_rate):
            while self.is_recording:
                sd.sleep(100)
                
    def stop_recording(self):
        self.is_recording = False
        
    def get_audio_data(self):
        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
        return np.concatenate(audio_data) if audio_data else np.array([])
        
    def transcribe_audio(self, audio_data):
        if len(audio_data) == 0:
            return ""
        temp_file = "temp_audio.wav"
        write(temp_file, self.sample_rate, audio_data)
        segments, _ = self.whisper_model.transcribe(temp_file)
        text = " ".join([segment.text for segment in segments])
        return text 