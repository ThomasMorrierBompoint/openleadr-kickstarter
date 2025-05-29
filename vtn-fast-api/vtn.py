import asyncio
from datetime import datetime, timezone, timedelta
from functools import partial
from openleadr import OpenADRServer, enable_default_logging
from local_lib.settings import settings

enable_default_logging()


async def on_create_party_registration(registration_info):
    """
    Inspect the registration info and return a ven_id and registration_id.
    """
    if registration_info['ven_name'] == settings.ven['name']:
        ven_id = settings.ven['id']
        registration_id = settings.ven['registration_id']
        return ven_id, registration_id
    else:
        return False


async def on_register_report(
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
    callback = partial(on_update_report, ven_id=ven_id, resource_id=resource_id, measurement=measurement)
    sampling_interval = min_sampling_interval
    return callback, sampling_interval


async def on_update_report(data, ven_id, resource_id, measurement):
    """
    Callback that receives report data from the VEN and handles it.
    """
    for time, value in data:
        print(f"Ven {ven_id} reported {measurement} = {value} at time {time} for resource {resource_id}")


async def event_response_callback(ven_id, event_id, opt_type):
    """
    Callback that receives the response from a VEN to an Event.
    """
    print(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")


# Hardcoded implementation normally you would perform something like a DB call fetch the ven info...
def ven_lookup(ven_id):
    print('ven_lookup', ven_id)
    if ven_id == settings.ven['id']:
        return {
            'ven_id': settings.ven['id'],
            'ven_name': settings.ven['name'],
            'fingerprint': settings.ven['fingerprint'],
            'registration_id': settings.ven['registration_id']
        }
    else:
        return {}


# Create the server object
server = OpenADRServer(
    vtn_id=settings.vtn['id'],
    http_port=settings.vtn['location']['port'],
    # ven_lookup=ven_lookup,
    fingerprint_lookup=ven_lookup,
    # Possibly deprecated see https://openleadr.org/docs/server.html#things-you-should-implement
    verify_message_signatures=False,
    show_server_cert_domain=False
)

# Add the handler for client (VEN) registrations
server.add_handler('on_create_party_registration', on_create_party_registration)

# Add the handler for report registrations from the VEN
server.add_handler('on_register_report', on_register_report)

# Add a prepared event for a VEN that will be picked up when it polls for new messages.
server.add_event(
    ven_id=settings.ven['id'],
    signal_name='simple',
    signal_type='level',
    intervals=[
        {
            'dtstart': datetime(2021, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'duration': timedelta(minutes=10),
            'signal_payload': 1
        }
    ],
    callback=event_response_callback
)

# Run the server on the asyncio event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(server.run())
loop.run_forever()
