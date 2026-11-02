# Dependency notices retained in the API image

These unchanged upstream notices supplement wheel installations that declare MIT
licensing but omit a separate license file. They do not license this project's code.

- `langchain-core` 0.3.76: https://raw.githubusercontent.com/langchain-ai/langchain/langchain-core%3D%3D0.3.76/LICENSE
  SHA-256: `4ec67e4ca6e6721dba849b2ca82261597c86a61ee214bbf21416006b7b2d0478`.
- `langsmith` 0.4.27, upstream tag commit `f034d39c68e69419a2995a3dfbf51e73474c0da6`:
  https://raw.githubusercontent.com/langchain-ai/langsmith-sdk/f034d39c68e69419a2995a3dfbf51e73474c0da6/LICENSE
  SHA-256: `34e0b9842c7a31d34e53bc7eb224e81e07a34996106e029bbc72dea2d449f496`.

The API Dockerfile copies this directory to `/usr/share/doc/project8-api/`.
Other installed Python distributions retain their wheel license/notice files;
Debian/Python base notices remain in the digest-pinned base image. Recheck this
inventory whenever the lock or base image changes. No Neo4j server, GDS JAR,
Ollama binary, model weights or source PDFs are bundled here.
