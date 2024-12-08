
from pydantic import BaseModel
from supabase import Client
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, Request
from fitting import process_hd
import io
from PIL import Image
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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Allow all origins, change to specific origins for better security
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


class FitGarmentRequest(BaseModel):
    model_image_path: str
    garment_image_path: str
    n_steps: int


@app.post("/fit_garment", dependencies=[Depends(JWTBearer())])
async def fit_garment(request: Request, json: FitGarmentRequest):
    token = get_token_from_request(request)
    local_supa = set_supabase_auth_to_user(token)
    user_id = decode_jwt(token)["sub"]

    pil_model_image = convert_blob_to_pillow_image(
        local_supa, json.model_image_path, user_id)
    pil_garment_image = convert_blob_to_pillow_image(
        local_supa, json.garment_image_path, user_id)

    n_steps = json.n_steps

    output_image = process_hd(pil_model_image, pil_garment_image, n_steps)

    output_image_bytes = convert_pillow_image_to_bytes(output_image)

    fitted_garment_image_name = f"fitted_garment_{n_steps}_{json.model_image_path.split('.')[0]}_{json.garment_image_path.split('.')[0]}.png"

    response = local_supa.storage.from_("user-images").upload(
        f"{user_id}/{fitted_garment_image_name}",
        output_image_bytes,
        file_options={"cache-control": "3600",
                      "upsert": "true", 'content-type': 'image/png'}
    )

    _ = local_supa.table('Log').insert(
      {"Activity": "fit_garment", "message": {"image_path": response.path}}
      , returning='minimal').execute()

    return response


def convert_pillow_image_to_bytes(output_image):
    output_image_stream = io.BytesIO()
    output_image.save(output_image_stream, format="PNG")
    output_image_bytes = output_image_stream.getvalue()
    return output_image_bytes

def convert_blob_to_pillow_image(supa: Client, file_name: str, user_id: str) -> Image:
    supabase_path = f"{user_id}/{file_name}"
    image_bytes = supa.storage.from_("user-images").download(
        path=supabase_path
    )
    image_stream = io.BytesIO(image_bytes)
    return Image.open(image_stream)
