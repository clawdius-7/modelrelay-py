"""
Model sources for AI availability checking.

Defines providers and their available models with context window sizes.
"""

from dataclasses import dataclass
from modelrelay.scores import get_score


@dataclass
class ModelInfo:
    """Information about a specific model."""

    model_id: str
    display_name: str
    context: str  # e.g., "128k", "256k"
    provider: str
    url: str
    score: float | None


# Provider configurations
SOURCES: dict[str, dict] = {
    "nvidia": {
        "name": "NIM",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "models": [
            ["deepseek-ai/deepseek-v3.2", "DeepSeek V3.2", "128k"],
            ["moonshotai/kimi-k2.5", "Kimi K2.5", "128k"],
            ["z-ai/glm5", "GLM 5", "128k"],
            ["z-ai/glm4.7", "GLM 4.7", "200k"],
            ["moonshotai/kimi-k2-thinking", "Kimi K2 Thinking", "256k"],
            ["minimaxai/minimax-m2.1", "MiniMax M2.1", "200k"],
            ["stepfun-ai/step-3.5-flash", "Step 3.5 Flash", "256k"],
            ["qwen/qwen3-coder-480b-a35b-instruct", "Qwen3 Coder 480B", "256k"],
            ["qwen/qwen3-235b-a22b", "Qwen3 235B", "128k"],
            ["mistralai/devstral-2-123b-instruct-2512", "Devstral 2 123B", "256k"],
            ["deepseek-ai/deepseek-v3.1-terminus", "DeepSeek V3.1 Terminus", "128k"],
            ["moonshotai/kimi-k2-instruct", "Kimi K2 Instruct", "128k"],
            ["minimaxai/minimax-m2", "MiniMax M2", "128k"],
            ["qwen/qwen3-next-80b-a3b-thinking", "Qwen3 80B Thinking", "128k"],
            ["qwen/qwen3-next-80b-a3b-instruct", "Qwen3 80B Instruct", "128k"],
            ["qwen/qwen3.5-397b-a17b", "Qwen3.5 400B", "128k"],
            ["openai/gpt-oss-120b", "GPT OSS 120B", "128k"],
            ["meta/llama-4-maverick-17b-128e-instruct", "Llama 4 Maverick", "1M"],
            ["deepseek-ai/deepseek-v3.1", "DeepSeek V3.1", "128k"],
            ["nvidia/llama-3.1-nemotron-ultra-253b-v1", "Nemotron Ultra 253B", "128k"],
            ["mistralai/mistral-large-3-675b-instruct-2512", "Mistral Large 675B", "256k"],
            ["qwen/qwq-32b", "QwQ 32B", "131k"],
            ["mistralai/mistral-medium-3-instruct", "Mistral Medium 3", "128k"],
            ["nvidia/llama-3.3-nemotron-super-49b-v1.5", "Nemotron Super 49B", "128k"],
            ["meta/llama-4-scout-17b-16e-instruct", "Llama 4 Scout", "10M"],
            ["meta/llama-3.3-70b-instruct", "Llama 3.3 70B", "128k"],
            ["deepseek-ai/deepseek-r1-distill-qwen-32b", "R1 Distill 32B", "128k"],
            ["qwen/qwen2.5-coder-32b-instruct", "Qwen2.5 Coder 32B", "32k"],
        ],
    },
    "groq": {
        "name": "Groq",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "models": [
            ["llama-3.3-70b-versatile", "Llama 3.3 70B", "128k"],
            ["meta-llama/llama-4-scout-17b-16e-preview", "Llama 4 Scout", "10M"],
            ["meta-llama/llama-4-maverick-17b-128e-preview", "Llama 4 Maverick", "1M"],
            ["deepseek-r1-distill-llama-70b", "R1 Distill 70B", "128k"],
            ["qwen-qwq-32b", "QwQ 32B", "131k"],
            ["moonshotai/kimi-k2-instruct", "Kimi K2 Instruct", "131k"],
            ["llama-3.1-8b-instant", "Llama 3.1 8B", "128k"],
        ],
    },
    "cerebras": {
        "name": "Cerebras",
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "models": [
            ["llama3.3-70b", "Llama 3.3 70B", "128k"],
            ["llama-4-scout-17b-16e-instruct", "Llama 4 Scout", "10M"],
            ["qwen-3-32b", "Qwen3 32B", "128k"],
            ["llama3.1-8b", "Llama 3.1 8B", "128k"],
            ["glm-4.6", "GLM 4.6", "128k"],
        ],
    },
    "openrouter": {
        "name": "OpenRouter",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "models": [
            ["qwen/qwen3-coder:free", "Qwen3 Coder", "256k"],
            ["stepfun/step-3.5-flash:free", "Step 3.5 Flash", "256k"],
            ["deepseek/deepseek-r1-0528:free", "DeepSeek R1 0528", "128k"],
            ["openai/gpt-oss-120b:free", "GPT OSS 120B", "128k"],
            ["meta-llama/llama-3.3-70b-instruct:free", "Llama 3.3 70B", "128k"],
            ["minimax/minimax-m2.5:free", "MiniMax M2.5", "128k"],
            ["anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet", "200k"],
            ["openai/gpt-4o", "GPT-4o", "128k"],
            ["google/gemini-2.5-pro-preview", "Gemini 2.5 Pro", "1M"],
            ["x-ai/grok-2-1212", "Grok 2", "131k"],
        ],
    },
    "codestral": {
        "name": "Codestral",
        "url": "https://codestral.mistral.ai/v1/chat/completions",
        "models": [
            ["codestral-latest", "Codestral", "256k"],
        ],
    },
    "scaleway": {
        "name": "Scaleway",
        "url": "https://api.scaleway.ai/v1/chat/completions",
        "models": [
            ["devstral-2-123b-instruct-2512", "Devstral 2 123B", "256k"],
            ["llama-3.3-70b-instruct", "Llama 3.3 70B", "128k"],
            ["mistral-small-3.2-24b-instruct-2506", "Mistral Small 3.2", "128k"],
        ],
    },
    "googleai": {
        "name": "Google AI",
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "models": [
            ["gemma-3-27b-it", "Gemma 3 27B", "128k"],
            ["gemma-3-12b-it", "Gemma 3 12B", "128k"],
            ["gemma-3-4b-it", "Gemma 3 4B", "128k"],
        ],
    },
    "cohere": {
        "name": "Cohere",
        "url": "https://api.cohere.ai/v2/chat/completions",
        "models": [
            ["command-r7b-12-2024", "Command R7B", "128k"],
            ["command-r-plus", "Command R+", "128k"],
        ],
    },
    "together": {
        "name": "Together AI",
        "url": "https://api.together.xyz/v1/chat/completions",
        "models": [
            ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "Llama 3.3 70B", "128k"],
            ["Qwen/Qwen2.5-72B-Instruct-Turbo", "Qwen2.5 72B", "128k"],
            ["deepseek-ai/DeepSeek-V3", "DeepSeek V3", "128k"],
        ],
    },
    "fireworks": {
        "name": "Fireworks AI",
        "url": "https://api.fireworks.ai/inference/v1/chat/completions",
        "models": [
            ["accounts/fireworks/models/llama-v3p3-70b-instruct", "Llama 3.3 70B", "128k"],
            ["accounts/fireworks/models/qwen2p5-72b-instruct", "Qwen2.5 72B", "128k"],
        ],
    },
}


def _build_models() -> list[ModelInfo]:
    """Build flattened list of all models from all providers."""
    result = []
    seen = set()  # Track unique (provider, model_id) pairs
    for provider_key, provider in SOURCES.items():
        url = provider["url"]
        for model in provider.get("models", []):
            model_id, display_name, context = model
            key = (provider_key, model_id)
            if key in seen:
                continue  # Skip duplicate
            seen.add(key)
            score = get_score(model_id)
            result.append(
                ModelInfo(
                    model_id=model_id,
                    display_name=display_name,
                    context=context,
                    provider=provider_key,
                    url=url,
                    score=score,
                )
            )
    return result


# Pre-built list of all models
MODELS = _build_models()


def get_available_models(
    provider: str | None = None, min_score: float | None = None
) -> list[ModelInfo]:
    """Get available models, optionally filtered by provider and minimum score."""
    models = MODELS

    if provider:
        models = [m for m in models if m.provider == provider]

    if min_score is not None:
        models = [m for m in models if m.score is not None and m.score >= min_score]

    return models


def get_best_model(
    provider: str | None = None, exclude: list[str] | None = None
) -> ModelInfo | None:
    """Get the highest-scored model, optionally filtered by provider."""
    models = get_available_models(provider=provider)

    if exclude:
        models = [m for m in models if m.model_id not in exclude]

    if not models:
        return None

    # Sort by score descending
    scored_models = [m for m in models if m.score is not None]
    if not scored_models:
        return models[0]

    scored_models.sort(key=lambda m: m.score, reverse=True)
    return scored_models[0]
