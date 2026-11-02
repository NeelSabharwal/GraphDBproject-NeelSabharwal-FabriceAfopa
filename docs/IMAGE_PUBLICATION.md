# API image publication — authorized, blocked before publication

The owner explicitly authorizes **only the API image** to become public once all
security/content/redistribution checks pass. The source repository must remain
**PRIVATE**. No package was pushed, visibility changed or anonymous pull claimed.
Intended package name (not an existing published-image claim):
`ghcr.io/neelsabharwal/graphdbproject-neelsabharwal-fabriceafopa-api`.

## Current blockers and actual checks — 2026-11-02

1. **Authentication:** the authorized Windows GitHub CLI account is NeelSabharwal,
   with `gist`, `read:org`, `repo`, `workflow` OAuth scopes, but no `write:packages`.
   Docker's desktop credential store lists no registry logins. No token was printed,
   requested in chat, refreshed to broader scopes or used for a failed upload.
2. **Redistribution evidence:** 94 installed Python distributions and 105 base-system
   copyright files were inventoried. All Python wheels retain notices except the
   two MIT notices supplied separately below. This is not a complete source-delivery
   compliance record. The image includes pylint 3.3.8 (GPL-2.0-or-later), astroid
   3.3.11 (LGPL-2.1-or-later), certifi 2026.10.18 (MPL-2.0), orjson 3.13.0
   (MPL-2.0 AND Apache-2.0-or-MIT), and Debian/native binary components. In particular,
   orjson's wheel contains license texts and a general upstream source URL, but no
   Cargo/source tree; an accessible exact-version corresponding-source route and
   recipient notice were not verified. Debian package source/build coverage likewise
   has not been established for every included binary. **Do not treat unknown or
   unverified obligations as permission.** This is an evidence gap, not a finding that
   these open-source licenses prohibit redistribution or require this GitHub repository
   to become public. Complete the source/notice mapping before any push. Mozilla's
   [MPL distribution FAQ, Q7–Q8](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)
   explains the relevant source-availability checks for libraries.

The final local API image is `linux/amd64`, 794,328,467 bytes, with 15 layers and
non-root `appuser` (UID 10001). Local image ID:
`sha256:422b77a9635d5b585385c241a39668674827cef0c2959ef0eaee20a46c3e4477`.
This is **not a registry manifest digest**. Every regular file in all saved layers
was checked for configured secret bytes; workspace token/private-key signatures and
forbidden paths had zero matches. No PDFs, raw exports, gold/ML annotation tables,
Neo4j data/GDS binaries, model weights, Git history or private reports were found in
the copied project files. Tests and tiny synthetic fixtures remain intentionally
included for the documented test workflow. This scoped scan is not a vulnerability
assessment or proof against every possible secret format. Details remain in ignored
`data/processed/final-acceptance/image-audit.json` and `license-inventory.json`.

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

The earlier `project8-api:rubric-audit` checks and the new final API build are
recorded separately in [FINAL_VALIDATION.md](FINAL_VALIDATION.md). Both are local only.

## Licensing and visibility gates

- The repository is currently **private** and has no project LICENSE. A public API
  image exposes the copied application, scripts and tests. The owners must explicitly
  authorize this distribution; that authorization is now explicit. No new reuse
  license is inferred or added, and repository visibility is unchanged.
- The pinned image contains 94 Python distributions. Preserve their bundled notices
  and the Debian/Python base notices. Two wheels omit separate notices; the exact
  upstream MIT notices for langchain-core 0.3.76 and langsmith 0.4.27 are retained in
  [docker/licenses](../docker/licenses/README.md) and copied into the image. This is
  a packaging check, not a legal opinion or a complete supply-chain security audit.
- Do not publish the custom Neo4j/GDS image. The GDS binary redistribution issue in
  [INFRASTRUCTURE.md](INFRASTRUCTURE.md) remains outside this release. Model/PDF terms
  do not grant redistribution rights, and none of those assets are in the API image.

## Exact operator procedure after both blockers are resolved

First complete the exact-version source/notice checks above and retain the evidence.
Use the reviewed clean revision; this branch is not automatically merged. Publication
authorization already exists and need not be requested again. Publication needs a GHCR account
with permission to create/write this package and a personal access token (classic)
with `write:packages` (and required SSO authorization if applicable). Create it via
[GitHub’s minimal package-write token form](https://github.com/settings/tokens/new?scopes=write:packages);
enter it only at the local `docker login` password prompt, never in chat. Avoid adding
`repo` or `delete:packages` merely for this operation. Do not reuse a
source-control token assuming it has package permissions. A future GitHub Actions
publisher can instead use its repository `GITHUB_TOKEN` with `contents: read` and
`packages: write`; no automatic publisher is enabled here.

```bash
# Run only after source/notice verification and package authentication are resolved.
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

GHCR packages are initially private. After a successful authorized push, the package administrator must
open the account’s Packages → this API package → Package settings → Danger Zone,
and change **this package only** to **Public**. Do not change repository settings; linking
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
