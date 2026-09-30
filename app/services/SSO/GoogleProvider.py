import httpx
from typing import Any, Dict

from authlib.integrations.httpx_client import AsyncOAuth2Client  # type: ignore[import-untyped]

from app.core.config import settings
from app.services.SSO.BaseProvider import BaseProvider


class GoogleProvider(BaseProvider):

    # Google OAuth endpoints
    AUTHORIZATION_ENDPOINT = (
        "https://accounts.google.com/o/oauth2/v2/auth"
    )

    TOKEN_ENDPOINT = (
        "https://oauth2.googleapis.com/token"
    )

    USER_INFO_ENDPOINT = (
        "https://openidconnect.googleapis.com/v1/userinfo"
    )

    # Google OAuth scopes
    SCOPES = [
        "openid",
        "email",
        "profile",
    ]

    def __init__(self):
        # Google Client ID
        self.client_id = settings.GOOGLE_CLIENT_ID

        # Google Client Secret
        self.client_secret = settings.GOOGLE_CLIENT_SECRET

        # Backend callback URL
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    def get_authorization_url(self, state: str) -> str:
        
        # Create the Google login URL

        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        authorization_url, generated_state = client.create_authorization_url(
            self.AUTHORIZATION_ENDPOINT,
            redirect_uri=self.redirect_uri,
            scope=self.SCOPES,
            state=state,
        )

        return authorization_url

    async def exchange_code(
        self,
        code: str,
    ) -> Dict[str, Any]:
        
        # Exchange Google's authorization code for Google's tokens
        
        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        token = await client.fetch_token(
            self.TOKEN_ENDPOINT,
            code=code,
            redirect_uri=self.redirect_uri,
        )

        return token

    async def get_user_info(
        self,
        token_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        # Get the authenticated user's information from Google
        
        access_token = token_data.get("access_token")

        if not access_token:
            raise ValueError(
                "Google access token was not returned."
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_INFO_ENDPOINT,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        response.raise_for_status()

        google_user = response.json()

        return {
            # Google's permanent unique user identifier
            "provider_user_id": google_user.get("sub"),

            "email": google_user.get("email"),

            "first_name": google_user.get("given_name"),

            "last_name": google_user.get("family_name"),

            "email_verified": google_user.get(
                "email_verified",
                False,
            ),
        }