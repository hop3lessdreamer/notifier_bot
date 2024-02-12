FROM python:3.11-alpine

LABEL image_name=wb_bot


WORKDIR /bot/

COPY . /bot/

RUN apk update && apk upgrade --available
RUN pip install poetry
RUN poetry install
