import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import httpx2
from pydantic import BaseModel
from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient

from typesafe_decisions import DecisionClient


class MatchResponse(BaseModel):
    selected: str


def make_client() -> DecisionClient:
    decisions = DecisionClient.__new__(DecisionClient)
    decisions.client = Mock(spec=TypeSafeClient)
    return decisions


class TestDecisionClientMatch(unittest.TestCase):
    def test_returns_selected_label(self):
        decisions = make_client()
        selected_label = "option-b"
        decisions.client.system_one.return_value = SimpleNamespace(
            choices={"match": SimpleNamespace(choice=selected_label)},
        )

        selected = decisions.match(
            {"input": "test value"},
            "Select the matching option.",
            {
                "option-a": "First test criterion",
                "option-b": "Second test criterion",
            },
        )

        self.assertEqual(selected, selected_label)

    def test_builds_choice_and_forwards_system_one_options(self):
        decisions = make_client()
        decisions.client.system_one.return_value = SimpleNamespace(
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

        selected = decisions.match(
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
        decisions.client.system_one.assert_called_once_with(
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
        decisions = make_client()
        response = MatchResponse(selected="option-a")
        decisions.client.system_one.return_value = response

        result = decisions.match(
            "test input",
            "Choose an option.",
            {"option-a": "First criterion", "option-b": "Second criterion"},
            response_model=MatchResponse,
        )

        self.assertIs(result, response)
        self.assertIs(
            decisions.client.system_one.call_args.kwargs["response_model"],
            MatchResponse,
        )


if __name__ == "__main__":
    unittest.main()
