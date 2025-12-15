"""etsy Authentication."""

from __future__ import annotations

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from datetime import datetime, timedelta
import requests
from singer_sdk.helpers._util import utc_now
import json
import sys

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class etsyAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for square."""

    def __init__(self, stream,auth_endpoint: str):
        super().__init__(stream, auth_endpoint=auth_endpoint)
        self._auth_endpoint = auth_endpoint
        
        # Initialize internal tracking attributes
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.last_refreshed: datetime | None = None
        self.expires_in: int | None = None
        self._tap = stream._tap
        self._tap_config = dict(self._tap.config)

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
        result = super().auth_headers
        if not self.is_token_valid():
            self.update_access_token()

        if not self.access_token:
            access_token = self.config.get("access_token")
        else:
            access_token = self.access_token
        result["Authorization"] = f"Bearer {access_token}"
        keystring = self.config["client_id"]
        secret = self.config["client_secret"]
        result["x-api-key"] = f"{keystring}:{secret}"
        return result

    def clean_shop_name(self, shop_name):
        clean_shop_name = shop_name
        # if .etsy. is in shop_name get the first part of the string
        if ".etsy." in clean_shop_name and clean_shop_name.split(".etsy")[0]:
            clean_shop_name = clean_shop_name.split(".etsy")[0]
        if "https://" in clean_shop_name and clean_shop_name.split("https://")[-1]:
            clean_shop_name = clean_shop_name.split("https://")[-1]
        if "http://" in clean_shop_name and clean_shop_name.split("http://")[-1]:
            clean_shop_name = clean_shop_name.split("http://")[-1]
        if any(substring in clean_shop_name for substring in ["www.", ".com"]):
            raise Exception(f"The shop id or shop name provided has not a valid format {shop_name}, please review.")
        # else use shop_name as it is
        return clean_shop_name
    
    @cached_property
    def shop_id(self) -> dict:
        shop_id = self.config.get("shop_id", "")
        shop_name =  self.config.get("shop_name", "")
        # fail if nor shop_id nor shop_name is in the config file
        if not shop_id and not shop_name:
            raise Exception("Shop id and shop name not found in config file.")
        # if shop id is a digit use that as it is -> currently there's no additional validation
        if shop_id and shop_id.isdigit():
            response = requests.get(f"https://openapi.etsy.com/v3/application/users/me", headers=self.auth_headers)
            user_shop_id = response.json().get("shop_id") 
            if int(shop_id) == user_shop_id:
                return int(shop_id)
            else:
                raise Exception(f"User does not own shop_id {shop_id}. Shop id owned by user is: {user_shop_id}")
        else:
            # if shop id is not a digit ot not provided look for a match to shop_name
            if shop_id:
                shop_id = self.clean_shop_name(shop_id)
                # try to find the shop matching shop_id to shop_name
                response = requests.get(f"https://openapi.etsy.com/v3/application/shops?shop_name={shop_id}", headers=self.auth_headers)
                #If token is invalid raise the exception
                response.raise_for_status()
                response = response.json()
                if response["results"]:
                    shop_id = response["results"][0]["shop_id"]
                    self.logger.info(f"Shop ID is {shop_id}")
                    return shop_id
            
            if shop_name:
                shop_name = self.clean_shop_name(shop_name)
                # try to find the shop matching shop_name to shop_name
                response = requests.get(f"https://openapi.etsy.com/v3/application/shops?shop_name={shop_name}", headers=self.auth_headers)
                #If token is invalid raise the exception
                response.raise_for_status()
                response = response.json()
                if response["results"]:
                    shop_id = response["results"][0]["shop_id"]
                    self.logger.info(f"Shop ID is {shop_id}")
                    return shop_id

            # raise an exception if no match was found
            raise Exception(f"Shop id not found for shop_id {shop_id} or for shop_name {shop_name}")

    def is_token_valid(self) -> bool:
        access_token = self.config.get("access_token")
        now = round(datetime.utcnow().timestamp())
        expires_in = self.expires_in

        return not bool(
            # token is valid if now < request time + token expiration in seconds
            (not access_token) or (not expires_in) or (expires_in - now < 120)
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
        request_time = round(datetime.utcnow().timestamp())
        auth_request_payload = self.oauth_request_payload
        token_response = requests.post(self.auth_endpoint, data=auth_request_payload)
        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt refresh token was successful.")
        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            )
        token_json = token_response.json()
        self.access_token = token_json["access_token"]
        headers = {"Authorization": f"Bearer {self.access_token}", "x-api-key": self.config["client_id"]}
        expires_in =  request_time + token_json.get("expires_in", self._default_expiration)
        self.expires_in = expires_in
        if self.expires_in is None:
            self.logger.debug(
                "No expires_in receied in OAuth response and no "
                "default_expiration set. Token will be treated as if it never "
                "expires."
            )
        self._tap_config['access_token'] = self.access_token
        self._tap_config['refresh_token'] = token_json.get("refresh_token")
        self._tap_config['expires_in'] = expires_in
        with open("config.json", "w") as outfile:
            json.dump(self._tap_config, outfile, indent=4)    
      
        self.last_refreshed = request_time