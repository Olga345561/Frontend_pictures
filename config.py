"""Centralized configuration — all settings loaded from environment variables."""

import os

# Server
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '8080'))

# Paths
IMAGES_DIR = os.environ.get('IMAGES_DIR', 'images')
LOGS_DIR = os.environ.get('LOGS_DIR', 'logs')
STATIC_DIR = os.environ.get('STATIC_DIR', 'static')

# Database host.docker.internal
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_NAME = os.environ.get('DB_NAME', 'images_db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '01@02@1990')

# Upload limits
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', str(5 * 1024 * 1024)))  # 5 MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '5'))

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
LOG_FORMAT = os.environ.get('LOG_FORMAT', '[%(asctime)s] %(message)s')
LOG_DATE_FORMAT = os.environ.get('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
