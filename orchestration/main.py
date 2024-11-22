from supabase import create_client, Client
from dotenv import load_dotenv
import os

from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Union
import base64
from io import BytesIO

from authentication.jwt_helpers import JWTBearer

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
def is_authenticated():
    return "Authenticated"

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
