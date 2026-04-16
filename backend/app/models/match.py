from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import json
from app.database import Base


class ScoreStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)

    fixture_id = Column(
        Integer,
        ForeignKey("fixtures.id"),
        unique=True,
        nullable=False
    )

    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)

    score_status = Column(
        SQLEnum(ScoreStatus),
        default=ScoreStatus.PENDING,
        nullable=False
    )

    submitted_by_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=True
    )

    submitted_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    is_locked = Column(Boolean, default=False, nullable=False)

    match_date = Column(DateTime, nullable=True)  # Scheduled date and time for the match
    week_start_date = Column(DateTime, nullable=True)  # Start of the week for match
    week_end_date = Column(DateTime, nullable=True)  # End of the week for match

    set_data = Column(
        Text,
        nullable=True
    )  # JSON: [{"set_number": 1, "home_score": 11, "away_score": 9, "home_players": ["P1", "P2"], "away_players": ["P3", "P4"]}]

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    fixture = relationship("Fixture", back_populates="match")
    submitted_by_team = relationship(
        "Team",
        foreign_keys=[submitted_by_team_id]
    )