# Testing a different PostgreSQL image without reusing its data directory

[Português](postgres-alternative.md) · English

This page records the earlier isolated test. Alpine has since been adopted in Docker and Kubernetes; see the [current adoption and rollback procedure](postgres-adoption.en.md).

The alternative keeps PostgreSQL 17.11 and moves to Alpine 3.24.2, with libxml2 2.13.9-r2. The CVE-2026-6653 finding is absent. The raw official image brought back an old Go runtime in gosu, so our Dockerfile copies only the static, already-corrected helper from the pinned Bookworm derivative. Debian libraries do not enter the final filesystem. zlib is updated to the available 1.3.2-r1 package.

The full scan reports zero findings in this Trivy database snapshot, with package inventory present and the same policy. This is not a guarantee that the image has no vulnerabilities. Intermediate reports retain the upstream Go findings and the zlib finding before its update. [Complete comparison and sources](https://github.com/tommmdl/security-lab/blob/main/docs/postgres-alternative.en.md).

## An isolated application

The default Compose configuration, existing database volumes and Kubernetes application keep their Bookworm image. The alternative gets a separate project, API port and volume. After publication, its overlay pins the API and database by digest.

```bash
bash scripts/prepare.sh
bash scripts/alternative.sh up
bash scripts/alternative.sh status
```

Open http://localhost:8015. The local validation preview contains seven controlled Unicode notes, not a replacement for the live database. `bash scripts/alternative.sh down` preserves this alternative's volume.

## Logical restore, not an image swap over PGDATA

Alpine uses musl and UID 70; Bookworm uses glibc and UID 999. Locale behavior can differ. The target is initialized with ICU/en-US and UTF8 in a new volume. The original uses libc/en_US.utf8. Their provider/version metadata is recorded; the notes application sorts by numeric ID, so the tested path does not depend on title collation. This does not certify arbitrary text indexes, extensions or locale-dependent applications.

The test exports a custom-format pg_dump, restores into an empty target as the ordinary application role, then compares every note field, column properties, indexes and identity-sequence state. It exercises new generated IDs, benign XPath/XML, API behavior and persistence through container recreation. It then dumps the target back into a separate Debian database to check a logical rollback. The original source rows and sequence stay unchanged. No original data directory is mounted into Alpine.

```bash
bash scripts/alternative.sh test
```

The repeatable test has 17 migration checks, 23 API checks and 20 privilege/resource checks. The local run additionally restored private backups of the three existing labs into separate target databases and compared note fields. Those live databases were empty, so the seven-note fixture is the nonempty data-preservation test. Backups and note contents remain under ignored `.local/`; only result JSON is public.

Roles and authentication are created by the existing lab hardening hook rather than restoring all cluster globals. The app stays non-superuser; maintenance roles remain TCP-rejected. Dumps use no-owner/no-acl and target ownership is assigned to lab. This scope covers the notes schema, not all grants or extensions in a general shared cluster. Original services remain available for rollback; writes made only on the alternative would require a fresh reverse dump and controlled cutover before returning to the source.

For development, build the app and `images/postgres-alpine/Dockerfile` as local images, then run `python3 tests/postgres_alternative.py`. `ALTERNATIVE_API_IMAGE` and `POSTGRES_ALTERNATIVE_IMAGE` can select already-published images instead. `KEEP_ALTERNATIVE=1` keeps only the successful target; failed test environments are cleaned up. `ALTERNATIVE_LIVE_MANIFEST` is an optional local manifest of private dumps and comparison snapshots, never a CI artifact.

## Published and verified

[GitHub Actions](https://github.com/tommmdl/github-actions-lab/actions/runs/39181777856) passed the 17 migration, 23 API and 20 security checks, then published the tested images. The Compose alternative pins that API/image pair by digest. A full scan pulled from GHCR still reports zero findings; manifest hashes and image config digests match the CI-tested images. The complete [publication and scan evidence](https://github.com/tommmdl/security-lab/tree/main/evidence/postgres-alternative) remains available. This is a dated scanner snapshot, not a guarantee against future findings.
