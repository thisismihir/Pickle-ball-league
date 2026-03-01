from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.models.standing import Standing
from app.models.team import Team, TeamStatus
from app.models.match import Match, ScoreStatus
from app.models.fixture import Fixture
from app.schemas.standing import StandingResponse


class StandingService:

    @staticmethod
    def recalculate_standings(db: Session) -> None:
        """Recalculate standings based on confirmed matches"""

        # Get all approved teams
        teams = db.query(Team).filter(
            Team.status == TeamStatus.APPROVED
        ).all()

        for team in teams:

            # Get or create standing
            standing = db.query(Standing).filter(
                Standing.team_id == team.id
            ).first()

            if not standing:
                standing = Standing(team_id=team.id)
                db.add(standing)

            # Reset stats
            standing.matches_played = 0
            standing.wins = 0
            standing.losses = 0
            standing.points = 0
            standing.score_for = 0
            standing.score_against = 0
            standing.score_difference = 0

            # Get confirmed home matches
            home_matches = db.query(Match, Fixture).join(
                Fixture, Match.fixture_id == Fixture.id
            ).filter(
                Fixture.home_team_id == team.id,
                Match.score_status == ScoreStatus.CONFIRMED
            ).all()

            # Get confirmed away matches
            away_matches = db.query(Match, Fixture).join(
                Fixture, Match.fixture_id == Fixture.id
            ).filter(
                Fixture.away_team_id == team.id,
                Match.score_status == ScoreStatus.CONFIRMED
            ).all()

            # Home stats
            for match, fixture in home_matches:
                standing.matches_played += 1
                standing.score_for += match.home_score
                standing.score_against += match.away_score

                # Points = sets won
                standing.points += match.home_score

                if match.home_score > match.away_score:
                    standing.wins += 1
                else:
                    standing.losses += 1

            # Away stats
            for match, fixture in away_matches:
                standing.matches_played += 1
                standing.score_for += match.away_score
                standing.score_against += match.home_score

                standing.points += match.away_score

                if match.away_score > match.home_score:
                    standing.wins += 1
                else:
                    standing.losses += 1

            # Score difference
            standing.score_difference = (
                standing.score_for - standing.score_against
            )

        db.commit()

    # --------------------------------------------------

    @staticmethod
    def get_standings(db: Session) -> List[StandingResponse]:
        """Get current standings ordered by points and score difference"""

        standings = db.query(Standing, Team).join(
            Team, Standing.team_id == Team.id
        ).filter(
            Team.status == TeamStatus.APPROVED
        ).order_by(
            Standing.points.desc(),
            Standing.score_difference.desc(),
            Standing.score_for.desc()
        ).all()

        result = []
        position = 1

        for standing, team in standings:
            standing_response = StandingResponse(
                team_id=team.id,
                team_name=team.name,
                matches_played=standing.matches_played,
                wins=standing.wins,
                losses=standing.losses,
                points=standing.points,
                score_for=standing.score_for,
                score_against=standing.score_against,
                score_difference=standing.score_difference,
                position=position
            )

            result.append(standing_response)
            position += 1

        return result

    # --------------------------------------------------

    @staticmethod
    def get_team_standing(
        db: Session,
        team_id: int
    ) -> StandingResponse:
        """Get standing for a specific team"""

        standing = db.query(Standing, Team).join(
            Team, Standing.team_id == Team.id
        ).filter(
            Standing.team_id == team_id
        ).first()

        if not standing:
            # Return default if no standing exists
            team = db.query(Team).filter(
                Team.id == team_id
            ).first()

            if not team:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Team not found"
                )

            return StandingResponse(
                team_id=team_id,
                team_name=team.name,
                matches_played=0,
                wins=0,
                losses=0,
                points=0,
                score_for=0,
                score_against=0,
                score_difference=0,
                position=0
            )

        standing_obj, team = standing

        # Calculate live position
        all_standings = StandingService.get_standings(db)
        position = next(
            (i + 1 for i, s in enumerate(all_standings)
             if s.team_id == team_id),
            0
        )

        return StandingResponse(
            team_id=team.id,
            team_name=team.name,
            matches_played=standing_obj.matches_played,
            wins=standing_obj.wins,
            losses=standing_obj.losses,
            points=standing_obj.points,
            score_for=standing_obj.score_for,
            score_against=standing_obj.score_against,
            score_difference=standing_obj.score_difference,
            position=position
        )