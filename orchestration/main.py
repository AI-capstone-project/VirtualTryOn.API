from supabase import create_client, Client
from dotenv import load_dotenv
import os

from fastapi import FastAPI, Depends, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Union
import base64

from pydantic import BaseModel

from virtualtryon_api_common.jwt_helper import JWTBearer, decode_jwt, init_jwt_config
from virtualtryon_api_common.supabase_helper import init_supabase_config, set_supabase_auth_to_user
from virtualtryon_api_common.fastapi_helper import get_token_from_request

load_dotenv()

JWT_SECRET: str = os.getenv("JWT_SECRET")
JWT_ALGORITHM: str = "HS256"

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

supa: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

init_jwt_config(JWT_SECRET, JWT_ALGORITHM)
init_supabase_config(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


class ImageInfoRequest(BaseModel):
    image_path: str


class SignInRequest(BaseModel):
    email: str
    password: str


class SignUpRequest(BaseModel):
    email: str
    password: str


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Allow all origins, change to specific origins for better security
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def read_root():
    return "Hello world"

# authentication


@app.post("/sign_up")
def sign_up(sign_up_request: SignUpRequest):
    try:
        res = supa.auth.sign_up(
            {
                "email": sign_up_request.email,
                "password": sign_up_request.password
            }
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=e.message)


@app.get("/sign_out", dependencies=[Depends(JWTBearer())])
def sign_out(request: Request):
    token = get_token_from_request(request)
    local_supa = set_supabase_auth_to_user(token)
    res = local_supa.auth.sign_out()
    return "success"


@app.post("/sign_in")
def sign_in(sign_in_request: SignInRequest):
    try:
        res = supa.auth.sign_in_with_password(
            {
                "email": sign_in_request.email,
                "password": sign_in_request.password
            })
        return res
    except Exception as e:
        raise HTTPException(status_code=401, detail=e)


@app.get("/anonymous_sign_in")
def anonymous_sign_in():
    res = supa.auth.sign_in_anonymously()
    return res


@app.get("/get_user", dependencies=[Depends(JWTBearer())])
def get_user(request: Request):
    token = get_token_from_request(request)
    decoded_token = decode_jwt(token)
    return decoded_token


@app.post("/upload_image", dependencies=[Depends(JWTBearer())])
def upload_image(request: Request, file: UploadFile = File(...)):
    token = get_token_from_request(request)
    local_supa = set_supabase_auth_to_user(token)
    user_id = decode_jwt(token)["sub"]
    extension, path = create_image_path(file)
    file_content = file.file.read()

    _ = local_supa.storage.from_('user-images').upload(
        file=file_content,
        path=f"{user_id}/{path}",
        file_options={"cache-control": "3600", "upsert": "false", 'content-type': f'image/{extension}'})

    res = local_supa.table('Log').insert(
      {"Activity": "upload_image", "message": {"image_path": path}}
      , returning='minimal').execute()



    return {"file_name": path}


@app.post('/signed_url', dependencies=[Depends(JWTBearer())])
def signed_url(request: Request, item: ImageInfoRequest):
    token = get_token_from_request(request)
    local_supa = set_supabase_auth_to_user(token)
    user_id = decode_jwt(token)["sub"]
    signed_url = local_supa.storage.from_("user-images").create_signed_url(
        f"{user_id}/{item.image_path.split('/')[-1]}", 60 * 5
    )
    return signed_url

def create_image_path(file):
    file_name = file.filename
    extension = file_name.split(".")[-1]
    random_name = base64.urlsafe_b64encode(
        os.urandom(6)).decode("utf-8").rstrip("=")
    path = f"{random_name}.{extension}"
    return extension, path
