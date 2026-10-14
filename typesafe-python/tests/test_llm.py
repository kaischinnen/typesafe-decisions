import json
import os
import unittest
from unittest.mock import Mock, patch

import httpx2

import demo
from main import JevLib


class TestJevLibLlm(unittest.TestCase):
    @patch("demo.run_feel")
    @patch("demo.run_feel_llm")
    @patch("demo.JevLib")
    def test_demo_uses_ts_api_key_for_typesafe_client(
        self,
        jevlib: Mock,
        run_feel_llm: Mock,
        run_feel: Mock,
    ):
        typesafe_instance = jevlib.return_value.__enter__.return_value

        with patch("builtins.print"):
            demo.main()

        run_feel_llm.assert_called_once_with()
        jevlib.assert_called_once_with(api_key="TS_API_KEY")
        run_feel.assert_called_once_with(typesafe_instance)

    @patch.dict(os.environ, {"CF_GATEWAY_API_KEY": "gateway-token"}, clear=True)
    @patch("demo.JevLib.llm")
    def test_demo_passes_cloudflare_key_only_to_llm(self, llm: Mock):
        llm.return_value = "A short reply."

        with patch("builtins.print"):
            demo.run_feel_llm()

        llm.assert_called_once_with(
            "Draft a calm, helpful reply in one short sentence.",
            using="Please resolve my email immediately!",
            api_token="gateway-token",
        )

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account/id",
            "CF_API_TOKEN": "cloudflare-token",
        },
        clear=True,
    )
    @patch("main.httpx2.post")
    def test_sends_only_instruction_and_explicit_context(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {
            "success": True,
            "result": {"response": "  A short reply.  "},
        }
        post.return_value = response

        result = JevLib.__new__(JevLib).llm(
            "Write a short reply.",
            using={"message": "Hello", "private": False},
        )

        self.assertEqual(result, "A short reply.")
        response.raise_for_status.assert_called_once_with()
        post.assert_called_once()
        call = post.call_args
        self.assertEqual(
            call.args[0],
            "https://api.cloudflare.com/client/v4/accounts/account%2Fid/ai/run",
        )
        self.assertEqual(
            call.kwargs["headers"],
            {
                "Authorization": "Bearer cloudflare-token",
                "Content-Type": "application/json",
                "cf-aig-gateway-id": "default",
            },
        )
        self.assertEqual(
            json.loads(call.kwargs["json"]["input"]["messages"][1]["content"]),
            {
                "instruction": "Write a short reply.",
                "context": {"message": "Hello", "private": False},
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
    @patch("main.httpx2.post")
    def test_explicit_options_override_environment(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {
            "result": {
                "choices": [{"message": {"content": "Generated text"}}],
            },
        }
        post.return_value = response

        result = JevLib.llm(
            "Generate without context.",
            account_id="explicit-account",
            api_token="explicit-token",
            gateway_id="explicit-gateway",
            model="explicit-model",
            max_tokens=100,
            temperature=0.2,
            timeout=5.0,
        )

        self.assertEqual(result, "Generated text")
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
            {"instruction": "Generate without context."},
        )
        self.assertEqual(call.kwargs["json"]["input"]["max_tokens"], 100)
        self.assertEqual(call.kwargs["json"]["input"]["temperature"], 0.2)
        self.assertEqual(call.kwargs["timeout"], 5.0)

    @patch.dict(os.environ, {}, clear=True)
    def test_requires_cloudflare_configuration_only_when_called(self):
        with self.assertRaisesRegex(RuntimeError, r"\$CF_ACCOUNT_ID"):
            JevLib.llm("Hello")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account",
            "CF_API_TOKEN": "token",
        },
        clear=True,
    )
    @patch("main.httpx2.post")
    def test_rejects_unsuccessful_cloudflare_envelope(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {"success": False, "errors": []}
        post.return_value = response

        with self.assertRaisesRegex(
            RuntimeError,
            "Cloudflare rejected the model request",
        ):
            JevLib.llm("Hello")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account",
            "CF_API_TOKEN": "token",
        },
        clear=True,
    )
    @patch("main.httpx2.post")
    def test_explains_cloudflare_billing_failure(self, post: Mock):
        request = httpx2.Request("POST", "https://api.cloudflare.test/ai/run")
        post.return_value = httpx2.Response(402, request=request)

        with self.assertRaisesRegex(
            RuntimeError,
            r"Cloudflare model request failed \(402\).*configure billing",
        ):
            JevLib.llm("Hello")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account",
            "CF_API_TOKEN": "token",
        },
        clear=True,
    )
    @patch("main.httpx2.post")
    def test_rejects_missing_generated_text(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {"success": True, "result": {}}
        post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "Text model returned no text"):
            JevLib.llm("Hello")

    @patch.dict(
        os.environ,
        {
            "CF_ACCOUNT_ID": "account",
            "CF_API_TOKEN": "token",
        },
        clear=True,
    )
    @patch("main.httpx2.post")
    def test_rejects_oversized_generated_text(self, post: Mock):
        response = Mock(spec=httpx2.Response)
        response.json.return_value = {
            "success": True,
            "result": {"response": "x" * 12_001},
        }
        post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "oversized text"):
            JevLib.llm("Hello", max_tokens=20_000)


if __name__ == "__main__":
    unittest.main()
