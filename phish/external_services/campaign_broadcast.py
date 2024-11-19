import json
from fastapi import WebSocket, FastAPI
from typing import List


websockets: List[WebSocket] = []

async def broadcast_campaign_details(campaign):
    data = {
        "id": campaign.id,
        "name": campaign.name,
        "delivery_status": campaign.delivery_status.value,
        "scheduled_date": str(campaign.scheduled_date),
        "scheduled_time": str(campaign.scheduled_time),
    }
    for websocket in websockets:
        await websocket.send_text(json.dumps(data))