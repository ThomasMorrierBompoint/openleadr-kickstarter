# Work in progress...

from fastapi import FastAPI
from pydantic import BaseModel
from vtn_service import VTNService
import asyncio

app = FastAPI(title="OpenADR VTN Dashboard")

vtn = VTNService()
vtn.run()  # starts the OpenADR server in the background

# --- API Models ---
class EventRequest(BaseModel):
    ven_id: str
    event_id: str
    signal_level: int = 1

# --- API Endpoints ---
@app.get("/vens")
def get_registered_ven_ids():
    return list(vtn.ven_ids)

@app.post("/send_event")
async def send_event(req: EventRequest):
    if req.ven_id not in vtn.ven_ids:
        return {"error": "VEN not registered"}
    await vtn.send_event(req.ven_id, req.event_id, req.signal_level)
    return {"status": "event sent"}
