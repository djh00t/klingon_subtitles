import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from subtitle_generator import generate_srt

def test_generate_srt():
    segments = [
        {'start': 0, 'end': 2, 'text': 'Hello'},
        {'start': 3, 'end': 5, 'text': 'World'}
    ]
    subs = generate_srt(segments)
    assert len(subs) == 2
    assert subs[0].text == 'Hello'
    assert subs[1].text == 'World'
    assert subs[0].start.seconds == 0
    assert subs[0].end.seconds == 2
    assert subs[1].start.seconds == 3
    assert subs[1].end.seconds == 5
