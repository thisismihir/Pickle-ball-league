from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.player import (
    PlayerCreate,
    PlayerResponse,
    PlayerUpdate,
    PlayerApproval,
    PlayerAssignment
)
from app.services.player_service import PlayerService
from app.auth.dependencies import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/api/players", tags=["Players"])


@router.post("", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_individual_player(
    player_data: PlayerCreate,
    db: Session = Depends(get_db)
):
    """Create an individual player (individual registration path - no auth required)"""
    return PlayerService.create_individual_player(db, player_data)


@router.get("", response_model=List[PlayerResponse])
def list_players(
    include_pending: bool = False,
    unassigned_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all players (admin only)"""
    return PlayerService.get_all_players(db, include_pending, unassigned_only)


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get player details (admin only)"""
    return PlayerService.get_player_by_id(db, player_id)


@router.put("/{player_id}/approve", response_model=PlayerResponse)
def approve_player(
    player_id: int,
    approval: PlayerApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Approve or reject a player (admin only)"""
    from app.models.player import PlayerStatus

    approve = approval.status == PlayerStatus.APPROVED
    return PlayerService.approve_player(db, player_id, approve)


@router.post("/{player_id}/assign", response_model=PlayerResponse)
def assign_player(
    player_id: int,
    assignment: PlayerAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Assign player to team (admin only)"""
    return PlayerService.assign_player_to_team(db, player_id, assignment.team_id)

@router.post("/{player_id}/remove", response_model=PlayerResponse)
def remove_player_from_team(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Remove player from team (admin only)"""
    return PlayerService.remove_player_from_team(db, player_id)


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update player details (admin only)"""
    return PlayerService.update_player(db, player_id, player_data)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a player (admin only)"""
    PlayerService.delete_player(db, player_id)
    return None