#!/bin/bash
set -e

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

echo "DB settings: DB_NAME=$DB_NAME, DB_USER=$DB_USER"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
    CREATE DATABASE $DB_NAME;
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOSQL
