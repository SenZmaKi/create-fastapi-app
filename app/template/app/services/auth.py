import secrets
from datetime import timedelta
from fastapi import Request, Response
from pydantic import SecretStr
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import bcrypt
from app.dtos.auth import UserCreateRequest, UserLoginRequest
from app.models.auth import User, Session
from app.services.utils.error import ServiceError
from app.services.utils.utils import BaseService
from app.utils.utils import utc_now
from app.utils.logger import logger
from app.utils.settings import settings
from sqlalchemy import update


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
        self, user_data: UserCreateRequest
    ) -> User | UserAlreadyExistsError:
        email = user_data.email
        name = user_data.name
        password = user_data.password
        phone_number = user_data.phone_number
        self.logger.info("Registering user", extra={"email": email, "user_name": name})

        existing_user = await self.db.execute(select(User).where(User.email == email))
        existing = existing_user.scalar_one_or_none()

        if existing:
            if existing.is_email_verified:
                self.logger.warning("User already exists", extra={"email": email})
                return UserAlreadyExistsError()
            else:
                self.logger.info(
                    "Deleting existing unverified user",
                    extra={"email": email, "user_id": existing.id},
                )
                await self.db.delete(existing)
                await self.db.flush()

        password_hash = self.get_password_hash(password)

        user = User(
            name=name,
            email=email,
            phone_number=phone_number,
            password_hash=password_hash,
            is_email_verified=False,
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        self.logger.info(
            "User registered successfully", extra={"user_id": user.id, "email": email}
        )

        return user

    async def authenticate_user(
        self, login_data: UserLoginRequest
    ) -> User | InvalidPasswordError | UserNotFoundError:
        email = login_data.email
        password = login_data.password
        self.logger.info("Authenticating user", extra={"email": email})

        user = (
            await self.db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if not user:
            self.logger.warning(
                "User not found during authentication", extra={"email": email}
            )
            return UserNotFoundError()

        if user and self.verify_password(password, user.password_hash):
            self.logger.info(
                "User authenticated successfully", extra={"user_id": user.id}
            )
            return user

        self.logger.warning("Invalid password for user", extra={"email": email})
        return InvalidPasswordError()

    async def create_session(
        self, user: User, request: Request | None = None
    ) -> Session:
        self.logger.info("Creating session for user", extra={"user_id": user.id})
        session_token = secrets.token_urlsafe(43)
        ip_address: str | None = None
        user_agent: str | None = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        expires_at = utc_now() + timedelta(hours=settings.session_lifetime_hours)

        session = Session(
            user_id=user.id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        self.logger.info(
            "Session created successfully",
            extra={"session_id": session.id, "user_id": user.id},
        )

        return session

    async def validate_session(self, session_token: str) -> User | None:
        self.logger.debug("Validating session")
        now = utc_now()
        result = await self.db.execute(
            select(Session)
            .where(Session.session_token == session_token, Session.expires_at > now)
            .options(selectinload(Session.user))
        )
        session = result.scalar_one_or_none()

        if session is None:
            self.logger.debug("Session not found or expired")
            return None

        self.logger.debug(
            "Session validated successfully",
            extra={"session_id": session.id, "user_id": session.user.id},
        )
        return session.user

    async def reset_session_expiration(self, session_token: str) -> None:
        self.logger.debug("Resetting session expiration")
        expires_at = utc_now() + timedelta(hours=settings.session_lifetime_hours)
        await self.db.execute(
            update(Session)
            .where(Session.session_token == session_token)  # <- Specific session
            .values(expires_at=expires_at)
        )
        await self.db.flush()
        self.logger.debug("Session expiration reset successfully")

    async def logout(self, session_token: str) -> None:
        self.logger.info("Logging out user")
        await self.db.execute(
            delete(Session).where(Session.session_token == session_token)
        )
        await self.db.flush()
        self.logger.info("User logged out successfully")

    async def get_user_by_email(self, email: str) -> User | None:
        self.logger.debug("Getting user by email", extra={"email": email})
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_verified_user_by_id(
        self, user_id: str
    ) -> User | UserNotFoundError | UserNotVerifiedError:
        self.logger.debug("Getting verified user by ID", extra={"user_id": user_id})
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            self.logger.warning("User not found", extra={"user_id": user_id})
            return UserNotFoundError()

        if not user.is_email_verified:
            self.logger.warning("User not verified", extra={"user_id": user_id})
            return UserNotVerifiedError()

        self.logger.debug("Verified user found", extra={"user_id": user_id})
        return user

    async def reset_password(self, user: User, new_password: SecretStr) -> None:
        self.logger.info("Resetting password for user", extra={"user_id": user.id})
        password_hash = self.get_password_hash(new_password)
        user.password_hash = password_hash
        # Invalidate all existing sessions
        await self.db.execute(delete(Session).where(Session.user_id == user.id))
        await self.db.flush()
        self.logger.info(
            "Password reset successfully for user", extra={"user_id": user.id}
        )
