from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.fixture import FixtureResponse, FixtureWithTeams
from app.services.fixture_service import FixtureService
from app.auth.dependencies import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/api/fixtures", tags=["Fixtures"])

@router.post("/generate", response_model=List[FixtureResponse], status_code=status.HTTP_201_CREATED)
def generate_fixtures(
    start_date: Optional[str] = Query(None, description="ISO format start date (YYYY-MM-DD). Defaults to 1 week from today."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Generate fixtures for all approved teams (admin only). Teams specify match dates within assigned week ranges."""
    return FixtureService.generate_fixtures(db, start_date)

@router.get("", response_model=List[FixtureWithTeams])
def list_fixtures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all fixtures"""
    fixtures = FixtureService.get_all_fixtures(db)

    # Build response with team names and scores
    result = []
    for fixture in fixtures:
        from app.services.match_service import MatchService
        try:
            match = MatchService.get_match_by_fixture_id(db, fixture.id)
            fixture_data = FixtureWithTeams(
                id=fixture.id,
                round_number=fixture.round_number,
                match_number=fixture.match_number,
                home_team_id=fixture.home_team_id,
                away_team_id=fixture.away_team_id,
                match_date=match.match_date,  # Get from match, not fixture
                venue=fixture.venue,
                status=fixture.status,
                created_at=fixture.created_at,
                home_team_name=fixture.home_team.name,
                away_team_name=fixture.away_team.name,
                home_score=match.home_score,
                away_score=match.away_score,
                score_status=match.score_status.value,
                week_start_date=match.week_start_date,
                week_end_date=match.week_end_date,
                set_data=match.set_data
            )
        except:
            fixture_data = FixtureWithTeams(
                id=fixture.id,
                round_number=fixture.round_number,
                match_number=fixture.match_number,
                home_team_id=fixture.home_team_id,
                away_team_id=fixture.away_team_id,
                match_date=fixture.match_date,
                venue=fixture.venue,
                status=fixture.status,
                created_at=fixture.created_at,
                home_team_name=fixture.home_team.name,
                away_team_name=fixture.away_team.name,
                set_data=None
            )
        
        result.append(fixture_data)

    return result

@router.get("/team/{team_id}", response_model=List[FixtureWithTeams])
def list_team_fixtures(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all fixtures for a specific team"""
    from app.models.user import UserRole
    from app.services.team_service import TeamService

    # Check if user is admin or manages this team
    if current_user.role != UserRole.ADMIN:
        team = TeamService.get_team_by_id(db, team_id)
        if team.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this team's fixtures"
            )

    fixtures = FixtureService.get_team_fixtures(db, team_id)

    # Build response with team names and scores
    result = []
    for fixture in fixtures:
        from app.services.match_service import MatchService
        try:
            match = MatchService.get_match_by_fixture_id(db, fixture.id)
            fixture_data = FixtureWithTeams(
                id=fixture.id,
                round_number=fixture.round_number,
                match_number=fixture.match_number,
                home_team_id=fixture.home_team_id,
                away_team_id=fixture.away_team_id,
                match_date=match.match_date,
                venue=fixture.venue,
                status=fixture.status,
                created_at=fixture.created_at,
                home_team_name=fixture.home_team.name,
                away_team_name=fixture.away_team.name,
                home_score=match.home_score,
                away_score=match.away_score,
                score_status=match.score_status.value,
                set_data=match.set_data
            )
        except:
            fixture_data = FixtureWithTeams(
                id=fixture.id,
                round_number=fixture.round_number,
                match_number=fixture.match_number,
                home_team_id=fixture.home_team_id,
                away_team_id=fixture.away_team_id,
                match_date=fixture.match_date,
                venue=fixture.venue,
                status=fixture.status,
                created_at=fixture.created_at,
                home_team_name=fixture.home_team.name,
                away_team_name=fixture.away_team.name,
                set_data=None
            )
        
        result.append(fixture_data)

    return result

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_fixtures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete all fixtures (admin only)"""
    FixtureService.delete_all_fixtures(db)
    return None