from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Standing(Base):
    __tablename__ = "standings"

    id = Column(Integer, primary_key=True, index=True)

    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        unique=True,
        nullable=False
    )

    matches_played = Column(Integer, default=0, nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)

    points = Column(Integer, default=0, nullable=False)  # 2 points per win

    score_for = Column(Integer, default=0, nullable=False)
    score_against = Column(Integer, default=0, nullable=False)
    score_difference = Column(Integer, default=0, nullable=False)

    # Relationships
    team = relationship("Team")