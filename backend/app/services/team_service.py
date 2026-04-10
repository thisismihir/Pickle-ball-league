from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.team import Team, TeamStatus
from app.models.player import Player, PlayerStatus
from app.models.user import User
from app.models.standing import Standing
from app.schemas.team import TeamCreate, TeamUpdate
from app.config import settings


class TeamService:

    @staticmethod
    def create_team(
        db: Session,
        team_data: TeamCreate,
        manager: User
    ) -> Team:
        """Create a new team with players (team registration path)"""

        # Check if user already manages a team
        existing_team = db.query(Team).filter(
            Team.manager_id == manager.id
        ).first()

        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already manages a team"
            )

        # Check if team name exists
        existing_name = db.query(Team).filter(
            Team.name == team_data.name
        ).first()

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team name already exists"
            )

        # Validate player count
        if len(team_data.players) < settings.MIN_PLAYERS_PER_TEAM:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team must have at least {settings.MIN_PLAYERS_PER_TEAM} players"
            )

        if len(team_data.players) > settings.MAX_PLAYERS_PER_TEAM:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team cannot have more than {settings.MAX_PLAYERS_PER_TEAM} players"
            )

        # Check duplicate emails in request
        player_emails = [p.email for p in team_data.players]
        if len(player_emails) != len(set(player_emails)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate player emails in team"
            )

        # Check if any player email already exists
        for email in player_emails:
            existing_player = db.query(Player).filter(
                Player.email == email
            ).first()
            if existing_player:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Player with email {email} already exists"
                )

        # Create team
        db_team = Team(
            name=team_data.name,
            description=team_data.description,
            manager_id=manager.id,
            status=TeamStatus.PENDING
        )

        db.add(db_team)
        db.flush()  # Get team.id before creating players

        # Create players
        for player_data in team_data.players:
            db_player = Player(
                first_name=player_data.first_name,
                last_name=player_data.last_name,
                email=player_data.email,
                phone=player_data.phone,
                team_id=db_team.id,
                status=PlayerStatus.PENDING,
                is_individual_registration=False
            )
            db.add(db_player)

        db.commit()
        db.refresh(db_team)

        return db_team

    # --------------------------------------------------

    @staticmethod
    def get_all_teams(
        db: Session,
        include_pending: bool = False
    ) -> List[Team]:
        """Get all teams"""

        query = db.query(Team)

        if not include_pending:
            query = query.filter(
                Team.status == TeamStatus.APPROVED
            )

        return query.all()

    # --------------------------------------------------

    @staticmethod
    def get_team_by_id(
        db: Session,
        team_id: int
    ) -> Team:
        """Get team by ID"""

        team = db.query(Team).filter(
            Team.id == team_id
        ).first()

        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        return team

    # --------------------------------------------------

    @staticmethod
    def approve_team(
        db: Session,
        team_id: int,
        approve: bool
    ) -> Team:
        """Approve or reject a team"""

        team = TeamService.get_team_by_id(db, team_id)

        if approve:

            # Check max teams limit
            approved_teams_count = db.query(Team).filter(
                Team.status == TeamStatus.APPROVED
            ).count()

            if approved_teams_count >= settings.MAX_TEAMS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot approve more than {settings.MAX_TEAMS} teams"
                )

            team.status = TeamStatus.APPROVED

            # Approve all players
            for player in team.players:
                player.status = PlayerStatus.APPROVED

            # Create standing entry if not exists
            existing_standing = db.query(Standing).filter(
                Standing.team_id == team_id
            ).first()

            if not existing_standing:
                standing = Standing(team_id=team_id)
                db.add(standing)

        else:
            team.status = TeamStatus.REJECTED

            # Reject all players
            for player in team.players:
                player.status = PlayerStatus.REJECTED

        db.commit()
        db.refresh(team)

        return team

    # --------------------------------------------------

    @staticmethod
    def update_team(
        db: Session,
        team_id: int,
        team_data: TeamUpdate
    ) -> Team:
        """Update team details"""

        team = TeamService.get_team_by_id(db, team_id)

        if team_data.name and team_data.name != team.name:
            existing_name = db.query(Team).filter(
                Team.name == team_data.name,
                Team.id != team_id
            ).first()

            if existing_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Team name already exists"
                )

            team.name = team_data.name

        if team_data.description is not None:
            team.description = team_data.description

        db.commit()
        db.refresh(team)

        return team

    # --------------------------------------------------

    @staticmethod
    def delete_team(
        db: Session,
        team_id: int
    ) -> None:
        """Delete a team"""

        team = TeamService.get_team_by_id(db, team_id)

        # Check if team has fixtures
        from app.models.fixture import Fixture

        fixtures = db.query(Fixture).filter(
            (Fixture.home_team_id == team_id) |
            (Fixture.away_team_id == team_id)
        ).first()

        if fixtures:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete team with existing fixtures"
            )

        # Delete standing
        standing = db.query(Standing).filter(
            Standing.team_id == team_id
        ).first()

        if standing:
            db.delete(standing)

        db.delete(team)
        db.commit()

    # --------------------------------------------------

    @staticmethod
    def get_team_player_count(
        db: Session,
        team_id: int
    ) -> int:
        """Get number of approved players in a team"""

        return db.query(Player).filter(
            Player.team_id == team_id,
            Player.status == PlayerStatus.APPROVED
        ).count()