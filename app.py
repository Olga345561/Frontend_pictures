"""
Сервер зображень — Python HTTP бекенд.
Тонкий HTTP-обробник, що делегує бізнес-логіку сервісам.
"""


import json
import mimetypes
import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from config import HOST, PORT, IMAGES_DIR, STATIC_DIR, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, MAX_FILE_SIZE
from db import ImageRepository
from logger import setup_logger
from services import ImageService

os.makedirs(IMAGES_DIR, exist_ok=True)

logger = setup_logger()

repo = ImageRepository(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
service = ImageService(repo, IMAGES_DIR)


class ImageServerHandler(BaseHTTPRequestHandler):
    """HTTP-обробник — лише маршрутизація та HTTP-відповіді."""

    # --- Routing ---

    def do_GET(self):
        path = self.path.split('?')[0]

        if path == '/' or path == '' or path == '/index.html':
            self._serve_static(os.path.join(STATIC_DIR, 'index.html'))
        elif path == '/upload' or path == '/upload.html':
            self._serve_static(os.path.join(STATIC_DIR, 'upload.html'))
        elif path == '/images-list' or path == '/images.html':
            self._serve_static(os.path.join(STATIC_DIR, 'images.html'))
        elif path == '/api/images':
            self._handle_api_images()
            # Обробка статики: CSS, JS, IMG
        elif any(path.startswith(prefix) for prefix in ['/js/', '/img/', '/file_style_css/', '/static/']):
            # 1. Прибираємо /static/ та початковий слеш
            rel_path = path.replace('/static/', '', 1).lstrip('/')
            # 2. ВАЖЛИВО: Замінюємо всі прямі слеші на ті, що любить ваша ОС (Windows)
            rel_path = rel_path.replace('/', os.sep)
            # 3. Будуємо повний шлях
            full_path = os.path.join(os.path.abspath(STATIC_DIR), rel_path)
            print(f"DEBUG: Спроба відкрити: {full_path}")
            self._serve_static(full_path)
        elif path.startswith('/images/'):
            self._serve_static(os.path.join(IMAGES_DIR, os.path.basename(path)))
        else:
            self._send_error(404, 'Сторінку не знайдено')

    def do_POST(self):
        path = self.path.split('?')[0]

        if path == '/upload':
            self._handle_upload()

        elif path.startswith('/delete/'):
            self._handle_delete_by_id(path)
        else:
            self._send_error(404, 'Маршрут не знайдено')

    def do_DELETE(self):
        path = self.path.split('?')[0]

        if path.startswith('/images/'):
            self._handle_delete(path)
        else:
            self._send_error(404, 'Маршрут не знайдено')

    # --- Route handlers ---

    def _handle_api_images(self):
        query_string = urlparse(self.path).query
        params = parse_qs(query_string)
        try:
            page = int(params.get('page', ['1'])[0])
        except ValueError:
            page = 1

        try:
            rows, page, total_pages = service.get_page(page)
        except Exception as e:
            logger.info('Помилка отримання списку зображень: %s', str(e))
            self._send_json(500, {'error': 'Помилка бази даних'})
            return

        items = []
        for row in rows:
            img_id, filename, original_name, size, file_type, upload_time = row
            items.append({
                'id': img_id,
                'filename': filename,
                'original_name': original_name,
                'size': size,
                'file_type': file_type,
                'upload_time': upload_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        self._send_json(200, {'items': items, 'page': page, 'total_pages': total_pages})

    def _handle_upload(self):
        file_data, original_filename, error = self._parse_upload_form()
        if error:
            self._send_json(400, {'success': False, 'error': error})
            return

        result, error = service.upload(file_data, original_filename)
        if error:
            self._send_json(400, {'success': False, 'error': error})
        else:
            self._send_json(200, {'success': True, **result})

    def _handle_delete(self, path):
        filename = os.path.basename(path)
        success, error, status = service.delete_by_filename(filename)
        if success:
            self._send_json(200, {'success': True})
        else:
            self._send_json(status, {'success': False, 'error': error})

    def _handle_delete_by_id(self, path):
        id_str = path.split('/delete/')[-1]
        try:
            image_id = int(id_str)
        except ValueError:
            self._send_error(400, 'Невірний ID')
            return

        try:
            success, error, status = service.delete_by_id(image_id)
        except Exception as e:
            logger.info('Помилка видалення за ID: %s', str(e))
            self._send_error(500, 'Помилка видалення')
            return

        if success:
            self._send_json(200, {'success': True})
        else:
            self._send_json(status, {'success': False, 'error': error})

    # --- Request parsing ---

    def _parse_upload_form(self):
        content_type = self.headers.get('Content-Type', '')

        if 'multipart/form-data' not in content_type:
            return None, None, 'Невірний Content-Type'

        # Отримуємо межу (boundary), яка розділяє дані у формі
        try:
            boundary = content_type.split("boundary=")[1].encode()
        except IndexError:
            return None, None, 'Не вдалося знайти boundary у запиті'

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > MAX_FILE_SIZE:
            return None, None, f'Файл занадто великий (макс. {MAX_FILE_SIZE // 1024 // 1024}MB)'

        body = self.rfile.read(content_length)

        # Шукаємо початок і кінець файлу всередині тіла запиту
        try:
            parts = body.split(boundary)
            for part in parts:
                if b'filename=' in part:
                    # Витягуємо назву файлу
                    header_end = part.find(b'\r\n\r\n')
                    headers = part[:header_end].decode('utf-8', errors='ignore')

                    for line in headers.split('\r\n'):
                        if 'filename=' in line:
                            original_filename = line.split('filename=')[1].strip('"')
                            break

                    # Самі дані файлу (те, що після заголовків)
                    file_data = part[header_end + 4:-4]  # Прибираємо зайві переноси
                    return file_data, original_filename, None
        except Exception as e:
            logger.info('Помилка парсингу: %s', str(e))

        return None, None, 'Файл не знайдено в даних форми'

    # --- Response helpers ---

    def _serve_static(self, file_path):
        import mimetypes
        # Додаємо явне визначення типів, якщо ОС їх не знає
        mimetypes.add_type('text/css', '.css')
        mimetypes.add_type('application/javascript', '.js')
        real_path = os.path.realpath(file_path)

        allowed_dirs = [os.path.realpath(STATIC_DIR), os.path.realpath(IMAGES_DIR)]
        if not any(real_path.startswith(d) for d in allowed_dirs):
            self._send_error(403, 'Доступ заборонено')
            return

        if not os.path.isfile(real_path):
            self._send_error(404, 'Файл не знайдено')
            return

        mime_type, _ = mimetypes.guess_type(real_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        with open(real_path, 'rb') as f:
            data = f.read()

        self.send_response(200)
        self.send_header('Content-Type', mime_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, status_code, data):
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _send_error(self, status_code, message):
        response = f'<html><body><h1>{status_code}</h1><p>{message}</p></body></html>'
        data = response.encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass


def main():
    repo.init_table()
    server = ThreadingHTTPServer((HOST, PORT), ImageServerHandler)
    logger.info('Сервер запущено на %s:%d', HOST, PORT)
    print(f'Сервер запущено на http://{HOST}:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Сервер зупинено.')
        print('\nСервер зупинено.')
        server.server_close()
        repo.close_connection()

if __name__ == '__main__':
    main()


