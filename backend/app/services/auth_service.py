from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.auth.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)


class AuthService:

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""

        # Check if username exists
        existing_user = (
            db.query(User)
            .filter(User.username == user_data.username)
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Check if email exists
        existing_email = (
            db.query(User)
            .filter(User.email == user_data.email)
            .first()
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create user
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def authenticate_user(
        db: Session, username: str, password: str
    ) -> User:
        """Authenticate user and return user object"""

        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """Create JWT token for user"""
        access_token = create_access_token(
            data={
                "sub": user.username,
                "role": user.role.value,
            }
        )
        return access_token

    @staticmethod
    def get_user_by_username(
        db: Session, username: str
    ) -> User:
        """Get user by username"""
        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    @staticmethod
    def initialize_admin(
        db: Session,
        username: str,
        email: str,
        password: str,
    ) -> User:
        """Initialize default admin user if not exists"""

        existing_admin = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_admin:
            return existing_admin

        admin_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        return admin_user