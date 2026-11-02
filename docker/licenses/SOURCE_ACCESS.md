# Third-party redistribution record — API release candidate

This record concerns third-party software only. It grants no new license to Project 8
and does not change the private GitHub repository's visibility. The previously unresolved `LIBQUADMATH-SOURCE` mapping is now backed by exact RPM
and ELF evidence in `release-manifest.json`. Publication still requires the reviewed
main workflow and all its checks; no package has been published by this preparation.

## What recipients receive

The API-only release wrapper retains installed license/copyright files, this directory,
`orjson-vendored-NOTICES.txt`, and the hash-pinned `release-manifest.json`. It additionally
copies 245 verified upstream source archives/descriptors into `sources/`. These include
all 73 Debian source packages corresponding to the 105 installed binaries, six selected
Python source distributions, ZeroMQ 4.3.5, and the two matching GCC source RPMs. Sources are public third-party code, not
student PDFs, gold, labels, research exports, model weights or database data.

Every archive's exact URL, version, size and SHA-256 is recorded in the manifest. The
release tool downloads archives without executing/extracting their source and rejects
hash changes, unexpected files and partial downloads. The official Debian `.dsc`,
original archives and Debian patches/build rules are all included, including epoch
and binary-only rebuild distinctions in the installed-package mapping. Source files
are available alongside binaries in the same API image, rather than depending only
on a private repository, a generic project homepage or an unfulfilled written offer.

After a real release, recipients can use the published digest in place of IMAGE below:

```bash
container=$(docker create IMAGE)
docker cp "$container:/usr/share/doc/project8-api" ./project8-third-party
# Remove only this new stopped container; no data volumes or running services.
docker rm "$container"
```

Choose an unused destination directory. The manifest's upstream URLs provide an
additional source route; bundled bytes remain available even if those URLs change.
Original Debian notices are under `/usr/share/doc/*/copyright`; Python wheel notices
remain under `/usr/local/lib/python3.12/site-packages/*dist-info/`. CPython's own
license is retained under `/usr/local/lib/python3.12/LICENSE.txt`.

## Material conditions and evidence

| Components / terms | Distribution condition and concrete handling |
|---|---|
| MIT/BSD/ISC/PSF and similar permissive notices | Retain required copyright/license/disclaimer texts. All 94 distributions were inventoried; existing MIT notices supplement langchain-core 0.3.76 and langsmith 0.4.27. No blanket claim that metadata alone establishes compliance. |
| Apache-2.0 dependencies and vendored code | Preserve license and applicable NOTICE attribution; identify modifications if made. No third-party source was edited. Actual orjson source notices, including vendored Rust/C components, retain their wording; trailing line whitespace is normalized. No general requirement to ship every Apache source tree is inferred. |
| orjson 3.13.0, MPL-2.0 AND (Apache-2.0 OR MIT) | Exact PyPI source archive downloaded and SHA-256 verified; Cargo manifest, Rust/C source and 22 vendored crate manifests inspected. All 45 source license/notice files retained separately, including build/optional components without claiming they are all linked. Exact source archive included for MPL source access. |
| certifi 2026.10.18 and pathspec 1.1.1, MPL-2.0 | Installed source and licenses retained; matching PyPI source archives downloaded, hash-verified and included. No source modifications or new restrictions on recipients' MPL rights. |
| pyzmq 27.2.0 / ZeroMQ 4.3.5 | Python wrapper BSD notice and bundled MPL ZeroMQ / ISC libsodium notices retained. `zmq.zmq_version()` returned 4.3.5, matching pyzmq's source build recipe. Matching ZeroMQ release archive downloaded, inspected, hash-pinned and included. |
| pylint 3.3.8 GPL-2.0-or-later / astroid 3.3.11 LGPL-2.1-or-later | Unmodified Python source/notice installations retained; full matching source distributions included, with tests/build metadata. Neither licenses the independent application merely through packaging these separate tools. |
| Debian GPL/LGPL native/system components | All 105 exact installed versions map to 73 official source packages. Source URLs responded; `.dsc` hashes matched official Sources indexes. The complete listed source set was subsequently downloaded and hash-verified. Providing sources alongside binaries addresses source delivery without relying on an indefinite third-party link or a new written offer. Dynamic libraries remain replaceable. |
| NumPy/SciPy native OpenBLAS/LAPACK and GCC runtimes | Bundled wheel notices include BSD terms and GPL with GCC Runtime Library Exception for designated runtimes. Do not extend that exception to other libraries. The binary inventory preserves actual hashes and observed compiler strings; these do not identify stripped sibling libraries' source revisions. |
| Three bundled libquadmath binaries, LGPL-2.1-or-later | SciPy auditwheel SBOM identified an AlmaLinux version; all three wheel files were then matched to official RPMs by ELF build ID and identical `.text`, `.rodata`, `.data` hashes. Two match AlmaLinux GCC 8.5.0-28.el8_10.alma.1; one matches CentOS GCC 4.8.5-44.el7. Exact source RPMs named by those binary headers are downloaded/hash-pinned and bundled, with GCC archives, gcc.spec and 59 / 136 patches respectively. Wheel repair changes SONAME/RPATH metadata; source and executable code are preserved. |

The Debian bundle deliberately includes a small number of permissively licensed
packages as a convenient complete version-mapped set. This is a packaging choice,
not an assertion that those licenses require complete source distribution. The six
Python source distributions were selected for concrete source-access obligations;
all 94 Python source trees are not indiscriminately bundled.

Primary license texts consulted:
[Apache §4](https://www.apache.org/licenses/LICENSE-2.0),
[MPL §§3.1–3.4](https://www.mozilla.org/en-US/MPL/2.0/),
[LGPL 2.1 §§4/6](https://raw.githubusercontent.com/gcc-mirror/gcc/master/COPYING.LIB),
[GPLv3 §6](https://raw.githubusercontent.com/gcc-mirror/gcc/master/COPYING3).
GPLv2 and GCC exception texts were also inspected in the retained wheel/base notices.
These records establish checked components and the source-delivery route, not a
blanket legal certification. Native hashes and source mappings are rechecked for
every image; a dependency or source change requires renewed review.

## Public test material found by the secret-signature scan

The first all-layer scan stopped on three upstream artifacts. Follow-up checks found:

- Five complete keys embedded in GnuTLS match public FIPS self-test vectors in the
  exact, bundled Debian GnuTLS source archive; remaining markers are parser strings.
- Tornado's TLS test key exactly matches the hash-pinned public 6.6 source archive.
- The SciPy HiGHS binary's token-like byte sequences exactly match the public,
  hash-verified 1.18.1 CPython 3.12 manylinux wheel binary.

These are public upstream bytes, not operator credentials. Their exact paths, file
hashes and upstream evidence are recorded in `public_test_fixtures` in the manifest.
Only unchanged hashes are exempt from generic signatures. A changed file or any
configured-secret match still blocks publication. This distinction is covered by a
regression test; no blanket directory exemption or redacted success report is used.

## Exact wheel-native source evidence

The SciPy 1.18.1 wheel includes `sboms/auditwheel.cdx.json` (auditwheel 6.7.0);
NumPy's installed wheel has no SBOM. The SBOM alone did not establish both sources.
Subsequent independent binary comparison established:

| Matching wheel names | Official source package | ELF build ID |
|---|---|---|
| libquadmath-2284e583.so; libquadmath-2284e583-a9307bba.so (full names in manifest) | gcc-8.5.0-28.el8_10.alma.1.src.rpm | c1c5f8d61f17e5579c4e85718845b74e4b94116c |
| libquadmath-96973f99-934c22de.so (full name in manifest) | gcc-4.8.5-44.el7.src.rpm | 549b4c82347785459571c79239872ad31509dcf4 |

Alma source SHA-256: `c94dbbd2cd6d5d01a5a6822ea18f8ce34942c25a80e17b4682d547d5e652dbd0`.
CentOS source SHA-256: `642c4085f6af9565e39583e54a9d7a5d9e6b93dd8c8e9474aec8a892d6c7aa36`.
Exact official URLs, binary RPM hashes, matching section hashes and the wheel-file
mapping are retained in `native_source_evidence`. Archives are public upstream
packages, not rebuilt from an arbitrary GCC version. The preflight requires these
mappings and matching source archives even if the generic blocking-issues list is empty.
