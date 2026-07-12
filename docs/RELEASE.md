# Release `stubborn-status`

## Automated (GitHub Actions)

1. Ensure repository secret **`PYPI_API_TOKEN`** is set.
2. For the **first** upload of package name `stubborn-status`, the token must have
   **Entire account (all projects)** scope on PyPI — project-scoped tokens copied
   from `stubborn-stub` / `stubborn-mcp` / `stubborn-watch` cannot create a new
   project.
3. Push tag `v0.10.0b1` (or run **Actions → Release → Run workflow**).

```bash
git tag -a v0.10.0b1 -m "Release stubborn-status 0.10.0b1."
git push origin v0.10.0b1
```

## Manual fallback

```bash
python -m pip install build twine
python -m build
TWINE_USERNAME=__token__ TWINE_PASSWORD=<pypi-api-token> \
  python -m twine upload dist/*
```

After the first successful upload, a project-scoped token for `stubborn-status`
is sufficient for later releases.

## Verify

```bash
python3 -c "import json,urllib.request; print(json.load(urllib.request.urlopen('https://pypi.org/pypi/stubborn-status/json'))['info']['version'])"
```

Hub release matrix: `stubborn-hub/scripts/check_release_matrix.py --pypi`
