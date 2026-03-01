from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PlayerStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PlayerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)


class PlayerResponse(PlayerBase):
    id: int
    status: PlayerStatus
    team_id: Optional[int] = None
    is_individual_registration: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayerApproval(BaseModel):
    status: PlayerStatus


class PlayerAssignment(BaseModel):
    team_id: int