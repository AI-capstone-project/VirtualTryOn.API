import glob
import subprocess
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from supabase import Client
from virtualtryon_api_common.jwt_helper import JWTBearer, decode_jwt, init_jwt_config
from virtualtryon_api_common.supabase_helper import init_supabase_config, set_supabase_auth_to_user, insert_log
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

class GenerateAllPoseItemRequest(BaseModel):
    image_name: str | None = None


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

    insert_log(local_supa, "prepare_texture", {"status_code": return_code})

    if return_code != 0:
        raise HTTPException(status_code=500, detail="3D try-on script failed")

    return {"message": "3D try-on script executed"}


@app.post("/generate_pose", dependencies=[Depends(JWTBearer())])
async def create_pose(request: Request, item: GeneratePoseItemRequest):
    token = get_token_from_request(request)
    local_supa = set_supabase_auth_to_user(token)

    if item.pose_id not in range(1, 4):
        raise HTTPException(
            status_code=400, detail="Pose ID should be between 1 and 3")

    user_id = decode_jwt(token)["sub"]
    extension = item.image_name.split(".")[-1]
    path = f"{user_id}/{item.image_name.removesuffix(f'.{extension}')}-POSEID-{item.pose_id}-360.gif"

    return_code = generate_pose(item)

    insert_log(local_supa, "create_pose", {
               "status_code": return_code, "pose_id": item.pose_id})

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

@app.post("/generate_all_pose", dependencies=[Depends(JWTBearer())])
async def create_all_pose(request: Request, item: GenerateAllPoseItemRequest):
    token = get_token_from_request(request)
    local_supa = set_supabase_auth_to_user(token)

    user_id = decode_jwt(token)["sub"]
    extension = item.image_name.split(".")[-1]
    
    res = []
    for i in range(1, 4):
        pose_item = GeneratePoseItemRequest(image_name=item.image_name, pose_id=i)
        
        path = f"{user_id}/{item.image_name.removesuffix(f'.{extension}')}-POSEID-{pose_item.pose_id}-360.gif"

        return_code = generate_pose(pose_item)

        insert_log(local_supa, "create_pose", {
            "status_code": return_code, "pose_id": pose_item.pose_id})

        if return_code != 0:
            raise HTTPException(status_code=500, detail="3D try-on script failed")

        # load the image and return it
        image_path = find_pose_path_from_file_system(pose_item, extension)
        try:
            with open(image_path, "rb") as f:
                image = f.read()

            try:
                upload_response = local_supa.storage.from_("user-images").upload(
                    file=image,
                    path=path,
                    file_options={"cache-control": "3600",
                                  "upsert": "true", 'content-type': 'image/gif'}
                )
                res.append(upload_response)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Image not found")

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
    return return_code


def find_pose_path_from_file_system(item, extension):
    image_name_without_extension = item.image_name.removesuffix(
        f".{extension}")
    image_path_pattern = f"/home/myuser/SMPLitex/scripts/dummy_data/3d_outputs/{image_name_without_extension}_*POSEID-{item.pose_id}-360.gif"
    matching_files = glob.glob(image_path_pattern)
    if not matching_files:
        raise HTTPException(
            status_code=404, detail=f"Image with path {image_path_pattern} not found")
    image_path = matching_files[0]
    return image_path


def save_image_in_file_system(supa: Client, json, user_id):
    image_path = f"/home/myuser/SMPLitex/scripts/dummy_data/stableviton-created_images/{json.image_name}"
    supabase_image_path = f"{user_id}/{json.image_name}"
    with open(image_path, "wb+") as f:
        response = supa.storage.from_("user-images").download(
            path=supabase_image_path
        )
        f.write(response)
    return supabase_image_path


def prepare_texture_for_the_last_image_added_to_file_system():
    process = subprocess.Popen(["sh", "/home/myuser/SMPLitex/scripts/create-texture.sh",
                                str(id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Print stdout line by line
    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line, end="")

    # Print stderr line by line
    for stderr_line in iter(process.stderr.readline, ""):
        print(stderr_line, end="")

    process.stdout.close()
    process.stderr.close()
    return_code = process.wait()
    return return_code
