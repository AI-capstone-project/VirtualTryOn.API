FROM python:3.9

WORKDIR /code

COPY ./orchestration/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./orchestration /code/orchestration

CMD ["fastapi", "run", "orchestration/main.py", "--reload", "--port", "80"]