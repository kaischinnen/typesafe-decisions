# Development

## Set up the project

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[docs]"
```

The `docs` extra installs Zensical and mkdocstrings. They are development tools,
not runtime dependencies of `typesafe-decisions`.

## Preview the documentation

```bash
zensical serve
```

Open `http://localhost:8000`. Zensical watches the Markdown files, configuration,
and Python source used by the API reference.

## Build the documentation

```bash
zensical build --clean
```

The generated static site is written to `site/`. That directory is ignored by
Git because it can always be rebuilt.

## Run the tests

```bash
python3 -m unittest
```

Run the tests and documentation build before submitting a change that affects
the public API or an example.

## Publish with GitHub Pages

`.github/workflows/docs.yml` builds and deploys the site after a push to `main`.
In the GitHub repository settings, select **GitHub Actions** as the Pages source
before the first deployment.
