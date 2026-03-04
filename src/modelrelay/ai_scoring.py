"""AI-based scoring using simple heuristics."""

from typing import Optional


# Heuristic scoring rules based on model characteristics
HEURISTICS = {
    # Size-based adjustments (larger is generally better for same family)
    "size_bonuses": {
        "70b": 0.05,
        "72b": 0.05,
        "120b": 0.08,
        "235b": 0.10,
        "400b": 0.12,
        "405b": 0.12,
        "480b": 0.13,
        "675b": 0.15,
    },
    "size_penalties": {
        "1b": -0.05,
        "2b": -0.04,
        "3b": -0.03,
        "7b": -0.02,
        "8b": -0.02,
    },
    
    # Model family adjustments
    "family_bonuses": {
        "claude": 0.08,
        "gpt-4": 0.10,
        "gemini": 0.06,
        "deepseek": 0.04,
        "qwen3": 0.03,
        "llama-4": 0.02,
    },
    
    # Reasoning/thinking models
    "reasoning_keywords": ["thinking", "reasoning", "r1", "qwq", "o1"],
    
    # Code models
    "code_keywords": ["coder", "code", "devstral", "codestral"],
    
    # Context window bonuses
    "context_bonuses": {
        "128k": 0.02,
        "200k": 0.03,
        "256k": 0.04,
        "1m": 0.06,
        "10m": 0.10,
    },
}


def apply_heuristics(model_id: str, base_score: float, context: str = "") -> float:
    """Apply heuristic adjustments to a base score."""
    score = base_score
    model_lower = model_id.lower()
    context_lower = context.lower()
    
    # Size-based adjustments
    for size, bonus in HEURISTICS["size_bonuses"].items():
        if size in model_lower:
            score += bonus
            break
    
    for size, penalty in HEURISTICS["size_penalties"].items():
        if size in model_lower:
            score += penalty
            break
    
    # Family adjustments
    for family, bonus in HEURISTICS["family_bonuses"].items():
        if family in model_lower:
            score += bonus
            break
    
    # Reasoning models bonus
    if any(kw in model_lower for kw in HEURISTICS["reasoning_keywords"]):
        score += 0.05
    
    # Code models bonus
    if any(kw in model_lower for kw in HEURISTICS["code_keywords"]):
        score += 0.03
    
    # Context window bonuses
    for ctx, bonus in HEURISTICS["context_bonuses"].items():
        if ctx in context_lower:
            score += bonus
            break
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, score))


def estimate_score(model_id: str, context: str = "") -> float:
    """Estimate a score for an unknown model."""
    model_lower = model_id.lower()
    
    # Base estimate
    base = 0.35  # Default middle ground
    
    # Look for indicators
    if "70b" in model_lower or "72b" in model_lower:
        base = 0.45
    elif "1b" in model_lower or "2b" in model_lower:
        base = 0.15
    elif "8b" in model_lower or "7b" in model_lower:
        base = 0.25
    
    # Family indicators
    for family, bonus in HEURISTICS["family_bonuses"].items():
        if family in model_lower:
            base += bonus * 0.5  # Partial bonus for estimates
            break
    
    return apply_heuristics(model_id, base, context)
