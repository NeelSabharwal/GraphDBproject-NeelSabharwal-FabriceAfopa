"""Create and validate an offline /data archive without deleting containers or volumes."""

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import time


def command(*args):
    """Capture selected non-secret command output; fail rather than continue silently."""
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"Backup command failed ({result.returncode}): {result.stderr.strip()}")
    return result.stdout.strip()


def main():
    """Stop cleanly, copy read-only data, validate, restart, then emit a receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fingerprint", required=True)
    parser.add_argument("--helper-image", default="ai-research-graphrag-api:infra")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    container = command("docker", "compose", "ps", "-q", "neo4j")
    if not container:
        raise RuntimeError("Neo4j container missing")
    mounts = json.loads(command("docker", "inspect", "--format", "{{json .Mounts}}", container))
    mount = next(m for m in mounts if m["Destination"] == "/data" and m["Type"] == "volume")
    command("docker", "volume", "inspect", mount["Name"], "--format", "{{.Name}}")
    # A running container's original image may have been removed from the store.
    image = command("docker", "image", "inspect", args.helper_image, "--format", "{{.Id}}")
    command("docker", "run", "--rm", "--network", "none", "--entrypoint", "tar", image, "--version")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = args.output_dir / f"neo4j-before-mentions-{stamp}.tar.gz"
    if archive.exists():
        raise FileExistsError(archive)
    command("docker", "compose", "stop", "-t", "60", "api", "neo4j")
    try:
        if command("docker", "inspect", "--format", "{{.State.Running}}", container) != "false":
            raise RuntimeError("Neo4j did not stop")
        command(
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--user",
            "0",
            "--mount",
            f'type=volume,source={mount["Name"]},target=/source,readonly',
            "--mount",
            f"type=bind,source={args.output_dir.resolve()},target=/backup",
            "--entrypoint",
            "tar",
            image,
            "-C",
            "/source",
            "-czf",
            f"/backup/{archive.name}",
            ".",
        )
        with gzip.open(archive, "rb") as stream:
            while stream.read(1024 * 1024):
                pass
        with tarfile.open(archive, "r:gz") as bundle:
            names = bundle.getnames()
        if not any("/databases/neo4j/" in n for n in names) or not any("/transactions/" in n for n in names):
            raise RuntimeError("Backup lacks database or transaction contents")
        with archive.open("rb") as stream:
            checksum = hashlib.file_digest(stream, "sha256").hexdigest()
        if archive.stat().st_size == 0:
            raise RuntimeError("Empty backup")
        archive.with_suffix(archive.suffix + ".sha256").write_text(f"{checksum}  {archive.name}\n")
    finally:
        command("docker", "compose", "up", "-d", "neo4j", "api")
    for _ in range(60):
        health = command("docker", "inspect", "--format", "{{.State.Health.Status}}", container)
        api = command("docker", "compose", "ps", "-q", "api")
        api_health = command("docker", "inspect", "--format", "{{.State.Health.Status}}", api)
        if health == api_health == "healthy":
            break
        time.sleep(2)
    else:
        raise RuntimeError("Services did not become healthy after backup")
    receipt = dict(
        archive=str(archive),
        absolute_path=str(archive.resolve()),
        volume=mount["Name"],
        size_bytes=archive.stat().st_size,
        sha256=checksum,
        archive_entries=len(names),
        integrity_verified=True,
        baseline_fingerprint=args.fingerprint,
        services_healthy=True,
    )
    receipt_path = archive.with_suffix(".receipt.json")
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    print("Receipt:", receipt_path)


if __name__ == "__main__":
    main()
