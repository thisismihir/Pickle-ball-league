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

        # Generate round-robin schedule for balanced weekly matchups
        def generate_round_robin_schedule(teams_list):
            """Generate a balanced round-robin schedule using proven algorithm"""
            n = len(teams_list)
            
            # Ensure even number of teams
            if n % 2 == 1:
                teams_list = teams_list + [None]  # Add bye team
                n = len(teams_list)
            
            schedule = []
            
            # Generate n-1 rounds (each team plays every other team once)
            for round_num in range(n - 1):
                matches = []
                
                # For odd-numbered rounds, pair teams normally
                # For even-numbered rounds, rotate for alternating home/away
                for i in range(n // 2):
                    home_idx = i
                    away_idx = n - 1 - i
                    
                    home = teams_list[home_idx]
                    away = teams_list[away_idx]
                    
                    # Skip if either team is None (bye)
                    if home is not None and away is not None:
                        matches.append((home, away))
                
                if matches:
                    schedule.append(matches)
                
                # Rotate all teams except the first one
                teams_list = [teams_list[0]] + [teams_list[-1]] + teams_list[1:-1]
            
            return schedule
        
        # Get the round-robin schedule (9 weeks of balanced matchups)
        schedule = generate_round_robin_schedule(teams[:])  # Pass a copy
        
        # For 2 rounds (Home + Away)
        for round_num in [1, 2]:
            # For 9 weeks (each team plays every other team once per round)
            for week, week_matchups in enumerate(schedule):
                # Calculate week date range
                if round_num == 1:
                    week_start = start_date + timedelta(weeks=week)
                else:
                    week_start = start_date + timedelta(weeks=9 + week)
                
                week_end = week_start + timedelta(days=6)
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)

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