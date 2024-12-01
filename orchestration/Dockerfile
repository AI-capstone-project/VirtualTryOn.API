FROM python:3.10.15-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/orchestration

# The following command should be run after copying the .env file into the orchestration folder
# CMD ["fastapi", "run", "orchestration/main.py", "--reload", "--port", "80"]
# fastapi run orchestration/main.py --reload --port 80
