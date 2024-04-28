# -*- mode: python ; coding: utf-8 -*-
import os

# parse command line arguments
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--mac_osx', action='store_true')
parser.add_argument('--win', action='store_true')

args = parser.parse_args()

a = Analysis(
    [
        'audio_capture.py',
        'audio_player.py',
        'file_poller.py',
        'language_codes.py',
        'lexisynth_types.py',
        'log_view.py',
        'ls_logging.py',
        'main.py',
        'model_download_dialog.py',
        'models_info.py',
        'obs_websocket.py',
        'settings_dialog.py',
        'storage.py',
        'transcription.py',
        'translation.py',
    ],
    pathex=[],
    binaries=[],
    datas=[
        ('about.ui', '.'),
        ('log_view.ui', '.'),
        ('mainwindow.ui', '.'),
        ('model_download_dialog.ui', '.'),
        ('settings_dialog.ui', '.'),
        ('.env', '.'),
        ('icons/splash.png', './icons'),
        ('icons/MacOS_icon.png', './icons'),
        ('icons/Windows-icon-open.ico', '.icons'),
        ('silero_vad.onnx', './faster_whisper/assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["botocore", "transformers", "IPython", "tensorflow", "matplotlib", "pandas", "sklearn", "skimage", "scipy", "torch", "torchvision", "torchaudio", "nltk", "cv2"],
    noarchive=False,
)

exclude = ["IPython", "tensorflow", "matplotlib", "pandas", "sklearn", "skimage", "scipy", "torch", "torchvision", "torchaudio", "nltk", "cv2"]
a.binaries = [x for x in a.binaries if not x[0].startswith(tuple(exclude))]

pyz = PYZ(a.pure)

if args.win:
    splash = Splash('icons/splash.png',
                    binaries=a.binaries,
                    datas=a.datas,
                    text_pos=(10, 20),
                    text_size=10,
                    text_color='black')
    exe = EXE(
        pyz,
        a.scripts,
        splash,
        name='lexisynth',
        icon='icons/Windows-icon-open.ico',
        debug=False,
        exclude_binaries=True,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        splash.binaries,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='lexisynth'
    )
elif args.mac_osx:
    exe = EXE(pyz,
            a.scripts,
            [],
            exclude_binaries=True,
            name='lexisynth',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            upx_exclude=[],
            runtime_tmpdir=None,
            console=False,
            disable_windowed_traceback=False,
            argv_emulation=False,
            target_arch=None,
            codesign_identity=os.environ.get('APPLE_APP_DEVELOPER_ID', ''),
            entitlements_file='./entitlements.plist',
            )
    coll = COLLECT(exe,
                a.binaries,
                a.zipfiles,
                a.datas,
                strip=False,
                upx=True,
                upx_exclude=[],
                name='lexisynth')
    app = BUNDLE(
        exe,
        coll,
        name='lexisynth.app',
        icon='icons/MacOS_icon.png',
        bundle_identifier='com.royshilkrot.lexisynth',
        version='0.0.1',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'NSMicrophoneUsageDescription': 'Getting audio from the microphone to perform speech-to-text'
        }
    )
else:
    # Linux
    splash = Splash('icons/splash.png',
                    binaries=a.binaries,
                    datas=a.datas,
                    text_pos=(10, 20),
                    text_size=10,
                    text_color='black')
    exe = EXE(
        pyz,
        a.binaries,
        a.datas,
        a.scripts,
        splash,
        splash.binaries,
        name='lexisynth',
        icon='icons/Windows-icon-open.ico',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
    )
