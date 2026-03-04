"""Test modelrelay package."""

import pytest
from modelrelay.scores import SCORES, get_score, canonicalize_model_id
from modelrelay.sources import SOURCES, MODELS, get_available_models, get_best_model


def test_scores_exist():
    """Test that scores are defined."""
    assert len(SCORES) > 0
    assert "meta-llama/llama-3.3-70b-instruct" in SCORES


def test_canonicalize_model_id():
    """Test model ID canonicalization."""
    assert canonicalize_model_id("model-name:free") == "model-name"
    assert canonicalize_model_id("model-name") == "model-name"
    assert canonicalize_model_id("provider/model:v1") == "provider/model"


def test_get_score():
    """Test score lookup."""
    score = get_score("meta-llama/llama-3.3-70b-instruct")
    assert score is not None
    assert 0 <= score <= 1

    # Unknown model
    assert get_score("unknown-model-xyz") is None


def test_sources_exist():
    """Test that sources are defined."""
    assert len(SOURCES) > 0
    assert "nvidia" in SOURCES
    assert "groq" in SOURCES


def test_models_flattened():
    """Test that models are properly flattened."""
    assert len(MODELS) > 0

    # Check that models have required fields
    for model in MODELS[:5]:
        assert model.model_id
        assert model.display_name
        assert model.context
        assert model.provider
        assert model.url


def test_get_available_models():
    """Test model filtering."""
    all_models = get_available_models()
    assert len(all_models) > 0

    # Filter by provider
    nvidia_models = get_available_models(provider="nvidia")
    assert len(nvidia_models) > 0
    assert all(m.provider == "nvidia" for m in nvidia_models)

    # Filter by score
    high_score = get_available_models(min_score=0.5)
    assert all(m.score is not None and m.score >= 0.5 for m in high_score)


def test_get_best_model():
    """Test best model selection."""
    best = get_best_model()
    assert best is not None
    assert best.score is not None

    # Best from specific provider
    best_groq = get_best_model(provider="groq")
    assert best_groq is not None
    assert best_groq.provider == "groq"


@pytest.mark.asyncio
async def test_router_init():
    """Test router initialization."""
    from modelrelay.router import ModelRouter, RouterConfig

    config = RouterConfig(timeout_seconds=10.0)
    router = ModelRouter(config)

    assert router.config.timeout_seconds == 10.0

    await router.close()


@pytest.mark.asyncio
async def test_router_check_provider():
    """Test provider checking."""
    from modelrelay.router import ModelRouter

    router = ModelRouter()

    # Check a provider (may fail if no network)
    status = await router.check_provider("groq")

    assert status.name == "groq"
    assert status.url
    assert status.last_check is not None

    await router.close()
