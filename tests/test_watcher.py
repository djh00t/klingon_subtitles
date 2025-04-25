import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from subtitle_generator import Watcher, SubTools

@pytest.fixture
def mock_config():
    return {
        'watch_directories': ['/test/dir1', '/test/dir2'],
        'output_extension': '.srt'
    }

@patch('subtitle_generator.watcher.Observer')
def test_start_watching(MockObserver, mock_config):
    sub_tools = SubTools()
    watcher = Watcher(mock_config, sub_tools)
    
    # Mock the observer's methods
    mock_observer_instance = MockObserver.return_value
    mock_observer_instance.schedule = MagicMock()
    mock_observer_instance.start = MagicMock()
    
    watcher.start_watching()
    
    # Assert that the observer was started
    assert mock_observer_instance.start.called
    
    # Assert that the observer was scheduled for each directory
    assert mock_observer_instance.schedule.call_count == len(mock_config['watch_directories'])

@patch('subtitle_generator.watcher.os.path.exists', return_value=True)
def test_start_watching_with_existing_directories(mock_exists, mock_config):
    sub_tools = SubTools()
    watcher = Watcher(mock_config, sub_tools)
    
    with patch('subtitle_generator.watcher.Observer') as MockObserver:
        mock_observer_instance = MockObserver.return_value
        mock_observer_instance.schedule = MagicMock()
        mock_observer_instance.start = MagicMock()
        
        watcher.start_watching()
        
        # Assert that the observer was scheduled for each directory
        assert mock_observer_instance.schedule.call_count == len(mock_config['watch_directories'])
