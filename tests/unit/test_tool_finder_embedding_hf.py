"""Tests for Hugging Face Inference API backend in ToolFinderEmbedding (Option D).

Contract: with embedding_backend: "huggingface" in the tool config and HF_TOKEN
set, ToolFinderEmbedding must select the hosted HF provider (already supported
by database_setup.Embedder) instead of rejecting it and falling back to the
local SentenceTransformer model.
"""

import pytest


class TestHuggingFaceBackend:
    @pytest.fixture
    def config(self):
        return {
            "name": "ToolFinderEmbedding",
            "type": "ToolFinderEmbedding",
            "configs": {
                "embedding_backend": "huggingface",
                "tool_finder_model": "sentence-transformers/all-MiniLM-L6-v2",
            },
        }

    def test_hf_backend_selected_when_configured(self, monkeypatch, config):
        """HF provider must be selected when embedding_backend=huggingface and
        HF_TOKEN is present -- the gate in __init__ must accept it."""
        monkeypatch.setenv("HF_TOKEN", "test-hf-token")
        # No local model, no network: hosted path only builds an Embedder client.
        from tooluniverse.tool_finder_embedding import ToolFinderEmbedding

        # Avoid loading tool embeddings (would need a ToolUniverse instance).
        monkeypatch.setattr(
            ToolFinderEmbedding, "load_tool_desc_embedding", lambda self, *a, **k: None
        )
        finder = ToolFinderEmbedding(config, tooluniverse=None)
        assert finder._embed_provider == "huggingface"
        assert finder.use_openai_embedding is True

    def test_hf_token_required_fails_loudly(self, monkeypatch, config):
        """Explicit huggingface config without HF_TOKEN must fail loudly at
        Embedder construction -- never silently fall back to a local model
        (a configured backend that cannot run is a config error)."""
        monkeypatch.delenv("HF_TOKEN", raising=False)
        from tooluniverse.tool_finder_embedding import ToolFinderEmbedding

        monkeypatch.setattr(
            ToolFinderEmbedding, "load_tool_desc_embedding", lambda self, *a, **k: None
        )
        with pytest.raises(RuntimeError, match="HF_TOKEN"):
            ToolFinderEmbedding(config, tooluniverse=None)
