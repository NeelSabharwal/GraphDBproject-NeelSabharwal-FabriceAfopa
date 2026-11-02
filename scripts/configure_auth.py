"""Append one local import token without displaying it or changing DB credentials."""

from pathlib import Path
import os
import secrets


def main():
    """Require prior configuration, preserve any existing token including disabled state."""
    path = Path(".env")
    content = path.read_text(encoding="utf-8")
    if any(line.startswith("CORPUS_IMPORT_TOKEN=") for line in content.splitlines()):
        print("Existing import authentication setting preserved.")
        return
    with path.open("a", encoding="utf-8") as output:
        output.write(("" if content.endswith("\n") else "\n") + f"CORPUS_IMPORT_TOKEN={secrets.token_hex(32)}\n")
    os.chmod(path, 0o600)
    print("Configured ignored local import token; value not displayed. Restart API to load it.")


if __name__ == "__main__":
    main()
