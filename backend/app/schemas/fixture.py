from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class FixtureStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FixtureBase(BaseModel):
    round_number: int
    match_number: int
    home_team_id: int
    away_team_id: int
    match_date: Optional[datetime] = None
    venue: Optional[str] = None


class FixtureCreate(FixtureBase):
    pass


class FixtureResponse(FixtureBase):
    id: int
    status: FixtureStatus
    created_at: datetime

    class Config:
        from_attributes = True


class FixtureWithTeams(FixtureResponse):
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    score_status: Optional[str] = None
    week_start_date: Optional[datetime] = None
    week_end_date: Optional[datetime] = None
    set_data: Optional[str] = None