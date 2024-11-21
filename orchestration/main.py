from typing import Union

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File
import base64
from PIL import Image
from io import BytesIO

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
    