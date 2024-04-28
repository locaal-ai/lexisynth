# LexiSynth

LexiSynth is an AI speech analysis and synthesis tool built with Python. It leverages the power of PyInstaller, CTranslate2, and Faster-Whisper to provide a robust and efficient solution for speech processing tasks.

## Features

- Speech Analysis: Analyze speech patterns and extract meaningful insights.
- Speech Synthesis: Convert text into natural-sounding speech.
- Built with Python: Leverage the power and simplicity of Python for customization and rapid development.
- CTranslate2 and Faster-Whisper: Utilize these powerful libraries for efficient and high-quality speech processing.

## Build Instructions

To build LexiSynth using PyInstaller, follow the steps below:

1. Ensure you have Python 3.11. You can check your Python version by running `python --version` in your terminal.

2. Install the required Python packages. In the root directory of the project, run:

```bash
pip install -r requirements.txt
```

3. Build the executable using PyInstaller. In the root directory of the project, run:

MacOSX:
```bash
pyinstaller --clean --noconfirm lexisynth.spec -- --mac_osx
```

Windows:
```bash
pyinstaller --clean --noconfirm lexisynth.spec -- --win
```

This will create a `dist` directory containing the executable file for LexiSynth.

## Usage

To use LexiSynth, simply run the executable file created in the `dist` directory.

## License

This project is released under the MIT license. See [LICENSE](LICENSE) for details.
