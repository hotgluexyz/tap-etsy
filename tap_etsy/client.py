"""REST client handling, including etsyStream base class."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterable
import requests
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseOffsetPaginator  # noqa: TCH002
from singer_sdk.streams import RESTStream
import datetime
from requests import Response
from tap_etsy.auth import etsyAuthenticator
from http import HTTPStatus
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]



class MyPaginator(BaseOffsetPaginator):
   
    def __init__(
        self,
        start_value: int,
        page_size: int,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        self.paginated_stream = kwargs.pop("paginated_stream", False)
        super().__init__(start_value, page_size, *args, **kwargs)

    def has_more(self, response):
        if not self.paginated_stream:
            return False
        data = response.json()
        if len(data['results']) == 0:
            return False
        return True
    
    def get_next(self, response: Response) -> int | None:
        """Get the next page offset.

        Args:
            response: API response object.

        Returns:
            The next page offset.
        """
        return self._value + self._page_size


class etsyStream(RESTStream):
    """etsy stream class."""

    paginated_stream = True
    
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        
        return f"https://openapi.etsy.com/v3/application"
    records_jsonpath = "$.results[*]"  # Or override `parse_response`.

    # Set this value or override `get_new_paginator`.
    next_page_token_jsonpath = "$.next_page"  # noqa: S105

    @cached_property
    def authenticator(self) -> _Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        self.access_token = self.config["access_token"]
        return etsyAuthenticator.create_for_stream(self)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_new_paginator(self):
        return MyPaginator(start_value=0, page_size=100, paginated_stream=self.paginated_stream)

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        params["limit"] = 100
        if next_page_token:
            params["offset"] = next_page_token
        if self.replication_key:
            timestamp = self.get_starting_timestamp(context)
            if timestamp:
                unix_time = int(datetime.datetime.timestamp(timestamp))
                params["min_last_modified"] = unix_time
            
        return params


    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        response_mapped = response.json()
        if self.replication_key:
            for record in response_mapped["results"]:
                record["updated_timestamp"] = datetime.datetime.fromtimestamp(record["updated_timestamp"])

        yield from extract_jsonpath(self.records_jsonpath, input=response_mapped)

    def _request(
        self, prepared_request: requests.PreparedRequest, context: dict | None
    ) -> requests.Response:
        """TODO.

        Args:
            prepared_request: TODO
            context: Stream partition or context dictionary.

        Returns:
            TODO
        """
        shop_id = self.authenticator.shop_id
        prepared_request.url = prepared_request.url.replace("shop_id", str(shop_id)) 
        response = self.requests_session.send(prepared_request, timeout=self.timeout)
        self._write_request_duration_log(
            endpoint=self.path,
            response=response,
            context=context,
            extra_tags={"url": prepared_request.path_url}
            if self._LOG_REQUEST_METRIC_URLS
            else None,
        )
        self.validate_response(response)
        return response
    
    def validate_response(self, response: requests.Response) -> None:
        if (
            response.status_code in self.extra_retry_statuses
            or HTTPStatus.INTERNAL_SERVER_ERROR
            <= response.status_code
            <= max(HTTPStatus)
        ):
            if response.status_code == 429:
                try:
                    header_keys_to_log = ["x-limit-per-second", "x-remaining-this-second", "x-limit-per-day", "x-remaining-today", "retry-after"]
                    headers_to_log = {key: response.headers.get(key) for key in header_keys_to_log}

                    self.logger.info(f"Request failed with 429 status code. Response headers: {headers_to_log}")
                    retry_after_seconds = int(response.headers.get("retry-after"))
                    self.logger.info(f"Sleeping for {retry_after_seconds} seconds.")
                    # will sleep for {retry_after_seconds} seconds then it'll raise the RetryAfterException so the request will be retried
                    time.sleep(retry_after_seconds)
                except Exception as e:
                    self.logger.exception("Request failed with 429 status code and no retry-after header. Falling back to default backoff strategy")

            msg = self.response_error_message(response)
            raise RetriableAPIError(f"{msg} with response: {response.text}")

        if (
            HTTPStatus.BAD_REQUEST
            <= response.status_code
            < HTTPStatus.INTERNAL_SERVER_ERROR
        ):
            msg = self.response_error_message(response)
            raise FatalAPIError(f"{msg} with response: {response.text}")