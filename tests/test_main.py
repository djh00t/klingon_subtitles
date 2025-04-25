import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from subtitle_generator import SubtitleGenerator

def test_main():
    try:
        generator = SubtitleGenerator()
        # We'll just initialize the generator without running it to avoid side effects
        assert isinstance(generator, SubtitleGenerator)
    except Exception as e:
        pytest.fail(f"SubtitleGenerator initialization raised {e} unexpectedly!")
