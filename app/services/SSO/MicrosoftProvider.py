import httpx
from typing import Any, Dict

from authlib.integrations.httpx_client import AsyncOAuth2Client  # type: ignore[import-untyped]

from app.core.config import settings
from app.services.SSO.BaseProvider import BaseProvider


class MicrosoftProvider(BaseProvider):
   
    AUTHORITY = (
        "https://login.microsoftonline.com/common"
    )

    AUTHORIZATION_ENDPOINT = (
        f"{AUTHORITY}/oauth2/v2.0/authorize"
    )

    TOKEN_ENDPOINT = (
        f"{AUTHORITY}/oauth2/v2.0/token"
    )

    USER_INFO_ENDPOINT = (
        "https://graph.microsoft.com/oidc/userinfo"
    )

    SCOPES = [
        "openid",
        "profile",
        "email",
    ]

    def __init__(self):

        self.client_id = settings.MICROSOFT_CLIENT_ID

        self.client_secret = settings.MICROSOFT_CLIENT_SECRET

        self.redirect_uri = settings.MICROSOFT_REDIRECT_URI

    def get_authorization_url(
        self,
        state: str,
    ) -> str:

        # Create the Microsoft login URL.

        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        authorization_url, generated_state = (
            client.create_authorization_url(
                self.AUTHORIZATION_ENDPOINT,
                redirect_uri=self.redirect_uri,
                scope=self.SCOPES,
                state=state,
            )
        )

        return authorization_url

    async def exchange_code(
        self,
        code: str,
    ) -> Dict[str, Any]:
        """
        Exchange the authorization code received from Microsoft for Microsoft tokens.
        """

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
        """
        Get the authenticated Microsoft user's information.
        """

        access_token = token_data.get(
            "access_token"
        )

        if not access_token:
            raise ValueError(
                "Microsoft access token was not returned."
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_INFO_ENDPOINT,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        response.raise_for_status()

        microsoft_user = response.json()

        return {

            "provider_user_id": microsoft_user.get(
                "sub"
            ),

            "email": (
                microsoft_user.get("email")
                or microsoft_user.get("preferred_username")
            ),

            "first_name": microsoft_user.get(
                "given_name"
            ),
            "last_name": microsoft_user.get(
                "family_name"
            ),
            "email_verified": True,
        }