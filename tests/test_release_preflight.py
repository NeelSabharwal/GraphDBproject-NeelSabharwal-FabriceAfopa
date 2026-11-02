"""Release gates must reject private files, dependency drift and incomplete licensing."""

import copy
import hashlib
import io
import json
import tarfile
from unittest.mock import patch

import pytest

from scripts.release_preflight import bundle_sources, download_source, scan_layers, scan_stream, validate_inventory


def fixture_inventory():
    """Return synthetic release evidence, never a real compliance approval."""
    manifest = {
        "python_distributions": [
            {"name": "example", "version": "1", "notices": [{"path": "example.dist-info/LICENSE", "sha256": "notice"}]}
        ],
        "debian_packages": [["example", "1", "example-src", "1"]],
        "native_libraries": [{"path": "/lib/example.so", "sha256": "native"}],
        "source_archives": [{"filename": "source.tar.gz", "sha256": "source"}],
        "blocking_issues": [],
    }
    actual = {
        "python": {"example": "1"},
        "notices": {"example.dist-info/LICENSE": "notice"},
        "debian": manifest["debian_packages"],
        "native": {"/lib/example.so": "native"},
        "sources": {"source.tar.gz": "source"},
    }
    return manifest, copy.deepcopy(actual)


def test_inventory_gate_and_unresolved_license():
    manifest, actual = fixture_inventory()
    assert validate_inventory(actual, manifest) == []
    manifest["blocking_issues"] = [{"id": "UNRESOLVED", "reason": "Exact source not established"}]
    assert validate_inventory(actual, manifest) == ["UNRESOLVED: Exact source not established"]


@pytest.mark.parametrize("field", ["python", "debian", "notices", "native", "sources"])
def test_dependency_or_source_drift_rejects(field):
    manifest, actual = fixture_inventory()
    actual[field] = [] if field == "debian" else {}
    assert validate_inventory(actual, manifest)


def test_secret_crossing_read_boundary():
    secret = b"synthetic-private-value"
    assert scan_stream(io.BytesIO(b"x" * (1024 * 1024 - 4) + secret), [secret])
    assert scan_stream(io.BytesIO(b"ghp_" + b"a" * 36))
    assert not scan_stream(io.BytesIO(b"ordinary source code"))


def image_archive(path, layers):
    """Create a tiny synthetic docker-save archive, including hidden earlier layers."""

    def add(archive, name, data):
        info = tarfile.TarInfo(name)
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))

    with tarfile.open(path, "w") as outer:
        names = []
        for index, files in enumerate(layers):
            buffer = io.BytesIO()
            with tarfile.open(fileobj=buffer, mode="w") as inner:
                for name, data in files.items():
                    add(inner, name, data)
            name = f"layer-{index}.tar"
            names.append(name)
            add(outer, name, buffer.getvalue())
        add(outer, "manifest.json", json.dumps([{"Layers": names}]).encode())


def test_every_layer_including_deleted_secret_is_checked(tmp_path):
    archive = tmp_path / "image.tar"
    image_archive(archive, [{"workspace/.env": b"private"}, {"workspace/.wh..env": b""}])
    result = scan_layers(archive, {}, {})
    assert result["layers"] == 2
    assert any("workspace/.env" in error for error in result["errors"])


def test_exact_application_and_source_allowlists(tmp_path):
    archive = tmp_path / "image.tar"
    source = b"public third-party archive"
    app = b"safe application"
    image_archive(archive, [{"workspace/app/main.py": app, "usr/share/doc/project8-api/sources/public.tar.gz": source}])
    expected = {"workspace/app/main.py": hashlib.sha256(app).hexdigest()}
    sources = {"public.tar.gz": hashlib.sha256(source).hexdigest()}
    assert scan_layers(archive, expected, sources)["errors"] == []
    assert scan_layers(archive, expected, {})["errors"]
    assert scan_layers(archive, {}, sources)["errors"]


def test_failed_source_download_preserves_existing_and_removes_temporary(tmp_path):
    item = {
        "filename": "source.tar.gz",
        "size": 4,
        "sha256": hashlib.sha256(b"good").hexdigest(),
        "url": "https://example.org/source.tar.gz",
    }
    existing = tmp_path / item["filename"]
    existing.write_bytes(b"old")
    with patch("scripts.release_preflight.urllib.request.urlopen", return_value=io.BytesIO(b"bad!")):
        with pytest.raises(ValueError, match="hash/size mismatch"):
            download_source(item, tmp_path)
    assert existing.read_bytes() == b"old"
    assert not list(tmp_path.glob("*.part"))


def test_source_context_rejects_unexpected_private_file(tmp_path):
    (tmp_path / ".env").write_text("synthetic")
    with pytest.raises(ValueError, match="unexpected files"):
        bundle_sources({"source_archives": []}, tmp_path)


def test_pdf_rejected_even_if_accidentally_in_application_copy_set(tmp_path):
    archive = tmp_path / "image.tar"
    image_archive(archive, [{"workspace/tests/private.pdf": b"synthetic"}])
    result = scan_layers(archive, {"workspace/tests/private.pdf": hashlib.sha256(b"synthetic").hexdigest()}, {})
    assert any("Forbidden application asset" in error for error in result["errors"])


def test_public_fixture_exception_is_hash_pinned_and_never_hides_configured_secrets(tmp_path):
    archive = tmp_path / "image.tar"
    name = "usr/lib/example-test-key"
    data = b"-----BEGIN " + b"PRIVATE KEY----- synthetic-public-fixture"
    image_archive(archive, [{name: data}])
    fixture = [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}]
    assert scan_layers(archive, {}, {})["errors"]
    assert scan_layers(archive, {}, {}, public_fixtures=fixture)["errors"] == []
    assert scan_layers(archive, {}, {}, secrets=[b"synthetic-public-fixture"], public_fixtures=fixture)["errors"]
    fixture[0]["sha256"] = "changed"
    assert scan_layers(archive, {}, {}, public_fixtures=fixture)["errors"]


def test_workflow_is_manual_main_only_and_gates_before_token_login():
    import yaml
    from pathlib import Path

    workflow = yaml.load(Path(".github/workflows/publish-api.yml").read_text(), Loader=yaml.BaseLoader)
    assert list(workflow["on"]) == ["workflow_dispatch"]
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["publish"]
    assert job["if"] == "github.ref == 'refs/heads/main'"
    assert job["permissions"] == {"contents": "read", "packages": "write"}
    steps = job["steps"]
    gate = next(i for i, step in enumerate(steps) if "release_preflight check" in step.get("run", ""))
    login = next(i for i, step in enumerate(steps) if "docker login" in step.get("run", ""))
    push = next(i for i, step in enumerate(steps) if "docker push" in step.get("run", ""))
    assert gate < login < push
    assert not steps[gate].get("continue-on-error")


def test_clearing_blocker_flag_does_not_bypass_missing_native_source_mapping():
    manifest, actual = fixture_inventory()
    path = "/lib/libquadmath.so"
    manifest["native_libraries"] = [{"path": path, "sha256": "native"}]
    actual["native"] = {path: "native"}
    assert "libquadmath corresponding-source mapping incomplete" in validate_inventory(actual, manifest)
    manifest["native_source_evidence"] = [
        {"source_filename": "source.tar.gz", "source_sha256": "source", "wheel_paths": [path]}
    ]
    assert validate_inventory(actual, manifest) == []
