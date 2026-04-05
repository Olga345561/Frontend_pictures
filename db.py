"""Database layer — ImageRepository for all image CRUD operations."""

import logging
import threading
import time

import mysql.connector

logger = logging.getLogger('image_server')


_thread_local = threading.local()


class ImageRepository:
    """Single-responsibility: all database operations for images."""

    def __init__(self, host, port, database, user, password):
        self._config = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password,
        }

    def _get_connection(self):
        # Отримуємо з'єднання з поточного потоку
        conn = getattr(_thread_local, 'connection', None)

        if conn is None or not conn.is_connected():
            conn = mysql.connector.connect(**self._config)
            conn.autocommit = False
            _thread_local.connection = conn
        return conn

    def close_connection(self):
        conn = getattr(_thread_local, 'connection', None)
        # перевіряємо чи з'єднання існує та активне
        if conn and conn.is_connected():
            conn.close()
            _thread_local.connection = None
            logger.info("З'єднання з БД закрито.")

    # створення таблиці в БД
    def init_table(self, retries=5):
        for attempt in range(1, retries + 1):
            try:
                conn = self._get_connection()
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS images (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL,
                        original_name VARCHAR(255) NOT NULL,
                        size INT NOT NULL,
                        file_type VARCHAR(10) NOT NULL,
                        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                cur.close()
                logger.info('Таблицю images ініціалізовано.')
                return
            except Exception as e:
                # Очищуємо з'єднання при помилці, щоб наступна спроба була "з чистого аркуша"
                if hasattr(_thread_local, 'connection'):
                    del _thread_local.connection
                logger.info('Спроба %d підключення до БД не вдалася: %s', attempt, str(e))
                if attempt < retries:
                    time.sleep(2)
                else:
                    raise

    # підрахунок картинок
    def count(self):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM images")
            return cur.fetchone()[0]
        finally:
            cur.close()

    # витягує з БД та сортує картинки на сторінці
    def list_page(self, limit, offset):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, filename, original_name, size, file_type, upload_time "
                "FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return cur.fetchall()
        finally:
            cur.close()

    # збереження картинок до БД
    def insert(self, filename, original_name, size, file_type):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO images (filename, original_name, size, file_type) VALUES (%s, %s, %s, %s)",
                (filename, original_name, size, file_type),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()

    # видалення з БД
    def delete_by_filename(self, filename):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM images WHERE filename = %s", (filename,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()

    # шукає в таблиці MySQL по імені
    def find_filename_by_id(self, image_id):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT filename FROM images WHERE id = %s", (image_id,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()

    # видаляє з таблиці в MySQL по id
    def delete_by_id(self, image_id):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM images WHERE id = %s", (image_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
