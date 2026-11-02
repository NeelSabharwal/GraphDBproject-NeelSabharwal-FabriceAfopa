"""Fail if installed model tags differ from the recorded manifest digests."""

import json
from pathlib import Path
import subprocess


def main() -> None:
    """Inspect model metadata through the API container without exposing a port."""
    expected = json.loads(Path("models.lock.json").read_text())["models"]
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "api",
            "python",
            "-c",
            "import httpx; print(httpx.get('http://ollama:11434/api/tags',timeout=5).text)",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    installed = {item["name"]: item for item in json.loads(result.stdout)["models"]}
    for model in expected:
        actual = installed.get(model["name"])
        if actual is None or actual["digest"] != model["digest"]:
            raise SystemExit(f"Model missing or digest changed: {model['name']}. Review before use; lock not modified.")
        print(f"Verified {model['name']} {model['digest']}")


if __name__ == "__main__":
    main()
