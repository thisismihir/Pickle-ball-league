from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TeamStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TeamBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    home_venue: Optional[str] = Field(None, max_length=200)


class TeamCreate(TeamBase):
    players: List['PlayerCreate'] = Field(..., min_items = 2, max_items=6)


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    home_venue: Optional[str] = Field(None, max_length=200)


class TeamResponse(TeamBase):
    id: int
    status: TeamStatus
    manager_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamApproval(BaseModel):
    status: TeamStatus


class TeamWithPlayers(TeamResponse):
    players: List['PlayerResponse'] = []
    
from app.schemas.player import PlayerCreate, PlayerResponse
TeamCreate.model_rebuild()
TeamWithPlayers.model_rebuild()