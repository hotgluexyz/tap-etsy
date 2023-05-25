"""REST client handling, including etsyStream base class."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Iterable

import requests
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseOffsetPaginator  # noqa: TCH002
from singer_sdk.streams import RESTStream

from tap_etsy.auth import etsyAuthenticator

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]



class MyPaginator(BaseOffsetPaginator):
    def has_more(self, response):
        data = response.json()
        if len(data.get("results", [])) == 0:
            return False
        return True


class etsyStream(RESTStream):
    """etsy stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        shop_id = self.config["shop_id"]
        return f"https://openapi.etsy.com/v3/application/shops/{shop_id}"
    records_jsonpath = "$[*]"  # Or override `parse_response`.

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
        return MyPaginator(start_value=0, page_size=100)

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
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params


    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

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
