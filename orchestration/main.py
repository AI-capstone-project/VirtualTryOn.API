from supabase import create_client, Client
from dotenv import load_dotenv
import os

from fastapi import FastAPI, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Union
import base64
import aiohttp

from authentication.jwt_helpers import JWTBearer, decode_jwt

load_dotenv()

JWT_SECRET: str = os.getenv("JWT_SECRET")
JWT_ALGORITHM: str = "HS256"

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

supa: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, change to specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def read_root():
    return "Hello world"

# authentication
@app.get("/sign_up")
def sign_up():
    res = supa.auth.sign_up(
        {
            "email":"testsupa@gmail.com",
            "password":"testsupabasenow"
        }
    )

    return res

@app.get("/sign_out")
def sign_out():
    res = supa.auth.sign_out()
    return "success"

@app.get("/sign_in")
def sign_in():
    res = supa.auth.sign_in_with_password({"email": "testsupa@gmail.com", "password": "testsupabasenow"})
    return res

@app.get("/anonymous_sign_in")
def anonymous_sign_in():
    res = supa.auth.sign_in_anonymously()
    return res


@app.get("/is_authenticated", dependencies=[Depends(JWTBearer())])
def is_authenticated(request: Request):
    token = request.headers["authorization"]
    decoded_token = decode_jwt(token.removeprefix("Bearer "))
    return decoded_token

@app.post("/upload_image", dependencies=[Depends(JWTBearer())])
def upload_image(request: Request, file: UploadFile = File(...)):
    file_name = file.filename
    file_content = file.file.read()
    token = request.headers["authorization"]
    user_id = decode_jwt(token.removeprefix("Bearer "))["sub"]
    extension = file_name.split(".")[-1]
    random_name = base64.urlsafe_b64encode(os.urandom(6)).decode("utf-8").rstrip("=")
    path = f"{random_name}.{extension}"

    _ = supa.storage.from_('user-images').upload(
                             file=file_content,
                             path=f"{user_id}/{path}",
                             file_options={"cache-control": "3600", "upsert": "false", 'content-type': f'image/{extension}'})

    signed_url = supa.storage.from_("user-images").create_signed_url(
      f"{user_id}/{path}", 60 * 5
    )

    return {"file_name": path}

@app.get("/pose/{image_path}", dependencies=[Depends(JWTBearer())])
async def pose(image_name: str, request: Request):
    token = request.headers["authorization"]
    user_id = decode_jwt(token.removeprefix("Bearer "))["sub"]
    signed_url = supa.storage.from_("user-images").create_signed_url(
      f"{user_id}/{image_name}", 60 * 5
    )

    async with aiohttp.ClientSession() as session:
        async with session.post("http://create_pose:8000/prepare", json={"image_name": image_name, "signed_url": "Hello"}) as response:
            image = await response.read()

    return image

@app.get("/pose/{image_path}/{pose_id}", dependencies=[Depends(JWTBearer())])
async def pose(image_name: str, pose_id: str, request: Request):
    token = request.headers["authorization"]
    user_id = decode_jwt(token.removeprefix("Bearer "))["sub"]
    signed_url = supa.storage.from_("user-images").create_signed_url(
      f"{user_id}/{image_name}", 60 * 5
    )

    async with aiohttp.ClientSession() as session:
        async with session.post("http://create_pose:8000/pose", data={"image_name": {image_name}, "signed_url": signed_url, "pose_id": pose_id}) as response:
            image = await response.read()

    return image
