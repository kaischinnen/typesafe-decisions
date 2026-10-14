import os
from collections.abc import Mapping
from types import TracebackType
from typing import Self, TypeVar, overload

import httpx2
from pydantic import BaseModel
from typesafe_sdk import (
    Choice,
    JSONContent,
    JSONValue,
    Noul,
    RetryPolicy,
    TypeSafeAPIError,
    TypeSafeClient,
)


ResponseT = TypeVar("ResponseT", bound=BaseModel)


class DecisionClient:
    """Convenience client for semantic decisions with TypeSafe System One."""

    def __init__(
        self,
        *,
        api_key_env: str | None = None,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        headers: Mapping[str, str] | None = None,
        transport: httpx2.BaseTransport | None = None,
        http_client: httpx2.Client | None = None,
        base_url: str | None = None,
    ) -> None:
        self.setup_api_key(api_key_env)
        self.setup_client(
            model=model,
            retry=retry,
            timeout=timeout,
            headers=headers,
            transport=transport,
            http_client=http_client,
            base_url=base_url,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.client.close()

    def setup_client(
        self,
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        headers: Mapping[str, str] | None = None,
        transport: httpx2.BaseTransport | None = None,
        http_client: httpx2.Client | None = None,
        base_url: str | None = None,
    ) -> None:
        self.client = TypeSafeClient(
            api_key=self.API_KEY,
            model=model,
            retry=retry,
            timeout=timeout,
            headers=headers,
            transport=transport,
            http_client=http_client,
            base_url=base_url,
        )

    def setup_api_key(self, api_key_env: str | None = None) -> None:
        environment_variable = api_key_env or "TYPESAFE_API_KEY"
        api_key = os.environ.get(environment_variable)

        if api_key is None:
            raise RuntimeError(
                f"Missing required environment variable: ${environment_variable}"
            )
        if not api_key.strip():
            raise RuntimeError(
                f"Required environment variable is empty: ${environment_variable}"
            )

        self.API_KEY = api_key

    def feels(
        self,
        state: JSONContent,
        question: str,
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        extra_headers: Mapping[str, str] | None = None,
        extra_body: Mapping[str, JSONValue | None] | None = None,
    ) -> float:
        try:
            result = self.client.system_one(
                state,
                {
                    "feels": Noul(instructions=question),
                },
                model=model,
                retry=retry,
                timeout=timeout,
                extra_headers=extra_headers,
                extra_body=extra_body,
            )
        except TypeSafeAPIError as error:
            print(error.status, error.request_id)
            raise

        return result.nouls["feels"].noul

    @overload
    def match(
        self,
        state: JSONContent,
        question: JSONContent,
        criteria: Mapping[str, JSONContent | None],
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        extra_headers: Mapping[str, str] | None = None,
        extra_body: Mapping[str, JSONValue | None] | None = None,
        response_model: None = None,
    ) -> str: ...

    @overload
    def match(
        self,
        state: JSONContent,
        question: JSONContent,
        criteria: Mapping[str, JSONContent | None],
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        extra_headers: Mapping[str, str] | None = None,
        extra_body: Mapping[str, JSONValue | None] | None = None,
        response_model: type[ResponseT],
    ) -> ResponseT: ...

    def match(
        self,
        state: JSONContent,
        question: JSONContent,
        criteria: Mapping[str, JSONContent | None],
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        extra_headers: Mapping[str, str] | None = None,
        extra_body: Mapping[str, JSONValue | None] | None = None,
        response_model: type[ResponseT] | None = None,
    ) -> str | ResponseT:
        """Select the criterion that best matches ``state``.

        The selected criterion name is returned by default. When ``response_model``
        is supplied, the custom parsed response is returned unchanged.
        """
        questions = {
            "match": Choice(instructions=question, criteria=criteria),
        }

        try:
            if response_model is not None:
                return self.client.system_one(
                    state,
                    questions,
                    model=model,
                    retry=retry,
                    timeout=timeout,
                    extra_headers=extra_headers,
                    extra_body=extra_body,
                    response_model=response_model,
                )

            result = self.client.system_one(
                state,
                questions,
                model=model,
                retry=retry,
                timeout=timeout,
                extra_headers=extra_headers,
                extra_body=extra_body,
                response_model=None,
            )
        except TypeSafeAPIError as error:
            print(error.status, error.request_id)
            raise

        return result.choices["match"].choice
