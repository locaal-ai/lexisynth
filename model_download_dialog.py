from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
import requests
import os
from platformdirs import user_data_dir
import zipfile
from ls_logging import logger
from models_info import checkForModelDownload
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import QThread
from os import path


class ModelDownloadDialog(QDialog):
    def __init__(self, modelInfo, parent=None):
        super(ModelDownloadDialog, self).__init__(parent)
        uic.loadUi(
            path.abspath(path.join(path.dirname(__file__), "model_download_dialog.ui")),
            self,
        )
        # start the download process
        self.modelInfo = modelInfo
        self.downloadThread = None
        self.startDownload()

    def startDownload(self):
        # start the download process
        self.label_modelDownloading.setText(
            f"Downloading {self.modelInfo['model_name']}"
        )
        # start the download on a separate QThread
        self.downloadThread = ModelDownloadThread(self.modelInfo)
        self.downloadThread.finished.connect(self.finished)
        self.downloadThread.progressSignal.connect(self.progress)
        self.downloadThread.start()

    def finished(self):
        self.downloadThread = None
        # close the dialog
        self.accept()

    def progress(self, progress: int, message: str):
        # update the progress bar
        self.progressBar.setValue(progress)
        self.label_progress.setText(message)

    def closeEvent(self, event):
        # stop the download thread if it is running
        if self.downloadThread is not None:
            self.downloadThread.running = False
            self.downloadThread.wait()
            self.downloadThread = None
        super(ModelDownloadDialog, self).closeEvent(event)


class ModelDownloadThread(QThread):
    # progress and message signal
    progressSignal = pyqtSignal(int, str)

    def __init__(self, modelInfo):
        super(ModelDownloadThread, self).__init__()
        self.modelInfo = modelInfo
        self.running = False

    def run(self):
        # download the model

        # get the file name
        url = self.modelInfo["url"]
        file_name = url.split("/")[-1]
        # put file in user data folder for lexisynth
        data_dir = user_data_dir("lexisynth")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        file_name = os.path.join(data_dir, file_name)
        logger.debug(f"Downloading model to {file_name}")

        # check if the file already exists
        if checkForModelDownload(self.modelInfo):
            # file already exists, no need to download
            self.progressSignal.emit((100, "Model already downloaded"))
            return
        # check if .zip leftover found from previous download
        if os.path.exists(file_name):
            os.remove(file_name)

        # download the file
        r = requests.get(url, stream=True)
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))

        self.running = True
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if not self.running:
                    return
                if chunk:
                    f.write(chunk)
                    # update progress bar according to the download
                    self.progressSignal.emit(
                        int(100 * f.tell() / total_size),
                        "Progress {0:.2f}%".format(100 * f.tell() / total_size),
                    )

        self.progressSignal.emit(100, "Model downloaded successfully. Unzipping...")
        # unzip the file
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(
                os.path.join(data_dir, self.modelInfo["model_folder_name"])
            )
        # remove the zip file
        os.remove(file_name)

        self.progressSignal.emit(100, "Model unzipped successfully")
