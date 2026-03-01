from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.team import (
    TeamCreate,
    TeamResponse,
    TeamWithPlayers,
    TeamUpdate,
    TeamApproval
)
from app.services.team_service import TeamService
from app.auth.dependencies import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/api/teams", tags=["Teams"])


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new team (team registration opt)"""
    return TeamService.create_team(db, team_data, current_user)


@router.get("", response_model=List[TeamWithPlayers])
def list_teams(
    include_pending: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all teams (admin can see all, users can see approved teams + their own)"""
    from app.models.user import UserRole

    # Admin can see all teams
    if current_user.role == UserRole.ADMIN:
        return TeamService.get_all_teams(db, include_pending)

    # Regular users see approved teams + their own team (even if pending)
    all_teams = TeamService.get_all_teams(db, include_pending=True)

    filtered_teams = [
        team for team in all_teams
        if team.status == "approved" or team.manager_id == current_user.id
    ]

    return filtered_teams


@router.get("/{team_id}", response_model=TeamWithPlayers)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team details"""
    return TeamService.get_team_by_id(db, team_id)


@router.put("/{team_id}/approve", response_model=TeamResponse)
def approve_team(
    team_id: int,
    approval: TeamApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Approve or reject a team (admin only)"""
    from app.models.team import TeamStatus

    approve = approval.status == TeamStatus.APPROVED
    return TeamService.approve_team(db, team_id, approve)


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update team details"""
    from app.models.user import UserRole

    # Check if user is admin or team manager
    team = TeamService.get_team_by_id(db, team_id)

    if current_user.role != UserRole.ADMIN and team.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this team"
        )

    return TeamService.update_team(db, team_id, team_data)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a team (admin only)"""
    TeamService.delete_team(db, team_id)
    return None