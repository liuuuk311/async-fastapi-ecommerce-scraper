from typing import Optional

from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from web.manager.user import UserManager


class MyAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if len(username) < 3:
            """Form data validation"""
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )

        user = await UserManager.authenticate_for_admin(
            request.state.session, email=username, password=password
        )
        if user:
            """Save `username` in session"""
            request.session.update({"username": username})
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        user_exists = await UserManager.get_by_email(
            request.state.session, email=request.session.get("username", None)
        )
        if user_exists:
            """
            Save current `user` object in the request state. Can be used later
            to restrict access to connected user.
            """
            request.state.user = user_exists
            return True

        return False

    def get_admin_user(self, request: Request) -> Optional[AdminUser]:
        user = request.state.user  # Retrieve current user
        return AdminUser(username=user.email)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
