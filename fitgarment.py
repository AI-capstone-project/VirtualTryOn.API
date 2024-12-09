#Unit testing on fitgarment.py


import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app, FitGarmentRequest
from PIL import Image
import io

# Mock FastAPI test client
client = TestClient(app)

@pytest.fixture
def mock_supabase():
    supabase_mock = MagicMock()
    supabase_mock.storage.from_.return_value.download.return_value = io.BytesIO().getvalue()
    supabase_mock.storage.from_.return_value.upload.return_value = {
        "path": "mock_path_to_fitted_image.png"
    }
    return supabase_mock

@pytest.fixture
def mock_jwt():
    jwt_mock = {
        "sub": "mock_user_id"
    }
    return jwt_mock

@pytest.fixture
def mock_pillow_image():
    # Create a blank PIL image for testing
    image = Image.new("RGB", (100, 100), color="red")
    return image

@patch("main.set_supabase_auth_to_user")
@patch("main.decode_jwt")
@patch("main.convert_blob_to_pillow_image")
@patch("main.process_hd")
def test_fit_garment(
    mock_process_hd,
    mock_convert_blob_to_pillow_image,
    mock_decode_jwt,
    mock_set_supabase_auth_to_user,
    mock_supabase,
    mock_jwt,
    mock_pillow_image
):
    # Mock dependencies
    mock_set_supabase_auth_to_user.return_value = mock_supabase
    mock_decode_jwt.return_value = mock_jwt
    mock_convert_blob_to_pillow_image.side_effect = [mock_pillow_image, mock_pillow_image]
    mock_process_hd.return_value = mock_pillow_image

    # Convert image to bytes for mock response
    image_bytes = io.BytesIO()
    mock_pillow_image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    # Create a valid request payload
    request_payload = {
        "model_image_path": "mock_model_image.png",
        "garment_image_path": "mock_garment_image.png",
        "n_steps": 5
    }

    # Make the POST request
    response = client.post(
        "/fit_garment",
        json=request_payload,
        headers={"Authorization": "Bearer mock_token"}
    )

    # Assertions
    assert response.status_code == 200
    assert response.json()["path"] == "mock_path_to_fitted_image.png"

    # Ensure mocks were called with correct arguments
    mock_set_supabase_auth_to_user.assert_called_with("mock_token")
    mock_decode_jwt.assert_called_with("mock_token")
    mock_convert_blob_to_pillow_image.assert_any_call(mock_supabase, "mock_model_image.png", "mock_user_id")
    mock_convert_blob_to_pillow_image.assert_any_call(mock_supabase, "mock_garment_image.png", "mock_user_id")
    mock_process_hd.assert_called_with(mock_pillow_image, mock_pillow_image, 5)
