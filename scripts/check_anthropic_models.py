import os
import requests
import json

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    # Try to read from .env if not in env
    try:
        with open("/Users/hafsahnuzhat/.clawdbot/.env", "r") as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    except Exception as e:
        print(f"Error reading .env: {e}")

if not api_key:
    print("Could not find ANTHROPIC_API_KEY")
    exit(1)

print(f"Using key: {api_key[:10]}...")

headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# There isn't a public 'list models' endpoint documented for standard keys in older docs, 
# but let's try a standard completion to see if we get a useful error listing models,
# or if there is a models endpoint now (2026).
# Actually, let's try the models endpoint which likely exists in 2026.

try:
    response = requests.get("https://api.anthropic.com/v1/models", headers=headers)
    if response.status_code == 200:
        models = response.json()
        print("Available Models:")
        for m in models.get("data", []):
            print(f"- {m['id']} ({m.get('display_name', 'No display name')})")
    else:
        print(f"Failed to list models: {response.status_code} {response.text}")
        
        # Fallback: try a dummy request with a wrong model to see if it lists available ones in error
        data = {
            "model": "claude-invalid-model-check",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 1
        }
        resp2 = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
        print("\nFallback check (invalid model error might list valid ones):")
        print(resp2.text)

except Exception as e:
    print(f"Error: {e}")
