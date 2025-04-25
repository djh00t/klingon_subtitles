import os
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from subtitle_generator import Processor

@pytest.fixture
def processor():
    return Processor(config_path='tests/test_config.yaml')

@pytest.fixture
def test_video_path(tmp_path):
    return tmp_path / "test_video.mp4"

@pytest.fixture
def test_audio_path(tmp_path):
    return tmp_path / "test_audio.wav"

def test_extract_audio(processor, test_video_path, test_audio_path):
    # Create a dummy video file
    test_video_path.write_bytes(b"dummy video content")
    
    audio_path = processor.extract_audio(str(test_video_path), str(test_audio_path))
    assert audio_path is not None
    assert os.path.exists(audio_path)
    os.remove(audio_path)

def test_process_file(processor, test_video_path):
    # Create a dummy video file
    test_video_path.write_bytes(b"dummy video content")
    
    processor.process_file(str(test_video_path))
    srt_path = test_video_path.with_suffix('.srt')
    assert srt_path.exists()
    srt_path.unlink()
