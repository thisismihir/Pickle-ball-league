from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class FixtureStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Fixture(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, nullable=False)
    match_number = Column(Integer, nullable=False)

    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    match_date = Column(DateTime, nullable=True)
    venue = Column(String(200))

    status = Column(
        SQLEnum(FixtureStatus),
        default=FixtureStatus.SCHEDULED,
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    home_team = relationship(
        "Team",
        foreign_keys=[home_team_id],
        back_populates="home_fixtures"
    )

    away_team = relationship(
        "Team",
        foreign_keys=[away_team_id],
        back_populates="away_fixtures"
    )

    match = relationship(
        "Match",
        back_populates="fixture",
        uselist=False,
        cascade="all, delete-orphan"
    )