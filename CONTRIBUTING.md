# Contributing & releasing

## Development

```bash
pip install -e ".[dev]"
ruff check src tests       # lint
ruff format src tests      # format
mypy -p trustat            # strict type-check
pytest -q                  # tests (respx-mocked, no network)
```

Or use the Makefile: `make install`, `make lint`, `make typecheck`, `make test`, `make build`.

## Models are generated

Response models in `src/trustat/_models/models.py` are **generated** from the OpenAPI
snapshot — do not hand-edit them. After the API contract changes, refresh
`codegen/openapi_snapshot.json` and run:

```bash
python scripts/generate_models.py
```

## Releasing to PyPI

Releases publish to PyPI automatically via GitHub Actions using **PyPI Trusted
Publishing** (OIDC) — no API tokens are stored.

### One-time setup (on PyPI)

1. Sign in at <https://pypi.org> with the Trustat-Analytics account.
2. Go to **Publishing → Add a pending publisher** and create:
   - **PyPI Project Name:** `trustat`
   - **Owner:** `Trustat-Analytics`
   - **Repository name:** `trustat-python`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
3. In the GitHub repo, create an **Environment** named `pypi`
   (Settings → Environments → New environment) — optionally add required reviewers
   so a human approves each publish.

### Cutting a release

1. Bump the version in `src/trustat/_version.py` and update `CHANGELOG.md`.
2. Commit and tag: `git tag v0.1.0 && git push --tags`.
3. Create a **GitHub Release** for that tag (Releases → Draft a new release).
4. Publishing the release triggers `.github/workflows/release.yml`, which builds the
   sdist + wheel, runs `twine check`, and publishes to PyPI via OIDC.

After it succeeds, `pip install trustat` installs the new version.
