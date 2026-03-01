from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import json

from app.models.match import Match, ScoreStatus
from app.models.fixture import Fixture, FixtureStatus
from app.models.team import Team
from app.schemas.match import ScoreSubmit, ScoreConfirm


class MatchService:

    @staticmethod
    def get_match_by_fixture_id(db: Session, fixture_id: int) -> Match:
        """Get match by fixture ID"""
        match = db.query(Match).filter(
            Match.fixture_id == fixture_id
        ).first()

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )

        return match

    @staticmethod
    def submit_score(
        db: Session,
        fixture_id: int,
        score_data: ScoreSubmit,
        team_id: int
    ) -> Match:
        """Submit match score (team manager)"""

        print("\n=== SUBMIT SCORE CALLED ===")
        print(f"Fixture ID: {fixture_id}")
        print(f"Team ID: {team_id}")
        print(f"Score data: {score_data}")
        print(f"Number of sets: {len(score_data.sets)}")

        for i, s in enumerate(score_data.sets):
            print(
                f"Set {i+1}: {s.home_score}-{s.away_score}, "
                f"Home: {s.home_players}, Away: {s.away_players}"
            )

        fixture = db.query(Fixture).filter(
            Fixture.id == fixture_id
        ).first()

        if not fixture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fixture not found"
            )

        # Verify team is part of this fixture
        if team_id != fixture.home_team_id and team_id != fixture.away_team_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team is not part of this fixture"
            )

        match = MatchService.get_match_by_fixture_id(db, fixture_id)

        # Check if match is locked
        if match.is_locked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match is locked and cannot be modified"
            )

        # Duplicate submission checks
        if match.score_status == ScoreStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score already submitted. Awaiting admin confirmation."
            )

        if match.score_status == ScoreStatus.CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score already confirmed by admin"
            )

        # Calculate sets won
        home_sets_won = sum(
            1 for s in score_data.sets if s.home_score > s.away_score
        )
        away_sets_won = sum(
            1 for s in score_data.sets if s.away_score > s.home_score
        )

        # Serialize set data
        set_data_list = [s.model_dump() for s in score_data.sets]
        set_data_json = json.dumps(set_data_list)

        # Store sets won
        match.home_score = home_sets_won
        match.away_score = away_sets_won
        match.set_data = set_data_json
        match.score_status = ScoreStatus.SUBMITTED
        match.submitted_by_team_id = team_id
        match.submitted_at = datetime.utcnow()

        # Update fixture status
        fixture.status = FixtureStatus.IN_PROGRESS

        db.commit()
        db.refresh(match)

        print("=== SUBMIT SCORE COMPLETED ===")

        return match

    @staticmethod
    def confirm_score(
        db: Session,
        fixture_id: int,
        score_data: ScoreConfirm
    ) -> Match:
        """Confirm or override match score (admin)"""

        print("\n=== CONFIRM SCORE CALLED ===")
        print(f"Fixture ID: {fixture_id}")
        print(f"Score data: {score_data}")
        print(f"Number of sets: {len(score_data.sets)}")

        fixture = db.query(Fixture).filter(
            Fixture.id == fixture_id
        ).first()

        if not fixture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fixture not found"
            )

        match = MatchService.get_match_by_fixture_id(db, fixture_id)

        if match.is_locked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match is locked and cannot be modified"
            )

        # Calculate sets won
        home_sets_won = sum(
            1 for s in score_data.sets if s.home_score > s.away_score
        )
        away_sets_won = sum(
            1 for s in score_data.sets if s.away_score > s.home_score
        )

        set_data_list = [s.model_dump() for s in score_data.sets]

        # Override score
        match.home_score = home_sets_won
        match.away_score = away_sets_won
        match.set_data = json.dumps(set_data_list)
        match.score_status = ScoreStatus.CONFIRMED
        match.confirmed_at = datetime.utcnow()

        # Update fixture status
        fixture.status = FixtureStatus.COMPLETED

        db.commit()

        # Update standings
        from app.services.standing_service import StandingService
        StandingService.recalculate_standings(db)

        db.refresh(match)
        return match

    @staticmethod
    def lock_match(db: Session, fixture_id: int) -> Match:
        """Lock a match to prevent further changes (admin)"""

        match = MatchService.get_match_by_fixture_id(db, fixture_id)

        if match.score_status != ScoreStatus.CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only lock confirmed matches"
            )

        match.is_locked = True
        db.commit()
        db.refresh(match)

        return match

    @staticmethod
    def unlock_match(db: Session, fixture_id: int) -> Match:
        """Unlock a match to allow changes (admin)"""

        match = MatchService.get_match_by_fixture_id(db, fixture_id)
        match.is_locked = False
        db.commit()
        db.refresh(match)

        return match

    @staticmethod
    def reset_score(db: Session, fixture_id: int) -> Match:
        """Reset match score to allow re-submission (admin)"""

        print(f"\n=== RESET SCORE CALLED for fixture {fixture_id} ===")

        match = MatchService.get_match_by_fixture_id(db, fixture_id)
        fixture = db.query(Fixture).filter(
            Fixture.id == fixture_id
        ).first()

        # Reset match fields
        match.home_score = None
        match.away_score = None
        match.set_data = None
        match.score_status = ScoreStatus.PENDING
        match.submitted_by_team_id = None
        match.submitted_at = None
        match.confirmed_at = None
        match.is_locked = False

        # Reset fixture status
        if fixture:
            fixture.status = FixtureStatus.SCHEDULED

        db.commit()
        db.refresh(match)

        print("=== RESET SCORE COMPLETED ===")

        return match