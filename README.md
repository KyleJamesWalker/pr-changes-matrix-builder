# PR Changes Matrix Builder

A GitHub Action that inspects which files changed in a pull request and outputs a dynamic JSON matrix — one entry per unique matched component. Downstream jobs use the matrix to fan out work in parallel, running only for the components that actually changed.

Common use cases:
- **Docker image monorepos** — build and test only the images whose folders changed
- **Schema / data contract repos** — validate only the schemas that were modified
- **Terraform repos** — plan only the infrastructure folders that changed
- **Helm / ArgoCD repos** — release only the charts or app definitions that were touched

## How It Works

1. Fetches the list of changed files from the PR using `gh pr view --json files`
2. Filters files against `paths_include` / `paths_ignore` glob patterns
3. Applies `extract_re` (a Python regex with named groups) to each surviving file path
4. Deduplicates extracted values — multiple changed files in the same component produce one matrix entry
5. Merges parameters in three layers (lowest → highest priority):
   - `default_params` — applied to every entry
   - `inject_params[<primary_key_value>]` — applied when the extracted primary key matches a key in `inject_params`
   - Extracted regex groups — always win; cannot be overridden

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `github_token` | No | `${{ github.token }}` | Token used to call `gh pr view`. Use a CI service account token for cross-repo workflows. |
| `repo` | No | `${{ github.event.repository.full_name }}` | Repository in `owner/repo` format. Override when the workflow runs in a different repo than the one being inspected. |
| `pr_number` | No | `${{ github.event.number }}` | PR number to inspect. |
| `extract_re` | No | `(?P<project_name>.*)/.*` | Python regex with one or more named groups (e.g. `(?P<project_name>.*)/.*`). Each matched file contributes its captured groups as matrix fields. |
| `paths_include` | No | _(all files)_ | JSON array of glob patterns. Only files matching at least one pattern are considered. Omit or set to `'["**"]'` to include all files. |
| `paths_ignore` | No | _(none)_ | JSON array of glob patterns. Files matching any pattern are excluded. Applied after `paths_include`. |
| `default_params` | No | `'{}'` | JSON object merged into every matrix entry. Useful for common fields like `environment` or `region`. |
| `inject_primary_key` | No | _(none)_ | Name of the extracted regex group used as a lookup key into `inject_params`. |
| `inject_params` | No | `'{}'` | JSON object where keys are possible values of `inject_primary_key` and values are parameter objects to merge into matching entries. |

## Outputs

| Output | Type | Description |
|---|---|---|
| `matrix` | JSON array string | Array of objects. Each object contains the extracted regex groups plus any injected parameters. Pass to `fromJson()` in a `strategy.matrix` block. |
| `matrix-populated` | `'true'` / `'false'` | Whether `matrix` contains any entries. Use in `if:` conditions to skip downstream jobs when nothing changed. |

## Examples

### Minimal — detect changed top-level folders

The default regex `(?P<project_name>.*)/.*` captures the top-level folder from every changed file. This is the most common pattern for root-level monorepos.

```yaml
jobs:
  pr-changes:
    runs-on: ubuntu-latest
    outputs:
      matrix-params: ${{ steps.matrix-builder.outputs.matrix }}
      matrix-populated: ${{ steps.matrix-builder.outputs.matrix-populated }}
    steps:
      - name: PR Changes Matrix Builder
        uses: KyleJamesWalker/pr-changes-matrix-builder@v0
        id: matrix-builder
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          paths_ignore: '[".github/**"]'

  build:
    needs: [pr-changes]
    if: needs.pr-changes.outputs.matrix-populated == 'true'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        params: ${{ fromJson(needs.pr-changes.outputs.matrix-params) }}
    steps:
      - run: echo "Building ${{ matrix.params.project_name }}"
```

**Changed files:** `service-a/main.py`, `service-a/tests/test_main.py`, `service-b/Dockerfile`, `.github/workflows/ci.yaml`

**Matrix output:**
```json
[
  {"project_name": "service-a"},
  {"project_name": "service-b"}
]
```

`.github/` files are excluded by `paths_ignore`. `service-a` appears only once despite two changed files.

---

### Scoped to a subdirectory

When components live under a common prefix, use `paths_include` to restrict scope and embed the prefix in `extract_re` to strip it from the captured value.

```yaml
- uses: KyleJamesWalker/pr-changes-matrix-builder@v0
  id: matrix-builder
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    extract_re: "packages/(?P<project_name>.*)/.*"
    paths_include: '["packages/**"]'
    paths_ignore: '[".github/**", "tools/**", "tests/**", "**/README.md"]'
```

**Changed files:** `packages/auth-service/handler.py`, `tools/validate.py`, `packages/billing-service/models.py`

**Matrix output:**
```json
[
  {"project_name": "auth-service"},
  {"project_name": "billing-service"}
]
```

`tools/validate.py` is excluded by `paths_ignore`. The `packages/` prefix is stripped by the regex so `project_name` is just the component name.

---

### Per-component parameter injection

Use `inject_params` to attach component-specific configuration (e.g. different runners, flags, or environment values) without a separate lookup step.

```yaml
- uses: KyleJamesWalker/pr-changes-matrix-builder@v0
  id: matrix-builder
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    extract_re: "(?P<project_name>.*)/.*"
    paths_ignore: '[".github/**"]'
    default_params: '{"environment": "staging"}'
    inject_primary_key: project_name
    inject_params: |
      {
        "gpu-service": {"runner": "gpu-runner", "needs_gpu": true},
        "heavy-service": {"runner": "large-runner"}
      }
```

**Changed files:** `gpu-service/train.py`, `api-service/handler.py`

**Matrix output:**
```json
[
  {"project_name": "gpu-service",  "environment": "staging", "runner": "gpu-runner", "needs_gpu": true},
  {"project_name": "api-service",  "environment": "staging"}
]
```

`api-service` has no entry in `inject_params`, so it gets only `default_params`.

---

### Guard on the matrix job itself (release workflows)

For release/tag workflows that only run on merged PRs, put the `if:` condition on the matrix-builder job directly rather than on all downstream jobs.

```yaml
jobs:
  pr-changes:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    outputs:
      matrix-params: ${{ steps.matrix-builder.outputs.matrix }}
      matrix-populated: ${{ steps.matrix-builder.outputs.matrix-populated }}
    steps:
      - uses: KyleJamesWalker/pr-changes-matrix-builder@v0
        id: matrix-builder
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          extract_re: "packages/(?P<project_name>.*)/.*"
          paths_include: '["packages/**"]'
          paths_ignore: '[".github/**", "tools/**", "**/README.md"]'

  tag-create:
    needs: [pr-changes]
    if: needs.pr-changes.outputs.matrix-populated == 'true'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        params: ${{ fromJson(needs.pr-changes.outputs.matrix-params) }}
    steps:
      - name: Create release
        run: |
          gh release create "${{ matrix.params.project_name }}-v${{ github.run_number }}" --generate-notes
```

---

### Serialized matrix jobs (avoid race conditions)

When all matrix entries write to shared state — like committing version bumps to the same branch — use `max-parallel: 1` to serialize execution.

```yaml
  version-bump:
    needs: [pr-changes]
    if: needs.pr-changes.outputs.matrix-populated == 'true'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      max-parallel: 1   # prevent concurrent git pushes to the same branch
      matrix:
        params: ${{ fromJson(needs.pr-changes.outputs.matrix-params) }}
    steps:
      - uses: actions/checkout@v4
      - run: |
          git pull --no-rebase
          # your per-component version bump here
          git add ${{ matrix.params.project_name }}
          git commit -m "Bump ${{ matrix.params.project_name }}"
          git push
```

---

### Matrix enrichment (two-stage pattern)

When per-component configuration lives in files inside the repo (e.g. YAML front matter in each component's `README.md`), use an intermediate job to enrich the matrix before expanding it.

```yaml
jobs:
  pr-changes:
    runs-on: ubuntu-latest
    outputs:
      matrix-params: ${{ steps.matrix-builder.outputs.matrix }}
      matrix-populated: ${{ steps.matrix-builder.outputs.matrix-populated }}
    steps:
      - uses: KyleJamesWalker/pr-changes-matrix-builder@v0
        id: matrix-builder
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          paths_ignore: '[".github/**"]'

  load-config:
    needs: [pr-changes]
    if: needs.pr-changes.outputs.matrix-populated == 'true'
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.enrich.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - name: Enrich matrix from per-component config
        id: enrich
        env:
          BASE_MATRIX: ${{ needs.pr-changes.outputs.matrix-params }}
        run: |
          out='[]'
          while read -r row; do
            name=$(echo "$row" | jq -r '.project_name')
            # read any per-component field from a config file in the component folder
            runner=$(jq -r '.runner // "ubuntu-latest"' "$name/component.json")
            out=$(echo "$out" | jq -c --arg r "$runner" '. + [$row + {runner: $r}]')
          done < <(echo "$BASE_MATRIX" | jq -c '.[]')
          echo "matrix=$out" >> "$GITHUB_OUTPUT"

  build:
    needs: [pr-changes, load-config]
    if: needs.pr-changes.outputs.matrix-populated == 'true'
    runs-on: ${{ matrix.params.runner }}
    strategy:
      fail-fast: false
      matrix:
        params: ${{ fromJson(needs.load-config.outputs.matrix) }}
    steps:
      - run: make build APP=${{ matrix.params.project_name }}
```

This keeps the action focused on change detection while allowing arbitrary per-component metadata to be loaded from the repo at runtime.

---

## Multiple capture groups

`extract_re` can define multiple named groups. Each group becomes a field in the matrix entry, and the deduplication key is the combination of all groups.

```yaml
extract_re: "(?P<project_name>[^/]+)/(?P<subpath>[^/]+)/.*"
```

**Changed files:** `service-a/v1/schema.avsc`, `service-a/v2/schema.avsc`, `service-b/v1/schema.avsc`

**Matrix output:**
```json
[
  {"project_name": "service-a", "subpath": "v1"},
  {"project_name": "service-a", "subpath": "v2"},
  {"project_name": "service-b", "subpath": "v1"}
]
```

Each unique `(project_name, subpath)` combination gets its own matrix entry.

## Tips

- **`paths_ignore` is evaluated after `paths_include`.** A file must first survive the include filter before the ignore filter is applied.
- **Extracted groups always win** over `default_params` and `inject_params`. You cannot override a captured group name with injected parameters.
- **The `matrix-populated` check is important.** GitHub Actions throws an error if `fromJson()` receives an empty array in a `strategy.matrix` block. Always guard downstream jobs with `if: needs.<job>.outputs.matrix-populated == 'true'`.
- **The action only reads PR file change metadata.** It does not check out your code. If you need per-component config from files in the repo, use the two-stage enrichment pattern above.
