from os import path
from platformdirs import user_data_dir


class ModelDownloadInfo:
    # URLs for downloading the models
    M2M_100 = {
        "url": "https://lexistream-downloads.s3.amazonaws.com/m2m_100_418M-ct2-int8.zip",
        "file_name": "m2m_100_418M-ct2-int8.zip",
        "model_folder_name": "M2M-100",
        "model_name": "M2M-100",
    }
    FASTER_WHISPER_TINY_CT2 = {
        "url": "https://lexistream-downloads.s3.amazonaws.com/faster-whisper-tiny-ct2-int8.zip",
        "file_name": "faster-whisper-tiny-ct2-int8.zip",
        "model_folder_name": "Faster-Whisper-Tiny-CT2",
        "model_name": "Faster-Whisper Tiny",
    }
    FASTER_WHISPER_BASE_CT2 = {
        "url": "https://lexistream-downloads.s3.amazonaws.com/faster-whisper-base-ct2-int8.zip",
        "file_name": "faster-whisper-base-ct2-int8.zip",
        "model_folder_name": "Faster-Whisper-Base-CT2",
        "model_name": "Faster-Whisper Base",
    }
    FASTER_WHISPER_SMALL_CT2 = {
        "url": "https://lexistream-downloads.s3.amazonaws.com/faster-whisper-small-ct2-int8.zip",
        "file_name": "faster-whisper-small-ct2-int8.zip",
        "model_folder_name": "Faster-Whisper-Small-CT2",
        "model_name": "Faster-Whisper Small",
    }


def checkForModelDownload(modelInfo):
    # check if the model has been downloaded to the data dir
    data_dir = user_data_dir("lexisynth")
    if not path.exists(data_dir):
        return False
    model_dir = path.join(data_dir, modelInfo["model_folder_name"])
    if not path.exists(model_dir):
        return False
    return True


def getAbsoluteModelPath(modelInfo):
    # get the absolute path to the model
    data_dir = user_data_dir("lexisynth")
    return path.join(data_dir, modelInfo["model_folder_name"])
