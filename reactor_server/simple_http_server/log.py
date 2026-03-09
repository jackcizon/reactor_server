import logging

from reactor_server.simple_http_server.conf import ACCESS_LOG

__all__ = ['logger']

logger = logging.getLogger('http_server_logger')
logging.basicConfig(filename=ACCESS_LOG, level=logging.INFO)
