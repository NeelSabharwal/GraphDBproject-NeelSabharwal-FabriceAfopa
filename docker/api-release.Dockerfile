# API-only wrapper. Build the root Dockerfile first; existing Compose images are unchanged.
ARG API_IMAGE=project8-api:release-base
FROM ${API_IMAGE}
# The named context contains only hash-verified public third-party source archives.
COPY --from=redistribution_sources / /usr/share/doc/project8-api/sources/
