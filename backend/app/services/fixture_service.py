from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.fixture import Fixture, FixtureStatus
from app.models.match import Match, ScoreStatus
from app.models.team import Team, TeamStatus
from app.config import settings
import itertools
from datetime import datetime, timedelta
import random


class FixtureService:

    @staticmethod
    def generate_fixtures(db: Session, start_date_str: Optional[str] = None) -> List[Fixture]:
        """Generate balanced round-robin fixtures with week ranges (no specific match dates)"""

        # Get all approved teams
        teams = db.query(Team).filter(
            Team.status == TeamStatus.APPROVED
        ).all()

        if len(teams) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Need at least 2 approved teams to generate fixtures"
            )

        if len(teams) > settings.MAX_TEAMS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot have more than {settings.MAX_TEAMS} teams"
            )

        # Check if fixtures already exist
        existing_fixtures = db.query(Fixture).first()
        if existing_fixtures:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fixtures already generated. Delete existing fixtures first."
            )

        # Parse or default start_date
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            # Default: 1 week from today
            today = datetime.utcnow().date()
            start_date = datetime(today.year, today.month, today.day) + timedelta(days=7)

        fixtures = []
        match_number = 1
        num_teams = len(teams)
        matches_per_week = num_teams // 2  # 10 teams → 5 matches, 6 teams → 3 matches

        # Generate all possible matchups using round-robin
        all_matchups = list(itertools.combinations(teams, 2))
        
        # For 2 rounds (Home + Away)
        for round_num in [1, 2]:
            # For 9 weeks (each team plays every other team once)
            for week in range(9):
                # Calculate week date range
                if round_num == 1:
                    week_start = start_date + timedelta(weeks=week)
                else:
                    week_start = start_date + timedelta(weeks=9 + week)
                
                week_end = week_start + timedelta(days=6)
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)

                # Get matches for this week
                week_match_start = week * matches_per_week
                week_match_end = week_match_start + matches_per_week
                week_matchups = all_matchups[week_match_start:week_match_end]

                # Create fixtures for this week
                for home_team, away_team in week_matchups:
                    if round_num == 2:
                        # For away round, flip home and away
                        home_team, away_team = away_team, home_team

                    fixture = Fixture(
                        round_number=round_num,
                        match_number=match_number,
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        status=FixtureStatus.SCHEDULED
                    )

                    db.add(fixture)
                    db.flush()  # Get fixture ID
                    fixtures.append(fixture)

                    # Create match with week range (no specific match_date)
                    match = Match(
                        fixture_id=fixture.id,
                        score_status=ScoreStatus.PENDING,
                        match_date=None,  # Teams decide when to play within the week
                        week_start_date=week_start,
                        week_end_date=week_end
                    )

                    db.add(match)
                    match_number += 1

        db.commit()

        # Refresh all fixtures
        for fixture in fixtures:
            db.refresh(fixture)

        return fixtures

    @staticmethod
    def get_all_fixtures(db: Session) -> List[Fixture]:
        """Get all fixtures"""
        return db.query(Fixture).order_by(
            Fixture.round_number,
            Fixture.match_number
        ).all()

    @staticmethod
    def get_fixture_by_id(db: Session, fixture_id: int) -> Fixture:
        """Get fixture by ID"""
        fixture = db.query(Fixture).filter(
            Fixture.id == fixture_id
        ).first()

        if not fixture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fixture not found"
            )

        return fixture

    @staticmethod
    def get_team_fixtures(db: Session, team_id: int) -> List[Fixture]:
        """Get all fixtures for a specific team"""
        fixtures = db.query(Fixture).filter(
            (Fixture.home_team_id == team_id) |
            (Fixture.away_team_id == team_id)
        ).order_by(
            Fixture.round_number,
            Fixture.match_number
        ).all()

        return fixtures

    @staticmethod
    def delete_all_fixtures(db: Session) -> None:
        """Delete all fixtures (admin only, for regeneration)"""

        # Delete all matches first (cascade should handle this)
        db.query(Match).delete()
        db.query(Fixture).delete()
        db.commit()