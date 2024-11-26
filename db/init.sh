#!/bin/bash
set -e

pwd

ENV_FILE="/.prod.env"

# Проверяем, существует ли файл
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: $ENV_FILE file not found!"
  exit 1
fi

# Загружаем переменные из .env файла
set -o allexport
. "$ENV_FILE"
set +o allexport


# Проверяем, что переменные окружения заданы
if [ -z "$DB_NAME" ]; then
  echo "Error: DB_NAME is not set. Please define it in your .env file or environment."
  exit 1
fi

if [ -z "$DB_USER" ]; then
  echo "Error: DB_USER is not set. Please define it in your .env file or environment."
  exit 1
fi

if [ -z "$DB_PASS" ]; then
  echo "Error: DB_PASS is not set. Please define it in your .env file or environment."
  exit 1
fi

echo "DB settings: || DB_NAME=$DB_NAME | DB_USER=$DB_USER ||"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE $POSTGRES_DB;
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $DB_USER;
EOSQL
