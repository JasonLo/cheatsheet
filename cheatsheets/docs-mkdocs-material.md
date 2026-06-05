# Documentation sites with MkDocs Material

_Grounded in JasonLo's repos as of 2026-06-05; current practice per squidfunk/mkdocs-material docs (context7)._

## Reference snippet

```yaml
# mkdocs.yml — minimal, idiomatic present-day Material site
site_name: My Project
site_url: https://jasonlo.github.io/my-project/   # required: SEO, social cards, instant nav
repo_url: https://github.com/JasonLo/my-project

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"       # auto light/dark via media queries
      scheme: default
      toggle: { icon: material/weather-sunny, name: Switch to dark mode }
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle: { icon: material/weather-night, name: Switch to light mode }
  features:
    - navigation.instant            # SPA-style page loads
    - navigation.instant.prefetch   # prefetch on hover (newer)
    - navigation.tabs
    - navigation.sections
    - content.code.copy             # copy button on code blocks

plugins:
  - search
  - mkdocstrings:                    # auto API docs from docstrings
      handlers:
        python:
          options: { show_source: false }

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences            # required for code highlight, tabs, mermaid
  - pymdownx.highlight: { anchor_linenums: true }
  - pymdownx.arithmatex: { generic: true }   # math (MathJax/KaTeX)
  - toc: { permalink: true }
```

```bash
uv run mkdocs serve     # live-reload dev server at :8000
uv run mkdocs build      # static site -> site/
uv run mkdocs gh-deploy  # build + push to gh-pages branch
```

## Typical usage patterns

- Material theme with dual light/dark `palette` blocks keyed on `prefers-color-scheme` + a toggle — your default look. (`JasonLo/connectionist:mkdocs.yml`)
- API reference auto-generated with `mkdocstrings` (python handler) — write a stub page per symbol containing only a `::: module.Class` block; docstrings render the rest. (`JasonLo/connectionist:docs/models/PMSP.md`)
- Navigation features `navigation.instant` + `navigation.tabs` + `navigation.sections` + `content.code.copy` as the standard feature set. (`JasonLo/connectionist:mkdocs.yml`)

## Learnings

- **Reach for raw MkDocs features → reach for Material theme features first.** Tabs, instant nav, code-copy, palette toggle, search ship as `theme.features`/`palette` flags — declarative config, not custom HTML/CSS/plugins.
- **`site_url` is cosmetic / optional → it is load-bearing.** Social cards, sitemap/SEO, and `navigation.instant` correctness all depend on it; omitting it silently degrades those features.
- **Docstrings live in the docs prose → docstrings ARE the docs.** mkdocstrings inverts ownership: a reference page is a one-line `:::` directive and the source docstring is the single source of truth — edit code, not the doc page.

## Agent rules

- ALWAYS set `theme.name: material` and prefer `theme.features` flags over custom HTML/CSS/JS for nav, code-copy, tabs, and palette.
- ALWAYS set a real `site_url` in `mkdocs.yml`.
- ALWAYS use `pymdownx.arithmatex` with `generic: true` for math; do not introduce `markdown_katex` or bespoke math plugins.
- ALWAYS include `pymdownx.superfences` when using code highlighting, content tabs, or mermaid.
- ALWAYS document a Python API with `mkdocstrings` `:::` autodoc directives and keep prose in docstrings, not in the `.md` page.
- ALWAYS pair `navigation.instant` with `navigation.instant.prefetch`.
- ALWAYS provide light + dark `palette` entries keyed on `prefers-color-scheme` with a toggle.
- ALWAYS run dev/build via `mkdocs serve` / `mkdocs build`, and add a `watch:` list when docs depend on source docstrings.
- NEVER hand-build theme behaviors (tabs, dark mode, copy buttons) that a Material feature flag already provides.
- NEVER duplicate docstring content into reference pages.
