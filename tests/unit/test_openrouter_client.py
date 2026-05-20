from unittest.mock import Mock

from tooluniverse.llm_clients import OpenRouterClient


def test_openrouter_test_api_uses_supported_token_floor():
    client = OpenRouterClient.__new__(OpenRouterClient)
    client.model_name = "openai/gpt-5"
    client.logger = Mock()
    client.client = Mock()

    client.test_api()

    call_kwargs = client.client.chat.completions.create.call_args.kwargs
    assert call_kwargs["max_tokens"] == OpenRouterClient.MIN_TEST_MAX_TOKENS
