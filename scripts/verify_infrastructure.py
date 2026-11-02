"""Host wrapper: preserve actual smoke output and container memory evidence."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess


def main() -> None:
    """Run bounded checks without mounting the Docker socket into any container."""
    process = subprocess.run(
        ["docker", "compose", "exec", "-T", "api", "python", "-m", "scripts.smoke"],
        text=True,
        capture_output=True,
        timeout=600,
        check=False,
    )
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError:
        print("Smoke command did not return a JSON report; inspect service status.")
        raise SystemExit(process.returncode or 1)
    report["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
    report["exit_code"] = process.returncode
    report["container_memory"] = {}
    for service in ["neo4j", "api", "ollama"]:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                service,
                "cat",
                "/sys/fs/cgroup/memory.current",
                "/sys/fs/cgroup/memory.peak",
                "/sys/fs/cgroup/memory.max",
                "/sys/fs/cgroup/memory.events",
            ],
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        report["container_memory"][service] = {"exit_code": result.returncode, "cgroup_output": result.stdout.strip()}
    report["memory_note"] = (
        "cgroup bytes include charged cache; memory.peak is since container creation, not a per-request peak."
    )
    report["service_status"] = subprocess.run(
        ["docker", "compose", "ps", "--format", "json"],
        text=True,
        capture_output=True,
        timeout=15,
        check=True,
    ).stdout.strip()
    destination = Path("data/processed/infrastructure-smoke.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Actual report saved to ignored {destination}")
    raise SystemExit(process.returncode)


if __name__ == "__main__":
    main()
