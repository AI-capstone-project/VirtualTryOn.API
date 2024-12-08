import requests

# Base URLs for the services
# BASE_URL_AUTH = 'http://0.0.0.0:8080'
# BASE_URL_FIT = 'http://0.0.0.0:8081'
# BASE_URL_GENERATE = 'http://0.0.0.0:8082'
# BASE_URL_AUTH = 'https://sbb81xkq-8080.use.devtunnels.ms'
# BASE_URL_FIT = 'https://sbb81xkq-8081.use.devtunnels.ms'
# BASE_URL_GENERATE = 'https://sbb81xkq-8082.use.devtunnels.ms'
# BASE_URL_AUTH = 'http://127.0.0.1:8080'
# BASE_URL_FIT = 'http://127.0.0.1:8081'
# BASE_URL_GENERATE = 'http://127.0.0.1:8082'
BASE_URL_AUTH = 'https://aa80-142-188-53-176.ngrok-free.app'
BASE_URL_FIT = 'https://acca-142-188-53-176.ngrok-free.app'
BASE_URL_GENERATE = 'https://e4d7-142-188-53-176.ngrok-free.app'

email = "testuser@virtualtryon.com"
password = "testpassword"


def sign_in():
    url = f"{BASE_URL_AUTH}/sign_in"
    payload = {
        "email": email,
        "password": password
    }
    headers = {'accept': 'application/json',
               'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    print("Sign-in response:", data)
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
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response content: {response.content}")
        raise
    data = response.json()
    print("Upload image response:", data)
    return data['file_name']


def main():
    token = sign_in()

    # Replace with your model image path
    model_image_path = upload_image(
        token, 'integration/examples/model/04913_00.jpg')


if __name__ == "__main__":
    main()
