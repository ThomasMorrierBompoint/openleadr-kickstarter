# Work in progress...

from openleadr import OpenADRServer
import asyncio
from datetime import timedelta

class VTNService:
    def __init__(self):
        self.server = OpenADRServer(vtn_id="vtn-server", http_host="0.0.0.0", http_port=8080)
        self.ven_ids = set()

        @self.server.add_handler("on_create_party_registration")
        async def on_register(payload):
            ven_name = payload['ven_name']
            self.ven_ids.add(ven_name)
            return {
                'registration_id': 'reg-123',
                'ven_id': ven_name,
                'profile_name': '2.0b'
            }

        @self.server.add_handler("on_event_response")
        async def on_event_response(ven_id, event_id, opt_type, *_):
            print(f"{ven_id} responded to {event_id} with {opt_type}")

    async def send_event(self, ven_id: str, event_id: str, signal_level: int = 1):
        await self.server.send_event(
            ven_id=ven_id,
            signal_name='simple',
            signal_type='level',
            intervals=[{
                'dtstart': self.server.now(),
                'duration': 'PT1H',
                'signal_payload': signal_level
            }],
            event_id=event_id,
            response_required='always'
        )

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.server.run_async())
