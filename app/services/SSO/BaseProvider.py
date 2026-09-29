from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseProvider(ABC):

    # Base class for all SSO providers

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:

       # Create the URL where the user will be redirected to the provider's login/consent page
        pass

    @abstractmethod
    async def exchange_code(self, code: str) -> Dict[str, Any]:

        # Exchange the authorization code received from the provider for provider-specific tokens/data
        pass

    @abstractmethod
    async def get_user_info(self, token_data: Dict[str, Any]) -> Dict[str, Any]:

        # Get the user's identity information from the provider
        
        pass