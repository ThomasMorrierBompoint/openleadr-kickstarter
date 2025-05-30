from enum import Enum

class RequestProtocol(Enum):
    HTTP = 'http'
    HTTPS = 'https'
    WS = 'ws'
    WSS = 'wss'