import re
import os
import sys

# Common secret patterns
SECRET_PATTERNS = [
    r'ghp_[a-zA-Z0-9]{36}',        # GitHub PAT
    r'AIza[0-9A-Za-z-_]{35}',      # Google/Gemini API Key
    r'sk-[a-zA-Z0-9]{48}',         # OpenAI/Anthropic Keys
    r'sq0atp-[a-zA-Z0-9-_]{22}',   # Square Access Token
    r'sq0csp-[a-zA-Z0-9-_]{43}',   # Square Client Secret
]

def scan_files():
    found_secrets = []
    # Only scan files likely to be pushed (exclude .git, memory/backup, etc)
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs: dirs.remove('.git')
        if 'node_modules' in dirs: dirs.remove('node_modules')
        
        for file in files:
            if file in ['pre-push-check.py', '.gitignore', 'package-lock.json']:
                continue
                
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in SECRET_PATTERNS:
                        if re.search(pattern, content):
                            found_secrets.append(f"{path} (Pattern: {pattern})")
            except Exception:
                continue
    return found_secrets

if __name__ == "__main__":
    secrets = scan_files()
    if secrets:
        print("🚨 SECRET LEAK DETECTED:")
        for s in secrets:
            print(f" - {s}")
        sys.exit(1)
    else:
        print("✅ No secrets detected. Safe to push.")
        sys.exit(0)
