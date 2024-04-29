import os
import platform
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi
import sys
from os import path
from audio_capture import AudioRecorder
from audio_player import AudioPlayer
from file_poller import FilePoller
from language_codes import LanguageCodes
from lexisynth_types import AudioSource
from log_view import LogViewerDialog
from ls_logging import logger
from obs_websocket import (
    OBSPoller,
    disconnect_obs_websocket,
    get_all_sources,
    get_all_text_sources,
    open_obs_websocket,
    open_obs_websocket_from_settings,
)
from settings_dialog import SettingsDialog
from storage import fetch_data, store_data
from transcription import AudioTranscriber
from translation import TranslationThread
from text_to_speech import TextToSpeechThread

NOT_IMPLEMENTED = "Not implemented yet"


def disable_dropdown_options_by_text(
    combo_box, text, negative_case=False
):
    for i in range(combo_box.count()):
        disable = False
        if (isinstance(text, list) and combo_box.itemText(i) in text) or (
            isinstance(text, str) and combo_box.itemText(i) == text
        ):
            if not negative_case:
                disable = True
        else:
            if negative_case:
                disable = True

        if disable:
            combo_box.model().item(i).setEnabled(False)
            combo_box.model().item(i).setToolTip(NOT_IMPLEMENTED)


def toggle_all_widgets_in_a_groupbox(group_box, enabled):
    # if the widget layout is form layout, iterate the layout and hide all the widgets
    if type(group_box.layout()) == QtWidgets.QFormLayout:
        for i in range(group_box.layout().rowCount()):
            group_box.layout().setRowVisible(i, enabled)
        return
    # iterate the layout and hide all the widgets
    for i in range(group_box.layout().count()):
        widget = group_box.layout().itemAt(i).widget()
        if widget:
            widget.setVisible(enabled)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(
            path.abspath(path.join(path.dirname(__file__), "mainwindow.ui")), self
        )

        # add File -> Settings menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Settings", self.openSettingsDialog)
        file_menu.addAction("About", self.openAboutDialog)
        file_menu.addAction("View Current Log", self.openLogsDialog)
        self.log_dialog = None

        # populate audio sources
        self.populateAudioSources()
        self.comboBox_audioSources.currentIndexChanged.connect(self.audioSourceChanged)
        self.audioSource = None
        self.audioCapture = None
        self.audioTranscriber = AudioTranscriber()
        self.audioTranscriber.text_available.connect(self.transcriptionAvailable)
        self.translator = TranslationThread()
        self.translator.text_available.connect(self.translationTextAvailable)
        self.translator.progress_available.connect(
            lambda progress: self.progressBar_translationProgress.setValue(progress)
        )
        self.translation_poller = None
        self.textToSpeech = TextToSpeechThread()
        self.textToSpeech.progress_available.connect(
            lambda progress: self.progressBar_ttsProgress.setValue(progress)
        )
        self.audioPlayer = AudioPlayer()
        self.textToSpeech.speech_available.connect(
            lambda audio: self.audioPlayer.add_to_queue(audio)
        )
        self.audioPlayer.start()

        # default chunk size is 3000ms
        self.horizontalSlider_chunkSize.setValue(3)
        self.comboBox_modelSize.currentTextChanged.connect(
            self.transcriptionModelSizeChanged
        )

        self.groupBox_statusTranscription.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_statusTranscription, checked
            )
        )
        self.groupBox_statusTranslate.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_statusTranslate, checked
            )
        )
        self.groupBox_cleanStream.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_cleanStream, checked
            )
        )
        toggle_all_widgets_in_a_groupbox(self.groupBox_cleanStream, False)
        self.groupBox_output.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_output, checked
            )
        )
        toggle_all_widgets_in_a_groupbox(self.groupBox_output, False)
        self.groupBox_transcriptionOpts.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_transcriptionOpts, checked
            )
        )
        toggle_all_widgets_in_a_groupbox(self.groupBox_transcriptionOpts, False)
        self.groupBox_langOutputs.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_langOutputs, checked
            )
        )
        toggle_all_widgets_in_a_groupbox(self.groupBox_langOutputs, False)
        self.groupBox_ttsOutput.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_ttsOutput, checked
            )
        )
        toggle_all_widgets_in_a_groupbox(self.groupBox_ttsOutput, False)
        self.groupBox_analyze.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_analyze, checked
            )
        )
        toggle_all_widgets_in_a_groupbox(self.groupBox_analyze, False)
        self.groupBox_translation.toggled.connect(
            lambda checked: toggle_all_widgets_in_a_groupbox(
                self.groupBox_translation, checked
            )
        )
        toggle_all_widgets_in_a_groupbox(self.groupBox_translation, False)

        # language engine change
        self.comboBox_languageEngine.currentIndexChanged.connect(
            self.languageEngineChanged
        )

        # populate languages
        self.comboBox_fromLanguage.addItems(LanguageCodes.getLanguageNames())
        self.comboBox_toLanguage.addItems(LanguageCodes.getLanguageNames())
        self.comboBox_toLanguage.setCurrentIndex(1)

        self.comboBox_transcriptionLanguage.addItem("Auto")
        self.comboBox_transcriptionLanguage.addItems(LanguageCodes.getLanguageNames())
        self.comboBox_transcriptionLanguage.setCurrentIndex(0)

        self.comboBox_transcriptionLanguage.currentTextChanged.connect(
            self.transcriptionLanguageChanged
        )
        self.comboBox_toLanguage.currentIndexChanged.connect(
            self.setTranslationLanguages
        )
        self.comboBox_fromLanguage.currentIndexChanged.connect(
            self.setTranslationLanguages
        )
        self.groupBox_translation.toggled.connect(self.startTranslation)

        # speech engine
        self.comboBox_speechEngine.currentIndexChanged.connect(self.speechEngineChanged)

        # disable everything on comboBox_transcriptionOutputText except for "Text File" and "No text output"
        disable_dropdown_options_by_text(
            self.comboBox_transcriptionOutputText,
            ["No text output", "Text File"],
            negative_case=True,
        )
        disable_dropdown_options_by_text(
            self.comboBox_translationOutputTextOptions,
            ["No text output", "Text File"],
            negative_case=True,
        )
        self.comboBox_transcriptionOutputText.currentIndexChanged.connect(
            self.transcriptionOutputTextChanged
        )
        self.comboBox_translationOutputTextOptions.currentIndexChanged.connect(
            self.translationOutputTextChanged
        )
        self.comboBox_translationSourceSelect.currentIndexChanged.connect(
            self.translationSourceChanged
        )
        disable_dropdown_options_by_text(self.comboBox_translationSourceSelect, "URL")

        self.outputsFolder = None
        self.transcriptionOutputTextFilePath = None
        self.translationOutputTextFilePath = None
        self.obs_client = None

        QTimer.singleShot(10, self.load_settings)

    def load_settings(self):
        main_settings = fetch_data("settings.json", "main", {})
        if main_settings.get("language_engine") is not None:
            self.comboBox_languageEngine.setCurrentText(
                main_settings.get("language_engine")
            )
        if main_settings.get("transcription_output") is not None:
            self.comboBox_transcriptionOutputText.setCurrentText(
                main_settings.get("transcription_output")
            )
        if main_settings.get("translation_output") is not None:
            self.comboBox_translationOutputTextOptions.setCurrentText(
                main_settings.get("translation_output")
            )
        if main_settings.get("translation_source") is not None:
            self.comboBox_translationSourceSelect.setCurrentText(
                main_settings.get("translation_source")
            )
        if main_settings.get("transcription_language") is not None:
            self.comboBox_transcriptionLanguage.setCurrentText(
                main_settings.get("transcription_language")
            )
        if main_settings.get("transcription_model_size") is not None:
            self.comboBox_modelSize.setCurrentText(
                main_settings.get("transcription_model_size")
            )
        if main_settings.get("audio_source") is not None:
            if main_settings.get("audio_source") == "device":
                self.comboBox_audioSources.setCurrentText(
                    main_settings.get("audio_device")
                )
                self.audioSource = AudioSource(
                    AudioSource.SourceType.DEVICE, main_settings.get("audio_device")
                )
            else:
                self.comboBox_audioSources.setCurrentText("Select Audio Source")
        if main_settings.get("from_language") is not None:
            self.comboBox_fromLanguage.setCurrentText(
                main_settings.get("from_language")
            )
        if main_settings.get("to_language") is not None:
            self.comboBox_toLanguage.setCurrentText(main_settings.get("to_language"))
        if main_settings.get("translation_on") is not None:
            self.groupBox_translation.setChecked(main_settings.get("translation_on"))
        if main_settings.get("speech_engine") is not None:
            self.comboBox_speechEngine.setCurrentText(
                main_settings.get("speech_engine")
            )

    def openLogsDialog(self):
        if self.log_dialog is None:
            # open the logs dialog
            self.log_dialog = LogViewerDialog()
            self.log_dialog.setWindowTitle("Logs")

        # show the dialog, non modal
        self.log_dialog.show()

    def openAboutDialog(self):
        # open the about dialog
        about_dialog = QDialog()
        loadUi(
            path.abspath(path.join(path.dirname(__file__), "about.ui")),
            about_dialog,
        )
        about_dialog.setWindowTitle("About Lexis")
        about_dialog.exec()

    def ensure_output_folder(self):
        if self.outputsFolder is None:
            self.outputsFolder = fetch_data("settings.json", "settings", {}).get(
                "outputs_folder", None
            )
        if self.outputsFolder is not None:
            if not path.exists(self.outputsFolder):
                try:
                    os.makedirs(self.outputsFolder)
                except Exception as e:
                    logger.error(f"Error creating outputs folder: {e}")
                    self.outputsFolder = None
                    return False
            return True
        return False

    def speechEngineChanged(self):
        self.textToSpeech.stop()
        if self.comboBox_speechEngine.currentText() == "OpenAI":
            if not fetch_data("settings.json", "settings", {}).get("openai_api_key"):
                self.comboBox_speechEngine.setCurrentIndex(0)
                self.openSettingsDialog(1)
                return
            self.textToSpeech.speech_engine = "OpenAI"
            self.textToSpeech.start()
        elif self.comboBox_speechEngine.currentText() == "ElevenLabs":
            if not fetch_data("settings.json", "settings", {}).get(
                "elevenlabs_api_key"
            ):
                self.comboBox_speechEngine.setCurrentIndex(0)
                self.openSettingsDialog(1)
                return
            self.textToSpeech.speech_engine = "ElevenLabs"
            self.textToSpeech.start()
        else:
            logger.error(
                f"Unknown speech engine: {self.comboBox_speechEngine.currentText()}"
            )
            self.comboBox_speechEngine.setCurrentIndex(0)

        store_data(
            "settings.json",
            "main",
            {"speech_engine": self.comboBox_speechEngine.currentText()},
        )

    def transcriptionLanguageChanged(self):
        logger.debug(
            "transcription language changed to:"
            + self.comboBox_transcriptionLanguage.currentText()
        )
        self.audioTranscriber.set_language(
            self.comboBox_transcriptionLanguage.currentText()
        )
        store_data(
            "settings.json",
            "main",
            {
                "transcription_language": self.comboBox_transcriptionLanguage.currentText()
            },
        )

    def transcriptionModelSizeChanged(self):
        self.audioTranscriber.set_model_size(self.comboBox_modelSize.currentText())
        store_data(
            "settings.json",
            "main",
            {"transcription_model_size": self.comboBox_modelSize.currentText()},
        )

    def transcriptionOutputTextChanged(self):
        self.transcriptionOutputTextFilePath = None
        if self.comboBox_transcriptionOutputText.currentText() == "Text File":
            if not self.ensure_output_folder():
                self.comboBox_transcriptionOutputText.setCurrentIndex(0)
                self.openSettingsDialog(0)
                return
            self.transcriptionOutputTextFilePath = path.join(
                self.outputsFolder, "captions.txt"
            )
            store_data("settings.json", "main", {"transcription_output": "text_file"})

    def translationOutputTextChanged(self):
        self.translationOutputTextFilePath = None
        if self.comboBox_translationOutputTextOptions.currentText() == "Text File":
            if not self.ensure_output_folder():
                self.comboBox_transcriptionOutputText.setCurrentIndex(0)
                self.openSettingsDialog(0)
                return
            self.translationOutputTextFilePath = path.join(
                self.outputsFolder, "translation.txt"
            )
            store_data("settings.json", "main", {"translation_output": "text_file"})

    def translationSourceChanged(self):
        self.textBrowser_transformedTextOutput.setText("")
        if self.transcriptionOutputTextFilePath is not None:
            if self.translation_poller:
                self.translation_poller.stop()
                self.translation_poller.wait()

        if self.comboBox_translationSourceSelect.currentText() == "File":
            fileDialog = QtWidgets.QFileDialog()
            fileDialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
            fileDialog.setNameFilter("Text Files (*.txt)")
            fileDialog.setViewMode(QtWidgets.QFileDialog.ViewMode.List)
            fileDialog.exec()
            fileNames = fileDialog.selectedFiles()
            if fileNames and len(fileNames) > 0:
                if self.translation_poller:
                    self.translation_poller.stop()
                    self.translation_poller.wait()

                self.translation_poller = FilePoller(
                    fileNames[0],
                    cadence=fetch_data("settings.json", "settings", {}).get(
                        "input_file_polling_freq", 1000
                    ),
                    queue=self.translator.input_queue,
                )
                self.translation_poller.start()
                store_data(
                    "settings.json",
                    "main",
                    {"translation_source": "file", "translation_file": fileNames[0]},
                )
        elif self.comboBox_translationSourceSelect.currentText() == "<-- Transcription":
            logger.info("transcription selected as translation source")
            store_data("settings.json", "main", {"translation_source": "transcription"})
        elif (
            self.comboBox_translationSourceSelect.currentText()
            == "--- Get OBS Sources ---"
        ):
            logger.info("Get OBS sources from websocket")
            self.getOBSSourcesForTranslation()
            self.comboBox_translationSourceSelect.setCurrentIndex(0)
        else:
            # obs source selected create an OBSPoller
            if self.obs_client is not None:
                source = self.comboBox_translationSourceSelect.currentText()
                if source.startswith("[OBS]"):
                    source_name = source.split(" - ")[1]
                    self.translation_poller = OBSPoller(
                        self.obs_client,
                        source_name,
                        self.translator.input_queue,
                        int(
                            fetch_data("settings.json", "settings", {}).get(
                                "obs_polling_freq", 1000
                            )
                        ),
                    )
                    self.translation_poller.start()
                    store_data(
                        "settings.json",
                        "main",
                        {"translation_source": "obs", "obs_source": source_name},
                    )
                else:
                    logger.error("Invalid OBS source selected")
                    self.comboBox_translationSourceSelect.setCurrentIndex(0)

    def getOBSSourcesForTranslation(self):
        if self.obs_client is None:
            self.obs_client = open_obs_websocket_from_settings()
        if self.obs_client is not None:
            sources = get_all_text_sources(self.obs_client)
            if sources is not None and len(sources) > 0:
                # remove all previous obs sources that begin from index 3
                if self.comboBox_translationSourceSelect.count() > 4:
                    for _ in range(4, self.comboBox_translationSourceSelect.count()):
                        self.comboBox_translationSourceSelect.removeItem(4)
                # add the new sources
                for source in sources:
                    self.comboBox_translationSourceSelect.addItem(
                        f"[OBS] {source['sceneName']} - {source['sourceName']}"
                    )
                self.comboBox_translationSourceSelect.setCurrentIndex(0)
            else:
                logger.warn("Can't get OBS sources or no sources available")
        else:
            logger.error("OBS client is not connected")
            # open settings dialog
            self.openSettingsDialog(2)

    def openSettingsDialog(self, page=None):
        settingsDialog = SettingsDialog(page, self)
        settingsDialog.exec()

    def languageEngineChanged(self):
        # disable the widgets
        self.widget_textSourceSelect.setEnabled(False)
        self.groupBox_translation.setEnabled(False)

        if self.comboBox_languageEngine.currentText() != "Select Language Engine":
            logger.info(
                f"language engine changed to: {self.comboBox_languageEngine.currentText()}"
            )
            settings = fetch_data("settings.json", "settings", {})
            if self.comboBox_languageEngine.currentText() == "Local LLM":
                # check settings for local LLM folder, if it doesn't exist, open settings dialog
                if not settings.get("local_llm_select"):
                    self.comboBox_languageEngine.setCurrentIndex(0)
                    self.openSettingsDialog(1)
                    return
            if self.comboBox_languageEngine.currentText() == "OpenAI API":
                # check settings for openai api key, if it doesn't exist, open settings dialog
                if not settings.get("openai_api_key"):
                    self.comboBox_languageEngine.setCurrentIndex(0)
                    self.openSettingsDialog(1)
                    return
            if self.comboBox_languageEngine.currentText() == "DeepL API":
                # check settings for deepl api key, if it doesn't exist, open settings dialog
                if not settings.get("deepl_api_key"):
                    self.comboBox_languageEngine.setCurrentIndex(0)
                    self.openSettingsDialog(1)
                    return
            # enable the widgets
            self.widget_textSourceSelect.setEnabled(True)
            self.groupBox_translation.setEnabled(True)
            self.translator.setTranslationEngine(
                self.comboBox_languageEngine.currentText()
            )
            store_data(
                "settings.json",
                "main",
                {"language_engine": self.comboBox_languageEngine.currentText()},
            )
        else:
            self.startTranslation(False)
            self.translator.setTranslationEngine(None)

    def setTranslationLanguages(self):
        self.translator.setLanguages(
            self.comboBox_fromLanguage.currentText(),
            self.comboBox_toLanguage.currentText(),
        )
        store_data(
            "settings.json",
            "main",
            {
                "from_language": self.comboBox_fromLanguage.currentText(),
                "to_language": self.comboBox_toLanguage.currentText(),
            },
        )

    def startTranslation(self, checked):
        store_data("settings.json", "main", {"translation_on": checked})
        if checked:
            self.translator.start()
        else:
            self.translator.stop()

    def populateAudioSources(self):
        self.comboBox_audioSources.clear()
        # add select audio source option
        self.comboBox_audioSources.insertItem(0, "Select Audio Source")
        self.comboBox_audioSources.setCurrentIndex(0)
        audioDevices = AudioRecorder.get_audio_devices()
        for device in audioDevices:
            self.comboBox_audioSources.addItem(device.sourceName)
        self.comboBox_audioSources.addItem("--- NDI Sources ---")
        disable_dropdown_options_by_text(
            self.comboBox_audioSources, "--- NDI Sources ---"
        )
        # add file input option
        self.comboBox_audioSources.addItem("File")
        # add stream option
        self.comboBox_audioSources.addItem("Stream")
        disable_dropdown_options_by_text(self.comboBox_audioSources, "Stream")

    def audioSourceChanged(self):
        logger.info("audio source changed")
        self.audioSource = None
        # if file input selected, open file dialog
        if self.comboBox_audioSources.currentText() == "File":
            logger.info("file input selected")
            fileDialog = QtWidgets.QFileDialog()
            fileDialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
            fileDialog.setNameFilter(
                "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a *.aac)"
            )
            fileDialog.setViewMode(QtWidgets.QFileDialog.ViewMode.List)
            fileDialog.exec()
            fileNames = fileDialog.selectedFiles()
            if fileNames and len(fileNames) > 0:
                logger.info(f"file selected: {fileNames[0]}")
                self.audioSource = AudioSource(
                    AudioSource.SourceType.FILE, fileNames[0]
                )
                store_data(
                    "settings.json",
                    "main",
                    {"audio_source": "file", "audio_file": fileNames[0]},
                )
        else:
            logger.info("device input selected")
            if self.comboBox_audioSources.currentText() != "Select Audio Source":
                self.audioSource = AudioSource(
                    AudioSource.SourceType.DEVICE,
                    self.comboBox_audioSources.currentText(),
                )
                store_data(
                    "settings.json",
                    "main",
                    {
                        "audio_source": "device",
                        "audio_device": self.comboBox_audioSources.currentText(),
                    },
                )

        self.startAudioCapture()

    def startAudioCapture(self):
        logger.info("stopping exsting audio capture and starting new")
        if self.audioCapture:
            self.audioTranscriber.stop()
            self.audioTranscriber.wait()
            self.audioCapture.stop()
            self.audioCapture.wait()
            self.audioCapture = None

        if self.audioSource:
            self.audioTranscriber.start()
            logger.info(f"audio source: {self.audioSource.sourceName}")
            # start audio capture
            logger.info(
                f"starting audio capture with chunk size: {self.horizontalSlider_chunkSize.value()}"
            )
            self.audioCapture = AudioRecorder(
                self.audioSource, self.horizontalSlider_chunkSize.value() * 1000
            )
            self.audioCapture.progress_and_volume.connect(self.audioCaptureProgress)
            self.audioCapture.data_available.connect(
                self.audioTranscriber.queue_audio_data
            )
            self.audioCapture.start()

    def audioCaptureProgress(self, progress):
        # update the volume progressbar
        self.progressBar_audioSignal.setValue(int(progress[1] * 300))
        # update the buffer progressbar
        chunk_size_ms = float(self.horizontalSlider_chunkSize.value()) * 1000.0
        buffer_capacity = int(float(progress[0]) / chunk_size_ms * 100.0)
        self.progressBar_audioBuffer.setValue(buffer_capacity)
        # redraw the progressbars
        self.progressBar_audioSignal.repaint()
        self.progressBar_audioBuffer.repaint()

    def transcriptionAvailable(self, text):
        logger.info(f"transcribed text available: {text}")
        self.textBrowser_output.setText(text)
        # if translation is on - send to translator thread
        if self.groupBox_translation.isChecked():
            if (
                self.comboBox_translationSourceSelect.currentText()
                == "<-- Transcription"
            ):
                if self.translator.running:
                    self.translator.input_queue.put_nowait(text)
                else:
                    logger.error("Translator thread is not running")
        if self.transcriptionOutputTextFilePath is not None:
            try:
                # save to file with utf-8 encoding
                with open(
                    self.transcriptionOutputTextFilePath, "w", encoding="utf-8"
                ) as f:
                    f.write(text + "\n")
            except Exception as e:
                logger.error(f"Error saving transcription to file: {e}")

    def translationTextAvailable(self, text):
        logger.info(f"translated text available: {text}")
        self.textBrowser_transformedTextOutput.setText(text)
        if self.translationOutputTextFilePath is not None:
            try:
                # save to file with utf-8 encoding
                with open(
                    self.translationOutputTextFilePath, "w", encoding="utf-8"
                ) as f:
                    f.write(text + "\n")
            except Exception as e:
                logger.error(f"Error saving translation to file: {e}")
        # check if tts is on
        if self.comboBox_speechEngine.currentText() != "Select TTS Engine":
            self.textToSpeech.add_text(text)

    def closeEvent(self, event):
        logger.debug("closing")
        if self.audioCapture:
            self.audioCapture.stop()
            logger.debug("audio capture stopped, waiting for thread to finish")
            self.audioCapture.wait()
        self.audioTranscriber.stop()
        logger.debug("transcription thread stopped. waiting for thread to finish")
        self.audioTranscriber.wait()
        self.translator.stop()
        logger.debug("translation thread stopped. waiting for thread to finish")
        self.translator.wait()
        if self.translation_poller:
            self.translation_poller.stop()
            self.translation_poller.wait()
        if self.obs_client:
            disconnect_obs_websocket(self.obs_client)
        event.accept()


if __name__ == "__main__":
    # only attempt splash when not on Mac OSX
    os_name = platform.system()
    if os_name != "Darwin":
        try:
            import pyi_splash  # type: ignore

            pyi_splash.close()
        except ImportError:
            pass

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
