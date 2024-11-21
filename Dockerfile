FROM python:3.11-alpine

LABEL image_name=wb_bot


WORKDIR /bot/

COPY . /bot/

RUN apk update && apk upgrade --available
RUN echo "Installing poetry..." && pip install poetry
RUN poetry config virtualenvs.create false  # Disable virtualenv creation to avoid cache issues
RUN poetry cache clear
RUN echo "Installing dependencies..." && poetry install --no-interaction
