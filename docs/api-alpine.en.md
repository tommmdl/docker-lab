# A separate Alpine API preview

Run `bash scripts/api-alpine.sh up -d --no-build --wait` and open http://localhost:8016. This uses its own project/database volume and does not replace the default API. Stop with `bash scripts/api-alpine.sh down`; the volume is retained. Build explicitly with `images/api-alpine/Dockerfile`, or use the published digest pinned by the overlay. `python3 tests/api_alpine.py` checks basic and traced images in unique disposable projects; only their own volumes are removed.

[Full bilingual analysis, tracing results and complete scans](https://github.com/tommmdl/security-lab/blob/main/docs/api-alpine.en.md).
