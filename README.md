# Subtitle Generator Daemon

## Overview

This project is a **subtitle generator daemon** that watches for new video or audio content in specified directories. It automatically extracts audio, transcribes it using a Hugging Face model, and generates fully timecode-aligned SRT subtitles. It handles sentence detection, speaker change detection, and punctuation, ensuring high-quality subtitles. Additionally, the system can detect broken or misaligned subtitles and realign or regenerate them.

Key Features:
- **Automatic Transcription**: Extracts audio from video files and uses machine learning models to generate subtitles.
- **Speaker Detection**: Detects and labels speaker changes using a speaker diarization model.
- **Subtitle Alignment**: Realigns subtitles if they are misaligned or regenerates them if they are broken.
- **Embedded Subtitle Management**: Strips embedded subtitles if necessary.
- **File System Watcher**: Monitors directories for new or modified files and automatically processes them.

---

## Architecture

The project consists of several modules:

1. **`sub_tools.py`**: Contains tools to manage subtitles, such as checking for existing subtitles, realigning, and formatting them.
2. **`processor.py`**: Handles the core functionality for processing video files, including transcription, speaker diarization, and subtitle generation.
3. **`srt_generator.py`**: Generates an SRT file from transcribed text and segments.
4. **`watcher.py`**: Monitors directories for new or modified video/audio files and triggers subtitle generation or correction.
5. **`__init__.py`**: Initializes the project and starts the watcher.
6. **`__main__.py`**: Entry point for running the application.

---

## Prerequisites

Before running this project, ensure you have the following installed:

1. **Python 3.8+**: This project requires Python 3.8 or later.
2. **Poetry**: Used for dependency management, building, and publishing to PyPI.
3. **ffmpeg**: Required for audio extraction and handling video files with embedded subtitles.
4. **Hugging Face Transformers**: Used for automatic speech recognition (ASR) with models like `openai/whisper-large`.
5. **pyannote.audio**: Used for speaker diarization.
6. **watchdog**: Monitors file system events to trigger the subtitle generation process.

You can install Poetry by following the official instructions:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/subtitle-generator-daemon.git
cd subtitle-generator-daemon
```

### 2. Install Dependencies with Poetry

Poetry handles all the dependencies, including those listed in the `pyproject.toml` file.

```bash
poetry install
```

### 3. Install **ffmpeg**

- On macOS: 
  ```bash
  brew install ffmpeg
  ```
- On Ubuntu:
  ```bash
  sudo apt install ffmpeg
  ```
- On Windows: Download it from [FFmpeg.org](https://ffmpeg.org/download.html).

### 4. Set up the Hugging Face API Token

Set the **Hugging Face API token** as an environment variable if you're using models that require authentication:

```bash
export HUGGINGFACE_TOKEN=your_token_here
```

---

## Configuration

The application uses a YAML configuration file located at `config/config.yaml`. This file contains settings for directories to watch, output subtitle extensions, and the Hugging Face ASR model to use. You can customize this file based on your environment.

Example `config.yaml`:

```yaml
log_level: "INFO"

# Directories to watch for new or modified video files
watch_directories:
  - "/path/to/your/video/files"

# The output extension for generated subtitle files
output_extension: ".srt"

# Hugging Face ASR model to use
huggingface_model: "openai/whisper-large"

# Directory for temporary audio extraction
temp_audio_directory: "/tmp"
```

### Customization

- **`watch_directories`**: List the directories where the watcher should monitor for new video/audio content.
- **`output_extension`**: Define the file extension for the generated subtitle files.
- **`huggingface_model`**: Specify the Hugging Face ASR model for transcription.
- **`temp_audio_directory`**: Set the directory where temporary audio files are stored during processing.

---

## Running the Application

### Run with Poetry

Once the environment is set up, you can run the project directly using Poetry:

```bash
poetry run python -m subtitle_generator_daemon
```

This will start watching the specified directories for new or modified video/audio files and generate subtitles automatically.

### Example Workflow

1. **Watching for New Files**:
   The daemon continuously monitors the configured directories. When a new video file (e.g., `.mp4`, `.mkv`) is detected, it processes the file, extracts audio, and transcribes it into subtitles.

2. **Processing Files**:
   If a video file has no external subtitles, the system generates an SRT file and saves it in the same directory as the video file. If the file contains broken or misaligned subtitles, the system will attempt to realign or regenerate them.

3. **Embedded Subtitle Stripping**:
   If a video contains embedded subtitles, the system can strip these subtitles and generate a clean subtitle file with the new transcription.

---

## Example

Assume you have a directory `/videos` with a video file `sample_video.mp4`. Here’s how you would set up and run the subtitle generator:

1. Update `config.yaml` to point to the `/videos` directory:

   ```yaml
   watch_directories:
     - "/videos"
   output_extension: ".srt"
   huggingface_model: "openai/whisper-large"
   ```

2. Start the subtitle generator:

   ```bash
   poetry run python -m subtitle_generator_daemon
   ```

3. Add a video file (`sample_video.mp4`) to the `/videos` directory. The system will detect the new file, extract the audio, transcribe it, and generate `sample_video.srt` in the same directory.

---

## Publishing to PyPI

### Build and Publish with Poetry

This project uses Poetry for packaging and publishing to PyPI.

1. **Configure PyPI credentials**:

   Make sure you have the following credentials stored in your Poetry configuration:

   ```bash
   poetry config pypi-token.pypi your-pypi-token-here
   ```

2. **Build the package**:

   You can build the project using Poetry's build command:

   ```bash
   poetry build
   ```

3. **Publish to PyPI**:

   After building, you can publish the package to PyPI:

   ```bash
   poetry publish --build
   ```

   This will upload your package to PyPI for distribution.

---

## Code Overview

### 1. `processor.py`
- **Handles the core processing of video/audio files**: Extracts audio, transcribes speech, and generates subtitles.
- **Speaker Diarization**: Uses the `pyannote.audio` library to detect speaker changes and annotate them in the subtitle file.
- **Embedded Subtitle Stripping**: Strips embedded subtitles from video files using `ffmpeg`.

### 2. `sub_tools.py`
- **Manages subtitle operations**: Checks if subtitles already exist, verifies alignment, removes formatting, and realigns or deletes broken subtitles.

### 3. `srt_generator.py`
- **Converts transcription segments into SRT format**: Generates time-aligned subtitle files from transcribed audio.

### 4. `watcher.py`
- **File system watcher**: Uses the `watchdog` library to monitor directories for new or modified files, triggering subtitle generation when necessary.

### 5. `__main__.py`
- **Main entry point**: Initializes the `SubtitleGenerator` and starts the file watcher.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests on GitHub.

---

## Authors

- **David Hooton** - _Initial Work_

---

This `README.md` now includes instructions on how to use **Poetry** for dependency management, running the project, and publishing it to **PyPI**. It also explains how to configure the system, run the watcher, and manage subtitle generation for video/audio files.