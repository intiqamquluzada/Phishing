from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from enum import Enum


class DeliveryStatusEnum(str, Enum):
    SENT = "SENT"
    OPENED = "OPENED"


class CampaignCreate(BaseModel):
    name: str
    delivery_status: Optional[DeliveryStatusEnum] = DeliveryStatusEnum.SENT
    scheduled_date: date
    scheduled_time: time
