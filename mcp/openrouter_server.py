#!/usr/bin/env python3
"""
OpenRouter MCP Server - Free LLM for Data Chunking & Summarization
For Clean Up Bros - Memory compression and text processing
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.logging_config import setup_logging

# Setup logging
logger = setup_logging(__name__)

# Load environment
def load_env():
    env_file = Path.home() / ".clawdbot" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

load_env()

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Free models for chunking/summarization
FREE_MODELS = {
    "qwen-2.5-7b": "qwen/qwen-2.5-7b-instruct:free",
    "phi-3": "microsoft/phi-3-mini-128k-instruct:free",
    "gemma-2-9b": "google/gemma-2-9b-it:free",
    "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct:free"
}

DEFAULT_MODEL = FREE_MODELS["qwen-2.5-7b"]  # Fast and good for summarization

# Create MCP server
mcp = FastMCP("OpenRouter")


def api_request(model: str, messages: list, temperature: float = 0.3, max_tokens: int = 2000) -> dict:
    """Make OpenRouter API request"""
    url = f"{OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://cleanupbros.com.au",
        "X-Title": "Bella AI Assistant"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            logger.info(f"OpenRouter request successful - Model: {model}")
            return result

    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:200]
        logger.error(f"OpenRouter API error: {e.code} - {error_msg}")
        return {"error": f"{e.code}: {error_msg}"}
    except Exception as e:
        logger.error(f"OpenRouter request failed: {e}")
        return {"error": str(e)}


@mcp.tool()
def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> str:
    """
    Chunk large text into smaller pieces with overlap

    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk (in characters)
        overlap: Number of characters to overlap between chunks

    Returns:
        JSON array of text chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append({
            "index": len(chunks),
            "text": chunk,
            "start": start,
            "end": min(end, len(text))
        })
        start = end - overlap

    logger.info(f"Chunked text into {len(chunks)} pieces")
    return json.dumps(chunks, indent=2)


@mcp.tool()
def summarize_text(text: str, max_length: int = 500, model: str = None) -> str:
    """
    Summarize text using free OpenRouter model

    Args:
        text: Text to summarize
        max_length: Target summary length in words
        model: Model to use (default: qwen-2.5-7b-instruct:free)

    Example:
        summarize_text("Long email content...", max_length=100)
    """
    if not OPENROUTER_API_KEY:
        logger.error("OpenRouter API key not configured")
        return "Error: OPENROUTER_API_KEY not set in .env"

    model = model or DEFAULT_MODEL

    messages = [
        {
            "role": "system",
            "content": f"You are a professional summarizer. Summarize the following text in {max_length} words or less. Focus on key information, numbers, dates, and action items."
        },
        {
            "role": "user",
            "content": text
        }
    ]

    result = api_request(model, messages, temperature=0.3, max_tokens=max_length * 2)

    if "error" in result:
        return f"Error: {result['error']}"

    summary = result.get('choices', [{}])[0].get('message', {}).get('content', '')
    logger.info(f"Summarized {len(text)} chars to {len(summary)} chars")
    return summary


@mcp.tool()
def summarize_session(session_content: str) -> str:
    """
    Summarize a session transcript for memory storage

    Args:
        session_content: Full session content

    Returns:
        Structured summary with key points
    """
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY not set"

    messages = [
        {
            "role": "system",
            "content": """You are summarizing a Bella AI assistant session for Clean Up Bros business.

Extract and structure the following:
1. **Tasks Completed:** List what was done
2. **Decisions Made:** Important decisions or changes
3. **Outstanding Items:** What needs follow-up
4. **Financial:** Any invoices, payments, or amounts mentioned
5. **Client Interactions:** Client names and their status

Keep it concise but preserve all critical data (names, amounts, dates)."""
        },
        {
            "role": "user",
            "content": session_content
        }
    ]

    result = api_request(DEFAULT_MODEL, messages, temperature=0.2, max_tokens=1000)

    if "error" in result:
        logger.error(f"Session summarization failed: {result['error']}")
        return f"Error: {result['error']}"

    summary = result.get('choices', [{}])[0].get('message', {}).get('content', '')
    logger.info("Session summarized successfully")
    return summary


@mcp.tool()
def extract_key_info(text: str, info_type: str) -> str:
    """
    Extract specific information from text

    Args:
        text: Text to analyze
        info_type: Type of information to extract
            - 'names': Extract person/company names
            - 'amounts': Extract dollar amounts
            - 'dates': Extract dates
            - 'action_items': Extract tasks/to-dos
            - 'emails': Extract email addresses
            - 'phones': Extract phone numbers

    Example:
        extract_key_info("Invoice for Claudia Alz $320 due 15/02/2026", "amounts")
        → ["$320"]
    """
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY not set"

    prompts = {
        'names': "Extract all person and company names from the text. Return as JSON array.",
        'amounts': "Extract all dollar amounts from the text. Return as JSON array.",
        'dates': "Extract all dates from the text. Return as JSON array in DD/MM/YYYY format.",
        'action_items': "Extract all tasks or action items from the text. Return as JSON array.",
        'emails': "Extract all email addresses from the text. Return as JSON array.",
        'phones': "Extract all phone numbers from the text. Return as JSON array."
    }

    if info_type not in prompts:
        return f"Error: Invalid info_type. Use one of: {', '.join(prompts.keys())}"

    messages = [
        {
            "role": "system",
            "content": prompts[info_type]
        },
        {
            "role": "user",
            "content": text
        }
    ]

    result = api_request(DEFAULT_MODEL, messages, temperature=0.1, max_tokens=500)

    if "error" in result:
        return f"Error: {result['error']}"

    extracted = result.get('choices', [{}])[0].get('message', {}).get('content', '')
    logger.info(f"Extracted {info_type} from text")
    return extracted


@mcp.tool()
def compress_memory_file(file_path: str, target_reduction: float = 0.6) -> str:
    """
    Compress a memory file by summarizing while preserving key data

    Args:
        file_path: Path to memory file to compress
        target_reduction: Target size reduction (0.6 = reduce to 40% of original)

    Returns:
        Compressed content
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        original_size = len(content)
        target_words = int(len(content.split()) * (1 - target_reduction))

        summary = summarize_text(content, max_length=target_words)

        compressed_size = len(summary)
        reduction_pct = ((original_size - compressed_size) / original_size) * 100

        logger.info(f"Compressed {file_path}: {original_size} → {compressed_size} chars ({reduction_pct:.1f}% reduction)")

        return f"""# Compressed Memory
Original size: {original_size} characters
Compressed size: {compressed_size} characters
Reduction: {reduction_pct:.1f}%

---

{summary}
"""

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return f"Error: File not found: {file_path}"
    except Exception as e:
        logger.error(f"Compression failed: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def openrouter_list_free_models() -> str:
    """
    List all available free models on OpenRouter
    """
    models_info = []
    for name, model_id in FREE_MODELS.items():
        models_info.append(f"• {name}: {model_id}")

    return "Available Free Models:\n" + "\n".join(models_info) + "\n\nDefault: qwen-2.5-7b-instruct:free"


if __name__ == "__main__":
    mcp.run()
