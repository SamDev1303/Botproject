#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Concrete token/key signatures.
SECRET_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{36}", "GitHub PAT"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "Fine-grained GitHub token"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google/Gemini API key"),
    (r"vck_[A-Za-z0-9]{20,}", "Vercel API key"),
    (r"sk-(?:proj-)?[A-Za-z0-9_\-]{20,}", "OpenAI style secret"),
    (r"sq0atp-[A-Za-z0-9\-_]{20,}", "Square access token"),
    (r"sq0csp-[A-Za-z0-9\-_]{20,}", "Square client secret"),
]

# Hardcoded secret assignment patterns.
HARDCODED_PATTERNS = [
    (
        re.compile(
            r"(?i)\b("
            r"api[_-]?key|token|secret|password|passwd|private[_-]?key|"
            r"client[_-]?secret|access[_-]?token|id[_-]?token"
            r")\b\s*[:=]\s*[\"'][^\"']{16,}[\"']"
        ),
        "Potential hardcoded credential assignment",
    ),
]

IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    "archive",
    "memory",
}
IGNORE_FILES = {"pre-push-check.py", ".gitignore", "package-lock.json"}
TEXT_EXTENSIONS = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".env",
    ".md",
    ".txt",
    ".ini",
    ".cfg",
}


def is_probably_text(path: str) -> bool:
    p = Path(path)
    if p.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if p.name.startswith(".env"):
        return True
    return False


def git_changed_files(staged_only: bool) -> list[str]:
    cmd = ["git", "diff", "--cached", "--name-only"] if staged_only else ["git", "ls-files"]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return []
    return [f for f in out.splitlines() if f.strip()]


def workspace_files(staged_only: bool) -> list[str]:
    files = git_changed_files(staged_only)
    if files:
        return files
    if staged_only:
        return []
    discovered: list[str] = []
    for root, dirs, names in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in names:
            if name in IGNORE_FILES:
                continue
            rel = os.path.join(root, name)
            rel = rel[2:] if rel.startswith("./") else rel
            discovered.append(rel)
    return discovered


def scan_file(path: str) -> list[str]:
    if Path(path).name in IGNORE_FILES:
        return []
    if not is_probably_text(path):
        return []
    if any(f"/{d}/" in f"/{path}/" for d in IGNORE_DIRS):
        return []
    p = Path(path)
    if not p.exists() or not p.is_file():
        return []
    try:
        content = p.read_text(encoding="utf-8")
    except Exception:
        return []
    findings: list[str] = []
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, content):
            findings.append(f"{path}: {label}")
    for pattern, label in HARDCODED_PATTERNS:
        if pattern.search(content):
            findings.append(f"{path}: {label}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true", help="Scan only staged files")
    args = parser.parse_args()

    files = workspace_files(args.staged)
    if args.staged and not files:
        print("ℹ️ No staged files detected; skipping secret scan.")
        return 0

    findings: list[str] = []
    for file_path in files:
        findings.extend(scan_file(file_path))

    if findings:
        print("🚨 SECRET OR HARDCODED KEY DETECTED:")
        for finding in sorted(set(findings)):
            print(f" - {finding}")
        print("\nMove secrets to environment variables before pushing.")
        return 1

    print("✅ No secrets or hardcoded credential assignments detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
