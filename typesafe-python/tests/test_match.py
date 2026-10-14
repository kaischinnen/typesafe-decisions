import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import httpx2
from pydantic import BaseModel
from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient

from main import JevLib


class MatchResponse(BaseModel):
    selected: str


def make_jevlib() -> JevLib:
    jevlib = JevLib.__new__(JevLib)
    jevlib.client = Mock(spec=TypeSafeClient)
    return jevlib


class TestJevLibMatch(unittest.TestCase):
    def test_returns_selected_label(self):
        jevlib = make_jevlib()
        selected_label = "option-b"
        jevlib.client.system_one.return_value = SimpleNamespace(
            choices={"match": SimpleNamespace(choice=selected_label)},
        )

        selected = jevlib.match(
            {"input": "test value"},
            "Select the matching option.",
            {
                "option-a": "First test criterion",
                "option-b": "Second test criterion",
            },
        )

        self.assertEqual(selected, selected_label)

    def test_builds_choice_and_forwards_system_one_options(self):
        jevlib = make_jevlib()
        jevlib.client.system_one.return_value = SimpleNamespace(
            choices={"match": SimpleNamespace(choice="option-b")},
        )
        state = {"record": {"value": "fixture"}}
        question = {"task": "Choose the matching option"}
        criteria = {
            "option-a": {"matches": ["first", "primary"]},
            "option-b": None,
        }
        retry = RetryPolicy(max_retries=0)
        timeout = httpx2.Timeout(5.0)
        extra_headers = {"x-trace-id": "match-test"}
        extra_body = {"metadata": {"source": "unit-test"}}

        selected = jevlib.match(
            state,
            question,
            criteria,
            model="jev-latest",
            retry=retry,
            timeout=timeout,
            extra_headers=extra_headers,
            extra_body=extra_body,
        )

        self.assertEqual(selected, "option-b")
        jevlib.client.system_one.assert_called_once_with(
            state,
            {
                "match": Choice(
                    instructions=question,
                    criteria=criteria,
                ),
            },
            model="jev-latest",
            retry=retry,
            timeout=timeout,
            extra_headers=extra_headers,
            extra_body=extra_body,
            response_model=None,
        )

    def test_returns_custom_response_model_unchanged(self):
        jevlib = make_jevlib()
        response = MatchResponse(selected="option-a")
        jevlib.client.system_one.return_value = response

        result = jevlib.match(
            "test input",
            "Choose an option.",
            {"option-a": "First criterion", "option-b": "Second criterion"},
            response_model=MatchResponse,
        )

        self.assertIs(result, response)
        self.assertIs(
            jevlib.client.system_one.call_args.kwargs["response_model"],
            MatchResponse,
        )


if __name__ == "__main__":
    unittest.main()
