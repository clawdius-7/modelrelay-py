"""Configuration management for modelrelay."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class APIKey:
    """API key configuration for a provider."""
    provider: str
    key: str
    prefix: str = "Bearer"


@dataclass 
class Config:
    """Main configuration for modelrelay."""
    
    # Provider API keys
    api_keys: dict[str, APIKey] = field(default_factory=dict)
    
    # Routing preferences
    preferred_provider: Optional[str] = None
    min_score: Optional[float] = None
    
    # Request settings
    timeout_seconds: float = 30.0
    max_retries: int = 3
    
    # Server settings
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        key_config = self.api_keys.get(provider)
        return key_config.key if key_config else None
    
    def set_api_key(self, provider: str, key: str, prefix: str = "Bearer"):
        """Set API key for a provider."""
        self.api_keys[provider] = APIKey(
            provider=provider,
            key=key,
            prefix=prefix
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config):
    """Set the global configuration."""
    global _config
    _config = config


def load_config_from_file(path: str) -> Config:
    """Load configuration from a JSON file."""
    import json
    from pathlib import Path
    
    config_file = Path(path)
    if not config_file.exists():
        return Config()
    
    with open(config_file, "r") as f:
        data = json.load(f)
    
    config = Config()
    
    # Load API keys
    for provider, key_data in data.get("api_keys", {}).items():
        if isinstance(key_data, str):
            config.set_api_key(provider, key_data)
        else:
            config.set_api_key(
                provider,
                key_data.get("key", ""),
                key_data.get("prefix", "Bearer")
            )
    
    # Load preferences
    if "preferred_provider" in data:
        config.preferred_provider = data["preferred_provider"]
    if "min_score" in data:
        config.min_score = data["min_score"]
    if "timeout_seconds" in data:
        config.timeout_seconds = data["timeout_seconds"]
    if "max_retries" in data:
        config.max_retries = data["max_retries"]
    if "server_host" in data:
        config.server_host = data["server_host"]
    if "server_port" in data:
        config.server_port = data["server_port"]
    
    return config


def load_config_from_env() -> Config:
    """Load configuration from environment variables."""
    import os
    
    config = Config()
    
    # Common environment variable patterns
    env_mappings = {
        "NVIDIA_API_KEY": "nvidia",
        "GROQ_API_KEY": "groq",
        "CEREBRAS_API_KEY": "cerebras",
        "OPENROUTER_API_KEY": "openrouter",
        "CODESTRAL_API_KEY": "codestral",
        "SCALEWAY_API_KEY": "scaleway",
        "GOOGLE_AI_API_KEY": "googleai",
        "OPENAI_API_KEY": "openai",
        "ANTHROPIC_API_KEY": "anthropic",
        "MISTRAL_API_KEY": "mistral",
    }
    
    for env_var, provider in env_mappings.items():
        key = os.environ.get(env_var)
        if key:
            config.set_api_key(provider, key)
    
    # Preferences from env
    if os.environ.get("MODELRELAY_PREFERRED_PROVIDER"):
        config.preferred_provider = os.environ["MODELRELAY_PREFERRED_PROVIDER"]
    if os.environ.get("MODELRELAY_MIN_SCORE"):
        config.min_score = float(os.environ["MODELRELAY_MIN_SCORE"])
    if os.environ.get("MODELRELAY_TIMEOUT"):
        config.timeout_seconds = float(os.environ["MODELRELAY_TIMEOUT"])
    if os.environ.get("MODELRELAY_SERVER_PORT"):
        config.server_port = int(os.environ["MODELRELAY_SERVER_PORT"])
    
    return config
