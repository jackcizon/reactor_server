from typing import Final

CHANNEL_TIMEOUT: Final[int] = 0b001
CHANNEL_READ_EVENT: Final[int] = 0b010
CHANNEL_WRITE_EVENT: Final[int] = 0b100

EPOLL_CTL_ADD: Final[int] = 1
EPOLL_CTL_MOD: Final[int] = 2
EPOLL_CTL_DEL: Final[int] = 3

EVENTLOOP_ACTION_ADD_CHANNEL: Final[int] = 4
EVENTLOOP_ACTION_DELETE_CHANNEL: Final[int] = 5
EVENTLOOP_ACTION_MODIFY_CHANNEL: Final[int] = 6

HTTP_PARSE_REQUEST_LINE: Final[int] = 1
HTTP_PARSE_REQUEST_HEADERS: Final[int] = 2
HTTP_PARSE_REQUEST_BODY: Final[int] = 3
HTTP_PARSE_REQUEST_DONE: Final[int] = 4

STATUS_UNKNOWN: Final[int] = 0
STATUS_OK: Final[int] = 200
STATUS_MOVE_PERM: Final[int] = 301
STATUS_MOVE_TEMP: Final[int] = 302
STATUS_BAD_REQUEST: Final[int] = 400
STATUS_NOT_FOUND: Final[int] = 404
STATUS_SERVER_ERROR: Final[int] = 500

HTTP_STATUS_CODES_MSG_MAP = {
    200: "OK",
    301: "Moved Permanently",
    302: "Found",
    400: "Bad Request",
    404: "Not Found",
}
