import os
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from subtitle_generator import SubTools, SubtitleVerifier

@pytest.fixture
def sub_tools():
    return SubTools()

@pytest.fixture
def test_srt_path(tmp_path):
    path = tmp_path / "test_subtitles.srt"
    path.write_text("1\n00:00:00,000 --> 00:00:02,000\nHello\n")
    return path

def test_has_external_subtitles(sub_tools, test_srt_path):
    assert sub_tools.has_external_subtitles(str(test_srt_path))

def test_remove_subtitle_formatting(sub_tools, test_srt_path):
    test_srt_path.write_text("1\n00:00:00,000 --> 00:00:02,000\n<i>Hello</i>\n")
    sub_tools.remove_subtitle_formatting(str(test_srt_path))
    content = test_srt_path.read_text()
    assert '<i>' not in content

def test_check_subtitle_alignment(sub_tools, test_srt_path, tmp_path):
    dummy_video = tmp_path / "test_video.mp4"
    dummy_video.write_bytes(b"dummy video content")
    assert sub_tools.check_subtitle_alignment(str(dummy_video), str(test_srt_path))

def test_realign_subtitles(sub_tools, test_srt_path, tmp_path):
    dummy_video = tmp_path / "test_video.mp4"
    dummy_video.write_bytes(b"dummy video content")
    assert sub_tools.realign_subtitles(str(dummy_video), str(test_srt_path))

def test_delete_subtitles(sub_tools, test_srt_path):
    sub_tools.delete_subtitles(str(test_srt_path))
    assert not test_srt_path.exists()

def test_is_subtitle_broken(test_srt_path):
    assert not SubtitleVerifier.is_subtitle_broken(str(test_srt_path))
