"""Fail-closed API redistribution checks; no registry or scientific database writes."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import urllib.request

MANIFEST = Path("docker/licenses/release-manifest.json")
SOURCE_DIR = "/usr/share/doc/project8-api/sources/"
TOKEN_PATTERN = re.compile(
    rb"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"
)


def sha256(path):
    """Hash exact bytes without loading large source archives into memory."""
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(*args):
    """Run a bounded local command and return its output without shell expansion."""
    return subprocess.check_output(args, text=True, timeout=600)


def inventory(manifest):
    """Inspect installed packages, notices and native binaries inside the API image."""
    distributions = {}
    notices = {}
    for package in importlib.metadata.distributions():
        distributions[package.metadata["Name"].lower().replace("_", "-")] = package.version
        for file in package.files or []:
            if any(word in str(file).lower() for word in ("license", "copying", "copyright", "notice")):
                path = Path(package.locate_file(file))
                if ".dist-info/" in str(file) and path.is_file():
                    notices[str(file)] = sha256(path)
    return {
        "python": distributions,
        "project_notices": {p.name: sha256(p) for p in Path("/usr/share/doc/project8-api").iterdir() if p.is_file()},
        "notices": notices,
        "debian": sorted(
            line.split("\t")
            for line in run(
                "dpkg-query", "-W", "-f=${binary:Package}\t${Version}\t${source:Package}\t${source:Version}\n"
            ).splitlines()
        ),
        "native": {item["path"]: sha256(item["path"]) for item in manifest["native_libraries"]},
        "sources": {
            item["filename"]: sha256(SOURCE_DIR + item["filename"])
            for item in manifest["source_archives"]
            if Path(SOURCE_DIR + item["filename"]).is_file()
        },
    }


def validate_inventory(actual, manifest):
    """Reject version drift, missing notices/sources and unresolved license evidence."""
    errors = []
    expected = {p["name"].lower().replace("_", "-"): p["version"] for p in manifest["python_distributions"]}
    if actual["python"] != expected:
        errors.append("Python distribution inventory differs from reviewed versions")
    if actual["debian"] != sorted(manifest["debian_packages"]):
        errors.append("Debian package/source-version inventory differs")
    for package in manifest["python_distributions"]:
        for notice in package["notices"]:
            if actual["notices"].get(notice["path"]) != notice["sha256"]:
                errors.append(f"Missing/changed notice: {notice['path']}")
    for native in manifest["native_libraries"]:
        if actual["native"].get(native["path"]) != native["sha256"]:
            errors.append(f"Native binary changed: {native['path']}")
    expected_sources = {item["filename"]: item["sha256"] for item in manifest["source_archives"]}
    if actual["sources"] != expected_sources:
        errors.append("Corresponding-source archives missing or changed")
    quadmath = {item["path"] for item in manifest["native_libraries"] if "libquadmath" in item["path"]}
    mapped = set()
    for evidence in manifest.get("native_source_evidence", []):
        if expected_sources.get(evidence["source_filename"]) == evidence["source_sha256"]:
            mapped.update(evidence["wheel_paths"])
    if quadmath - mapped:
        errors.append("libquadmath corresponding-source mapping incomplete")
    errors.extend(f"{issue['id']}: {issue['reason']}" for issue in manifest["blocking_issues"])
    return errors


def download_source(item, destination):
    """Download one public source archive, verify its size/hash, then publish locally."""
    name = item["filename"]
    if Path(name).name != name or not item["url"].startswith("https://"):
        raise ValueError("Unsafe source archive path or URL")
    path = destination / name
    if path.exists() and path.stat().st_size == item["size"] and sha256(path) == item["sha256"]:
        return
    temporary = path.with_suffix(path.suffix + ".part")
    try:
        with urllib.request.urlopen(item["url"], timeout=60) as response, temporary.open("wb") as stream:
            total = 0
            while block := response.read(1024 * 1024):
                total += len(block)
                if total > item["size"]:
                    raise ValueError(f"Oversized source archive: {name}")
                stream.write(block)
        if total != item["size"] or sha256(temporary) != item["sha256"]:
            raise ValueError(f"Source hash/size mismatch: {name}")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def bundle_sources(manifest, destination):
    """Prepare a source-only build context; never copy arbitrary local data into it."""
    destination.mkdir(parents=True, exist_ok=True)
    expected = {item["filename"] for item in manifest["source_archives"]}
    if any(path.name not in expected for path in destination.iterdir()):
        raise ValueError("Source build context contains unexpected files")
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda item: download_source(item, destination), manifest["source_archives"]))


def scan_stream(stream, secrets=(), signatures=True):
    """Find configured secret bytes and token/key signatures across buffer boundaries."""
    tail = b""
    overlap = max([256] + [len(secret) for secret in secrets])
    while block := stream.read(1024 * 1024):
        data = tail + block
        if (signatures and TOKEN_PATTERN.search(data)) or any(secret in data for secret in secrets):
            return True
        tail = data[-overlap:]
    return False


def workspace_files(root):
    """Map the root Dockerfile's explicit application COPY inputs to exact file hashes."""
    paths = [p for folder in ("app", "scripts", "tests") for p in (root / folder).rglob("*") if p.is_file()]
    paths += [
        root / name
        for name in (
            "requirements.txt",
            "requirements-dev.txt",
            "requirements.lock.txt",
            "pyproject.toml",
            "models.lock.json",
            "corpus/corpus_manifest.json",
            "corpus/citation_evidence.csv",
        )
    ]
    return {
        "workspace/" + str(p.relative_to(root)): sha256(p)
        for p in paths
        if "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def scan_layers(archive, expected, source_hashes, secrets=(), public_fixtures=()):
    """Inspect every saved API image layer, including files hidden by later layers."""
    errors = []
    count = 0
    known = {item["path"]: item["sha256"] for item in public_fixtures}
    exceptions = []
    with tarfile.open(archive) as outer:
        manifests = json.load(outer.extractfile("manifest.json"))
        if len(manifests) != 1:
            raise ValueError("Expected exactly one API image")
        for layer in manifests[0]["Layers"]:
            with tarfile.open(fileobj=outer.extractfile(layer), mode="r|*") as inner:
                for member in inner:
                    name = member.name.removeprefix("./")
                    if name.startswith(("root/.ssh/", "root/.docker/", "workspace/.git", "workspace/.env")):
                        errors.append(f"Forbidden layer path: {name}")
                    if ".." in Path(name).parts or name.startswith(("var/lib/neo4j/", "var/lib/ollama/")):
                        errors.append(f"Forbidden layer path: {name}")
                    if name.startswith("workspace/") and (
                        Path(name).name.startswith(".env")
                        or name.endswith((".pdf", ".gguf", ".safetensors", ".p12", ".pfx", ".jar"))
                    ):
                        errors.append(f"Forbidden application asset: {name}")
                    if (member.issym() or member.islnk()) and name.startswith(("workspace/", SOURCE_DIR.lstrip("/"))):
                        errors.append(f"Unexpected application/source link: {name}")
                    if not member.isfile():
                        continue
                    count += 1
                    stream = inner.extractfile(member)
                    if name.startswith("workspace/"):
                        data = stream.read()
                        if name not in expected or hashlib.sha256(data).hexdigest() != expected[name]:
                            errors.append(f"Unexpected/changed application file: {name}")
                        if TOKEN_PATTERN.search(data) or any(secret in data for secret in secrets):
                            errors.append(f"Secret signature in: {name}")
                    elif name.startswith(SOURCE_DIR.lstrip("/")):
                        filename = name.removeprefix(SOURCE_DIR.lstrip("/"))
                        if hashlib.file_digest(stream, "sha256").hexdigest() != source_hashes.get(filename):
                            errors.append(f"Unexpected/changed source archive: {name}")
                    elif name in known:
                        data = stream.read()
                        if hashlib.sha256(data).hexdigest() != known[name]:
                            errors.append(f"Public fixture changed: {name}")
                        elif scan_stream(io.BytesIO(data), secrets, signatures=False):
                            errors.append(f"Configured secret in public fixture: {name}")
                        else:
                            exceptions.append(name)
                    elif scan_stream(stream, secrets):
                        errors.append(f"Secret signature in: {name}")
        return {
            "layers": len(manifests[0]["Layers"]),
            "regular_files": count,
            "errors": errors,
            "verified_public_fixture_exceptions": exceptions,
        }


def audit_image(image, revision, manifest, output, secrets_file=None):
    """Audit a local image offline and retain failures; never login, push or mutate Neo4j."""
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Expected a full reviewed Git commit SHA")
    output.mkdir(parents=True, exist_ok=True)
    config = json.loads(run("docker", "image", "inspect", image))[0]
    actual = json.loads(
        run(
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--entrypoint",
            "python",
            image,
            "-m",
            "scripts.release_preflight",
            "inventory",
        )
    )
    errors = validate_inventory(actual, manifest)
    if actual["project_notices"] != {p.name: sha256(p) for p in Path("docker/licenses").iterdir() if p.is_file()}:
        errors.append("Project-supplied license/source notices missing or changed")
    if TOKEN_PATTERN.search(json.dumps(config["Config"]).encode()):
        errors.append("Secret signature in image configuration")
    if config["Architecture"] != "amd64" or config["Os"] != "linux" or config["Config"]["User"] != "appuser":
        errors.append("Unexpected platform or runtime user")
    if config["Config"].get("Labels", {}).get("org.opencontainers.image.revision") != revision:
        errors.append("Image revision does not match the requested main commit")
    if sha256("requirements.lock.txt") != manifest["requirements_sha256"]:
        errors.append("Dependency lock changed without renewed redistribution review")
    if Path("Dockerfile").read_text().splitlines()[0] != "FROM " + manifest["base_image"]:
        errors.append("Pinned base image differs")
    secrets = []
    if secrets_file:
        for line in secrets_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                value = value.strip().strip("\"'")
                if re.search("PASSWORD|TOKEN|SECRET", key) and len(value) > 8:
                    secrets.append(value.encode())
    if any(secret in json.dumps(config["Config"]).encode() for secret in secrets):
        errors.append("Configured secret in image configuration")
    archive = output / "api-image.tar"
    run("docker", "image", "save", "-o", str(archive), image)
    scan = scan_layers(
        archive,
        workspace_files(Path.cwd()),
        {x["filename"]: x["sha256"] for x in manifest["source_archives"]},
        secrets,
        manifest.get("public_test_fixtures", []),
    )
    errors.extend(scan["errors"])
    report = {
        "image_id_not_registry_digest": config["Id"],
        "size_bytes": config["Size"],
        "platform": "linux/amd64",
        "revision": revision,
        "scan": scan,
        "blocking_errors": errors,
        "publication_allowed": not errors,
    }
    (output / "preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 2 if errors else 0


def main():
    """Prepare public sources or run the mandatory offline publication gate."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sources", "inventory", "check"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/ghcr-release/preflight"))
    parser.add_argument("--image")
    parser.add_argument("--revision")
    parser.add_argument("--secrets-file", type=Path)
    args = parser.parse_args()
    path = Path("/usr/share/doc/project8-api/release-manifest.json") if args.command == "inventory" else MANIFEST
    manifest = json.loads(path.read_text())
    if args.command == "inventory":
        print(json.dumps(inventory(manifest)))
        return 0
    if args.command == "sources":
        bundle_sources(manifest, args.output)
        print(f"Verified {len(manifest['source_archives'])} public source archives")
        return 0
    if not args.image or not args.revision:
        parser.error("check requires --image and --revision")
    return audit_image(args.image, args.revision, manifest, args.output, args.secrets_file)


if __name__ == "__main__":
    raise SystemExit(main())
