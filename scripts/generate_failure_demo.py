"""Generate a controlled negative-test report from a temporary fixture mutation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def generate() -> int:
    """Mutate one temporary fixture, require exit 1, and retain only the report."""

    with tempfile.TemporaryDirectory(prefix="hashmark-mutation-") as temporary:
        vectors = Path(temporary) / "vectors"
        shutil.copytree(PROJECT_ROOT / "vectors", vectors)
        fixture_path = vectors / "sha256" / "known-answer.json"
        document = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture = next(item for item in document["vectors"] if item["id"] == "sha256-abc")
        fixture["expected_digest_hex"] = "00" * 32
        fixture_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "hashmark",
                "run",
                "--vector",
                "sha256-abc",
                "--backend",
                "evm",
                "--format",
                "all",
                "--vectors-dir",
                str(vectors),
                "--output-dir",
                str(PROJECT_ROOT / "reports" / "demo-failure"),
                "--force",
            ],
            cwd=PROJECT_ROOT,
            check=False,
        )
    if completed.returncode != 1:
        raise RuntimeError(f"controlled mutation should exit 1; observed {completed.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate())
