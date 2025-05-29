import asyncio
from time import sleep
from datetime import timedelta
from openleadr import OpenADRClient, enable_default_logging
from local_lib.settings import settings

enable_default_logging()


async def collect_report_value():
    # This callback is called when you need to collect a value for your Report
    return 1.23


async def handle_event(event):
    # This callback receives an Event dict.
    if settings.core.DEBUG:
        print(f"Received event: {event['event_descriptor']['event_id']}")
    # You should include code here that sends control signals to your resources.
    return 'optIn'  # Accept the event


# Hacky way to make sure the VTN server is up and running.
# Should be replaced by something like a while health => wait than continue...
sleep(3)

# Create a VEN and connect to the VTN
client = OpenADRClient(
    ven_name=settings.ven["name"],
    ven_id=settings.ven["id"],
    vtn_url=f'{settings.ven["vtn_url"]}/OpenADR2/Simple/2.0b',
    debug=True,
    check_hostname=False,  # Not sure if this is required or not but should probably be removed in production..
    disable_signature=True  # Not sure if this is required or not but should probably be removed in production..
)

# Add the report capability to the client
client.add_report(
    callback=collect_report_value,
    resource_id=settings.ven["id"],
    report_duration=timedelta(seconds=3600),
    measurement=settings.ven["registration_id"],
    sampling_rate=timedelta(seconds=10)
)

# Add event handling capability to the client
client.add_handler('on_event', handle_event)

# Run the client in the Python AsyncIO Event Loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(client.run())
loop.run_forever()
