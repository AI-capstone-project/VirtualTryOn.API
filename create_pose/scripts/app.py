from http.client import HTTPException
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
print(f"{SUPABASE_URL=}")
print(f"{SUPABASE_KEY=}")

supa: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


from fastapi import FastAPI
from pydantic import BaseModel, AnyUrl

import subprocess
import requests
import glob

app = FastAPI()

class Item(BaseModel):
    image_name: str | None = None
    signed_url: AnyUrl | None = None

class GeneratePoseItem(BaseModel):
    image_name: str | None = None
    pose_id: int | None = None
    signed_url: AnyUrl | None = None
    user_id: str | None = None

@app.post("/prepare")
async def read_root(json: Item):
    # Download the file from the signed URL
    response = requests.get(json.signed_url)
    if response.status_code != 200:
      raise HTTPException(status_code=400, detail="Failed to download the image")

    # Save the file to the desired location
    image_path = f"/home/myuser/SMPLitex/scripts/dummy_data/stableviton-created_images/{json.image_name}"
    with open(image_path, "wb") as f:
      f.write(response.content)

    print(f"Downloaded {json.image_name} from {json.signed_url}")
    process = subprocess.Popen(["sh", "/home/myuser/SMPLitex/scripts/create-texture.sh", str(id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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

@app.post("/generate_pose")
async def create_pose(item: GeneratePoseItem):
    extension = item.image_name.split(".")[-1]
    path = f"{item.user_id}/{item.image_name.removesuffix(f'.{extension}')}-POSEID-{item.pose_id}-360.gif"
    print(path)
    print(item.user_id)

    process = subprocess.Popen(["sh", "/home/myuser/SMPLitex/scripts/3d-render.sh", str(item.image_name), str(item.pose_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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

    _ = supa.auth.sign_in_with_password({"email": "testsupa@gmail.com", "password": "testsupabasenow"})


    # load the image and return it
    extension = item.image_name.split(".")[-1]
    image_name_without_extension = item.image_name.removesuffix(f".{extension}")
    image_path_pattern = f"/home/myuser/SMPLitex/scripts/dummy_data/3d_outputs/{image_name_without_extension}_*POSEID-{item.pose_id}-360.gif"
    matching_files = glob.glob(image_path_pattern)
    if not matching_files:
        raise HTTPException(status_code=404, detail="Image not found")
    image_path = matching_files[0]
    try:
      with open(image_path, "rb") as f:
          image = f.read()

      try:
        res = supa.storage.from_("user-images").upload(
            file=image,
            path=path,
            file_options={"cache-control": "3600", "upsert": "true", 'content-type': 'image/gif'}
        )
        res = res.json()
      except Exception as e:
        print(f"UPLOAD FAILED: Failed to upload {path}")
        print(e)
    except:
      print(f"READ FILE FAILED: Failed to read {image_path}")


    print(f"{res=}")

    return res
