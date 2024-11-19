from typing import Union

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

@app.get("/fit")
async def fit():
    prepare()
    return "fitting garment"



# @app.post("/upload-model-image")
# async def upload_model_image(File: UploadFile = File(...)):
#     # save to supabase
    