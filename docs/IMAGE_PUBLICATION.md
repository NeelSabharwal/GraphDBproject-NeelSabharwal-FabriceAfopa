# API image publication — local gates passed; reviewed-main publication pending

The owner authorizes public publication of **only the API image**, after all release
gates pass. The source repository remains **PRIVATE**. No API image has been pushed,
no package visibility changed, and no registry digest or anonymous-pull success is
claimed. The intended package is:
`ghcr.io/neelsabharwal/graphdbproject-neelsabharwal-fabriceafopa-api`.

## What changed after merged PR #13

The release worktree is based on reviewed main
`d35cd2e5c145f38c5c041f6b05768d6b50b86a32`. Application code, dependency versions,
ordinary Compose Dockerfile/services, scientific graph, approvals and the frozen
0/5 ML experiment are unchanged. Local release candidates add proposed packaging
files on that baseline; their revision label identifies the application baseline,
not a claim that uncommitted packaging was already reviewed. The actual workflow
requires an exact committed current-main revision after review/merge.

The previous personal-credential limitation is avoided by a **manual-only GitHub
Actions workflow** using its short-lived `GITHUB_TOKEN`. No PAT is requested or stored.
Repository default workflow permissions were observed as `read`; the publication job
explicitly requests only `contents: read` and `packages: write`. Successful package
authorization is not claimed until that reviewed workflow actually runs.

## Redistribution checks and resolved native-source mapping

[Recipient source/notice record](../docker/licenses/SOURCE_ACCESS.md) and the
[machine-readable manifest](../docker/licenses/release-manifest.json) record the exact
versions, source URLs, hashes, notices and remaining issue. Actual checks:

- 94 Python distributions and 105 Debian binary packages inventoried.
- All 105 Debian binaries mapped to 73 exact source-package versions in official
  Debian/security Sources indexes. Every source URL responded; all `.dsc` hashes
  matched. Then **all 245 selected source archives/descriptors** were downloaded and
  verified against size/SHA-256, including the six selected Python sdists, ZeroMQ and two GCC source RPMs.
- orjson 3.13.0 source was downloaded from PyPI and verified as
  `d1de5eb04485110c5da4c657e49168995d55e076b1ce60f1a042e254f4186c4f`.
  Rust/C source, Cargo/build metadata and 22 vendored crate manifests were inspected;
  45 license/notice texts are retained separately with only trailing whitespace normalized.
- Exact certifi, pathspec, pylint, astroid and pyzmq source distributions were checked;
  actual bundled ZeroMQ 4.3.5 matches its source recipe/release archive. MPL source
  access, GPL/LGPL source delivery, Apache/other attribution and GCC runtime exception
  scope are distinguished. Permissive licenses are not assumed to require full sources.
- `docker/api-release.Dockerfile` wraps the existing API image and includes the verified
  public source bundle at `/usr/share/doc/project8-api/sources/`. This supplies source
  alongside the binary instead of relying solely on upstream URLs/private repository
  access. The ordinary Compose image does not acquire the large source bundle.

**Resolved: `LIBQUADMATH-SOURCE`.** Initial string inspection could not identify
three stripped wheel libraries. A final metadata check found SciPy's auditwheel SBOM,
which named AlmaLinux libquadmath 8.5.0-28.el8_10.alma.1. Actual official RPM comparison
then established all three mappings using matching ELF build IDs and identical
`.text`, `.rodata` and `.data` section hashes:

| Wheel libraries | Exact matching source RPM |
|---|---|
| NumPy libquadmath-2284e583-a9307bba.so.0.0.0 and SciPy libquadmath-2284e583.so.0.0.0 | gcc-8.5.0-28.el8_10.alma.1.src.rpm |
| SciPy libquadmath-96973f99-934c22de.so.0.0.0 | gcc-4.8.5-44.el7.src.rpm |

The source RPM filenames come from the matched binary RPM headers, not guesses based
on adjacent compiler strings. Exact official AlmaLinux/CentOS source RPMs were
downloaded/hash-pinned and inspected: each includes GCC source archives and gcc.spec,
with 59 and 136 distribution patches respectively. Both source RPMs are bundled.
The source hashes, official URLs, binary hashes and section comparisons are recorded
in `native_source_evidence`. Wheel repair modifies SONAME/RPATH metadata; executable
code/data match the mapped distribution libraries.

The **final real preflight exits 0**, with `publication_allowed: true` and no unresolved
manifest issues. The earlier failed reports are preserved. It has no force/ignore flag
and requires the native mappings plus their source archives even if someone merely
clears the generic blocking-issues list. Any future drift requires renewed review.
No remaining identified redistribution blocker is recorded for this candidate; this
is a scoped evidence conclusion, not a blanket legal or vulnerability certification.
No new project LICENSE was invented.

Publication is still **pending release-PR review/merge**. The workflow must be on main
and invoked with the full reviewed current-main SHA; a feature-branch run is not an
acceptable substitute. No external login/push was performed during this preparation.

## Actual local candidate audit

- Local image ID, **not registry digest**: `sha256:ea688da565fdfdd6bb12981a1809b546fd445af27e77f46b0c5e3271be2ed09e`.
- Architecture: linux/amd64; non-root appuser; size: 1,713,743,997 bytes.
- All 16 layers / 25,045 regular-file entries inspected.
- Application COPY contents must exactly match reviewed local inputs. Missing/changed
  dependency versions, native hashes, notices, source archives, unexpected files,
  PDFs, env files and model weights fail the gate. Configured secrets and generic
  token/private-key signatures are checked without logging their values.
- **Zero unknown content/secret findings** after three exact upstream-byte checks:
  five GnuTLS keys matched public FIPS self-test vectors in its pinned source archive;
  Tornado's test key matched its pinned public sdist; SciPy HiGHS token-like strings
  matched its exact public wheel. Only those file hashes are exempt from generic
  signatures. Any configured-secret match still blocks, even in those files.
- The source bundle contains public third-party code, not PDFs from the corpus, raw
  research text, gold/ML tables, database backups/volumes, weights, Git history or
  private reports. Neo4j/GDS binaries are not in this API image.
- Offline liveness and Swagger checks pass. This is not dependency readiness or a
  comprehensive vulnerability audit. All private logs/image archives stay ignored.

## Reproduce the candidate checks locally

From the reviewed checkout after the release PR is integrated:

```bash
release_revision=$(git rev-parse HEAD)
python3 -m scripts.release_preflight sources --output data/processed/release-sources
docker build --platform linux/amd64 \
  --label "org.opencontainers.image.revision=$release_revision" \
  -t project8-api:release-base .
docker build --platform linux/amd64 -f docker/api-release.Dockerfile \
  --build-context redistribution_sources=data/processed/release-sources \
  -t project8-api:release-candidate .
python3 -m scripts.release_preflight check --image project8-api:release-candidate \
  --revision "$release_revision" --output data/processed/release-preflight
```

Optional local `--secrets-file /absolute/path/to/.env` checks configured secret bytes
without printing or copying them. The final candidate passed this gate; rerun it for the committed release revision. Versions
and source hashes are pinned; byte-identical rebuilds are not guaranteed. Docker
image IDs are distinct from the registry manifest digest recorded after a real push.

## Exact GitHub operator steps

1. Review the release PR, including the resolved native-source mappings and gate
   implementation. Do not manufacture scientific/code review approvals. Merge only
   after required review and CI; this task does not merge the PR automatically.
2. In this private repository, open **Actions → Publish reviewed API image → Run
   workflow**. Select branch **main**. Paste the full 40-character SHA of current main
   into `revision`; click **Run workflow**. Choosing an unreviewed branch skips the
   publication job, and a different/main-stale SHA fails before build/login.
   Equivalent CLI after those gates are resolved:
   `gh workflow run publish-api.yml --repo NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa --ref main -f revision=FULL_REVIEWED_MAIN_SHA`.
3. The workflow downloads/verifies sources, builds only the API plus its source wrapper,
   scans every layer, checks liveness, refuses an existing `sha-<full-commit>` tag,
   then authenticates with `GITHUB_TOKEN` and pushes. It never runs on source pushes.
   The verified registry reference is saved in the job summary and private evidence
   artifact. SHA tags are not overwritten by this workflow; registry administrators
   could still retag manually, so deploy by the actual digest.
4. If GitHub refuses `packages: write`, inspect the actual job error and repository/
   organization Actions/package policy. Do not broaden permissions speculatively or
   create a PAT to bypass a policy. Source visibility must stay private.
5. After a successful push, open your GitHub profile → **Packages** →
   **graphdbproject-neelsabharwal-fabriceafopa-api** → **Package settings** →
   **Danger Zone → Change visibility → Public**, and confirm only that package name.
   Never use the source repository's visibility setting. This UI step may require
   the package administrator; no visibility change is claimed in advance.
6. Copy the real digest from the successful workflow and verify anonymous access:

```bash
release_image=ghcr.io/neelsabharwal/graphdbproject-neelsabharwal-fabriceafopa-api
read -r -p 'Actual registry digest (sha256:...): ' release_digest
[[ "$release_digest" =~ ^sha256:[0-9a-f]{64}$ ]] || exit 1
anonymous_config=$(mktemp -d)
DOCKER_CONFIG="$anonymous_config" docker pull "$release_image@$release_digest"
rmdir "$anonymous_config"
docker run --rm --network none --read-only \
  -e NEO4J_PASSWORD=synthetic-offline-smoke-password \
  --entrypoint python "$release_image@$release_digest" -c \
  'from fastapi.testclient import TestClient; from app.main import create_app; c=TestClient(create_app()); assert c.get("/health/live").status_code == 200; assert c.get("/docs").status_code == 200'
gh api repos/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa --jq .private
```

The last command must return `true`. Only after anonymous pull and offline smoke
succeed should README/R04 record the real public package URL, digest and publication
date. Source repository access and public package access are separate.
[GitHub's official GHCR authentication/visibility guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).
