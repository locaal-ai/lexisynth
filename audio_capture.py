import time
import sounddevice as sd
from PyQt6 import QtCore
import numpy as np
from lexisynth_types import AudioSource
from ls_logging import logger
import queue
import soundfile as sf


class AudioRecorder(QtCore.QThread):
    data_available = QtCore.pyqtSignal(np.ndarray)
    progress_and_volume = QtCore.pyqtSignal(tuple)

    def __init__(
        self,
        audio_source: AudioSource,
        chunk_size_ms,
        fs=44100,
        channels=1,
        dtype="float32",
    ):
        super().__init__()
        self.chunk_size_ms = chunk_size_ms
        self.fs = fs
        self.channels = channels
        self.dtype = dtype
        self.stream = None
        self.audio_source = audio_source
        self.block_read_freq_ms = 33  # 33ms
        self.number_of_blocks = chunk_size_ms / self.block_read_freq_ms
        self.q = queue.Queue(maxsize=self.number_of_blocks)
        self.soundfile = None
        self.running = False
        self.last_run_time = time.time()
        self.output_queue = None

    def run(self) -> None:
        self.running = True
        while self.running:
            # check if enough time passed since the last run
            if (time.time() - self.last_run_time) < (
                float(self.block_read_freq_ms) / 1000.0
            ):
                # sleep to avoid busy waiting
                time.sleep(0.001)
                continue
            self.last_run_time = time.time()

            magnitude = 0
            new_data = False
            if self.audio_source.sourceType == AudioSource.SourceType.FILE:
                if self.soundfile is None:
                    logger.error("Soundfile is not initialized")
                    break
                # read a block of data from the soundfile
                data = self.soundfile.read(self.read_size_frames())
                if not len(data):
                    logger.warning("File data is empty. End of file?")
                    continue
                magnitude = np.max(np.abs(data))
                self.q.put_nowait(data)
                new_data = True
            elif self.audio_source.sourceType == AudioSource.SourceType.DEVICE:
                while (
                    self.stream.read_available >= self.read_size_frames()
                    and not self.q.full()
                ):
                    # read a block of data from the sounddevice
                    data, overflowed = self.stream.read(self.read_size_frames())
                    # take one channel if there are multiple channels
                    if len(data.shape) > 1:
                        # merge the channels by averaging
                        data = np.mean(data, axis=1)
                    if overflowed:
                        logger.warning(f"Overflowed (got {len(data)})")
                    magnitude = np.max(np.abs(data))
                    self.q.put_nowait(data)
                    new_data = True
            else:
                logger.error("Unknown audio source type")
                break

            if new_data:
                # emit progress signal with the buffer capacity in milliseconds and the volume in the frame
                self.progress_and_volume.emit(
                    (self.q.qsize() * self.block_read_freq_ms, magnitude)
                )
                # check if q has enough data to emit according to the chunk size
                if self.q.full():
                    # emit the entire chunk of data
                    self.data_available.emit(
                        np.concatenate(
                            [self.q.get() for _ in range(self.q.qsize())], axis=0
                        )
                    )

        logger.info("Audio capture thread stopped")

    def start(self):
        logger.info(
            f"Starting audio capture with {self.fs} Hz, {self.channels} channels, and {self.dtype} data type"
        )
        # if this is a file source, stream the file progressively with soundfile
        if self.audio_source.sourceType == AudioSource.SourceType.FILE:
            logger.info(f"Opening file {self.audio_source.sourceName}")
            self.soundfile = sf.SoundFile(self.audio_source.sourceName)
            self.fs = self.soundfile.samplerate
            logger.debug(f"File info: {self.soundfile}")

        # if this is a device source, stream the device with sounddevice
        elif self.audio_source.sourceType == AudioSource.SourceType.DEVICE:
            logger.info(f"Opening device {self.audio_source.sourceName}")
            self.stream = sd.InputStream(
                device=self.audio_source.sourceName,
                samplerate=self.fs,
                blocksize=self.read_size_frames(),
                channels=self.channels,
                dtype=self.dtype,
            )
            logger.info(f"Stream samplerate: {self.stream.samplerate}")
            self.stream.start()
        else:
            logger.error("Unknown audio source type")
            return

        super().start()

    def stop(self):
        logger.info("Stopping audio capture")
        self.running = False
        if self.soundfile:
            self.soundfile.close()
        if self.stream:
            self.stream.stop()

    def read_size_frames(self):
        return int(self.fs * self.block_read_freq_ms / 1000)

    def get_chunk_size_frames(self):
        return int(self.fs * self.chunk_size_ms / 1000)

    @staticmethod
    def get_audio_devices() -> list[AudioSource]:
        devices = sd.query_devices()
        devices_list = []
        if type(devices) is dict:
            devices_list = [devices]
        else:
            for device in devices:
                if device["max_input_channels"] > 0:
                    logger.debug(f"Audio device: {device}")
                    devices_list.append(device)
        return [
            AudioSource(
                sourceName=device["name"],
                sourceType=AudioSource.SourceType.DEVICE,
            )
            for device in devices_list
        ]
