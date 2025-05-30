import threading
from typing import Optional

import uvicorn
from fastapi import FastAPI

from vtn_fast_api.dto.main import SendEventRequest
from vtn_fast_api.vtn_service import VTNService
from local_lib.settings import settings
from local_lib.utils.main import SingletonMeta

vtn_service = VTNService()


class APIService(metaclass=SingletonMeta):
    """
    A singleton service class that manages the FastAPI application instance.
    Handles server initialization and runtime operations.
    """

    def __init__(self, title: str = settings.fast_api['title'], debug: bool = settings.core['DEBUG']):
        self.debug = debug
        self._is_running = False
        self._server_thread: Optional[threading.Thread] = None

        # Create the FastAPI app
        app = FastAPI(title=title)
        self.__app = app

        # --- API Endpoints ---
        @app.get("/ven/registered")
        def get_registered_ven():
            if not vtn_service.is_running:
                return {"error": "VTN server is not running"}

            return vtn_service.ven_props_list()

        @app.get("/ven/connected")
        def get_connected_ven():
            if not vtn_service.is_running:
                return {"error": "VTN server is not running"}

            return vtn_service.ven_connected()

        @app.get("/ven/connect")
        def get_connect_ven():
            if not vtn_service.is_running:
                return {"error": "VTN server is not running"}

            vtn_service.ven_connect()
            return {"status": "vent connection started"}

        @app.post("/ven/create")
        def create_ven():
            if not vtn_service.is_running:
                return {"error": "VTN server is not running"}

            return {"status": "Not implemented yet"}

        @app.delete("/ven/delete")
        def delete_ven():
            if not vtn_service.is_running:
                return {"error": "VTN server is not running"}

            return {"status": "Not implemented yet"}

        @app.post("/event/send-event")
        async def send_event(req: SendEventRequest):
            if not vtn_service.is_running:
                return {"error": "VTN server is not running"}

            if req.ven_id not in vtn_service.ven_ids():
                return {"error": "VEN not registered"}

            await vtn_service.send_event(req.ven_id, req.signal_level)
            return {"status": "event sent"}

    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        pass

    @property
    def app(self) -> FastAPI:
        return self.__app

    @app.setter
    def app(self, _):
        if self.debug:
            print(f'Warning set app is not allowed...')

    def _run_server(self, host: str, port: int) -> None:
        """Internal method to run the server in a separate thread."""
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            loop="asyncio",
            reload=False
        )
        server = uvicorn.Server(config)
        server.run()

    def run(self, host: str = settings.fast_api['location']['host'], port: int = settings.fast_api['location']['port']):
        """
        Starts the FastAPI server with the specified host and port in a non-blocking manner.

        Args:
            host: The host address to bind the server to
            port: The port number to listen on

        Raises:
            RuntimeError: If the server is already running
        """
        if self._is_running:
            print(f'API server is already running at {settings.vtn_url}...')
            return

        try:
            self._server_thread = threading.Thread(
                target=self._run_server,
                args=(host, port),
                daemon=True
            )
            self._server_thread.start()
            self._is_running = True
        except Exception as e:
            self._is_running = False
            raise RuntimeError(f"Failed to start API server: {str(e)}") from e
