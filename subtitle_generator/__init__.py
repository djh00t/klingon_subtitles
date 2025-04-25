# subtitle_generator/__init__.py
from subtitle_generator.watcher import Watcher
from subtitle_generator.sub_tools import SubTools, SubtitleVerifier
from subtitle_generator.processor import Processor
from subtitle_generator.srt_generator import generate_srt
from subtitle_generator.utils import load_config

__all__ = ['Watcher', 'SubTools', 'SubtitleVerifier', 'Processor', 'generate_srt', 'SubtitleGenerator']

class SubtitleGenerator:
    """
    Main class for initializing and running the subtitle generation process.
    Loads the configuration and starts the watcher for subtitle processing.
    """

    def __init__(self, config_path='config/config.yaml'):
        """
        Initializes the subtitle generator by loading configuration settings.
        
        Args:
            config_path (str): Path to the YAML configuration file.
        """
        self.config = load_config(config_path)
        self.sub_tools = SubTools()

    def run(self):
        """
        Starts the file watcher and processes any newly added files based on configuration.
        """
        watcher = Watcher(self.config, self.sub_tools)
        watcher.start_watching()
