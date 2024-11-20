FROM python:3.10.15-slim

WORKDIR /code

RUN apt-get update && apt-get -y install ffmpeg \
    libsm6 \
    libxext6

COPY ./checkpoints /code/fit_garment/checkpoints

COPY requirements-base.txt /code/requirements-base.txt
COPY requirements-secondary.txt /code/requirements-secondary.txt

RUN pip install --default-timeout=100 --no-cache-dir -r requirements-base.txt
RUN pip install --default-timeout=100 --no-cache-dir -r requirements-secondary.txt

COPY ./cldm ./config ./preprocess ./__init__.py ./fitting.py ./utils_stableviton.py /code/fit_garment/
COPY ./fit_garment_integration_tests/ /code/fit_garment/fit_garment_integration_tests/