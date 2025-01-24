import os
import pytest
from unittest.mock import MagicMock, patch
from aidoc.AiDoc import ConsoleLogHandler, AdvancedFeatures, Colors

@pytest.fixture
def console_handler():
    return ConsoleLogHandler()

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    driver.current_url = "http://example.com"
    driver.get_cookies.return_value = [{"name": "test", "value": "value"}]
    driver.execute_script.return_value = {"key": "value"}
    return driver

def test_console_handler_categorization(console_handler):
    # Test error categorization
    log_entry = {
        "level": "SEVERE",
        "message": "Cannot read properties of undefined",
        "source": "javascript",
        "timestamp": 1234567890
    }
    console_handler.add_log(log_entry)
    assert "JavaScript" in console_handler.error_categories
    assert console_handler.error_categories["JavaScript"] == 1

def test_advanced_features_screenshot(mock_driver, tmp_path):
    # Test screenshot capture
    with patch('os.makedirs'):
        features = AdvancedFeatures(
            mock_driver,
            enable_screenshots=True
        )
        mock_driver.save_screenshot.return_value = True
        result = features.capture_screenshot(1)
        assert result is not None
        assert mock_driver.save_screenshot.called

def test_advanced_features_memory():
    # Test memory monitoring
    driver = MagicMock()
    features = AdvancedFeatures(
        driver,
        enable_memory=True
    )
    memory_info = features.get_memory_usage()
    assert memory_info is not None
    assert 'rss' in memory_info
    assert 'vms' in memory_info
    assert 'percent' in memory_info

def test_advanced_features_storage(mock_driver):
    # Test storage inspection
    features = AdvancedFeatures(
        mock_driver,
        enable_storage=True
    )
    storage_info = features.inspect_storage()
    assert storage_info is not None
    assert 'cookies' in storage_info
    assert 'localStorage' in storage_info
    assert len(storage_info['cookies']) == 1
    assert len(storage_info['localStorage']) == 1

def test_colors():
    # Test ANSI color codes
    assert Colors.RED.startswith('\033[')
    assert Colors.GREEN.startswith('\033[')
    assert Colors.BLUE.startswith('\033[')
    assert Colors.ENDC == '\033[0m'

def test_export_results(mock_driver, tmp_path):
    # Test HTML export
    features = AdvancedFeatures(
        mock_driver,
        export_format='html'
    )
    
    with patch('os.makedirs'):
        features.export_results(
            console_logs=[{"level": "ERROR", "message": "Test error"}],
            page_info={"url": "http://example.com", "title": "Test"}
        )
        assert mock_driver.save_screenshot.called

if __name__ == '__main__':
    pytest.main([__file__])
