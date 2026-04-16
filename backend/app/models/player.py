from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class PlayerStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20))

    status = Column(
        SQLEnum(PlayerStatus),
        default=PlayerStatus.PENDING,
        nullable=False
    )

    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    is_individual_registration = Column(
        Boolean,
        default=False,
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
    team = relationship("Team", back_populates="players")