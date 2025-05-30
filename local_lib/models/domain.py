import asyncio
import threading
import time
from datetime import timedelta

from faker import Faker
from functools import cached_property
from typing import TypedDict, List, Optional
from openleadr import OpenADRClient, enable_default_logging

from local_lib.settings import settings
from local_lib.utils.main import slugify, generate_id

ID_PREFIX = 'ID'
REGISTRATION_PREFIX = 'REG'

fake = Faker()

if settings.core['DEBUG']:
    enable_default_logging()


class VenProps(TypedDict):
    name: str
    id: str
    registration_id: str
    fingerprint: str


class Ven:
    def __init__(self, ven_props: VenProps):
        self._client_thread: Optional[threading.Thread] = None
        self._is_connected = False
        self.name = ven_props['name']
        self.id = ven_props['id']
        self.registration_id = ven_props['registration_id']
        self.fingerprint = ven_props['fingerprint']

    @property
    def is_connected(self):
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value):
        pass

    async def collect_report_value(self):
        # This callback is called when you need to collect a value for your Report
        return 1.23

    async def handle_event(self, event):
        # This callback receives an Event dict.
        if settings.core['DEBUG']:
            print(f"Received event: {event['event_descriptor']['event_id']}")
        # You should include code here that sends control signals to your resources.
        return 'optIn'  # Accept the event

    def _run_client(self, ven_name, ven_id, registration_id, vtn_url, debug, check_hostname, disable_signature) -> None:
        """Internal method to run the client in a separate thread."""
        # Create a VEN and connect to the VTN
        client = OpenADRClient(
            ven_name=ven_name,
            ven_id=ven_id,
            vtn_url=vtn_url,
            debug=debug,
            check_hostname=check_hostname,
            disable_signature=disable_signature
        )

        # TODO this could be added/customized dynamically
        # Add the report capability to the client
        client.add_report(
            callback=self.collect_report_value,
            resource_id=ven_id,
            report_duration=timedelta(seconds=3600),
            measurement=registration_id,
            sampling_rate=timedelta(seconds=10)
        )

        # Add event handling capability to the client
        client.add_handler('on_event', self.handle_event)

        # Run the client in the Python AsyncIO Event Loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(client.run())
        loop.run_forever()

    def run(self):
        try:
            self._client_thread = threading.Thread(
                target=self._run_client,
                args=(
                    self.name,
                    self.id,
                    self.registration_id,
                    f'{settings.vtn_url}/OpenADR2/Simple/2.0b',
                    True,
                    False,  # Should probably be True in production
                    False,  # Should probably be True in production
                ),
                daemon=True
            )
            self._client_thread.start()
            self._is_connected = True
        except Exception as e:
            self._is_connected = False
            raise RuntimeError(f"Failed to connect VEN client: {str(e)}") from e

    def __str__(self) -> str:
        return f"VEN(name={self.name}, id={self.id}, registration_id={self.registration_id}, fingerprint={self.fingerprint}), is_connected={self._is_connected})"


class VenList:
    __ven_list: List[Ven] = []

    def __init__(self, ven_list: List[Ven], debug: bool = settings.core['DEBUG']):
        self.debug = debug
        self.__ven_list = ven_list

    # Here I'm just experimenting with a cached property
    @cached_property
    def ven_props_list(self) -> List[VenProps]: # TODO VenProps union { 'is_connected': bool }
        """
        Computes and stores a cached version of the VEN list.
        Whenever accessed, it returns a deep copy of the internal VEN list (ensure immutability).

        @return: A deep copy of the internal VEN list
        @rtype: list
        """
        # return copy.deepcopy(self.__ven_list) @DEPRECATED remove deep copy to test another flow...
        return [
            {
                'name': ven.name,
                'id': ven.id,
                'registration_id': ven.registration_id,
                'fingerprint': ven.fingerprint,
                'is_connected': ven.is_connected,
            }
            for ven in self.__ven_list
        ]

    def ven_instances(self) -> List[Ven]:
        return self.__ven_list.copy() # Shallow Copy

    def get_ids(self) -> List[str]:
        return [ven.id for ven in self.__ven_list]

    def get_names(self) -> List[str]:
        return [ven.name for ven in self.__ven_list]

    def find_by_id(self, ven_id: str) -> Ven | None:
        return next((ven for ven in self.__ven_list if ven.id == ven_id), None)

    def find_by_mame(self, ven_name: str) -> Ven | None:
        return next((ven for ven in self.__ven_list if ven.name == ven_name), None)

    def find_by_registration_id(self, registration_id: str) -> Ven | None:
        return next((ven for ven in self.__ven_list if ven.registration_id == registration_id), None)

    def has_ven_with_id(self, id: str) -> bool:
        return any(ven.id == id for ven in self.__ven_list)

    def has_ven_with_name(self, name: str) -> bool:
        return any(ven.name == name for ven in self.__ven_list)

    def append(self, ven: Ven) -> None:
        self.__ven_list.append(ven)

        # Safely clear the cached property if it exists
        if "ven_props_list" in self.__dict__:
            del self.__dict__["ven_props_list"]

        new_count = len(self.ven_props_list)  # Computes and caches again
        if self.debug:
            print(f"Adding VEN: {ven.name} at index {new_count - 1}")

    def __str__(self) -> str:
        return f"VenList({len(self.__ven_list)} VENs)"

    def __len__(self) -> int:
        return len(self.__ven_list)


def generate_ven_props(index: int = 0) -> VenProps:
    """
    Generates a VEN dictionary containing specific identification and registration details.

    The function utilizes a series of helper functions and randomized data generation
    to create a dictionary that uniquely identifies a Virtual End Node (VEN). It assigns
    a name, an identifier, a registration ID, and a fingerprint to the VEN.

    Args:
        index (int, optional): An optional integer representing the index which may
        be used in generating unique identifiers. Defaults to 0.

    Returns:
        VenProps: A dictionary containing 'name', 'id', 'registration_id', and
        'fingerprint' keys.
    """
    current_timestamp = time.time()
    name = slugify(fake.name()).lower()

    return {
        'name': name,
        'id': generate_id(ID_PREFIX, index, current_timestamp),
        'registration_id': generate_id(REGISTRATION_PREFIX, index, current_timestamp),
        'fingerprint': fake.sha256()
    }


if __name__ == "__main__":
    """
    For learning purposes...
    """
    vens = [Ven(generate_ven_props(i)) for i in range(5)]
    ven_list = VenList(vens)
    ven_list.append(Ven(generate_ven_props(ven_list.__len__())))

    print(ven_list.get_names())
