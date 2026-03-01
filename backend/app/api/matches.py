from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.match import ScoreSubmit, ScoreConfirm, MatchResponse
from app.services.match_service import MatchService
from app.services.team_service import TeamService
from app.auth.dependencies import get_current_user, get_current_admin_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/matches", tags=["Matches"])

@router.post("/{fixture_id}/submit-score", response_model=MatchResponse)
def submit_score(
    fixture_id: int,
    score_data: ScoreSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit match score (team manager only)"""
    print(f"\n>>>>> ENDPOINT HIT: submit_score")
    print(f">>>>> fixture_id: {fixture_id}")
    print(f">>>>> score_data type: {type(score_data)}")
    print(f">>>>> score_data.sets length: {len(score_data.sets)}")
    print(f">>>>> Raw score_data: {score_data}")

    # Get team managed by current user
    if current_user.role != UserRole.TEAM_MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team managers can submit scores"
        )
    
    from app.models.team import Team
    team = db.query(Team).filter(Team.manager_id == current_user.id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not manage any team"
        )

    result = MatchService.submit_score(db, fixture_id, score_data, team.id)
    print(f"\n>>>>> ENDPOINT RETURNING:")
    print(f">>>>> result.id: {result.id}")
    print(f">>>>> result.set_data type: {type(result.set_data)}")
    print(f">>>>> result.set_data length: {len(result.set_data) if result.set_data else 0}")
    print(f">>>>> result.set_data content: {result.set_data[:200] if result.set_data else 'NULL'}")
    return result

@router.put("/{fixture_id}/confirm-score", response_model=MatchResponse)
def confirm_score(
    fixture_id: int,
    score_data: ScoreConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Confirm or override match score (admin only)"""
    return MatchService.confirm_score(db, fixture_id, score_data)

@router.post("/{fixture_id}/lock", response_model=MatchResponse)
def lock_match(
    fixture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Lock match to prevent further changes (admin only)"""
    return MatchService.lock_match(db, fixture_id)

@router.post("/{fixture_id}/unlock", response_model=MatchResponse)
def unlock_match(
    fixture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Unlock match to allow changes (admin only)"""
    return MatchService.unlock_match(db, fixture_id)

@router.delete("/{fixture_id}/reset-score", response_model=MatchResponse)
def reset_score(
    fixture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Reset match score to allow re-submission (admin only)"""
    return MatchService.reset_score(db, fixture_id)