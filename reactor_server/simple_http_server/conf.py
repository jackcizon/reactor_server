import os
from pathlib import Path

HOST = 'localhost'
PORT = 8000

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = os.path.join(BASE_DIR, 'logs')
ACCESS_LOG = os.path.join(LOG_DIR, 'access.log')

STATIC_DIR = os.path.join(BASE_DIR, 'static')
