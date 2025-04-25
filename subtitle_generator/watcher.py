# subtitle_generator/watcher.py

import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subtitle_generator.processor import Processor
from subtitle_generator.sub_tools import SubTools, SubtitleVerifier
from subtitle_generator.utils import load_config

class SubtitleEventHandler(FileSystemEventHandler):
    """
    Handles file system events, particularly watching for new or modified video files
    to process and generate subtitles.
    """

    def __init__(self, output_extension, processor, sub_tools):
        """
        Initializes the event handler with necessary tools for subtitle processing.

        Args:
            output_extension (str): Extension for the output subtitle file (e.g., .srt).
            processor (Processor): The Processor object responsible for file transcription and processing.
            sub_tools (SubTools): The SubTools object to manage subtitle operations.
        """
        super().__init__()
        self.output_extension = output_extension
        self.processor = processor
        self.sub_tools = sub_tools
        logging.info("SubtitleEventHandler initialized")
        logging.debug(f"Output extension: {output_extension}")

    def process(self, file_path):
        """
        Processes the video file to check for subtitles, strip embedded ones if needed,
        and generate new subtitles if none exist or if they are broken.

        Args:
            file_path (str): Path to the video or audio file being processed.
        """
        logging.info(f"Processing file: {file_path}")
        
        # Only process video or audio files
        if not file_path.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.aac', '.flac')):
            logging.info(f"Unsupported file type: {file_path}")
            return

        logging.debug("Checking for existing subtitles")
        # Check for external and embedded subtitles
        external_subs = self.sub_tools.has_external_subtitles(file_path, self.output_extension)
        embedded_subs = self.sub_tools.has_embedded_subtitles(file_path)
        srt_path = os.path.splitext(file_path)[0] + self.output_extension

        if external_subs:
            logging.info(f"External subtitles found for {file_path}")
            if SubtitleVerifier.is_subtitle_broken(srt_path):
                logging.info(f"Broken subtitles detected for {file_path}. Regenerating...")
                logging.debug(f"Removing broken subtitles: {srt_path}")
                os.remove(srt_path)  # Delete broken subtitles
                logging.info("Generating new subtitles")
                self.processor.process_file(file_path, self.output_extension)  # Generate new subtitles
            else:
                logging.info(f"Valid external subtitles exist for {file_path}. Skipping...")
        elif embedded_subs:
            logging.info(f"Embedded subtitles found in {file_path}")
            if self.should_strip_subtitles(file_path):
                logging.info(f"Stripping embedded subtitles from {file_path}")
                new_file_path = self.processor.strip_embedded_subtitles(file_path)
                if new_file_path:
                    logging.info(f"Generating new subtitles for stripped file: {new_file_path}")
                    self.processor.process_file(new_file_path, self.output_extension)  # Generate new subtitles
            else:
                logging.info(f"Keeping embedded subtitles in {file_path}. Skipping...")
        else:
            logging.info(f"No subtitles found for {file_path}. Generating new subtitles...")
            self.processor.process_file(file_path, self.output_extension)

    def should_strip_subtitles(self, file_path):
        """
        Determines if embedded subtitles should be stripped based on logic or configuration.

        Args:
            file_path (str): Path to the video file.

        Returns:
            bool: True if embedded subtitles should be stripped, False otherwise.
        """
        # Custom logic or config-based condition to decide when to strip subtitles.
        # Currently set to always strip embedded subtitles for simplicity.
        return True

    def on_created(self, event):
        """
        Called when a new file is created in the watched directory.

        Args:
            event (FileSystemEvent): Event data describing the created file or directory.
        """
        if not event.is_directory:
            logging.info(f"New file detected: {event.src_path}")
            self.process(event.src_path)

    def on_modified(self, event):
        """
        Called when a file is modified in the watched directory.

        Args:
            event (FileSystemEvent): Event data describing the modified file or directory.
        """
        if not event.is_directory:
            logging.info(f"File modified: {event.src_path}")
            self.process(event.src_path)

class Watcher:
    """
    Watches for file system changes in specified directories and triggers subtitle processing.
    """

    def __init__(self, config, sub_tools):
        """
        Initializes the watcher with the provided configuration and tools.

        Args:
            config (dict): Configuration settings, typically loaded from a YAML file.
            sub_tools (SubTools): The SubTools object to manage subtitle operations.
        """
        self.config = config
        self.output_extension = config.get('output_extension', '.srt')
        self.processor = Processor(self.config)
        self.sub_tools = sub_tools
        self.observer = Observer()

    def start_watching(self):
        """
        Starts the file system watcher, monitoring directories specified in the configuration.
        """
        logging.info("Watcher started.")
        event_handler = SubtitleEventHandler(self.output_extension, self.processor, self.sub_tools)

        for directory in self.config.get('watch_directories', []):
            if os.path.exists(directory):
                logging.info(f"Watching directory: {directory}")
                self.observer.schedule(event_handler, directory, recursive=True)
            else:
                logging.warning(f"Directory does not exist and will not be watched: {directory}")

        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Watcher stopped.")
            self.observer.stop()

        self.observer.join()

if __name__ == "__main__":
    config = load_config()
    logging.basicConfig(level=config.get('log_level', 'DEBUG'))
    sub_tools = SubTools()
    watcher = Watcher(config, sub_tools)
    watcher.start_watching()
