import time
import queue
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import requests
from ls_logging import logger

from storage import fetch_data


class TextToSpeechThread(QThread):
    speech_available = pyqtSignal(object)
    progress_available = pyqtSignal(int)
    start_progress = pyqtSignal()
    stop_progress = pyqtSignal()

    def __init__(self, parent=None):
        super(TextToSpeechThread, self).__init__(parent)
        self.input_queue = queue.Queue()
        self.running = False
        self.openai_api_key = None
        self.elevenlabs_api_key = None
        self.last_run_time_ms = 1000
        self.run_time_avg_moving_window = 500
        self.current_run_time_start = time.time()
        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(self.progressCallback)
        self.start_progress.connect(self.progressTimer.start)
        self.stop_progress.connect(self.progressTimer.stop)
        self.speech_engine = "OpenAI"

    def add_text(self, text):
        self.input_queue.put(text)

    def stop(self):
        self.running = False

    def run(self):
        while True:
            # Get the next text from the queue
            try:
                text = self.input_queue.get(block=False)
            except queue.Empty:
                time.sleep(0.1)
                continue

            if text is None:
                # sleep for a bit to avoid busy waiting
                time.sleep(0.1)
                continue

            self.current_run_time_start = time.time()
            self.start_progress.emit()

            # Time the translation operation
            start_time = time.time()

            if self.speech_engine == "OpenAI":
                self.synthesize_speech_openai(text)
            else:
                logger.error(f"Unknown speech engine: {self.speech_engine}")
                self.running = False
                return

            end_time = time.time()

            self.stop_progress.emit()
            self.progress_available.emit(0)

            # prevent 0 time
            self.last_run_time_ms = max(100, (end_time - start_time) * 1000)
            self.run_time_avg_moving_window = (
                self.run_time_avg_moving_window * 0.9
            ) + (self.last_run_time_ms * 0.1)

    def synthesize_speech_openai(self, text):
        if self.openai_api_key is None:
            self.openai_api_key = fetch_data("settings.json", "settings", {}).get(
                "openai_api_key"
            )
        if self.openai_api_key is None:
            logger.error("OpenAI API key not found")
            return
        # send a request to openai with requests
        # build API request
        data = {"model": "tts-1", "input": text, "voice": "alloy"}
        # send the request
        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=data,
        )
        if response.status_code != 200:
            logger.error(f"OpenAI API request failed: {response.status_code}")
            return "Error: OpenAI API request failed"
        # the response should be a .mp3 file
        self.speech_available.emit(response.content)

    def synthesize_speech_elevenlabs(self, text):
        if self.elevenlabs_api_key is None:
            self.elevenlabs_api_key = fetch_data("settings.json", "settings", {}).get(
                "elevenlabs_api_key"
            )
        if self.elevenlabs_api_key is None:
            logger.error("Elevenlabs API key not found")
            return
        # send a request to elevenlabs with requests
        # build API request
        data = {"text": text}
        # send the request
        response = requests.post(
            "https://api.eleven-labs.com/text-to-speech/v1/synthesize",
            headers={
                "Authorization": f"Bearer {self.elevenlabs_api_key}",
                "Content-Type": "application/json",
            },
            json=data,
        )
        if response.status_code != 200:
            logger.error(f"Elevenlabs API request failed: {response.status_code}")
            return "Error: Elevenlabs API request failed"
        # the response should be a .mp3 file
        self.speech_available.emit(response.content)

    def progressCallback(self):
        # calculate how much time in ms passed since the start of the current translation
        current_run_time_elapsed = (time.time() - self.current_run_time_start) * 1000
        # calculate the progress in percentage
        progress = min(
            100, int(current_run_time_elapsed / self.run_time_avg_moving_window * 100)
        )
        self.progress_available.emit(progress)
