import queue
import time
from PyQt6 import QtCore
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QDialog
from faster_whisper import WhisperModel
from language_codes import LanguageCodes
from ls_logging import logger
import numpy as np
from model_download_dialog import ModelDownloadDialog

from models_info import ModelDownloadInfo, checkForModelDownload, getAbsoluteModelPath


def linear_interpolate_audio(audio_frame, original_rate, target_rate):
    # Calculate the duration of the audio in seconds
    duration = audio_frame.shape[0] / original_rate

    # Calculate the number of samples in the resampled audio
    target_length = int(duration * target_rate)

    # Generate sample number arrays for original and target
    original_samples = np.arange(audio_frame.shape[0])
    target_samples = np.linspace(0, audio_frame.shape[0] - 1, target_length)

    # Use numpy's interpolation function
    resampled_audio = np.interp(target_samples, original_samples, audio_frame)
    return resampled_audio


def find_point_of_repetition(sentence):
    # i'd like to find the point where the token start to repeat.
    # for example: 6952, 345, 11, 5613, 13, 314, 1053, 587, 5613, 13, 314, 1053, 587, 5613, 13, 314, 1053
    # the point of repetition is 5613, 13, 314, 1053, 587,
    # therefore the function should return 3, 8, 6
    # find the location of a sequence of at least two tokens that repeats
    words = sentence.lower().split()
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            if words[i] == words[j]:
                # check if the sequence repeats
                k = 1
                while j + k < len(words) and words[i + k] == words[j + k]:
                    k += 1
                if k > 1:
                    return i, j, k
    return None


def checkAndDownloadModel(modelInfo):
    if not checkForModelDownload(modelInfo):
        # show the download dialog
        modelDownloadDialog = ModelDownloadDialog(modelInfo)
        modelDownloadDialog.exec()


class AudioTranscriber(QThread):
    text_available = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.input_queue = queue.Queue()
        self.model = None
        self.running = False
        self.language = None
        # check if model has been downloaded already
        checkAndDownloadModel(ModelDownloadInfo.FASTER_WHISPER_TINY_CT2)

    def set_language(self, language: str):
        if language is None:
            self.language = None
            return
        if language == "Auto":
            self.language = None
            return
        if language in LanguageCodes.getLanguageCodes():
            self.language = language
            return
        if language in LanguageCodes.getLanguageNames():
            self.language = LanguageCodes.getLanguageCode(language)
            return
        logger.error(f"Language {language} not found")
        self.language = None

    def set_model_size(self, model_size: str):
        if model_size is None:
            return
        if model_size == "Tiny (75Mb)":
            checkAndDownloadModel(ModelDownloadInfo.FASTER_WHISPER_TINY_CT2)
            self.model = WhisperModel(
                getAbsoluteModelPath(ModelDownloadInfo.FASTER_WHISPER_TINY_CT2),
                device="cpu",
                compute_type="int8",
            )
            logger.info("Model loaded: tiny")
            return
        if model_size == "Small (400Mb)":
            checkAndDownloadModel(ModelDownloadInfo.FASTER_WHISPER_SMALL_CT2)
            self.model = WhisperModel(
                getAbsoluteModelPath(ModelDownloadInfo.FASTER_WHISPER_SMALL_CT2),
                device="cpu",
                compute_type="int8",
            )
            logger.info("Model loaded: small")
            return
        if model_size == "Base (140Mb)":
            checkAndDownloadModel(ModelDownloadInfo.FASTER_WHISPER_BASE_CT2)
            self.model = WhisperModel(
                getAbsoluteModelPath(ModelDownloadInfo.FASTER_WHISPER_BASE_CT2),
                device="cpu",
                compute_type="int8",
            )
            logger.info("Model loaded: base")
            return
        logger.error(f"Model size {model_size} not found")

    def stop(self):
        self.running = False

    def run(self):
        logger.info("Transcription thread started")
        if self.model is None:
            model_size = "tiny.en"
            self.model = WhisperModel(
                getAbsoluteModelPath(ModelDownloadInfo.FASTER_WHISPER_TINY_CT2),
                device="cpu",
                compute_type="int8",
            )
            logger.info(f"Model loaded: {model_size}")

        self.running = True
        while self.running:
            try:
                audio_data = self.input_queue.get_nowait()
            except queue.Empty:
                # sleep for a bit to avoid busy waiting
                time.sleep(0.1)
                continue
            if audio_data is None or len(audio_data) == 0:
                # sleep for a bit to avoid busy waiting
                time.sleep(0.1)
                continue

            # resample the audio data to 16kHz
            resampled_audio_data = linear_interpolate_audio(
                audio_data, 44100, 16000
            ).astype(np.float32)

            # transcribe the audio data
            segments, _ = self.model.transcribe(
                resampled_audio_data,
                language=self.language,
                max_new_tokens=40,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
                temperature=0.0,
            )

            segments_list = list(segments)
            if len(segments_list) == 0:
                logger.debug("No segments found")
                continue

            # get one single segment from the segments iterator
            segment = segments_list[0]
            if segment is None:
                logger.debug("None segment found")
                continue
            repetition = find_point_of_repetition(segment.text)
            result_text = segment.text.strip()
            if repetition:
                # remove the repetition
                result_text = " ".join(segment.text.split()[: repetition[1]])

            self.text_available.emit(result_text)

        logger.info("Transcription thread stopped")

    def queue_audio_data(self, audio_data):
        self.input_queue.put_nowait(audio_data)
