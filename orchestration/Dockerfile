FROM python:3.10.15-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/orchestration

CMD ["fastapi", "run", "orchestration/main.py", "--reload", "--port", "80"]