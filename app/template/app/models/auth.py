from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.utils.utils import (
    Base,
    BaseMixin,
    CanExpireMixin,
    CreatedAtMixin,
    IdMixin,
    OwnedByUserMixin,
    StrColumn,
)


class User(BaseMixin):
    """
    User model representing system users.
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(StrColumn, nullable=False)
    email: Mapped[str] = mapped_column(StrColumn, unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    password_hash: Mapped[str] = mapped_column(StrColumn, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )


    @property
    def first_name(self) -> str:
        return self.name.split(" ")[0]

    def __repr__(self) -> str:
        return f"<User(name={self.name}, email={self.email})>"


class Session(Base, IdMixin, CreatedAtMixin, CanExpireMixin, OwnedByUserMixin):
    __tablename__ = "sessions"

    session_token: Mapped[str] = mapped_column(StrColumn, unique=True, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(StrColumn, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Session(user_id={self.user_id}, token={self.session_token[:8]}...)>"


class VerificationCodeMixin(BaseMixin, OwnedByUserMixin, CanExpireMixin):
    __abstract__ = True

    code: Mapped[str] = mapped_column(String(6), nullable=False)


class EmailVerificationCode(VerificationCodeMixin):
    __tablename__ = "email_verification_codes"

    def __repr__(self) -> str:
        return f"<EmailVerificationCode(user_id={self.user_id}, code={self.code})>"


class PasswordResetCode(VerificationCodeMixin):
    __tablename__ = "password_reset_codes"

    def __repr__(self) -> str:
        return f"<PasswordResetCode(user_id={self.user_id}, code={self.code})>"
