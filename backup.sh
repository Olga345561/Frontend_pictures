#!/bin/bash

# Створюємо папку для бекапів, якщо її немає
mkdir -p backups

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_BACKUP="backups/db_backup_${TIMESTAMP}.sql"
FILES_BACKUP="backups/images_backup_${TIMESTAMP}.tar.gz"

echo "--- Starting Backup Process ---"

# 1. Бекап бази даних Postgres
# Ми передаємо пароль через змінну оточення PGPASSWORD, щоб скрипт не запитував його вручну
docker exec -e PGPASSWORD=postgres image-server-db pg_dump -U postgres images_db > "$DB_BACKUP"

if [ $? -eq 0 ]; then
    echo "✔ Database backup saved to: $DB_BACKUP"
else
    echo "✘ Database backup FAILED!"
    exit 1
fi

# 2. Бекап папки з картинками
# Ми архівуємо папку ./images
tar -czf "$FILES_BACKUP" ./images 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✔ Images folder archived to: $FILES_BACKUP"
else
    echo "✘ Images archive FAILED!"
fi

echo "--- Backup Completed Successfully ---"