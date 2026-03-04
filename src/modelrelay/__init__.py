"""
ModelRelay - Intelligent LLM Model Routing

Routes requests to the best available model based on quality scores and availability.

This is a Python port of the original modelrelay by Elliptic Marketing:
https://github.com/ellipticmarketing/modelrelay
"""

__version__ = "0.1.0"
__author__ = "OpenClaw (clawdius-7)"
__original_author__ = "Elliptic Marketing"

from modelrelay.scores import SCORES
from modelrelay.sources import SOURCES, MODELS, get_available_models
from modelrelay.router import ModelRouter

__all__ = ["SCORES", "SOURCES", "MODELS", "get_available_models", "ModelRouter"]
