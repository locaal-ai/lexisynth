import queue
import time
from pydub import AudioSegment
from pydub.playback import play
import io
from PyQt6.QtCore import QThread


class AudioBuffer:
    class AudioBufferType:
        RAW = 0
        MP3 = 1

    def __init__(self, type, bytes):
        self.buffer = queue.Queue()
        self.type = type
        self.bytes = bytes


class AudioPlayer(QThread):
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.isRunning = False

    def add_to_queue(self, audio: AudioBuffer):
        self.queue.put(audio)

    def stop(self):
        self.isRunning = False

    def run(self):
        while self.isRunning:
            if self.queue.empty():
                time.sleep(0.1)
                continue
            audio = self.queue.get()
            if audio.type == AudioBuffer.AudioBufferType.MP3:
                audio = AudioSegment.from_mp3(io.BytesIO(audio.bytes))
                play(audio)
