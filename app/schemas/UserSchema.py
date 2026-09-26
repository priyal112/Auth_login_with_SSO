from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):

    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    email: EmailStr
    password: str


class UserUpdate(BaseModel):

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    email_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    updated_by: Optional[int] = None


class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[int] = None

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None

    email: Optional[EmailStr] = None
    email_verified: Optional[bool] = False

    created_at: Optional[datetime] = None
    created_by: Optional[int] = None

    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    is_active: Optional[bool] = True


class UserLogin(BaseModel):

    email: EmailStr
    password: str

