"""etsy Authentication."""

from __future__ import annotations

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from datetime import datetime, timedelta
import requests
from singer_sdk.helpers._util import utc_now

# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class etsyAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for square."""
    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the AutomaticTestTap API.

        Returns:
            A dict with the request body
        """
       
        return {
            'client_id': self.config["client_id"],
            'grant_type': 'refresh_token',
            'refresh_token': self.config['refresh_token'],
        }

    @property
    def auth_headers(self) -> dict:
        """Return a dictionary of auth headers to be applied.

        These will be merged with any `http_headers` specified in the stream.

        Returns:
            HTTP headers for authentication.
        """
        if not self.is_token_valid():
            self.update_access_token()
        result = super().auth_headers
        access_token = self.config["access_token"]
        result["Authorization"] = f"Bearer {access_token}"
        result["x-api-key"] = self.config["client_id"]
        return result

    def is_token_valid(self) -> bool:
        access_token = self.config.get("access_token")
        now = round(datetime.utcnow().timestamp())
        expires_in = self.config.get("expires_in")

        return not bool(
            # token is valid if now < request time + token expiration in seconds
            (not access_token) or (not expires_in) or (now < expires_in)
        )


    @classmethod
    def create_for_stream(cls, stream) -> "etsyAuthenticator":
        """Instantiate an authenticator for a specific Singer stream.

        Args:
            stream: The Singer stream instance.

        Returns:
            A new authenticator.
        """
        
        return cls(
            stream=stream,
            auth_endpoint="https://api.etsy.com/v3/public/oauth/token"
        )

     # Authentication and refresh
    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`.

        Raises:
            RuntimeError: When OAuth login fails.
        """
        request_time = utc_now()
        auth_request_payload = self.oauth_request_payload
        token_response = requests.post(self.auth_endpoint, data=auth_request_payload)
        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            )
        token_json = token_response.json()
        self.access_token = token_json["access_token"]
        self.expires_in = token_json.get("expires_in", self._default_expiration)
        if self.expires_in is None:
            self.logger.debug(
                "No expires_in receied in OAuth response and no "
                "default_expiration set. Token will be treated as if it never "
                "expires."
            )
        self.last_refreshed = request_time