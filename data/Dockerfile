FROM python:3.9


WORKDIR /code


COPY /data/requirements.txt /code/data/requirements.txt


RUN pip install -r /code/data/requirements.txt


COPY . /code


CMD ["uvicorn", "data.api.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
