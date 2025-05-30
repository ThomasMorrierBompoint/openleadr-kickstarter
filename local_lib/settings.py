import os
from dotenv import load_dotenv

from local_lib.constants import RequestProtocol
from local_lib.utils.main import SingletonMeta

load_dotenv()

default_protocol = RequestProtocol.HTTP.value


class Settings(metaclass=SingletonMeta):
    def __init__(self):
        DEBUG = os.getenv("OPEN_KICK__CORE__DEBUG", "false").lower() == "true"
        stage = os.environ.get("OPEN_KICK__STAGE", "local").lower()  # local | dev | staging | prod...

        self.core = {
            'DEBUG': DEBUG,
            'stage': stage,
        }

        fast_api_host = os.environ.get("OPEN_KICK__FAST_API__LOCATION__HOST", "0.0.0.0").lower()
        fast_api_hostname = os.environ.get("OPEN_KICK__FAST_API__LOCATION__HOSTNAME", "fast-api").lower()
        fast_api_wan_protocol = os.environ.get("OPEN_KICK__FAST_API__LOCATION__WAN_PROTOCOL", default_protocol).lower()
        fast_api_lan_protocol = os.environ.get("OPEN_KICK__FAST_API__LOCATION__LAN_PROTOCOL", default_protocol).lower()
        fast_api_port = int(os.environ.get("OPEN_KICK__FAST_API__LOCATION__PORT", 8000))
        fast_api_id = os.environ.get("OPEN_KICK__FAST_API__ID", "OpenADR VTN Dashboard").lower()

        self.fast_api = {
            'title': fast_api_id,
            'location': {
                'port': fast_api_port,
                'host': fast_api_host,
                'hostname': fast_api_hostname,
                'protocol': fast_api_lan_protocol,  # default protocol is http
                'wan': f'{fast_api_wan_protocol}://{fast_api_hostname}{(":" + str(fast_api_port)) if fast_api_port else ""}',
                'lan': f'{fast_api_lan_protocol}://localhost{(":" + str(fast_api_port)) if fast_api_port else ""}',
            },
        }

        vtn_host = os.environ.get("OPEN_KICK__VTN__LOCATION__HOST", "0.0.0.0").lower()
        vtn_hostname = os.environ.get("OPEN_KICK__VTN__LOCATION__HOSTNAME", "vtn").lower()
        vtn_wan_protocol = os.environ.get("OPEN_KICK__VTN__LOCATION__WAN_PROTOCOL", default_protocol).lower()
        vtn_lan_protocol = os.environ.get("OPEN_KICK__VTN__LOCATION__LAN_PROTOCOL", default_protocol).lower()
        vtn_port = int(os.environ.get("OPEN_KICK__VTN__LOCATION__PORT", 8080))
        vtn_id = os.environ.get("OPEN_KICK__VTN__ID", vtn_hostname).lower()

        self.vtn = {
            'id': os.environ.get("OPEN_KICK__VTN__ID", vtn_hostname).lower(),
            'location': {
                'port': vtn_port,
                'hostname': vtn_hostname,
                'protocol': vtn_lan_protocol,  # default protocol is http
                'wan': f'{vtn_wan_protocol}://{vtn_hostname}{(":" + str(vtn_port)) if vtn_port else ""}',
                'lan': f'{vtn_lan_protocol}://localhost{(":" + str(vtn_port)) if vtn_port else ""}',
            },
            'OpenADRServerOptions': {
                'vtn_id': vtn_id,
                'http_host': vtn_host,
                'http_port': vtn_port,
                'verify_message_signatures': False,
                'show_server_cert_domain': False,
            }
        }

    @property
    def fast_api_url(self) -> str:
        lan_url = self.fast_api["location"]["lan"]
        wan_url = self.fast_api["location"]["wan"]
        return lan_url if self.core['stage'] == 'local' else wan_url

    @property
    def vtn_url(self) -> str:
        lan_url = self.vtn["location"]["lan"]
        wan_url = self.vtn["location"]["wan"]
        return lan_url if self.core['stage'] == 'local' else wan_url


# Singleton pattern — one shared instance
settings = Settings()
