"""Database layer — ImageRepository for all image CRUD operations (PostgreSQL version)."""

import logging
import threading
import time
import psycopg2

logger = logging.getLogger('image_server')

_thread_local = threading.local()

class ImageRepository:
    """Single-responsibility: all database operations for images using PostgreSQL."""

    def __init__(self, host, port, database, user, password):
        self._config = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password,
        }

    def _get_connection(self):
        conn = getattr(_thread_local, 'connection', None)
        if conn is None or conn.closed:
            conn = psycopg2.connect(**self._config)
            conn.autocommit = False
            _thread_local.connection = conn
        return conn

    def close_connection(self):
        conn = getattr(_thread_local, 'connection', None)
        if conn and not conn.closed:
            conn.close()
            _thread_local.connection = None
            logger.info("З'єднання з БД закрито.")

    def init_table(self, retries=5):
        for attempt in range(1, retries + 1):
            try:
                conn = self._get_connection()
                cur = conn.cursor()
                # Змінено AUTO_INCREMENT на SERIAL для PostgreSQL
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS images (
                        id SERIAL PRIMARY KEY,
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
                if hasattr(_thread_local, 'connection'):
                    del _thread_local.connection
                logger.info('Спроба %d підключення до БД не вдалася: %s', attempt, str(e))
                if attempt < retries:
                    time.sleep(2)
                else:
                    raise

    def count(self):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM images")
            return cur.fetchone()[0]
        finally:
            cur.close()

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

    def find_filename_by_id(self, image_id):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT filename FROM images WHERE id = %s", (image_id,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()

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