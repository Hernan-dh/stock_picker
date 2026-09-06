"""Run dependency-free repository verification locally, in Git hooks, and in CI."""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_SECRET_SCAN_SIZE = 1024 * 1024
ESSENTIAL_DOCS = ("README.md", "LICENSE", ".env.example", "AGENTS.md", "docs/ARCHITECTURE.md", "docs/OPERATIONS.md", "docs/decisions/README.md")
PRIVATE_NAMES = {".env", "credentials.json", "secrets.json", "secrets.yaml", "id_rsa", "id_ed25519"}
PRIVATE_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
GENERATED_PARTS = {"__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
TEXT_SUFFIXES = {".css", ".env", ".html", ".ini", ".js", ".json", ".md", ".py", ".sh", ".toml", ".txt", ".yaml", ".yml"}
TEXT_NAMES = {".env.example", ".gitattributes", "AGENTS.md", "Dockerfile", "pre-commit"}
SECRET_PATTERNS = (
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"\b(?:gsk_|github_pat_|sk-or-v1-)[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[opurs]_[A-Za-z0-9_]{30,}\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*[\"']?([^\s\"'#]{12,})"),
)
PLACEHOLDER_PREFIXES = ("your-", "your_", "example", "placeholder", "change-me", "changeme")


class Verification:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def run(self, label: str, command: list[str]) -> None:
        print(f"[check] {label}")
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode:
            self.error(f"{label} failed with exit code {result.returncode}")


def repository_files(verification: Verification) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=False, capture_output=True,
    )
    if result.returncode:
        verification.error("Could not list repository files")
        return []
    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def check_python_syntax(verification: Verification, files: list[Path]) -> None:
    print("[check] Python syntax")
    for path in files:
        if path.suffix != ".py" or not path.is_file():
            continue
        try:
            with tokenize.open(path) as source:
                ast.parse(source.read(), filename=str(path))
        except (SyntaxError, UnicodeError) as error:
            verification.error(f"Invalid syntax in {path.relative_to(ROOT)}: {error}")


def check_existing_tests(verification: Verification, files: list[Path]) -> None:
    tests = [path for path in files if path.suffix == ".py" and path.is_file() and path.name.startswith("test_")]
    if not tests:
        verification.error("No regression tests found")
        return
    if (ROOT / "pyproject.toml").is_file():
        uv = shutil.which("uv")
        if uv is None:
            verification.error("Tests require uv. Install uv and run uv sync first.")
            return
        command = [uv, "run", "--project", str(ROOT), "python", "-m", "unittest", "discover"]
    else:
        candidates = [ROOT / ".venv" / "Scripts" / "python.exe", ROOT / ".venv" / "bin" / "python"]
        python = next((str(path) for path in candidates if path.is_file()), sys.executable)
        command = [python, "-m", "unittest", "discover"]
    verification.run("tests", command)


def check_files(verification: Verification, files: list[Path]) -> None:
    print("[check] private, generated, and large files")
    for path in files:
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        private_environment = path.name.startswith(".env.") and path.name != ".env.example"
        if private_environment or path.name.lower() in PRIVATE_NAMES or path.suffix.lower() in PRIVATE_SUFFIXES:
            verification.error(f"Private file is not allowed: {relative}")
        if {part.lower() for part in relative.parts} & GENERATED_PARTS:
            verification.error(f"Generated file is not ignored: {relative}")
        if path.stat().st_size > MAX_FILE_SIZE:
            verification.error(f"File exceeds 5 MiB: {relative}")


def check_secrets(verification: Verification, files: list[Path]) -> None:
    print("[check] potential secrets")
    for path in files:
        if not path.is_file() or path.stat().st_size > MAX_SECRET_SCAN_SIZE:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, 1):
            for pattern in SECRET_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                raw_candidate = match.group(1).rstrip(",)]}") if match.lastindex else ""
                candidate = raw_candidate.lower()
                if candidate.startswith(PLACEHOLDER_PREFIXES):
                    continue
                if raw_candidate and re.fullmatch(r"[A-Z][A-Z0-9_]+", raw_candidate):
                    continue
                verification.error(f"Sensitive value candidate at {path.relative_to(ROOT)}:{line_number}")
                break


def check_documentation(verification: Verification) -> None:
    print("[check] essential documentation")
    for relative in ESSENTIAL_DOCS:
        if not (ROOT / relative).is_file():
            verification.error(f"Missing essential documentation: {relative}")


def main() -> int:
    verification = Verification()
    files = repository_files(verification)
    verification.run("git diff --check", ["git", "--no-pager", "diff", "--check"])
    verification.run("git diff --cached --check", ["git", "--no-pager", "diff", "--cached", "--check"])
    check_python_syntax(verification, files)
    check_existing_tests(verification, files)
    check_files(verification, files)
    check_secrets(verification, files)
    check_documentation(verification)
    if verification.errors:
        print("\nVerification failed:")
        for error in verification.errors:
            print(f"- {error}")
        return 1
    print("\nVerification completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
