import secrets
from datetime import timedelta
from fastapi import Request, Response
from pydantic import SecretStr
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from app.dtos.auth import UserCreateRequest, UserLoginRequest
from app.models.auth import User, Session
from app.services.utils.error import ServiceError
from app.services.utils.utils import BaseService
from app.utils.utils import utc_now
from app.utils.logger import logger
from app.utils.settings import settings


class AuthServiceError(ServiceError):
    pass


class UserAlreadyExistsError(AuthServiceError):
    pass


class InvalidPasswordError(AuthServiceError):
    pass


class UserNotFoundError(AuthServiceError):
    pass


class UserNotVerifiedError(AuthServiceError):
    pass


class AuthService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.logger = logger.getChild("auth")

    @staticmethod
    def get_password_hash(password: SecretStr) -> str:
        password_bytes = password.get_secret_value().encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: SecretStr, hashed_password: str) -> bool:
        password_bytes = plain_password.get_secret_value().encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    @staticmethod
    def parse_session_token(authorization_header: str) -> str | None:
        if not authorization_header:
            return None
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1]

    @staticmethod
    def set_session_header(response: Response, session: Session) -> None:
        response.headers["Authorization"] = f"Bearer {session.session_token}"

    async def register_user(
        self, user_data: UserCreateRequest, request: Request
    ) -> tuple[User, Session] | UserAlreadyExistsError:
        email = user_data.email

        # Check if user already exists
        result = await self.db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            self.logger.warning(
                "User registration failed: email already exists", extra={"email": email}
            )
            return UserAlreadyExistsError(f"User with email {email} already exists")

        # Create new user
        password_hash = self.get_password_hash(user_data.password)
        user = User(
            name=user_data.name,
            email=email,
            phone_number=user_data.phone_number,
            password_hash=password_hash,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Create session
        session_token = secrets.token_urlsafe(32)
        expires_at = utc_now() + timedelta(hours=settings.session_lifetime_hours)

        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        session = Session(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        self.logger.info(
            "User registered successfully", extra={"user_id": user.id, "email": email}
        )
        return user, session

    async def login_user(
        self, login_data: UserLoginRequest, request: Request
    ) -> (
        tuple[User, Session]
        | UserNotFoundError
        | InvalidPasswordError
        | UserNotVerifiedError
    ):
        email = login_data.email

        # Find user
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            self.logger.warning("Login failed: user not found", extra={"email": email})
            return UserNotFoundError(f"User with email {email} not found")

        # Verify password
        if not self.verify_password(login_data.password, user.password_hash):
            self.logger.warning(
                "Login failed: invalid password", extra={"user_id": user.id}
            )
            return InvalidPasswordError("Invalid password")

        # Check email verification
        if not user.is_email_verified:
            self.logger.warning(
                "Login failed: email not verified", extra={"user_id": user.id}
            )
            return UserNotVerifiedError("Email not verified")

        # Create session
        session_token = secrets.token_urlsafe(32)
        expires_at = utc_now() + timedelta(hours=settings.session_lifetime_hours)

        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        session = Session(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        self.logger.info("User logged in successfully", extra={"user_id": user.id})
        return user, session

    async def logout_user(self, user_id: str) -> None:
        await self.db.execute(delete(Session).where(Session.user_id == user_id))
        await self.db.commit()
        self.logger.info("User logged out", extra={"user_id": user_id})

    async def get_session(self, session_token: str) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.session_token == session_token)
        )
        session = result.scalar_one_or_none()

        if session and session.is_expired:
            await self.db.delete(session)
            await self.db.commit()
            return None

        return session

    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def validate_session(self, session_token: str) -> User | None:
        """Validate session token and return user if valid."""
        session = await self.get_session(session_token)
        if not session:
            return None
        return await self.get_user_by_id(session.user_id)

    async def reset_session_expiration(self, session_token: str) -> None:
        """Reset session expiration time."""
        result = await self.db.execute(
            select(Session).where(Session.session_token == session_token)
        )
        session = result.scalar_one_or_none()

        if session:
            session.expires_at = utc_now() + timedelta(
                hours=settings.session_lifetime_hours
            )
            await self.db.commit()

    def set_session_cookie(self, response: Response, session: Session) -> None:
        """Set session token in response header."""
        response.headers["Authorization"] = f"Bearer {session.session_token}"

    def clear_session_cookie(self, response: Response) -> None:
        """Clear session token from response."""
        response.headers["Authorization"] = ""
