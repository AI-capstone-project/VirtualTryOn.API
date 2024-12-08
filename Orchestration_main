import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from your_module import app  # Import your FastAPI app


class TestAPI(unittest.TestCase):
    def setUp(self):
        # Create the test client for the FastAPI app
        self.client = TestClient(app)

    @patch('your_module.supa.auth.sign_up')
    def test_sign_up(self, mock_sign_up):
        # Setup mock return value for sign up
        mock_sign_up.return_value = {"user": {"email": "test@example.com"}}
        
        # Create the request data
        sign_up_data = {"email": "test@example.com", "password": "password123"}
        
        # Call the endpoint
        response = self.client.post("/sign_up", json=sign_up_data)
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.json())  # Ensure the response contains the user data
        mock_sign_up.assert_called_once_with({
            "email": "test@example.com",
            "password": "password123"
        })

    @patch('your_module.supa.auth.sign_in_with_password')
    def test_sign_in(self, mock_sign_in):
        # Setup mock return value for sign in
        mock_sign_in.return_value = {"access_token": "fake_token", "user": {"email": "test@example.com"}}
        
        # Create the request data
        sign_in_data = {"email": "test@example.com", "password": "password123"}
        
        # Call the endpoint
        response = self.client.post("/sign_in", json=sign_in_data)
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())  # Ensure the response contains the access token
        mock_sign_in.assert_called_once_with({
            "email": "test@example.com",
            "password": "password123"
        })

    @patch('your_module.supa.auth.sign_out')
    @patch('your_module.get_token_from_request')
    def test_sign_out(self, mock_get_token, mock_sign_out):
        # Setup mock return value for sign out
        mock_get_token.return_value = "fake_token"
        mock_sign_out.return_value = None
        
        # Call the endpoint
        response = self.client.get("/sign_out", headers={"Authorization": "Bearer fake_token"})
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "success")
        mock_sign_out.assert_called_once()

    @patch('your_module.supa.storage.from_')
    @patch('your_module.get_token_from_request')
    @patch('your_module.create_image_path')
    def test_upload_image(self, mock_create_image_path, mock_get_token, mock_storage):
        # Setup mock returns
        mock_get_token.return_value = "fake_token"
        mock_create_image_path.return_value = ("jpg", "random_name.jpg")
        mock_storage.return_value.upload.return_value = {"Key": "fake_path"}
        
        # Simulate a file upload
        file_mock = MagicMock()
        file_mock.filename = "test_image.jpg"
        file_mock.file.read.return_value = b"fake_image_data"
        
        response = self.client.post(
            "/upload_image",
            files={"file": ("test_image.jpg", file_mock.file, "image/jpg")},
            headers={"Authorization": "Bearer fake_token"}
        )
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("file_name", response.json())  # Ensure 'file_name' is returned
        mock_create_image_path.assert_called_once_with(file_mock)
        mock_storage.return_value.upload.assert_called_once()

    @patch('your_module.supa.storage.from_')
    @patch('your_module.get_token_from_request')
    def test_signed_url(self, mock_get_token, mock_storage):
        # Setup mock return values for signed URL generation
        mock_get_token.return_value = "fake_token"
        mock_storage.return_value.create_signed_url.return_value = {"signed_url": "https://example.com/signed_url"}
        
        # Create the request data
        image_info = {"image_path": "images/test_image.jpg"}
        
        # Call the endpoint
        response = self.client.post(
            "/signed_url", json=image_info, headers={"Authorization": "Bearer fake_token"}
        )
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("signed_url", response.json())  # Ensure the signed URL is returned
        mock_storage.return_value.create_signed_url.assert_called_once()

if __name__ == "__main__":
    unittest.main()
