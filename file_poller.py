import os
import time
from PyQt6.QtCore import QThread
from queue import Queue
from ls_logging import logger


class FilePoller(QThread):
    def __init__(self, filename: str, cadence_ms: int, queue: Queue):
        super().__init__()
        self.filename = filename
        self.cadence_seconds = cadence_ms / 1000.0  # Convert ms to seconds
        self.queue = queue
        self.stop_flag = False
        self.last_content = None

    def run(self):
        # check if file exists
        if not os.path.exists(self.filename):
            logger.error(f"File {self.filename} does not exist")
            return
        while not self.stop_flag:
            if os.path.exists(self.filename):
                with open(self.filename, "r") as file:
                    content = file.read()
                    if content and content != self.last_content:
                        self.queue.put_nowait(content)
                        self.last_content = content
            time.sleep(self.cadence_seconds)

    def stop(self):
        self.stop_flag = True
