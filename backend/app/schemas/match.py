from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ScoreStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"


class SetScore(BaseModel):
    set_number: int = Field(..., ge=1, le=5)
    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)
    home_players: List[str] = Field(..., min_items=1, max_items=2)
    away_players: List[str] = Field(..., min_items=1, max_items=2)


class ScoreSubmit(BaseModel):
    sets: List[SetScore] = Field(..., min_items=1, max_items=5)


class ScoreConfirm(BaseModel):
    sets: List[SetScore] = Field(..., min_items=1, max_items=5)


class MatchResponse(BaseModel):
    id: int
    fixture_id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    score_status: ScoreStatus
    submitted_by_team_id: Optional[int] = None
    submitted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    is_locked: bool
    match_date: Optional[datetime] = None
    week_start_date: Optional[datetime] = None
    week_end_date: Optional[datetime] = None
    set_data: Optional[str] = None

    class Config:
        from_attributes = True