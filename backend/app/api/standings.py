from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.standing import StandingResponse
from app.services.standing_service import StandingService
from app.auth.dependencies import get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/api/standings", tags=["Standings"])


@router.get("", response_model=List[StandingResponse])
def get_standings(db: Session = Depends(get_db)):
    """Get current league standings (public)"""
    return StandingService.get_standings(db)


@router.get("/{team_id}", response_model=StandingResponse)
def get_team_standing(team_id: int, db: Session = Depends(get_db)):
    """Get standing for a specific team (public)"""
    return StandingService.get_team_standing(db, team_id)


@router.post("/recalculate", status_code=204)
def recalculate_standings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Manually recalculate standings (admin only)"""
    StandingService.recalculate_standings(db)
    return None