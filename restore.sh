#!/bin/bash

# Перевіряємо, чи вказав користувач файл для відновлення
if [ -z "$1" ]; then
    echo "Використання: ./restore.sh backups/db_backup_XXXXXXXX.sql"
    exit 1
fi

DB_BACKUP_FILE=$1
# Шукаємо архів з картинками з тією ж датою (автоматично)
TIMESTAMP=$(echo $DB_BACKUP_FILE | grep -oE '[0-9]{8}_[0-9]{6}')
IMAGES_BACKUP="backups/images_backup_${TIMESTAMP}.tar.gz"

echo "--- Початок відновлення проекту ---"

# 1. Відновлення бази даних у Postgres всередині Docker
echo "Відновлення бази даних з $DB_BACKUP_FILE..."
docker exec -i image-server-db psql -U postgres images_db < "$DB_BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✔ База даних успішно відновлена."
else
    echo "✘ Помилка при відновленні бази!"
fi

# 2. Відновлення картинок
if [ -f "$IMAGES_BACKUP" ]; then
    echo "Розпакування картинок з $IMAGES_BACKUP..."
    # Очищуємо поточну папку images перед відновленням (обережно!)
    rm -rf ./images/*
    tar -xzf "$IMAGES_BACKUP" -C .
    echo "✔ Картинки успішно повернуті в папку images."
else
    echo "⚠ Архів з картинками не знайдено, відновлено тільки базу."
fi

echo "--- Відновлення завершено! Перевірте сайт на localhost:8080 ---"

# команда для запуску відновлення
# & "C:\Program Files\Git\bin\bash.exe" ./restore.sh backups/db_backup_20260402_153000.sql
# db_backup_20260402_153000.sql - копіюємо з папки backups пакет який потрібно затянути