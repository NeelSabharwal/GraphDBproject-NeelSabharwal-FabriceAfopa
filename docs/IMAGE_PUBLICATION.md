# API image publication — prepared, not published

Only the root API Dockerfile is eligible for this procedure. Publication is **not
authorized by the rubric-completion task**. No GHCR package URL or registry digest
is claimed. Proposed image reference:
`ghcr.io/neelsabharwal/graphdbproject-neelsabharwal-fabriceafopa-api`.

## Build and contents

The base is Python 3.12.13 slim-bookworm pinned by SHA-256; all Python packages use
`requirements.lock.txt`. The same dependency lock is used in CI and local tests.
This reproduces selected versions, not a guarantee of byte-identical builds: wheel
hashes are not locked and packaging timestamps can differ. Preserve the pushed digest
for deployment; do not use a floating `latest` tag as reproducibility evidence.

`.dockerignore` allowlists application/scripts/tests, dependency files, the pinned
corpus/citation/model manifests and third-party notices. The Dockerfile copies only
those API inputs. It excludes `.env`, Git/IDE files, raw PDFs, extracted text, gold
answers, ML annotations/models, database volumes, backups and generated reports.
No build secret arguments or host credentials are used. The image runs as `appuser`
(UID 10001); its Neo4j and Ollama dependencies remain separate services.

The local `project8-api:rubric-audit` build, offline endpoint smoke and filesystem
inspection are recorded in [FINAL_VALIDATION.md](FINAL_VALIDATION.md). This tag is
local only. Do not confuse a local image ID with a published registry digest.

## Licensing and visibility gates

- The repository is currently **private** and has no project LICENSE. A public API
  image exposes the copied application, scripts and tests. The owners must explicitly
  authorize this distribution and choose/document reuse terms; this task does not
  invent a license or change repository visibility.
- The pinned image contains 94 Python distributions. Preserve their bundled notices
  and the Debian/Python base notices. Two wheels omit separate notices; the exact
  upstream MIT notices for langchain-core 0.3.76 and langsmith 0.4.27 are retained in
  [docker/licenses](../docker/licenses/README.md) and copied into the image. This is
  a packaging check, not a legal opinion or a complete supply-chain security audit.
- Do not publish the custom Neo4j/GDS image. The GDS binary redistribution issue in
  [INFRASTRUCTURE.md](INFRASTRUCTURE.md) remains outside this release. Model/PDF terms
  do not grant redistribution rights, and none of those assets are in the API image.

## Exact operator procedure after separate approval

First review/commit/merge this branch through the normal PR workflow (not performed
by this task). Use the approved clean revision. Publication needs a GHCR account
with permission to create/write this package and a personal access token (classic)
with `write:packages` (and required SSO authorization if applicable). Do not reuse a
source-control token assuming it has package permissions. A future GitHub Actions
publisher can instead use its repository `GITHUB_TOKEN` with `contents: read` and
`packages: write`; no automatic publisher is enabled here.

```bash
# Run only after separate explicit publication approval, from a clean approved checkout.
test -z "$(git status --porcelain)" || exit 1
release_revision=$(git rev-parse HEAD)
release_image=ghcr.io/neelsabharwal/graphdbproject-neelsabharwal-fabriceafopa-api
release_tag="sha-${release_revision}"
docker build --pull --platform linux/amd64 \
  --label "org.opencontainers.image.revision=${release_revision}" \
  -t "${release_image}:${release_tag}" .
# Interactive password prompt: enter a suitably scoped token; never paste it into commands/logs.
docker login ghcr.io --username NeelSabharwal
docker push "${release_image}:${release_tag}"
```

GHCR packages are initially private. After approval, the package administrator must
change this package's visibility to **Public** in its GitHub package settings; linking
a private source repository does not prove anonymous image access. Public GHCR pulls
are free and support anonymous access. Check current account policies before release.
See [GitHub's container registry instructions](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
and [package visibility permissions](https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages).

Record the *actual* digest printed by the successful push. In a shell with the image
variables above, verify anonymous access using that digest and an empty Docker config:

```bash
read -r -p 'Paste the digest reported by docker push (sha256:...): ' release_digest
[[ "$release_digest" =~ ^sha256:[0-9a-f]{64}$ ]] || exit 1
anonymous_config=$(mktemp -d)
DOCKER_CONFIG="$anonymous_config" docker pull "${release_image}@${release_digest}"
# Only the newly created empty configuration directory is removed.
rmdir "$anonymous_config"
docker run --rm --network none --read-only \
  -e NEO4J_PASSWORD=synthetic-offline-smoke-password \
  --entrypoint python "${release_image}@${release_digest}" -c \
  'from fastapi.testclient import TestClient; from app.main import create_app; c=TestClient(create_app()); assert c.get("/health/live").status_code == 200; assert c.get("/docs").status_code == 200'
```

Then add the real package page URL, digest, anonymous-pull result and publication date
to README and R04. Offline liveness is not dependency readiness; the existing local
Compose readiness checks remain necessary. Stop on a failed build, login, push,
visibility or anonymous-pull check. Do not mark R04 verified merely from these commands.
