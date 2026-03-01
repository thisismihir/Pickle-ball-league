from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.fixture import Fixture, FixtureStatus
from app.models.match import Match, ScoreStatus
from app.models.team import Team, TeamStatus
from app.config import settings
import itertools
from datetime import datetime, timedelta


class FixtureService:

    @staticmethod
    def generate_fixtures(db: Session) -> List[Fixture]:
        """Generate round-robin fixtures for all approved teams (home & away)"""

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

        fixtures = []
        match_number = 1

        # Start date: March 1st, 2026 at 6:00 PM
        start_date = datetime(2026, 3, 1, 18, 0)

        # Calculate total number of matches
        num_team = len(teams)
        matches_per_round = num_team * (num_team - 1) // 2
        total_matches = matches_per_round * 2  # Home and away

        # Schedule 2 matches per team per week
        # For simplicity, schedule matches on Tuesday and Friday evenings
        match_days = [1, 4]  # Tuesday=1, Friday=4
        matches_scheduled = 0

        match_dates = []
        current_date = start_date

        while matches_scheduled < total_matches:
            for day_offset in match_days:
                if matches_scheduled >= total_matches:
                    break

                # Find next occurrence of the target weekday
                days_ahead = day_offset - current_date.weekday()
                if days_ahead < 0:
                    days_ahead += 7

                match_date = current_date + timedelta(days=days_ahead)
                match_dates.append(match_date)
                matches_scheduled += 1

            current_date += timedelta(weeks=1)

        match_index = 0

        # Generate home and away fixtures
        # Round 1: Each team plays every other team at home
        # Round 2: Each team plays every other team away
        for round_num in [1, 2]:
            for home_team, away_team in itertools.combinations(teams, 2):

                if round_num == 1:
                    fixture = Fixture(
                        round_number=round_num,
                        match_number=match_number,
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        status=FixtureStatus.SCHEDULED
                    )
                else:
                    fixture = Fixture(
                        round_number=round_num,
                        match_number=match_number,
                        home_team_id=away_team.id,
                        away_team_id=home_team.id,
                        status=FixtureStatus.SCHEDULED
                    )

                db.add(fixture)
                db.flush()  # Get fixture ID before creating match
                fixtures.append(fixture)

                # Create corresponding match record
                match_date = (
                    match_dates[match_index]
                    if match_index < len(match_dates)
                    else None
                )

                week_start = None
                week_end = None

                if match_date:
                    # Monday of the week
                    days_to_monday = match_date.weekday()
                    week_start = match_date - timedelta(days=days_to_monday)
                    week_start = week_start.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )

                    # Sunday of the week
                    week_end = week_start + timedelta(days=6)
                    week_end = week_end.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )

                match = Match(
                    fixture_id=fixture.id,
                    score_status=ScoreStatus.PENDING,
                    match_date=match_date,
                    week_start_date=week_start,
                    week_end_date=week_end
                )

                db.add(match)

                match_number += 1
                match_index += 1

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