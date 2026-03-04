"""
HTTP server for modelrelay.

Provides an OpenAI-compatible API for model routing.
"""

import json
import time
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from modelrelay.router import ModelRouter, RouterConfig


# Request models
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: list[ChatMessage]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[list[str]] = None


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "modelrelay"


class ModelsResponse(BaseModel):
    object: str = "list"
    data: list[ModelInfo]


# Global router instance
_router: Optional[ModelRouter] = None
_config: Optional[RouterConfig] = None


def create_app(config: Optional[RouterConfig] = None) -> FastAPI:
    """Create the FastAPI application."""
    global _router, _config

    _config = config or RouterConfig()
    _router = ModelRouter(_config)

    app = FastAPI(
        title="ModelRelay",
        description="Intelligent LLM Model Routing - OpenAI-compatible API",
        version="0.1.0",
    )

    @app.on_event("startup")
    async def startup():
        """Check providers on startup."""
        await _router.check_all_providers()

    @app.on_event("shutdown")
    async def shutdown():
        """Clean up resources."""
        await _router.close()

    @app.get("/")
    async def root():
        return {
            "name": "ModelRelay",
            "version": "0.1.0",
            "status": "running",
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.get("/v1/models")
    async def list_models():
        """List available models."""
        from modelrelay.sources import MODELS

        models = [
            ModelInfo(id=m.model_id, owned_by=m.provider)
            for m in MODELS
        ]
        return ModelsResponse(data=models)

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatCompletionRequest):
        """Handle chat completion requests."""
        global _router

        if not _router:
            raise HTTPException(status_code=503, detail="Router not initialized")

        # Convert messages
        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        # Build kwargs
        kwargs: dict[str, Any] = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            kwargs["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            kwargs["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            kwargs["presence_penalty"] = request.presence_penalty
        if request.stop:
            kwargs["stop"] = request.stop

        try:
            result = await _router.route_request(
                messages=messages,
                model=request.model,
                **kwargs,
            )
            return JSONResponse(content=result)

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))

    @app.get("/providers/status")
    async def provider_status():
        """Get provider status."""
        global _router

        if not _router:
            raise HTTPException(status_code=503, detail="Router not initialized")

        status = {}
        for key, s in _router._provider_status.items():
            status[key] = {
                "available": s.available,
                "latency_ms": s.latency_ms,
                "last_check": s.last_check,
                "error": s.error,
            }
        return status

    @app.post("/providers/check")
    async def check_providers():
        """Force provider check."""
        global _router

        if not _router:
            raise HTTPException(status_code=503, detail="Router not initialized")

        status = await _router.check_all_providers()
        return {k: {"available": v.available, "latency_ms": v.latency_ms} for k, v in status.items()}

    @app.get("/best-model")
    async def get_best():
        """Get the best available model."""
        global _router

        if not _router:
            raise HTTPException(status_code=503, detail="Router not initialized")

        model = await _router.get_best_available_model()

        if not model:
            raise HTTPException(status_code=503, detail="No models available")

        return {
            "model_id": model.model_id,
            "display_name": model.display_name,
            "score": model.score,
            "provider": model.provider,
            "context": model.context,
        }

    return app


# For uvicorn
app = create_app()
