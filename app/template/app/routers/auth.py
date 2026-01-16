from typing import Annotated
from fastapi import APIRouter, HTTPException, Header, Request, status, Response
from app.dtos.auth import (
    EmailVerificationRequest,
    ResetPasswordRequest,
    ForgotPasswordRequest,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
)
from app.dtos.utils.utils import MessageResponse
from app.models.auth import User
from app.services.auth import (
    AuthService,
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.utils.dependencies import (
    AuthServiceDependency,
    CurrentUserDependency,
    EmailServiceDependency,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def create_session(
    auth_service: AuthService, user: User, request: Request, response: Response
) -> None:
    session = await auth_service.create_session(user=user, request=request)
    AuthService.set_session_header(response=response, session=session)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateRequest,
    auth_service: AuthServiceDependency,
    email_service: EmailServiceDependency,
    request: Request,
    response: Response,
) -> UserResponse:
    """
    Create a new user account and send email verification code.

    Sets a session token at "Authorization" header key.
    """
    result = await auth_service.register_user(user_data=user_data)
    if isinstance(result, UserAlreadyExistsError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    verification_code = await email_service.create_verification_code(result)
    await email_service.send_verification_email(
        user=result, code=verification_code.code
    )

    await create_session(
        auth_service=auth_service, user=result, request=request, response=response
    )
    return UserResponse.model_validate(result)


@router.post(
    "/login",
)
async def login(
    login_data: UserLoginRequest,
    auth_service: AuthServiceDependency,
    request: Request,
    response: Response,
) -> UserResponse:
    """
    Login a user with email and password.

    Sets the session token at "Authorization" header key.
    """
    user = await auth_service.authenticate_user(login_data=login_data)
    if isinstance(user, InvalidPasswordError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    elif isinstance(user, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    await create_session(
        auth_service=auth_service, user=user, request=request, response=response
    )
    return UserResponse.model_validate(user)


@router.post(
    "/logout",
)
async def logout(
    auth_service: AuthServiceDependency,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> MessageResponse:
    """
    Log out a user.

    Deletes the session token from the database.
    """
    if not authorization:
        return MessageResponse(message="Already logged out")
    session_token = AuthService.parse_session_token(authorization)
    if not session_token:
        return MessageResponse(message="Already logged out")
    await auth_service.logout(session_token=session_token)

    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
)
async def get_current_user_info(
    current_user: CurrentUserDependency,
) -> UserResponse:
    """
    Get current authenticated user information.
    """
    return UserResponse.model_validate(current_user)


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    current_user: CurrentUserDependency,
    email_service: EmailServiceDependency,
) -> MessageResponse:
    """
    Verify user's email address using the verification code sent via email.
    """
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
        )

    is_valid = await email_service.verify_email_verification_code(
        user=current_user, code=verification_data.code
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )

    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification-email")
async def resend_email_verification(
    current_user: CurrentUserDependency,
    email_service: EmailServiceDependency,
) -> MessageResponse:
    """
    Resend email verification code to current user.

    Generates a new verification code and sends it via email.
    """
    if current_user.is_email_verified:
        return MessageResponse(message="Email already verfied")

    verification = await email_service.create_verification_code(current_user)
    await email_service.send_verification_email(
        user=current_user, code=verification.code
    )
    return MessageResponse(message="A new verification code has been sent")


@router.post("/forgot-password")
async def request_password_reset(
    forgot_password_data: ForgotPasswordRequest,
    auth_service: AuthServiceDependency,
    email_service: EmailServiceDependency,
) -> MessageResponse:
    """
    Request a password reset code to be sent via email.

    Generates a password reset code and sends it to the user's email address.
    """
    user = await auth_service.get_user_by_email(forgot_password_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    reset_code = await email_service.create_password_reset_code(user=user)
    await email_service.send_password_reset_email(
        user=user,
        code=reset_code.code,
    )
    return MessageResponse(
        message="A password reset code has been sent to your email address"
    )


@router.post("/reset-password")
async def confirm_password_reset(
    reset_data: ResetPasswordRequest,
    auth_service: AuthServiceDependency,
    email_service: EmailServiceDependency,
) -> MessageResponse:
    """
    Reset user password using the reset code sent via email.

    Validates the reset code and updates the user's password if valid.
    """
    user = await auth_service.get_user_by_email(reset_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    is_valid = await email_service.verify_password_reset_code(
        user=user, code=reset_data.code
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code",
        )

    await auth_service.reset_password(user, reset_data.new_password)

    return MessageResponse(message="Password reset successfully")
