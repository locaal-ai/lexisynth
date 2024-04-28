import json
from os import path
import queue
import time
import ctranslate2
from PyQt6.QtCore import QThread
from PyQt6 import QtCore
from platformdirs import user_data_dir
from ls_logging import logger
import sentencepiece as spm
from language_codes import LanguageCodes
from models_info import ModelDownloadInfo
from storage import fetch_data
import requests


class TranslationThread(QThread):
    text_available = QtCore.pyqtSignal(str)
    progress_available = QtCore.pyqtSignal(int)
    start_progress = QtCore.pyqtSignal()
    stop_progress = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.input_queue = queue.Queue()
        self.translator = None
        self.tokenizer = None
        self.source_language = "English"
        self.target_language = "Spanish"
        self.running = False
        # warm up the model
        self.progressTimer = QtCore.QTimer()
        self.progressTimer.timeout.connect(self.progressCallback)
        self.last_run_time_ms = 1000
        self.run_time_avg_moving_window = 500
        self.current_run_time_start = time.time()
        self.start_progress.connect(self.progressTimer.start)
        self.stop_progress.connect(self.progressTimer.stop)
        self.translationEngine = None
        self.openai_api_key = None
        self.deepl_api_key = None

    def setTranslationEngine(self, translationEngine):
        self.translationEngine = translationEngine

    def setupModel(self):
        local_llm_select = fetch_data("settings.json", "settings", {}).get(
            "local_llm_select"
        )
        if local_llm_select is None:
            logger.error("Local LLM select is not set")
            return False
        if local_llm_select == 1:
            model_path = path.join(
                user_data_dir("lexisynth"),
                ModelDownloadInfo.M2M_100["model_folder_name"],
            )
            if not path.exists(model_path):
                logger.error("M2M-100 model is not downloaded")
                return False
        else:
            model_path = fetch_data("settings.json", "settings", {}).get(
                "local_llm_folder"
            )
            if model_path is None:
                logger.error("Custom Local LLM folder is not set")
                return False
            if not path.exists(model_path):
                logger.error("Custom Local LLM folder does not exist")
                return False

        self.translator = ctranslate2.Translator(model_path)
        self.tokenizer = spm.SentencePieceProcessor(
            path.join(model_path, "sentencepiece.bpe.model")
        )
        return True

    def setLanguages(self, source_language, target_language):
        self.source_language = source_language
        self.target_language = target_language

    def stop(self):
        self.running = False

    def progressCallback(self):
        # calculate how much time in ms passed since the start of the current translation
        current_run_time_elapsed = (time.time() - self.current_run_time_start) * 1000
        # calculate the progress in percentage
        progress = min(
            100, int(current_run_time_elapsed / self.run_time_avg_moving_window * 100)
        )
        self.progress_available.emit(progress)

    def translateLocalLLM(self, text):
        src_language_code = LanguageCodes.getLanguageCode(self.source_language)
        tgt_language_code = LanguageCodes.getLanguageCode(self.target_language)

        source = [f"__{src_language_code}__"] + self.tokenizer.EncodeAsPieces(
            text, add_eos=True
        )
        results = self.translator.translate_batch(
            [source], target_prefix=[[f"__{tgt_language_code}__"]]
        )
        output_tokens = results[0].hypotheses[0][1:]
        return self.tokenizer.Decode(output_tokens)

    def translateOpenAI(self, text):
        if self.openai_api_key is None:
            self.openai_api_key = fetch_data("settings.json", "settings", {}).get(
                "openai_api_key"
            )
        if self.openai_api_key is None:
            logger.error("OpenAI API key is not set")
            return "Error: OpenAI API key is not set"
        # build API request
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": f"translate from {self.source_language} to {self.target_language}: {text}",
                }
            ],
        }
        # send the request
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=data,
        )
        if response.status_code != 200:
            logger.error(f"OpenAI API request failed: {response.status_code}")
            return "Error: OpenAI API request failed"
        # parse the response
        response_json = response.json()
        if "choices" not in response_json or len(response_json["choices"]) == 0:
            logger.error("OpenAI API response is empty")
            return "Error: OpenAI API response is empty"
        return response_json["choices"][0]["message"]["content"]

    def translateDeepL(self, text):
        if self.deepl_api_key is None:
            self.deepl_api_key = fetch_data("settings.json", "settings", {}).get(
                "deepl_api_key"
            )
        if self.deepl_api_key is None:
            logger.error("DeepL API key is not set")
            return "Error: DeepL API key is not set"
        # build API request
        data = {
            "text": [text],
            "source_lang": LanguageCodes.getLanguageCode(self.source_language),
            "target_lang": LanguageCodes.getLanguageCode(self.target_language),
        }
        # send the request
        response = requests.post(
            "https://api-free.deepl.com/v2/translate",
            headers={
                "Authorization": f"DeepL-Auth-Key {self.deepl_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "LexiSynth/1.0 (+https://scoresight.live/lexisynth)",
                "Accept": "application/json",
            },
            json=data,
        )
        if response.status_code != 200:
            logger.error(f"DeepL API request failed: {response.status_code}")
            logger.error(response.text)
            return "Error: DeepL API request failed"
        # parse the response
        response_json = response.json()
        if (
            "translations" not in response_json
            or len(response_json["translations"]) == 0
        ):
            logger.error("DeepL API response is empty")
            return "Error: DeepL API response is empty"
        return response_json["translations"][0]["text"]

    def run(self):
        if self.translationEngine is None:
            logger.error("Translation engine is not set")
            self.running = False
            return

        logger.info("Translation thread started")
        self.running = True
        while self.running:
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
            if self.translationEngine == "Local LLM":
                if self.translator is None or self.tokenizer is None:
                    if not self.setupModel():
                        logger.error(
                            "Cannot start translation thread, model is not set up"
                        )
                        self.running = False
                        return

                output_text = self.translateLocalLLM(text)
            elif self.translationEngine == "OpenAI API":
                output_text = self.translateOpenAI(text)
            elif self.translationEngine == "DeepL API":
                output_text = self.translateDeepL(text)
            else:
                logger.error(f"Unknown translation engine: {self.translationEngine}")
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

            # Emit the translated text
            self.text_available.emit(output_text)

        logger.info("Translation thread stopped")
