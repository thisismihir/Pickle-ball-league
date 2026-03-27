from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.player import Player, PlayerStatus
from app.models.team import Team, TeamStatus
from app.schemas.player import PlayerCreate, PlayerUpdate
from app.config import settings


class PlayerService:

    @staticmethod
    def create_individual_player(
        db: Session,
        player_data: PlayerCreate
    ) -> Player:
        """Create an individual player (individual registration path)"""

        # Check if email exists
        existing_player = db.query(Player).filter(
            Player.email == player_data.email
        ).first()

        if existing_player:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player with this email already exists"
            )

        # Create player without team
        db_player = Player(
            first_name=player_data.first_name,
            last_name=player_data.last_name,
            email=player_data.email,
            phone=player_data.phone,
            status=PlayerStatus.PENDING,
            is_individual_registration=True,
            team_id=None
        )

        db.add(db_player)
        db.commit()
        db.refresh(db_player)

        return db_player

    @staticmethod
    def get_all_players(
        db: Session,
        include_pending: bool = False,
        unassigned_only: bool = False
    ) -> List[Player]:
        """Get all players"""

        query = db.query(Player)

        if not include_pending:
            query = query.filter(Player.status == PlayerStatus.APPROVED)

        if unassigned_only:
            query = query.filter(Player.team_id == None)

        return query.all()

    @staticmethod
    def get_player_by_id(db: Session, player_id: int) -> Player:
        """Get player by ID"""

        player = db.query(Player).filter(
            Player.id == player_id
        ).first()

        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )

        return player

    @staticmethod
    def approve_player(
        db: Session,
        player_id: int,
        approve: bool
    ) -> Player:
        """Approve or reject a player"""

        player = PlayerService.get_player_by_id(db, player_id)

        if approve:
            player.status = PlayerStatus.APPROVED
        else:
            player.status = PlayerStatus.REJECTED

        db.commit()
        db.refresh(player)

        return player

    @staticmethod
    def assign_player_to_team(
        db: Session,
        player_id: int,
        team_id: int
    ) -> Player:
        """Assign an individual player to a team"""

        player = PlayerService.get_player_by_id(db, player_id)

        # Check if already assigned
        if player.team_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player is already assigned to a team"
            )

        # Get team
        team = db.query(Team).filter(
            Team.id == team_id
        ).first()

        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        # Check if team is approved
        if team.status != TeamStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only assign players to approved teams"
            )

        # Check max players limit
        current_player_count = db.query(Player).filter(
            Player.team_id == team_id,
            Player.status == PlayerStatus.APPROVED
        ).count()

        if current_player_count >= settings.MAX_PLAYERS_PER_TEAM:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team already has maximum {settings.MAX_PLAYERS_PER_TEAM} players"
            )

        # Assign player
        player.team_id = team_id

        if player.status == PlayerStatus.PENDING:
            player.status = PlayerStatus.APPROVED

        db.commit()
        db.refresh(player)

        return player

    @staticmethod
    def remove_player_from_team(
        db: Session,
        player_id: int
    ) -> Player:
        """Remove a player from their team"""

        player = PlayerService.get_player_by_id(db, player_id)

        if player.team_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player is not assigned to any team"
            )

        team_id = player.team_id

        # Check minimum player requirement
        current_player_count = db.query(Player).filter(
            Player.team_id == team_id,
            Player.status == PlayerStatus.APPROVED
        ).count()

        if current_player_count <= settings.MIN_PLAYERS_PER_TEAM:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot remove player. Team must have at least {settings.MIN_PLAYERS_PER_TEAM} players"
            )

        player.team_id = None

        db.commit()
        db.refresh(player)

        return player

    @staticmethod
    def update_player(
        db: Session,
        player_id: int,
        player_data: PlayerUpdate
    ) -> Player:
        """Update player details"""

        player = PlayerService.get_player_by_id(db, player_id)

        # Email change validation
        if player_data.email and player_data.email != player.email:
            existing_email = db.query(Player).filter(
                Player.email == player_data.email,
                Player.id != player_id
            ).first()

            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )

            player.email = player_data.email

        if player_data.first_name:
            player.first_name = player_data.first_name

        if player_data.last_name:
            player.last_name = player_data.last_name

        if player_data.phone is not None:
            player.phone = player_data.phone

        db.commit()
        db.refresh(player)

        return player

    @staticmethod
    def delete_player(
        db: Session,
        player_id: int
    ) -> None:
        """Delete a player"""

        player = PlayerService.get_player_by_id(db, player_id)

        # If player is in a team, check minimum requirement
        if player.team_id:
            current_player_count = db.query(Player).filter(
                Player.team_id == player.team_id,
                Player.status == PlayerStatus.APPROVED
            ).count()

            if current_player_count <= settings.MIN_PLAYERS_PER_TEAM:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete player. Team must have at least {settings.MIN_PLAYERS_PER_TEAM} players"
                )

        db.delete(player)
        db.commit()

    @staticmethod
    def add_player_to_team_post_registration(
        db: Session,
        team_id: int,
        player_data: PlayerCreate,
        current_user
    ) -> Player:
        """Add a new player to an existing approved team (post-registration)"""
        from app.models.user import UserRole

        # Get team
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        # Check if team is approved
        if team.status != TeamStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only add players to approved teams"
            )

        # Check authorization: user must be team manager or admin
        if current_user.role != UserRole.ADMIN and team.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add players to this team"
            )

        # Check if email already exists
        existing_player = db.query(Player).filter(
            Player.email == player_data.email
        ).first()
        if existing_player:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player with this email already exists"
            )

        # Check team's current player count (all statuses)
        current_player_count = db.query(Player).filter(
            Player.team_id == team_id
        ).count()

        if current_player_count >= settings.MAX_PLAYERS_PER_TEAM:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team already has maximum {settings.MAX_PLAYERS_PER_TEAM} players"
            )

        # Create player with PENDING status (requires admin approval)
        db_player = Player(
            first_name=player_data.first_name,
            last_name=player_data.last_name,
            email=player_data.email,
            phone=player_data.phone,
            team_id=team_id,
            status=PlayerStatus.PENDING,  # Requires admin approval
            is_individual_registration=False
        )

        db.add(db_player)
        db.commit()
        db.refresh(db_player)

        return db_player

    @staticmethod
    def get_team_players(
        db: Session,
        team_id: int
    ) -> List[Player]:
        """Get all players for a specific team"""
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        return db.query(Player).filter(
            Player.team_id == team_id
        ).order_by(Player.created_at).all()