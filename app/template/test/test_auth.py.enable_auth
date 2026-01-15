import pytest
from httpx import AsyncClient
from app.dtos.auth import UserResponse
from app.dtos.utils.utils import MessageResponse
from test.utils.utils import build_user_data, register_user, assert_status_code


@pytest.mark.asyncio(loop_scope="session")
async def test_registration(client: AsyncClient):
    user_data = build_user_data()

    response = await client.post("auth/register", json=user_data)
    await assert_status_code(response, 201)

    response_json = response.json()
    user = UserResponse.model_validate(response_json)
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.phone_number == user_data["phone_number"]

    assert "authorization" in response.headers


@pytest.mark.asyncio(loop_scope="session")
async def test_register_duplicate_email(client: AsyncClient):
    result = await register_user(client)
    duplicate_response = await client.post(
        "auth/register",
        json=result.user_data,
        headers={"authorization": result.token},
    )
    await assert_status_code(duplicate_response, 409)


@pytest.mark.asyncio(loop_scope="session")
async def test_register_invalid_email(client: AsyncClient):
    user_data = build_user_data(email="invalid-email")
    response = await client.post("auth/register", json=user_data)
    await assert_status_code(response, 422)


@pytest.mark.asyncio(loop_scope="session")
async def test_register_short_password(client: AsyncClient):
    user_data = build_user_data(password="short")

    response = await client.post("auth/register", json=user_data)
    await assert_status_code(response, 422)


@pytest.mark.asyncio(loop_scope="session")
async def test_login_success(client: AsyncClient):
    result = await register_user(client, verify=False)
    login_data = {
        "email": result.user_data["email"],
        "password": result.user_data["password"],
    }

    response = await client.post(
        "auth/login", json=login_data, headers={"authorization": result.token}
    )
    await assert_status_code(response, 200)

    response_json = response.json()
    user = UserResponse.model_validate(response_json)
    assert user.email == result.user_data["email"]

    assert "authorization" in response.headers


@pytest.mark.asyncio(loop_scope="session")
async def test_login_invalid_credentials(client: AsyncClient):
    login_data = build_user_data()

    response = await client.post("auth/login", json=login_data)
    await assert_status_code(response, 404)

    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_login_wrong_password(client: AsyncClient):
    result = await register_user(client, verify=False)

    login_data = {"email": result.user_data["email"], "password": "wrongpassword"}

    response = await client.post("auth/login", json=login_data)
    await assert_status_code(response, 401)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_current_user(client: AsyncClient):
    result = await register_user(client, verify=False)

    response = await client.get("auth/me", headers={"authorization": result.token})
    await assert_status_code(response, 200)

    response_json = response.json()
    user = UserResponse.model_validate(response_json)
    assert user.email == result.user_data["email"]
    assert user.name == result.user_data["name"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_current_user_unauthorized(client: AsyncClient):
    response = await client.get("auth/me")
    await assert_status_code(response, 401)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_current_user_invalid_token(client: AsyncClient):
    response = await client.get(
        "auth/me", headers={"authorization": "Bearer invalid_token"}
    )
    await assert_status_code(response, 401)


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_success(client: AsyncClient):
    result = await register_user(client, verify=False)

    response = await client.post("auth/logout", headers={"authorization": result.token})
    await assert_status_code(response, 200)

    response_json = response.json()
    message = MessageResponse.model_validate(response_json)
    assert message.message == "Successfully logged out"

    me_response = await client.get("auth/me", headers={"authorization": result.token})
    await assert_status_code(me_response, 401)


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_without_token(client: AsyncClient):
    response = await client.post("auth/logout")
    await assert_status_code(response, 200)

    response_json = response.json()
    message = MessageResponse.model_validate(response_json)
    assert message.message == "Already logged out"


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_invalid_token(client: AsyncClient):
    response = await client.post(
        "auth/logout", headers={"authorization": "Bearer invalid_token"}
    )
    await assert_status_code(response, 200)

    response_json = response.json()
    message = MessageResponse.model_validate(response_json)
    assert message.message


@pytest.mark.asyncio(loop_scope="session")
async def test_forgot_password_success(client: AsyncClient):
    result = await register_user(client, verify=False)

    forgot_password_data = {"email": result.user_data["email"]}

    response = await client.post("auth/forgot-password", json=forgot_password_data)
    await assert_status_code(response, 200)


@pytest.mark.asyncio(loop_scope="session")
async def test_forgot_password_nonexistent_email(client: AsyncClient):
    forgot_password_data = {"email": "nonexistent@example.com"}

    response = await client.post("auth/forgot-password", json=forgot_password_data)
    await assert_status_code(response, 404)


@pytest.mark.asyncio(loop_scope="session")
async def test_forgot_password_invalid_email(client: AsyncClient):
    forgot_password_data = {"email": "invalid-email"}

    response = await client.post("auth/forgot-password", json=forgot_password_data)
    await assert_status_code(response, 422)


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_success(client: AsyncClient):
    result = await register_user(client, verify=False)

    forgot_password_data = {"email": result.user_data["email"]}
    forgot_response = await client.post(
        "auth/forgot-password", json=forgot_password_data
    )
    await assert_status_code(forgot_response, 200)

    new_password = "newpassword123"
    reset_data = {
        "email": result.user_data["email"],
        "code": "jUo13p",
        "new_password": new_password,
    }

    reset_response = await client.post("auth/reset-password", json=reset_data)
    await assert_status_code(reset_response, 200)

    login_data = {"email": result.user_data["email"], "password": new_password}
    login_response = await client.post("auth/login", json=login_data)
    await assert_status_code(login_response, 200)


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_nonexistent_email(client: AsyncClient):
    reset_data = {
        "email": "nonexistent@example.com",
        "code": "jUo13p",
        "new_password": "newpassword123",
    }

    reset_response = await client.post("auth/reset-password", json=reset_data)
    await assert_status_code(reset_response, 404)


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_short_password(client: AsyncClient):
    result = await register_user(client, verify=False)

    forgot_password_data = {"email": result.user_data["email"]}
    await client.post("auth/forgot-password", json=forgot_password_data)

    reset_data = {
        "email": result.user_data["email"],
        "code": "jUo13p",
        "new_password": "short",
    }

    reset_response = await client.post("auth/reset-password", json=reset_data)
    await assert_status_code(reset_response, 422)


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_old_password_fails(client: AsyncClient):
    result = await register_user(client, verify=False)
    old_password = result.user_data["password"]

    forgot_password_data = {"email": result.user_data["email"]}
    await client.post("auth/forgot-password", json=forgot_password_data)

    new_password = "newpassword123"
    reset_data = {
        "email": result.user_data["email"],
        "code": "jUo13p",
        "new_password": new_password,
    }

    reset_response = await client.post("auth/reset-password", json=reset_data)
    await assert_status_code(reset_response, 200)

    old_login_data = {"email": result.user_data["email"], "password": old_password}
    old_login_response = await client.post("auth/login", json=old_login_data)
    await assert_status_code(old_login_response, 401)
