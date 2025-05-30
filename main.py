import asyncio
import time
from local_lib.models.in_memory_db import InMemoryDB
from vtn_fast_api.api_service import APIService
from vtn_fast_api.vtn_service import VTNService


def health_check_loop():
    # TODO implement health check
    while True:
        time.sleep(10)  # pause 10 second each loop


if __name__ == "__main__":
    db = InMemoryDB()
    db.seed()

    # Starts the FastAPI server in the background
    api_service = APIService()
    api_service.run()

    # Starts the OpenADR server in the background
    vtn_service = VTNService()
    vtn_service.run()

    # Prevent the main process from exiting since both servers are running in the background
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(health_check_loop())
    loop.run_forever()
