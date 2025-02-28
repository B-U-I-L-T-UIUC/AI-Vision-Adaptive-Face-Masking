import pytest
from unittest.mock import patch, MagicMock
from ml_backend.face_detection import initialize_camera

def test_camera_basic():
    """Basic test for face detection."""
    assert True

@patch('cv2.VideoCapture')
def test_camera_initialization_success(mock_video_capture):
    """Test if camera initializes successfully."""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_video_capture.return_value = mock_cap

    cap = initialize_camera()
    assert cap.isOpened(), "Camera should open successfully"

@patch('cv2.VideoCapture')
def test_camera_initialization_failure(mock_video_capture):
    """Test camera failure to open."""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    mock_video_capture.return_value = mock_cap

    with pytest.raises(Exception, match="Error: Could not open camera."):
        initialize_camera()
