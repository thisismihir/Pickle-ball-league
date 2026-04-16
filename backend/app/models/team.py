from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TeamStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500))
    home_venue = Column(String(200))  # Home turf/venue for the team

    status = Column(
        SQLEnum(TeamStatus),
        default=TeamStatus.PENDING,
        nullable=False
    )

    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    manager = relationship("User", back_populates="managed_team")

    players = relationship(
        "Player",
        back_populates="team",
        cascade="all, delete-orphan"
    )

    home_fixtures = relationship(
        "Fixture",
        foreign_keys="Fixture.home_team_id",
        back_populates="home_team"
    )

    away_fixtures = relationship(
        "Fixture",
        foreign_keys="Fixture.away_team_id",
        back_populates="away_team"
    )