import requests
import json

# Base URLs for the services
# BASE_URL_AUTH = 'http://0.0.0.0:8080'
BASE_URL_AUTH = 'https://bb20-142-188-53-176.ngrok-free.app'
# BASE_URL_FIT = 'http://0.0.0.0:8081'
BASE_URL_FIT = 'https://b3be-142-188-53-176.ngrok-free.app'
# BASE_URL_GENERATE = 'http://0.0.0.0:8082'
BASE_URL_GENERATE = 'https://f597-142-188-53-176.ngrok-free.app'

# User credentials
email = "testuser@virtualtryon.com"
password = "testpassword"

def sign_up():
    url = f"{BASE_URL_AUTH}/sign_up"
    payload = {
        "email": email,
        "password": password
    }
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    print("Sign-up response:", data)
    return data['session']['access_token']

def anonymous_sign_in():
    url = f"{BASE_URL_AUTH}/anonymous_sign_in"
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Anonymous sign-in response:", data)
    return data['session']['access_token']

def upload_image(token, file_path):
    url = f"{BASE_URL_AUTH}/upload_image"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    data = response.json()
    print("Upload image response:", data)
    return data['file_name']

def fit_garment(token, model_image_path, garment_image_path, n_steps=20):
    url = f"{BASE_URL_FIT}/fit_garment"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model_image_path": model_image_path,
        "garment_image_path": garment_image_path,
        "n_steps": n_steps
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    print("Fit garment response:", data)
    return data['path'].split('/')[-1]

def prepare_image(token, image_name):
    url = f"{BASE_URL_GENERATE}/prepare"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"image_name": image_name}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    print("Prepare image response:", data)
    return data

def generate_pose(token, image_name, pose_id=1):
    url = f"{BASE_URL_GENERATE}/generate_pose"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "image_name": image_name,
        "pose_id": pose_id
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    print("Generate pose response:", data)
    return data['Key'].split('/')[-1]

def get_signed_url(token, image_path):
    url = f"{BASE_URL_AUTH}/signed_url"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"image_path": image_path}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    print("Signed URL response:", data)
    return data

def main():
    # Step 1: Sign up or anonymous sign-in to get the token
    try:
        token = sign_up()
    except requests.exceptions.HTTPError:
        print("User already exists, trying anonymous sign-in.")
        token = anonymous_sign_in()

    # Step 2: Upload model image
    model_image_path = upload_image(token, 'integration/examples/model/04913_00.jpg')  # Replace with your model image path

    # Step 3: Upload garment image
    garment_image_path = upload_image(token, 'integration/examples/model/04913_00.jpg')  # Replace with your garment image path

    # Step 4: Fit garment
    fitted_image_name = fit_garment(token, model_image_path, garment_image_path)

    # Step 5: Prepare image
    prepare_image(token, fitted_image_name)

    # Step 6: Generate pose
    posed_image_name = generate_pose(token, fitted_image_name)

    # Step 7: Get signed URL
    signed_url_data = get_signed_url(token, posed_image_name)
    print("Final signed URL:", signed_url_data['signedURL'])

if __name__ == "__main__":
    main()
