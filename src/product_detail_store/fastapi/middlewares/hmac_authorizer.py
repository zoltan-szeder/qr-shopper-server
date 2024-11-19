import base64
import hmac
import http.client
from datetime import UTC, datetime
from typing import Tuple, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from product_detail_store import service_factory


class HMACAuthorizer(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if await self.hmac_signature_invalid(request):
            return JSONResponse(
                status_code=http.client.UNAUTHORIZED,
                content={"error": "Unauthorized"}
            )

        return await call_next(request)

    async def hmac_signature_invalid(self, request: Request):
        auth_time = request.headers.get("Authorization-Time")
        if self._has_expired(auth_time):
            return True

        auth_user, auth_password = await self._get_credentials(request.headers.get("Authorization-User"))
        if auth_user is None or auth_password is None:
            return True

        msg = (
                f"{request.method.upper()} {request.url.path}\n" +
                f"Authorization-Time: {auth_time}\n" +
                f"Authorization-User: {auth_user}"
        )
        hmac_signature = hmac.digest(
            auth_password.encode(),
            msg.encode(),
            "sha-256"
        )
        b64_signature = base64.b64encode(hmac_signature).decode()

        return request.headers.get("Authorization") != f"HMAC {b64_signature}"

    def _has_expired(self, auth_time):
        if not auth_time:
            return True

        if not auth_time.isnumeric():
            return True

        now = datetime.now(tz=UTC).timestamp()
        return abs(now - int(auth_time)) > 300

    async def _get_credentials(self, auth_user) -> Tuple[Optional[str], Optional[str]]:
        if not auth_user:
            return None, None

        return auth_user, await self._get_password(auth_user)

    async def _get_password(self, auth_user):
        factory = service_factory.get_instance()
        repository = factory.get_users_repository()
        return await repository.get_password_for_user(auth_user)
