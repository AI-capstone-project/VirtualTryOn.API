FROM python:3.10.15-slim

WORKDIR /code

RUN apt-get update && apt-get -y install ffmpeg \
    libsm6 \
    libxext6

COPY ./checkpoints /code/fit_garment/checkpoints

COPY requirements.txt /code/requirements.txt

RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY ./cldm ./config ./preprocess ./__init__.py ./fitting.py ./utils_stableviton.py /code/fit_garment/
