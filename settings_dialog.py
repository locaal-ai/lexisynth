from model_download_dialog import ModelDownloadDialog
from models_info import ModelDownloadInfo, checkForModelDownload
from obs_websocket import disconnect_obs_websocket, open_obs_websocket
from os import path
from platformdirs import user_data_dir
from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QFileDialog
from PyQt6.uic import loadUi
from storage import fetch_data, store_data


class SettingsDialog(QDialog):
    settingsChanged = pyqtSignal(dict)

    def __init__(self, page=None, parent=None):
        super(SettingsDialog, self).__init__(parent)

        loadUi(
            path.abspath(path.join(path.dirname(__file__), "settings_dialog.ui")), self
        )

        # select the page if provided in tabWidget
        if page is not None:
            self.tabWidget.setCurrentIndex(page)

        # load data from settings
        self.loadSettings()

        # if dialog is accepted, save the settings
        self.accepted.connect(self.saveSettings)

        self.toolButton_selectLLMFolder.clicked.connect(
            lambda: self.selectFolderForLineEdit(self.lineEdit_localLLMFolder)
        )
        self.toolButton_outputsFolderSelect.clicked.connect(
            lambda: self.selectFolderForLineEdit(self.lineEdit_outputsFolder)
        )
        self.comboBox_localLLMSelect.currentIndexChanged.connect(
            self.localLLMSelectChanged
        )
        self.pushButton_obsTestConnection.clicked.connect(self.testObsConnection)
        self.lineEdit_inputFilePollingFreq.setValidator(
            QtGui.QIntValidator(100, 100000, self)
        )
        self.lineEdit_obsPollingFreq.setValidator(
            QtGui.QIntValidator(100, 100000, self)
        )

    def localLLMSelectChanged(self, index):
        if self.comboBox_localLLMSelect.currentText() == "Custom":
            self.lineEdit_localLLMFolder.setEnabled(True)
            self.toolButton_selectLLMFolder.setEnabled(True)
        else:
            self.lineEdit_localLLMFolder.setEnabled(False)
            self.toolButton_selectLLMFolder.setEnabled(False)
            if self.comboBox_localLLMSelect.currentText() == "M2M-100 Translation":
                # check if model has been downloaded already
                if checkForModelDownload(ModelDownloadInfo.M2M_100):
                    return
                # show the download dialog
                modelDownloadDialog = ModelDownloadDialog(
                    ModelDownloadInfo.M2M_100, self
                )
                if modelDownloadDialog.exec() == QDialog.DialogCode.Rejected:
                    # if the download was cancelled, revert to the previous selection
                    self.comboBox_localLLMSelect.setCurrentIndex(0)
                    return

                if not checkForModelDownload(ModelDownloadInfo.M2M_100):
                    # if the model was not downloaded, revert to the previous selection
                    self.comboBox_localLLMSelect.setCurrentIndex(0)
                    return

    def selectFolderForLineEdit(self, lineEdit):
        # open a file dialog to select the LLM folder
        folder = lineEdit.text()
        folder = QFileDialog.getExistingDirectory(self, "Select a folder", folder)
        if folder:
            lineEdit.setText(folder)

    def loadSettings(self):
        # load settings from storage
        settings = fetch_data("settings.json", "settings", {})
        self.lineEdit_localLLMFolder.setText(settings.get("local_llm_folder", ""))
        self.lineEdit_openaiapikey.setText(settings.get("openai_api_key", ""))
        self.lineEdit_deeplapikey.setText(settings.get("deepl_api_key", ""))
        self.lineEdit_obsHost.setText(settings.get("obs_host", "localhost"))
        self.lineEdit_obsPort.setText(settings.get("obs_port", "4455"))
        self.lineEdit_obsPassword.setText(settings.get("obs_password", ""))
        self.lineEdit_obsPollingFreq.setText(settings.get("obs_polling_freq", "1000"))
        self.lineEdit_inputFilePollingFreq.setText(
            settings.get("input_file_polling_freq", "1000")
        )
        self.lineEdit_elevenlabsAPIKey.setText(settings.get("elevenlabs_api_key", ""))

        if settings.get("local_llm_select") is not None:
            self.comboBox_localLLMSelect.setCurrentIndex(
                settings.get("local_llm_select")
            )

        if settings.get("outputs_folder", "") == "":
            settings["outputs_folder"] = path.join(
                user_data_dir("lexisynth"), "outputs"
            )
            store_data("settings.json", "settings", settings)
        self.lineEdit_outputsFolder.setText(settings.get("outputs_folder", ""))

    def saveSettings(self):
        # save settings to storage
        settings = {"outputs_folder": self.lineEdit_outputsFolder.text()}
        if self.lineEdit_localLLMFolder.text() != "":
            settings["local_llm_folder"] = self.lineEdit_localLLMFolder.text()
        if self.lineEdit_openaiapikey.text() != "":
            settings["openai_api_key"] = self.lineEdit_openaiapikey.text()
        if self.lineEdit_deeplapikey.text() != "":
            settings["deepl_api_key"] = self.lineEdit_deeplapikey.text()
        if self.lineEdit_obsHost.text() != "":
            settings["obs_host"] = self.lineEdit_obsHost.text()
        if self.lineEdit_obsPort.text() != "":
            settings["obs_port"] = self.lineEdit_obsPort.text()
        if self.label_obsPollingFreq.text() != "":
            settings["obs_polling_freq"] = self.lineEdit_obsPollingFreq.text()
        if self.lineEdit_obsPassword.text() != "":
            settings["obs_password"] = self.lineEdit_obsPassword.text()
        if self.lineEdit_inputFilePollingFreq.text() != "":
            settings["input_file_polling_freq"] = (
                self.lineEdit_inputFilePollingFreq.text()
            )
        if self.comboBox_localLLMSelect.currentIndex() != 0:
            settings["local_llm_select"] = self.comboBox_localLLMSelect.currentIndex()
        if self.lineEdit_elevenlabsAPIKey.text() != "":
            settings["elevenlabs_api_key"] = self.lineEdit_elevenlabsAPIKey.text()

        store_data("settings.json", "settings", settings)

        # emit a signal to notify the main window that settings have changed
        self.settingsChanged.emit(settings)

    def testObsConnection(self):
        # test the OBS connection
        obs_host = self.lineEdit_obsHost.text()
        obs_port = self.lineEdit_obsPort.text()
        obs_password = self.lineEdit_obsPassword.text()
        obs_client = open_obs_websocket(
            {"ip": obs_host, "port": obs_port, "password": obs_password}
        )
        if obs_client is not None:
            self.label_obsConnectionStatus.setText("Connection Successful")
            # close the connection
            disconnect_obs_websocket(obs_client)
        else:
            self.label_obsConnectionStatus.setText("Failed")
