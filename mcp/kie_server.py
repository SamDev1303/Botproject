#!/usr/bin/env python3
"""
Kie.AI MCP Server
"""
import os
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Add tools directory to path
tools_path = Path.home() / "clawd" / "tools"
sys.path.append(str(tools_path))

# Import API functions
try:
    import kie_ai
except ImportError:
    pass

# Create server
mcp = FastMCP("KieAI")

@mcp.tool()
def generate_video(prompt: str, model: str = "sora2", duration: int = 5) -> str:
    """Generate a video using Kie.AI (Sora, Veo, Kling)"""
    try:
        kie_ai.load_env()
        result = kie_ai.generate_video(prompt, model=model, duration=duration)
        if result:
            return f"Video generated: {result}"
        return "Failed to generate video"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def generate_image(prompt: str, model: str = "flux2") -> str:
    """Generate an image using Kie.AI (Flux, Grok)"""
    try:
        kie_ai.load_env()
        result = kie_ai.generate_image(prompt, model=model)
        if result:
            return f"Image generated: {result}"
        return "Failed to generate image"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
