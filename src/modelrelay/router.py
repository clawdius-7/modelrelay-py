"""
Model router - intelligently routes requests to best available model.
"""

import asyncio
import time
from typing import Any
from dataclasses import dataclass, field

import httpx

from modelrelay.sources import ModelInfo, get_available_models, get_best_model


@dataclass
class ProviderStatus:
    """Status of a provider."""

    name: str
    url: str
    available: bool = False
    latency_ms: float | None = None
    last_check: float | None = None
    error: str | None = None


@dataclass
class RouterConfig:
    """Configuration for the model router."""

    timeout_seconds: float = 30.0
    check_timeout_seconds: float = 5.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    cache_ttl_seconds: float = 60.0
    min_score: float | None = None
    preferred_provider: str | None = None


class ModelRouter:
    """
    Intelligent model router.

    Routes requests to the best available model based on:
    - Model quality scores
    - Provider availability
    - Latency
    """

    def __init__(self, config: RouterConfig | None = None):
        self.config = config or RouterConfig()
        self._provider_status: dict[str, ProviderStatus] = {}
        self._status_cache_time: float = 0
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout_seconds)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def check_provider(self, provider_key: str) -> ProviderStatus:
        """Check if a provider is available."""
        from modelrelay.sources import SOURCES

        provider = SOURCES.get(provider_key)
        if not provider:
            return ProviderStatus(
                name=provider_key, url="", available=False, error="Unknown provider"
            )

        url = provider["url"]
        status = ProviderStatus(name=provider_key, url=url)

        try:
            client = await self._get_client()
            start = time.time()

            # Simple health check - just check if endpoint responds
            # Some providers may not have a dedicated health endpoint
            response = await client.options(url, timeout=self.config.check_timeout_seconds)

            elapsed = (time.time() - start) * 1000
            status.available = response.status_code < 500
            status.latency_ms = elapsed
            status.last_check = time.time()

        except httpx.TimeoutException:
            status.available = False
            status.error = "Timeout"
            status.last_check = time.time()

        except Exception as e:
            status.available = False
            status.error = str(e)
            status.last_check = time.time()

        self._provider_status[provider_key] = status
        return status

    async def check_all_providers(self) -> dict[str, ProviderStatus]:
        """Check all providers for availability."""
        from modelrelay.sources import SOURCES

        tasks = [self.check_provider(pk) for pk in SOURCES.keys()]
        await asyncio.gather(*tasks)
        self._status_cache_time = time.time()
        return self._provider_status

    def is_cache_valid(self) -> bool:
        """Check if provider status cache is still valid."""
        if self._status_cache_time == 0:
            return False
        elapsed = time.time() - self._status_cache_time
        return elapsed < self.config.cache_ttl_seconds

    async def get_best_available_model(
        self,
        provider: str | None = None,
        exclude: list[str] | None = None,
        force_check: bool = False,
    ) -> ModelInfo | None:
        """Get the best available model."""
        # Check provider status if needed
        if force_check or not self.is_cache_valid():
            await self.check_all_providers()

        # Filter available providers
        available_providers = [
            k for k, v in self._provider_status.items() if v.available
        ]

        if not available_providers:
            # Fallback: return best scored model regardless of availability
            return get_best_model(provider=provider, exclude=exclude)

        # Get best model from available providers
        models = get_available_models(provider=provider)

        if exclude:
            models = [m for m in models if m.model_id not in exclude]

        # Filter to available providers
        models = [m for m in models if m.provider in available_providers]

        if self.config.min_score is not None:
            models = [m for m in models if m.score and m.score >= self.config.min_score]

        if not models:
            return None

        # Sort by score and return best
        scored = [m for m in models if m.score is not None]
        if scored:
            scored.sort(key=lambda m: m.score, reverse=True)  # type: ignore
            return scored[0]

        return models[0]

    async def route_request(
        self,
        messages: list[dict],
        model: str | None = None,
        exclude: list[str] | None = None,
        max_fallbacks: int = 3,
        **kwargs,
    ) -> dict[str, Any]:
        """Route a chat completion request to the best available model with fallback chain."""
        from modelrelay.sources import SOURCES

        tried_models = exclude or []
        last_error = None

        for attempt in range(max_fallbacks):
            # Determine which model to use
            if model and attempt == 0:
                # First attempt: use specified model
                target_model = None
                for m in get_available_models():
                    if m.model_id == model:
                        target_model = m
                        break
                if not target_model:
                    raise ValueError(f"Unknown model: {model}")
            else:
                # Fallback: auto-select best available (excluding tried)
                target_model = await self.get_best_available_model(exclude=tried_models)
                if not target_model:
                    if last_error:
                        raise RuntimeError(f"All fallbacks exhausted. Last error: {last_error}")
                    raise RuntimeError("No models available")

            tried_models.append(target_model.model_id)

            # Get provider URL
            provider = SOURCES.get(target_model.provider)
            if not provider:
                raise RuntimeError(f"Unknown provider: {target_model.provider}")

            url = provider["url"]

            # Build request payload
            payload = {
                "model": target_model.model_id,
                "messages": messages,
                **kwargs,
            }

            # Make request with retries
            client = await self._get_client()

            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                last_error = f"{target_model.model_id}: HTTP {e.response.status_code}"
                # Continue to next fallback
                continue

            except httpx.TimeoutException:
                last_error = f"{target_model.model_id}: Timeout"
                # Continue to next fallback
                continue

            except Exception as e:
                last_error = f"{target_model.model_id}: {str(e)}"
                # Continue to next fallback
                continue

        raise RuntimeError(f"Request failed after {max_fallbacks} fallbacks: {last_error}")
