FROM python:3.11-alpine

LABEL image_name=wb_bot


WORKDIR /bot/


RUN apk update && apk upgrade --available
RUN echo "Installing poetry..." && pip install poetry


COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false  # Disable virtualenv creation to avoid cache issues
# RUN poetry cache clear
RUN echo "Installing dependencies..." && poetry install --no-interaction --no-root --only main

COPY . .
