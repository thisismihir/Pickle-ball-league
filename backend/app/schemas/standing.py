from pydantic import BaseModel

class StandingResponse(BaseModel):
    team_id: int
    team_name: str
    matches_played: int
    wins: int
    losses: int
    points: int
    score_for: int
    score_against: int
    score_difference: int
    position: int
    
    class Config:
        from_attributes = True