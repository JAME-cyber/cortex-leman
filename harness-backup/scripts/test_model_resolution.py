import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path so we can import from gateway
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from hermes import _resolve_gateway_model


def test_model_resolution():
    """Test that model resolution works correctly with config, env, and fallback."""
    # Test 1: Basic model resolution from config
    model = _resolve_gateway_model()
    assert model == "openai/gpt-4o-mini", f"Expected openai/gpt-4o-mini but got {model"
    
    # Test 2: Model resolution with explicit None config
    model = _resolve_gateway_model(None)
    assert model == "openai/gpt-4o-mini", f"Expected openai/gpt-4o-mini but got {model"
    
    # Test 3: Model resolution with empty dict config
    model = _resolve_gateway_model({})
    assert model == "openai/gpt-4o-mini", f"Expected openai/gpt-4o-mini but got {model"
    
    # Test 4: Model resolution with config having only model default
    config_with_default = {"model": {"default": "gpt-4o-mini"}
    model = _resolve_gateway_model(config_with_default)
    assert model == "gpt-4o-mini", f"Expected gpt-4o-mini but got {model"

    print("All model resolution tests passed!")

if __name__ == "__main__":
    test_model_resolution()
