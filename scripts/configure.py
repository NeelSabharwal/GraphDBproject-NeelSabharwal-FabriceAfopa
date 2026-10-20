"""Create one ignored local password file without exposing its value."""

import os
from pathlib import Path
import secrets


def main() -> None:
    """Preserve existing credentials and create new files with owner-only access."""
    path = Path(".env")
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print("Existing .env preserved; no credential changed.")
        return
    with os.fdopen(descriptor, "w") as output:
        output.write(f"NEO4J_PASSWORD={secrets.token_hex(32)}\n")
    print("Created ignored .env with a random local password (mode 0600); value not displayed.")


if __name__ == "__main__":
    main()
