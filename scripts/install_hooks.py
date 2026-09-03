"""Enable the repository-managed Git hooks for this clone."""

import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".githooks" / "pre-commit"

HOOK.chmod(HOOK.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
subprocess.run(["git", "-C", str(ROOT), "config", "core.hooksPath", ".githooks"], check=True)
print("Hooks enabled for this clone: .githooks")
