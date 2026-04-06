"""Бізнес-логіка — ImageService координує перевірку, файловий ввід/вивід та базу даних."""

import io
import logging
import os
import uuid

from PIL import Image

from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, ITEMS_PER_PAGE

logger = logging.getLogger('image_server')


class ImageService:
    """Single-responsibility: business logic for image upload, delete, and listing."""

    def __init__(self, repository, images_dir):
        self._repo = repository
        self._images_dir = images_dir

    def upload(self, file_data, original_filename):
        _, ext = os.path.splitext(original_filename)
        ext = ext.lower()

        if ext not in ALLOWED_EXTENSIONS:
            return None, f'Непідтримуваний формат файлу. Дозволені: {", ".join(ALLOWED_EXTENSIONS)}'

        try:
            img = Image.open(io.BytesIO(file_data))
            img.verify()
        except Exception:
            return None, 'Файл не є дійсним зображенням'

        if len(file_data) > MAX_FILE_SIZE:
            return None, 'Файл занадто великий. Максимальний розмір: 5 МБ'

        unique_filename = uuid.uuid4().hex + ext
        save_path = os.path.join(self._images_dir, unique_filename)

        try:
            with open(save_path, 'wb') as f:
                f.write(file_data)
        except OSError as e:
            logger.info('Помилка: не вдалося зберегти файл (%s).', str(e))
            return None, 'Не вдалося зберегти файл'

        file_type = ext.lstrip('.')
        try:
            self._repo.insert(unique_filename, original_filename, len(file_data), file_type)
            logger.info('Метадані збережено в БД: %s', unique_filename)
        except Exception as e:
            logger.info('Помилка збереження в БД: %s', str(e))
            try:
                os.remove(save_path)
            except OSError:
                pass
            return None, 'Не вдалося зберегти метадані в базу даних'

        image_url = f'/images/{unique_filename}'
        logger.info('Успіх: зображення %s завантажено.', original_filename)
        return {
            'filename': unique_filename,
            'original_name': original_filename,
            'url': image_url,
        }, None

    def delete_by_filename(self, filename):
        file_path = os.path.join(self._images_dir, filename)
        real_path = os.path.realpath(file_path)

        if not real_path.startswith(os.path.realpath(self._images_dir)):
            return False, 'Доступ заборонено', 403

        if not os.path.isfile(real_path):
            return False, 'Файл не знайдено', 404

        try:
            self._repo.delete_by_filename(filename)
        except Exception as e:
            logger.info('Помилка видалення з БД: %s', str(e))

        try:
            os.remove(real_path)
            logger.info('Видалено зображення: %s', filename)
            return True, None, 200
        except OSError as e:
            logger.info('Помилка видалення файлу: %s', str(e))
            return False, 'Не вдалося видалити файл', 500

    def delete_by_id(self, image_id):
        filename = self._repo.find_filename_by_id(image_id)
        if not filename:
            return False, 'Зображення не знайдено', 404

        self._repo.delete_by_id(image_id)

        file_path = os.path.join(self._images_dir, filename)
        try:
            os.remove(file_path)
        except OSError as e:
            logger.info('Файл не знайдено на диску: %s', str(e))

        logger.info('Видалено зображення (id=%d): %s', image_id, filename)
        return True, None, 200

    def get_page(self, page):
        total = self._repo.count()
        total_pages = max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages

        offset = (page - 1) * ITEMS_PER_PAGE
        rows = self._repo.list_page(ITEMS_PER_PAGE, offset)
        return rows, page, total_pages

