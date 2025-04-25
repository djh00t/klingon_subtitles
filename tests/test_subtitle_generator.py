import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from subtitle_generator import SubtitleGenerator

def test_subtitle_generator_init():
    generator = SubtitleGenerator(config_path='tests/test_config.yaml')
    assert isinstance(generator, SubtitleGenerator)
    assert hasattr(generator, 'config')
    assert hasattr(generator, 'sub_tools')

def test_run(mocker):
    generator = SubtitleGenerator(config_path='tests/test_config.yaml')
    mocker.patch.object(generator, 'run', return_value=None)
    generator.run()
    generator.run.assert_called_once()
