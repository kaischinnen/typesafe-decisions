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
    """Make semantic decisions with TypeSafe System One.

    Args:
        api_key_env: Name of the environment variable containing the TypeSafe
            API key. Defaults to ``TYPESAFE_API_KEY``. This is a variable name,
            not the API key itself.
        model: Default TypeSafe model passed to the underlying client.
        retry: Default retry policy passed to the underlying client.
        timeout: Default request timeout passed to the underlying client.
        headers: Default HTTP headers passed to the underlying client.
        transport: Optional HTTP transport used by the underlying client.
        http_client: Optional preconfigured HTTP client.
        base_url: Optional TypeSafe API base URL.

    Raises:
        RuntimeError: If the selected API-key environment variable is missing
            or empty.

    Notes:
        Use the client as a context manager so its HTTP resources are closed
        after use.
    """

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
        """Measure how strongly a state satisfies a semantic question.

        Args:
            state: Text or JSON-compatible data to evaluate.
            question: The property to measure, for example whether the state
                needs an urgent reply.
            model: Model override for this request.
            retry: Retry-policy override for this request.
            timeout: Timeout override for this request.
            extra_headers: Additional HTTP headers for this request.
            extra_body: Additional JSON fields for this request.

        Returns:
            The score returned for the question by TypeSafe System One.

        Raises:
            TypeSafeAPIError: If the TypeSafe request fails. The exception is
                re-raised unchanged after its status and request ID are printed.
        """
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

        Args:
            state: Text or JSON-compatible data to classify.
            question: The decision instruction sent to TypeSafe.
            criteria: Mapping of returned labels to their semantic definitions.
                A definition may be ``None`` when the label is self-explanatory.
            model: Model override for this request.
            retry: Retry-policy override for this request.
            timeout: Timeout override for this request.
            extra_headers: Additional HTTP headers for this request.
            extra_body: Additional JSON fields for this request.
            response_model: Optional Pydantic model describing the System One
                response body.

        Returns:
            The selected criterion label. If ``response_model`` is provided,
            the parsed model instance returned by the SDK is returned unchanged.

        Raises:
            TypeSafeAPIError: If the TypeSafe request fails. The exception is
                re-raised unchanged after its status and request ID are printed.
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
