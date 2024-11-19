from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session
from phish.models.campaign import Campaign
from phish.schemas.campaign import CampaignCreate
from ..database import get_db

from phish.external_services.campaign_broadcast import broadcast_campaign_details



router = APIRouter(
    prefix="/campaigns",
    tags=['Campaign']
)

@router.post("/campaigns/")
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    new_campaign = Campaign(
        name=campaign.name,
        delivery_status=campaign.delivery_status,
        scheduled_date=campaign.scheduled_date,
        scheduled_time=campaign.scheduled_time,
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    await broadcast_campaign_details(new_campaign)

    return new_campaign
