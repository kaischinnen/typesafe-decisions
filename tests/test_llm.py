import json
import os
import unittest
from unittest.mock import Mock, patch

import httpx2

from typesafe_decisions import llm


class TestLlm(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "test/account",
            "CF_API_TOKEN": "test-token",
        },
        clear=True,
    )
    @patch("typesafe_decisions.cloudflare.httpx2.post")
    def test_sends_only_instruction_and_explicit_context(self, post: Mock):
        instruction = "Transform the supplied test data."
        context = {"value": "fixture", "enabled": True}
        generated_text = "Generated from the fixture."
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {
            "success": True,
            "result": {"response": f"  {generated_text}  "},
        }
        post.return_value = response

        result = llm(instruction, using=context)

        self.assertEqual(result, generated_text)
        response.raise_for_status.assert_called_once_with()
        post.assert_called_once()
        call = post.call_args
        self.assertEqual(
            call.args[0],
            "https://api.cloudflare.com/client/v4/accounts/test%2Faccount/ai/run",
        )
        self.assertEqual(
            call.kwargs["headers"],
            {
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json",
                "cf-aig-gateway-id": "default",
            },
        )
        self.assertEqual(
            json.loads(call.kwargs["json"]["input"]["messages"][1]["content"]),
            {
                "instruction": instruction,
                "context": context,
            },
        )
        self.assertEqual(call.kwargs["json"]["input"]["max_tokens"], 300)
        self.assertEqual(call.kwargs["json"]["input"]["temperature"], 0.9)
        self.assertEqual(call.kwargs["timeout"], 25.0)

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "environment-account",
            "CF_API_TOKEN": "environment-token",
            "GATEWAY_ID": "environment-gateway",
            "TEXT_MODEL": "environment-model",
        },
        clear=True,
    )
    @patch("typesafe_decisions.cloudflare.httpx2.post")
    def test_explicit_options_override_environment(self, post: Mock):
        instruction = "Produce test output."
        generated_text = "Test output"
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {
            "result": {
                "choices": [{"message": {"content": generated_text}}],
            },
        }
        post.return_value = response

        result = llm(
            instruction,
            account_id="explicit-account",
            api_token="explicit-token",
            gateway_id="explicit-gateway",
            model="explicit-model",
            max_tokens=100,
            temperature=0.2,
            timeout=5.0,
        )

        self.assertEqual(result, generated_text)
        call = post.call_args
        self.assertIn("explicit-account", call.args[0])
        self.assertEqual(
            call.kwargs["headers"]["Authorization"],
            "Bearer explicit-token",
        )
        self.assertEqual(
            call.kwargs["headers"]["cf-aig-gateway-id"],
            "explicit-gateway",
        )
        self.assertEqual(call.kwargs["json"]["model"], "explicit-model")
        self.assertEqual(
            json.loads(call.kwargs["json"]["input"]["messages"][1]["content"]),
            {"instruction": instruction},
        )
        self.assertEqual(call.kwargs["json"]["input"]["max_tokens"], 100)
        self.assertEqual(call.kwargs["json"]["input"]["temperature"], 0.2)
        self.assertEqual(call.kwargs["timeout"], 5.0)

    @patch.dict(os.environ, {}, clear=True)
    def test_requires_cloudflare_configuration_only_when_called(self):
        with self.assertRaisesRegex(RuntimeError, r"\$CF_ACCOUNT_ID"):
            llm("Hello")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account",
            "CF_API_TOKEN": "token",
        },
        clear=True,
    )
    @patch("typesafe_decisions.cloudflare.httpx2.post")
    def test_rejects_unsuccessful_cloudflare_envelope(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {"success": False, "errors": []}
        post.return_value = response

        with self.assertRaisesRegex(
            RuntimeError,
            "Cloudflare rejected the model request",
        ):
            llm("Hello")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "test-account",
            "CF_API_TOKEN": "test-token",
        },
        clear=True,
    )
    @patch("typesafe_decisions.cloudflare.httpx2.post")
    def test_rejects_invalid_json_response(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.side_effect = ValueError("invalid test response")
        post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "returned invalid JSON"):
            llm("Test instruction")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "test-account",
            "CF_API_TOKEN": "test-token",
        },
        clear=True,
    )
    @patch("typesafe_decisions.cloudflare.httpx2.post")
    def test_rejects_empty_generated_text(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {
            "success": True,
            "result": {"response": "   "},
        }
        post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "returned no text"):
            llm("Test instruction")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account",
            "CF_API_TOKEN": "token",
        },
        clear=True,
    )
    @patch("typesafe_decisions.cloudflare.httpx2.post")
    def test_explains_cloudflare_billing_failure(self, post: Mock):
        request = httpx2.Request("POST", "https://api.cloudflare.test/ai/run")
        post.return_value = httpx2.Response(402, request=request)

        with self.assertRaisesRegex(
            RuntimeError,
            r"Cloudflare model request failed \(402\).*configure billing",
        ):
            llm("Hello")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account",
            "CF_API_TOKEN": "token",
        },
        clear=True,
    )
    @patch("typesafe_decisions.cloudflare.httpx2.post")
    def test_rejects_missing_generated_text(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {"success": True, "result": {}}
        post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "Text model returned no text"):
            llm("Hello")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account",
            "CF_API_TOKEN": "token",
        },
        clear=True,
    )
    @patch("typesafe_decisions.cloudflare.httpx2.post")
    def test_rejects_oversized_generated_text(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {
            "success": True,
            "result": {"response": "x" * 12_001},
        }
        post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "oversized text"):
            llm("Hello", max_tokens=20_000)


if __name__ == "__main__":
    unittest.main()
