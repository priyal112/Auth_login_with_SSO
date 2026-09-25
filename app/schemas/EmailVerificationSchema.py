from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict



class EmailVerificationRequest(BaseModel):

    token: str


# Schema used when requesting another verification email 
class ResendVerificationRequest(BaseModel): 
    
    email: str
    

# Schema used when returning verification token information
class EmailVerificationResponse(BaseModel):

    # Allow conversion from SQLAlchemy model
    model_config = ConfigDict(from_attributes=True)

    token_id: Optional[int] = None

    user_id: Optional[int] = None

    expires_at: Optional[datetime] = None

    used_at: Optional[datetime] = None

    created_at: Optional[datetime] = None

