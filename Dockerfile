FROM python:3.10

WORKDIR /qlapp

COPY ./requirements.txt /qlapp/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /qlapp/requirements.txt

