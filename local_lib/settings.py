import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


class Settings:
    def __init__(self):
        DEBUG = os.getenv("OPEN_KICK__CORE__DEBUG", "false").lower() == "true"
        stage = os.environ.get("OPEN_KICK__STAGE", "local").lower()  # local | dev | staging | prod...

        protocol = os.environ.get("OPEN_KICK__VTN__LOCATION__PROTOCOL", "http").lower()
        hostname = os.environ.get("OPEN_KICK__VTN__LOCATION__HOSTNAME", "vtn").lower()
        port = int(os.environ.get("OPEN_KICK__VTN__LOCATION__PORT", 8080))

        self.core = {
            'DEBUG': DEBUG,
            'stage': stage,
        }
        self.vtn = {
            'id': os.environ.get("OPEN_KICK__VTN__ID", hostname).lower(),
            'location': {
                'protocol': protocol,
                'hostname': hostname,
                'port': port,
                'origin': f'{protocol}://{hostname}{(":" + str(port)) if port else ""}'
            }
        }
        self.ven = {
            'vtn_url': 'http://localhost:8080' if stage == 'local' else settings.vtn["location"]["origin"],
            'name': os.environ.get("OPEN_KICK__VEN__NAME", "ven123"),
            'id': os.environ.get("OPEN_KICK__VEN__ID", "ven_id_123"),
            'registration_id': os.environ.get("OPEN_KICK__VEN__REGISTRATION_ID", "reg_id_123"),
            'fingerprint': os.environ.get("OPEN_KICK__VEN__FINGERPRINT",
                                          "A3:9F:57:2E:44:12:AB:45:78:3D:21:09:9E:FF:01:CD:78:2A:4C:33:15:6B:76:2E:98:5C:AE:57:67:AB:1D:F2"),
        }
        if DEBUG:
            print("Running in DEBUG mode")


# Singleton pattern — one shared instance
settings = Settings()
