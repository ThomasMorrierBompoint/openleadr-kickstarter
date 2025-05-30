from pydantic import BaseModel

from local_lib.models.domain import generate_ven_props

default_ven_prop = generate_ven_props(-1)


# --- API Models ---
class CreateVenRequest(BaseModel):
    ven_name: str = default_ven_prop['name']
    ven_id: str = default_ven_prop['id']
    signal_level: int = 1


class SendEventRequest(BaseModel):
    ven_id: str = default_ven_prop['id']
    signal_level: int = 1
