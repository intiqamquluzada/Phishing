from database import Base, engine
from models.target import TargetUser, Target
from models.users import User
from models.role import Role
from models.campaign import Campaign
from models.administration import Administration, Invite
from models.email import EmailTemplate, EmailReadEvent
from models.training import Training, TrainingInformation, Question

Base.metadata.create_all(bind=engine)
