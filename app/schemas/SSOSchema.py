from typing import Optional

from pydantic import BaseModel, ConfigDict


# Schema used when starting an SSO login
class SSOLoginRequest(BaseModel):

    provider: str


# Schema used for provider identity information
class SSOIdentityResponse(BaseModel):

    # Allows Pydantic to read data directly
    model_config = ConfigDict(from_attributes=True)
    identity_id: Optional[int] = None
    user_id: Optional[int] = None
    provider: Optional[str] = None
    provider_user_id: Optional[str] = None
    provider_email: Optional[str] = None