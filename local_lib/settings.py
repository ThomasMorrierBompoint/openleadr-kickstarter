import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


class Settings:
    def __init__(self):
        DEBUG = os.getenv("OPEN_KICK__CORE__DEBUG", "false").lower() == "true"

        protocol = os.environ.get("OPEN_KICK__VTN__LOCATION__PROTOCOL", "http").lower()
        hostname = os.environ.get("OPEN_KICK__VTN__LOCATION__HOSTNAME", "vtn-fast-api").lower()
        port = int(os.environ.get("OPEN_KICK__VTN__LOCATION__PORT", 8080))

        self.core = {
            'DEBUG': DEBUG
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
            'name': os.environ.get("OPEN_KICK__VEN__NAME", "ven123"),
            'id': os.environ.get("OPEN_KICK__VEN__ID", "ven_id_123"),
            'registration_id': os.environ.get("OPEN_KICK__VEN__REGISTRATION_ID", "reg_id_123"),
        }
        if DEBUG:
            print("Running in DEBUG mode")


# Singleton pattern — one shared instance
settings = Settings()
