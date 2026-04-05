from __future__ import annotations
from typing import Any, Dict, List, Optional
import os
import time
import json as _json


class BaseLLMClient:
    def test_api(self) -> None:
        raise NotImplementedError

    def infer(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 5,
        retry_delay: int = 5,
    ) -> Optional[str]:
        raise NotImplementedError

    def infer_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 5,
        retry_delay: int = 5,
    ):
        """Default streaming implementation falls back to regular inference."""
        result = self.infer(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            return_json=return_json,
            custom_format=custom_format,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )
        if result is not None:
            yield result


class GeminiClient(BaseLLMClient):
    def __init__(self, model_name: str, logger):
        try:
            import google.generativeai as genai  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("google.generativeai not available") from e
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        self._genai = genai
        self._genai.configure(api_key=api_key)
        self.model_name = model_name
        self.logger = logger

    def _build_model(self):
        return self._genai.GenerativeModel(self.model_name)

    def test_api(self) -> None:
        model = self._build_model()
        model.generate_content(
            "ping",
            generation_config={
                "max_output_tokens": 8,
                "temperature": 0,
            },
        )

    def infer(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 5,
        retry_delay: int = 5,
    ) -> Optional[str]:
        if return_json:
            raise ValueError("Gemini JSON mode not supported here")
        contents = ""
        for m in messages:
            if m["role"] in ("user", "system"):
                contents += f"{m['content']}\n"
        retries = 0
        while retries < max_retries:
            try:
                gen_cfg: Dict[str, Any] = {
                    "temperature": (temperature if temperature is not None else 0)
                }
                if max_tokens is not None:
                    gen_cfg["max_output_tokens"] = max_tokens
                model = self._build_model()
                resp = model.generate_content(contents, generation_config=gen_cfg)
                return getattr(resp, "text", None) or getattr(resp, "candidates", [{}])[
                    0
                ].get("content")
            except Exception as e:  # noqa: BLE001
                self.logger.error(f"Gemini error: {e}")
                retries += 1
                time.sleep(retry_delay * retries)
        return None

    @staticmethod
    def _extract_text_from_stream_chunk(chunk) -> Optional[str]:
        if chunk is None:
            return None
        text = getattr(chunk, "text", None)
        if text:
            return text

        candidates = getattr(chunk, "candidates", None)
        if not candidates and isinstance(chunk, dict):
            candidates = chunk.get("candidates")
        if not candidates:
            return None

        candidate = candidates[0]
        content = getattr(candidate, "content", None)
        if content is None and isinstance(candidate, dict):
            content = candidate.get("content")
        if not content:
            return None

        parts = getattr(content, "parts", None)
        if parts is None and isinstance(content, dict):
            parts = content.get("parts")
        if parts and isinstance(parts, list):
            fragments: List[str] = []
            for part in parts:
                piece = getattr(part, "text", None)
                if piece is None and isinstance(part, dict):
                    piece = part.get("text")
                if piece:
                    fragments.append(piece)
            return "".join(fragments) if fragments else None

        final_text = getattr(content, "text", None)
        if final_text is None and isinstance(content, dict):
            final_text = content.get("text")
        return final_text

    def infer_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 5,
        retry_delay: int = 5,
    ):
        if return_json:
            raise ValueError("Gemini JSON mode not supported here")

        contents = ""
        for m in messages:
            if m["role"] in ("user", "system"):
                contents += f"{m['content']}\n"

        retries = 0
        while retries < max_retries:
            try:
                gen_cfg: Dict[str, Any] = {
                    "temperature": (temperature if temperature is not None else 0)
                }
                if max_tokens is not None:
                    gen_cfg["max_output_tokens"] = max_tokens

                model = self._build_model()
                stream = model.generate_content(
                    contents, generation_config=gen_cfg, stream=True
                )
                for chunk in stream:
                    text = self._extract_text_from_stream_chunk(chunk)
                    if text:
                        yield text
                return
            except Exception as e:  # noqa: BLE001
                self.logger.error(f"Gemini streaming error: {e}")
                retries += 1
                time.sleep(retry_delay * retries)

        yield from super().infer_stream(
            messages,
            temperature,
            max_tokens,
            return_json,
            custom_format,
            max_retries,
            retry_delay,
        )


class OpenRouterClient(BaseLLMClient):
    """
    OpenRouter client using OpenAI SDK with custom base URL.
    Supports models from OpenAI, Anthropic, Google, Qwen, and many other providers.
    """

    # Default model limits based on latest OpenRouter offerings
    DEFAULT_MODEL_LIMITS: Dict[str, Dict[str, int]] = {
        "openai/gpt-5": {"max_output": 128_000, "context_window": 400_000},
        "openai/gpt-5-codex": {"max_output": 128_000, "context_window": 400_000},
        "google/gemini-2.5-flash": {"max_output": 65_536, "context_window": 1_000_000},
        "google/gemini-2.5-pro": {"max_output": 65_536, "context_window": 1_000_000},
        "anthropic/claude-sonnet-4.5": {
            "max_output": 16_384,
            "context_window": 1_000_000,
        },
    }

    def __init__(self, model_id: str, logger):
        try:
            from openai import OpenAI as _OpenAI  # type: ignore
            import openai as _openai  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("openai client is not available") from e

        self._OpenAI = _OpenAI
        self._openai = _openai
        self.model_name = model_id
        self.logger = logger

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not set")

        # Optional headers for OpenRouter
        default_headers = {}
        if site_url := os.getenv("OPENROUTER_SITE_URL"):
            default_headers["HTTP-Referer"] = site_url
        if site_name := os.getenv("OPENROUTER_SITE_NAME"):
            default_headers["X-Title"] = site_name

        self.client = self._OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers=default_headers if default_headers else None,
        )

        # Load env overrides for model limits
        env_limits_raw = os.getenv("OPENROUTER_DEFAULT_MODEL_LIMITS")
        self._default_limits: Dict[str, Dict[str, int]] = (
            self.DEFAULT_MODEL_LIMITS.copy()
        )
        if env_limits_raw:
            try:
                env_limits = _json.loads(env_limits_raw)
                for k, v in env_limits.items():
                    if isinstance(v, dict):
                        base = self._default_limits.get(k, {}).copy()
                        base.update(
                            {
                                kk: int(vv)
                                for kk, vv in v.items()
                                if isinstance(vv, (int, float, str))
                            }
                        )
                        self._default_limits[k] = base
            except Exception:
                pass

    def _resolve_default_max_tokens(self, model_id: str) -> Optional[int]:
        """Resolve default max tokens for a model."""
        # Highest priority: explicit env per-model tokens mapping
        mapping_raw = os.getenv("OPENROUTER_MAX_TOKENS_BY_MODEL")
        mapping: Dict[str, Any] = {}
        if mapping_raw:
            try:
                mapping = _json.loads(mapping_raw)
            except Exception:
                mapping = {}

        if model_id in mapping:
            try:
                return int(mapping[model_id])
            except Exception:
                pass

        # Check for prefix match
        for k, v in mapping.items():
            try:
                if model_id.startswith(k):
                    return int(v)
            except Exception:
                continue

        # Next: built-in/default-limits map
        if model_id in self._default_limits:
            return int(self._default_limits[model_id].get("max_output", 0)) or None

        # Check for prefix match in default limits
        for k, v in self._default_limits.items():
            try:
                if model_id.startswith(k):
                    return int(v.get("max_output", 0)) or None
            except Exception:
                continue

        return None

    def test_api(self) -> None:
        """Test API connectivity with minimal token usage."""
        test_messages = [{"role": "user", "content": "ping"}]
        token_attempts = [1, 4, 16, 32]
        last_error: Optional[Exception] = None

        for tok in token_attempts:
            try:
                self.client.chat.completions.create(
                    model=self.model_name,
                    messages=test_messages,
                    max_tokens=tok,
                    temperature=0,
                )
                return
            except Exception as e:  # noqa: BLE001
                last_error = e
                msg = str(e).lower()
                if (
                    "max_tokens" in msg
                    or "model output limit" in msg
                    or "finish the message" in msg
                ) and tok != token_attempts[-1]:
                    continue
                break

        if last_error:
            raise ValueError(f"OpenRouter API test failed: {last_error}")
        raise ValueError("OpenRouter API test failed: unknown error")

    def infer(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 5,
        retry_delay: int = 5,
    ) -> Optional[str]:
        """Execute inference using OpenRouter."""
        retries = 0
        call_fn = (
            self.client.chat.completions.parse
            if custom_format is not None
            else self.client.chat.completions.create
        )

        response_format = (
            custom_format
            if custom_format is not None
            else ({"type": "json_object"} if return_json else None)
        )

        eff_max = (
            max_tokens
            if max_tokens is not None
            else self._resolve_default_max_tokens(self.model_name)
        )

        while retries < max_retries:
            try:
                kwargs: Dict[str, Any] = {
                    "model": self.model_name,
                    "messages": messages,
                }

                if response_format is not None:
                    kwargs["response_format"] = response_format
                if temperature is not None:
                    kwargs["temperature"] = temperature
                if eff_max is not None:
                    kwargs["max_tokens"] = eff_max

                resp = call_fn(**kwargs)

                if custom_format is not None:
                    return resp.choices[0].message.parsed.model_dump()
                return resp.choices[0].message.content

            except self._openai.RateLimitError:  # type: ignore[attr-defined]
                self.logger.warning(
                    f"Rate limit exceeded. Retrying in {retry_delay} seconds..."
                )
                retries += 1
                time.sleep(retry_delay * retries)
            except Exception as e:  # noqa: BLE001
                self.logger.error(f"OpenRouter error: {e}")
                import traceback

                traceback.print_exc()
                break

        self.logger.error("Max retries exceeded. Unable to complete the request.")
        return None


class VLLMClient(BaseLLMClient):
    def __init__(self, model_name: str, server_url: str, logger):
        try:
            from openai import OpenAI
        except Exception as e:
            raise RuntimeError("openai package not available for vLLM client") from e

        if not server_url:
            raise ValueError("VLLM_SERVER_URL must be provided")

        self.model_name = model_name
        # Ensure server_url ends with /v1 for OpenAI-compatible API
        if not server_url.endswith("/v1"):
            server_url = server_url.rstrip("/") + "/v1"
        self.server_url = server_url
        self.logger = logger

        self.client = OpenAI(
            api_key="EMPTY",
            base_url=self.server_url,
        )

    def test_api(self) -> None:
        test_messages = [{"role": "user", "content": "ping"}]
        try:
            self.client.chat.completions.create(
                model=self.model_name,
                messages=test_messages,
                max_tokens=8,
                temperature=0,
            )
        except Exception as e:
            raise ValueError(f"vLLM API test failed: {e}")

    def infer(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 5,
        retry_delay: int = 5,
    ) -> Optional[str]:
        if custom_format is not None:
            self.logger.warning("vLLM does not support custom format, ignoring")

        retries = 0
        while retries < max_retries:
            try:
                kwargs: Dict[str, Any] = {
                    "model": self.model_name,
                    "messages": messages,
                }

                if temperature is not None:
                    kwargs["temperature"] = temperature

                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens

                if return_json:
                    kwargs["response_format"] = {"type": "json_object"}

                resp = self.client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content

            except Exception as e:
                self.logger.error(f"vLLM error: {e}")
                retries += 1
                if retries < max_retries:
                    time.sleep(retry_delay * retries)

        self.logger.error("Max retries exceeded for vLLM request")
        return None


class OllamaClient(BaseLLMClient):
    """Ollama native client — calls /api/chat directly, no OpenAI SDK needed."""

    DEFAULT_SERVER_URL = "http://localhost:11434"

    def __init__(self, model_name: str, server_url: str | None, logger):
        import requests as _req

        self._requests = _req
        self.model_name = model_name
        self.server_url = (
            server_url or os.environ.get("OLLAMA_SERVER_URL", self.DEFAULT_SERVER_URL)
        ).rstrip("/")
        self.logger = logger

    def test_api(self) -> None:
        try:
            resp = self._requests.get(f"{self.server_url}/api/tags", timeout=5)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            if not any(self.model_name in m for m in models):
                raise ValueError(
                    f"Model '{self.model_name}' not found in Ollama. "
                    f"Available: {', '.join(models)}"
                )
        except self._requests.ConnectionError as e:
            raise ValueError(f"Ollama not reachable at {self.server_url}: {e}")

    def infer(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 3,
        retry_delay: int = 3,
    ) -> Optional[str]:
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
        }
        if temperature is not None:
            payload.setdefault("options", {})["temperature"] = temperature
        if max_tokens is not None:
            payload.setdefault("options", {})["num_predict"] = max_tokens
        if return_json:
            payload["format"] = "json"

        retries = 0
        while retries < max_retries:
            try:
                resp = self._requests.post(
                    f"{self.server_url}/api/chat",
                    json=payload,
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]
            except Exception as e:
                self.logger.error(f"Ollama error (attempt {retries + 1}): {e}")
                retries += 1
                if retries < max_retries:
                    time.sleep(retry_delay * retries)

        self.logger.error("Max retries exceeded for Ollama request")
        return None


class ClaudeCliClient(BaseLLMClient):
    """Claude Code CLI client — uses `claude --print` for subscription-free LLM calls."""

    def __init__(self, model_name: str, server_url: str | None, logger):
        import subprocess as _sp
        import shutil

        self._subprocess = _sp
        self.model_name = model_name or "sonnet"
        self.logger = logger
        self.timeout = int(os.environ.get("CLAUDE_CLI_TIMEOUT", "120"))
        self.budget = os.environ.get("CLAUDE_CLI_BUDGET", "0.10")
        claude_path = shutil.which("claude")
        if not claude_path:
            raise ValueError("claude CLI not found on PATH")
        self._claude_path: str = claude_path

    def test_api(self) -> None:
        try:
            result = self._subprocess.run(
                [self._claude_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise ValueError(f"claude --version failed: {result.stderr}")
        except self._subprocess.TimeoutExpired:
            raise ValueError("claude --version timed out")

    def infer(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 2,
        retry_delay: int = 3,
    ) -> Optional[str]:
        # Build the prompt from messages
        system_parts = []
        user_parts = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
            else:
                user_parts.append(msg["content"])

        prompt = "\n\n".join(user_parts)
        system_prompt = "\n\n".join(system_parts) if system_parts else None

        cmd = [
            self._claude_path,
            "--print",
            "--output-format",
            "json",
            "--model",
            self.model_name,
            "--fallback-model",
            "haiku",
            "--max-budget-usd",
            self.budget,
            "--no-session-persistence",
            "--permission-mode",
            "auto",
        ]
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        retries = 0
        while retries < max_retries:
            try:
                result = self._subprocess.run(
                    cmd,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                if result.returncode != 0:
                    self.logger.error(f"claude CLI error: {result.stderr[:500]}")
                    retries += 1
                    if retries < max_retries:
                        time.sleep(retry_delay)
                    continue

                # Parse JSON output — extract the result field
                response = _json.loads(result.stdout)
                content = response.get("result", "")
                cost = response.get("cost_usd", 0)
                self.logger.info(f"Claude CLI cost: ${cost:.4f}")
                return self._strip_markdown_fences(content)

            except self._subprocess.TimeoutExpired:
                self.logger.error(f"claude CLI timed out after {self.timeout}s")
                retries += 1
                if retries < max_retries:
                    time.sleep(retry_delay)
            except (_json.JSONDecodeError, KeyError) as e:
                self.logger.error(f"claude CLI parse error: {e}")
                retries += 1
                if retries < max_retries:
                    time.sleep(retry_delay)

        self.logger.error("Max retries exceeded for Claude CLI")
        return None

    def infer_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        return_json: bool,
        custom_format: Any = None,
        max_retries: int = 2,
        retry_delay: int = 3,
    ):
        """Yield text chunks via claude --print --output-format stream-json."""
        system_parts = []
        user_parts = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
            else:
                user_parts.append(msg["content"])

        prompt = "\n\n".join(user_parts)
        system_prompt = "\n\n".join(system_parts) if system_parts else None

        cmd = [
            self._claude_path,
            "--print",
            "--output-format",
            "stream-json",
            "--model",
            self.model_name,
            "--fallback-model",
            "haiku",
            "--max-budget-usd",
            self.budget,
            "--no-session-persistence",
            "--permission-mode",
            "auto",
        ]
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        proc = self._subprocess.Popen(
            cmd,
            stdin=self._subprocess.PIPE,
            stdout=self._subprocess.PIPE,
            stderr=self._subprocess.PIPE,
            text=True,
        )
        assert proc.stdin is not None
        proc.stdin.write(prompt)
        proc.stdin.close()

        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = _json.loads(line)
                if event.get("type") == "assistant" and "message" in event:
                    yield event["message"]
            except _json.JSONDecodeError:
                continue

        proc.wait(timeout=10)

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Strip ```json ... ``` fences that Claude often wraps around JSON output."""
        import re

        stripped = text.strip()
        match = re.match(r"^```(?:json)?\s*\n(.*?)```\s*$", stripped, re.DOTALL)
        return match.group(1).strip() if match else stripped
