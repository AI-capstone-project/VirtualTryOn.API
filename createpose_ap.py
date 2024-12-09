import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from your_module import app  # Import your FastAPI app

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Create the test client for the FastAPI app
        self.client = TestClient(app)

    @patch('your_module.get_token_from_request')
    @patch('your_module.set_supabase_auth_to_user')
    @patch('your_module.save_image_in_file_system')
    @patch('your_module.prepare_texture_for_the_last_image_added_to_file_system')
    def test_prepare(self, mock_prepare_texture, mock_save_image, mock_set_supabase_auth, mock_get_token):
        # Setup mock returns
        mock_get_token.return_value = "fake_token"
        mock_set_supabase_auth.return_value = MagicMock()
        mock_save_image.return_value = "user-id/fake_image.png"
        mock_prepare_texture.return_value = 0  # Assume the script runs successfully
        
        # Create the request data
        request_data = {"image_name": "fake_image.png"}
        
        # Call the endpoint
        response = self.client.post("/prepare", json=request_data, headers={"Authorization": "Bearer fake_token"})

        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "3D try-on script executed"})
        mock_prepare_texture.assert_called_once()  # Ensure it was called
        mock_save_image.assert_called_once()  # Ensure it was called

    @patch('your_module.get_token_from_request')
    @patch('your_module.set_supabase_auth_to_user')
    @patch('your_module.generate_pose')
    @patch('your_module.find_pose_path_from_file_system')
    def test_generate_pose(self, mock_find_pose, mock_generate_pose, mock_set_supabase_auth, mock_get_token):
        # Setup mock returns
        mock_get_token.return_value = "fake_token"
        mock_set_supabase_auth.return_value = MagicMock()
        mock_generate_pose.return_value = 0  # Assume the pose generation script runs successfully
        mock_find_pose.return_value = "/path/to/pose.gif"  # Mock the pose file path
        
        # Create the request data
        request_data = {"image_name": "fake_image.png", "pose_id": 1}
        
        # Call the endpoint
        response = self.client.post("/generate_pose", json=request_data, headers={"Authorization": "Bearer fake_token"})
        
        # Validate the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('path', response.json())  # Check that the response contains a 'path' field
        mock_generate_pose.assert_called_once()  # Ensure it was called
        mock_find_pose.assert_called_once()  # Ensure it was called

    @patch('your_module.subprocess.Popen')
    def test_generate_pose_subprocess_error(self, mock_popen):
        # Simulate subprocess error by making the process return a non-zero exit code
        mock_process = MagicMock()
        mock_process.wait.return_value = 1  # Non-zero exit code indicates failure
        mock_popen.return_value = mock_process
        
        request_data = {"image_name": "fake_image.png", "pose_id": 1}
        response = self.client.post("/generate_pose", json=request_data, headers={"Authorization": "Bearer fake_token"})
        
        # The response should indicate an error since the subprocess failed
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "3D try-on script failed"})

    @patch('your_module.glob.glob')
    @patch('your_module.open')
    @patch('your_module.supabase.Client')
    def test_save_image_and_upload(self, mock_supabase, mock_open, mock_glob):
        # Mocking supabase interaction
        mock_supa = MagicMock()
        mock_supabase.from_.return_value = mock_supa
        mock_supa.download.return_value = b"fake_image_data"

        # Mocking file system interaction
        mock_glob.return_value = ["/path/to/fake_image.png"]
        mock_open.return_value = MagicMock()

        image_path = "/home/myuser/SMPLitex/scripts/dummy_data/stableviton-created_images/fake_image.png"
        user_id = "user-id"
        request_data = {"image_name": "fake_image.png"}

        # Simulate image saving process
        save_image_path = save_image_in_file_system(mock_supa, request_data, user_id)
        self.assertEqual(save_image_path, "user-id/fake_image.png")

        # Check the calls to the methods
        mock_glob.assert_called_once_with("/home/myuser/SMPLitex/scripts/dummy_data/3d_outputs/fake_image-POSEID-1-360.gif")
        mock_open.assert_called_once_with(image_path, "wb+")
        mock_supa.download.assert_called_once()

if __name__ == "__main__":
    unittest.main()
