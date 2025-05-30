import asyncio
import threading
from functools import partial
from datetime import datetime, timezone, timedelta
from typing import Optional

from openleadr import OpenADRServer, enable_default_logging

from local_lib.models.domain import Ven, VenList
from local_lib.settings import settings
from local_lib.models.in_memory_db import InMemoryDB
from local_lib.utils.main import SingletonMeta

if settings.core['DEBUG']:
    enable_default_logging()

db = InMemoryDB()


class VTNService(metaclass=SingletonMeta):
    """
    VTNService is responsible for managing and operating a Virtual Top Node (VTN) server as part of
    an OpenADR (Automated Demand Response) system. This includes handling client (VEN) registrations,
    report registrations, and event notifications. It facilitates interaction between the VTN and the
    VENs (Virtual End Nodes).

    This class is designed to manage the lifecycle of the VTN server and handle various OpenADR server
    functionalities. It includes mechanisms for the lookup of VEN information, managing event
    responses, report callbacks, and communication with registered VENs. This implementation aligns
    with OpenADR specifications and uses the SingletonMeta for ensuring a single instance.

    Attributes:
        debug: Indicates whether debugging mode is enabled for the VTN service.
        _is_running: Represents the running state of the VTN server.
        server: The OpenADR server instance that manages the core OpenADR functionalities.
    """

    ven_list: VenList

    def __init__(self, debug: bool = settings.core['DEBUG']):
        self.debug = debug
        self._is_running = False
        self._server_thread: Optional[threading.Thread] = None

        # Create the OpenADR Server
        self.server = OpenADRServer(
            # ven_lookup=ven_lookup,
            **settings.vtn['OpenADRServerOptions'],
            fingerprint_lookup=self.ven_lookup
            # Possibly deprecated (but still works) see https://openleadr.org/docs/server.html#things-you-should-implement
        )

        # Add the handler for client (VEN) registrations
        self.server.add_handler('on_create_party_registration', self.on_create_party_registration)

        # Add the handler for report registrations from the VEN
        self.server.add_handler('on_register_report', self.on_register_report)

    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        pass

    def ven_props_list(self):
        return self.ven_list.ven_props_list

    def ven_ids(self):
        return self.ven_list.get_ids()

    def ven_names(self):
        return self.ven_list.get_names()

    def ven_connected(self):
        return [ven for ven in self.ven_list.ven_props_list if ven['is_connected']]

    def ven_connect(self):
        try:
            for ven in self.ven_list.ven_instances():
                if not ven.is_connected:
                    ven.run()
        except Exception as e:
            print(f"Error connecting VEN: {str(e)}")
            raise

    def ven_lookup(self, ven_id):
        ven = self.ven_list.find_by_id(ven_id)
        if ven:
            return {
                'ven_id': ven.id,
                'ven_name': ven.name,
                'fingerprint': ven.fingerprint,
                'registration_id': ven.registration_id
            }
        else:
            return {}

    async def on_create_party_registration(self, registration_info):
        """
        Inspect the registration info and return a ven_id and registration_id.
        """
        ven = self.ven_list.find_by_mame(registration_info['ven_name'])
        if ven:
            return ven.id, ven.registration_id
        else:
            return False

    async def on_update_report(data, ven_id, resource_id, measurement):
        """
        Callback that receives report data from the VEN and handles it.
        """
        for time, value in data:
            print(f"Ven {ven_id} reported {measurement} = {value} at time {time} for resource {resource_id}")

    async def on_register_report(self,
                                 ven_id,
                                 resource_id,
                                 measurement,
                                 unit,
                                 scale,
                                 min_sampling_interval,
                                 max_sampling_interval
                                 ):
        """
        Inspect a report offering from the VEN and return a callback and sampling interval for receiving the reports.
        """
        callback = partial(self.on_update_report, ven_id=ven_id, resource_id=resource_id, measurement=measurement)
        sampling_interval = min_sampling_interval
        return callback, sampling_interval

    async def event_response_callback(ven_id, event_id, opt_type):
        """
        Callback that receives the response from a VEN to an Event.
        """
        print(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")

    async def send_event(self, ven_id: str, signal_level: int = 1):
        await self.server.add_event(
            ven_id=ven_id,
            signal_name='simple',
            signal_type='level',
            intervals=[
                {
                    'dtstart': datetime(2021, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                    'duration': timedelta(minutes=10),
                    'signal_payload': signal_level,
                }
            ],
            callback=self.event_response_callback
        )

    def _run_server(self) -> None:
        """Internal method to run the server in a separate thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.server.run())  # Run the server on the asyncio event loop
        loop.run_forever()

    def run(self):
        if self._is_running:
            print(f'VTN server is already running at {settings.vtn_url}...')
            return

        # Normally we would perform something like a DB call to fetch all VENs...
        if self.debug:
            print(f'Loading Allowed VENs from DB...')
        results = db.find('ven_props')
        self.ven_list = VenList([Ven(ven_prop) for ven_prop in results])

        if self.debug:
            print(f'Starting VTN server with VENs ({self.ven_list.__len__()}) at {settings.vtn_url}...')

        try:
            self._server_thread = threading.Thread(
                target=self._run_server,
                args=(),
                daemon=True
            )
            self._server_thread.start()
            self._is_running = True
        except Exception as e:
            self._is_running = False
            raise RuntimeError(f"Failed to start VTN server: {str(e)}") from e


if __name__ == "__main__":
    """
    For learning purposes...
    """
    vtn_service1 = VTNService()
    vtn_service2 = VTNService()

    if id(vtn_service1) == id(vtn_service2):
        print("Singleton works, both variables contain the same instance.")
    else:
        print("Singleton failed, variables contain different instances.")
