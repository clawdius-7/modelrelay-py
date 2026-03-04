# ModelRelay

Intelligent LLM Model Routing - Python Edition

Routes requests to the best available model based on quality scores and provider availability.

## Features

- **Smart Routing**: Automatically selects the best available model based on quality scores
- **Multi-Provider Support**: NVIDIA NIM, Groq, Cerebras, OpenRouter, Codestral, Scaleway, Google AI
- **Health Checking**: Monitors provider availability and latency
- **OpenAI-Compatible API**: Drop-in replacement for OpenAI API clients
- **CLI Tools**: Manage models, providers, and check availability

## Installation

```bash
pip install modelrelay
```

For the HTTP server:
```bash
pip install modelrelay[server]
```

## Quick Start

### CLI Usage

List available models:
```bash
modelrelay models
```

Show best available model:
```bash
modelrelay best
```

Check provider status:
```bash
modelrelay check
```

### Python API

```python
import asyncio
from modelrelay import ModelRouter

async def main():
    router = ModelRouter()

    # Get best available model
    model = await router.get_best_available_model()
    print(f"Best model: {model.model_id} (score: {model.score})")

    # Route a chat completion request
    response = await router.route_request(
        messages=[
            {"role": "user", "content": "Hello, world!"}
        ]
    )
    print(response["choices"][0]["message"]["content"])

    await router.close()

asyncio.run(main())
```

### HTTP Server

Start the OpenAI-compatible server:
```bash
modelrelay serve --port 8000
```

Then use with any OpenAI client:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Supported Providers

| Provider | Models | Specialization |
|----------|--------|----------------|
| NVIDIA NIM | 30+ | Best variety, high quality |
| Groq | 7 | Ultra-fast inference |
| Cerebras | 5 | Fast inference |
| OpenRouter | 6+ | Free tier available |
| Codestral | 1 | Code generation |
| Scaleway | 3 | European hosting |
| Google AI | 3 | Gemma models |

## Model Scoring

Models are scored from 0.0 to 1.0 based on quality benchmarks. Higher scores indicate better performance.

View all scores:
```bash
modelrelay scores
```

## License

MIT
