import glob
import subprocess
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from supabase import Client
from virtualtryon_api_common.jwt_helper import JWTBearer, decode_jwt, init_jwt_config
from virtualtryon_api_common.supabase_helper import init_supabase_config, set_supabase_auth_to_user
from virtualtryon_api_common.fastapi_helper import get_token_from_request
from pydantic import BaseModel

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


class PrepareItemRequest(BaseModel):
    image_name: str | None = None


class GeneratePoseItemRequest(BaseModel):
    image_name: str | None = None
    pose_id: int | None = None


class SignInRequest(BaseModel):
    email: str
    password: str


class SignUpRequest(BaseModel):
    email: str
    password: str


@app.post("/prepare", dependencies=[Depends(JWTBearer())])
async def read_root(request: Request, json: PrepareItemRequest):
    token = get_token_from_request(request)
    local_supa = set_supabase_auth_to_user(token)
    user_id = decode_jwt(token)["sub"]

    # Save the file to the desired location
    supabase_image_path = save_image_in_file_system(local_supa, json, user_id)

    print(f"Downloaded {json.image_name} from {supabase_image_path}")
    return_code = prepare_texture_for_the_last_image_added_to_file_system()

    if return_code != 0:
        raise HTTPException(status_code=500, detail="3D try-on script failed")

    return {"message": "3D try-on script executed"}


@app.post("/generate_pose", dependencies=[Depends(JWTBearer())])
async def create_pose(request: Request, item: GeneratePoseItemRequest):
    token = get_token_from_request(request)
    local_supa = set_supabase_auth_to_user(token)
    user_id = decode_jwt(token)["sub"]
    extension = item.image_name.split(".")[-1]
    path = f"{user_id}/{item.image_name.removesuffix(f'.{extension}')}-POSEID-{item.pose_id}-360.gif"

    return_code = generate_pose(item)

    if return_code != 0:
        raise HTTPException(status_code=500, detail="3D try-on script failed")

    # load the image and return it
    image_path = find_pose_path_from_file_system(item, extension)
    try:
        with open(image_path, "rb") as f:
            image = f.read()

        try:
            res = local_supa.storage.from_("user-images").upload(
                file=image,
                path=path,
                file_options={"cache-control": "3600",
                              "upsert": "true", 'content-type': 'image/gif'}
            )
            res = res.json()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Failed to upload image from server to storage service")
    except:
        HTTPException(status_code=500,
                      detail="Failed to read image from server")

    print(f"{res=}")

    return res


def generate_pose(item):
    process = subprocess.Popen(["sh", "/home/myuser/SMPLitex/scripts/3d-render.sh", str(
        item.image_name), str(item.pose_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Print stdout line by line
    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line, end="")

    # Print stderr line by line
    for stderr_line in iter(process.stderr.readline, ""):
        print(stderr_line, end="")

    process.stdout.close()
    process.stderr.close()
    return_code = process.wait()

    if return_code != 0:
        raise HTTPException(status_code=500, detail="3D try-on script failed")

    return {"message": "3D try-on script executed"}

@app.get("/pose/{id:int}/{pose_id:int}")
async def create_pose(id: int, pose_id: int):
    process = subprocess.Popen(["sh", "/home/myuser/SMPLitex/scripts/3d-render.sh", str(id), str(pose_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Print stdout line by line
    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line, end="")

    # Print stderr line by line
    for stderr_line in iter(process.stderr.readline, ""):
        print(stderr_line, end="")

    process.stdout.close()
    process.stderr.close()
    return_code = process.wait()

    if return_code != 0:
        raise HTTPException(status_code=500, detail="3D try-on script failed")

    return {"message": "3D try-on script executed"}
