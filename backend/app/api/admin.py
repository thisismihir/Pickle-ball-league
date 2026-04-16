from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.models.user import User, UserRole
from app.models.team import Team
from app.models.player import Player
from app.models.fixture import Fixture
from app.models.match import Match
from app.models.standing import Standing
from app.auth.dependencies import get_current_user

# Admin router with /api/admin prefix
router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)

@router.delete("/reset-tournament")
def reset_tournament(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset tournament: Delete all teams, players, fixtures, matches, and standings.
    Keep only admin users intact.
    """
    # Verify user is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset the tournament"
        )
    
    try:
        # Delete in correct order to respect foreign key constraints
        deleted_matches = db.query(Match).delete()
        deleted_fixtures = db.query(Fixture).delete()
        deleted_standings = db.query(Standing).delete()
        deleted_players = db.query(Player).delete()
        deleted_teams = db.query(Team).delete()

        # Delete non-admin users
        deleted_users = db.query(User).filter(User.role != UserRole.ADMIN).delete()

        db.commit()

        return {
            "message": "Tournament reset successfully",
            "deleted": {
                "matches": deleted_matches,
                "fixtures": deleted_fixtures,
                "standings": deleted_standings,
                "players": deleted_players,
                "teams": deleted_teams,
                "users": deleted_users
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset tournament: {str(e)}"
        )