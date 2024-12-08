from supabase import create_client, Client
from dotenv import load_dotenv
import os

from fastapi import FastAPI, Depends, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

init_jwt_config(JWT_SECRET, JWT_ALGORITHM)
init_supabase_config(SUPABASE_URL, SUPABASE_KEY)

supa: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    fitted_garment = fit()
    return {fitted_garment}


@app.post("/upload-images")
async def upload_images(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    image1_b64 = base64.b64encode(await image1.read()).decode('utf-8')
    image2_b64 = base64.b64encode(await image2.read()).decode('utf-8')
    process_images(image1_b64, image2_b64)
    def b64_to_pil(image_b64: str) -> Image.Image:
        image_data = base64.b64decode(image_b64)
        return Image.open(BytesIO(image_data))

    def pil_to_b64(image: Image.Image) -> str:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    image1_pil = b64_to_pil(image1_b64)
    image2_pil = b64_to_pil(image2_b64)

    # Example of converting back to base64 if needed
    image1_b64_converted = pil_to_b64(image1_pil)
    image2_b64_converted = pil_to_b64(image2_pil)
    return JSONResponse(content={"message": "Images processed successfully"})

def process_images(image1_b64: str, image2_b64: str):
    # Implement your image processing logic here
    pass



# @app.post("/upload-model-image")
# async def upload_model_image(File: UploadFile = File(...)):
#     # save to supabase
