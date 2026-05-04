# GitHub Actions Pipelines Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Schedule the MLB Stats ingestion + dbt pipeline and the Firecrawl scrape pipeline on daily GitHub Actions workflows, running April–September.

**Architecture:** Two separate workflow files — `pipeline.yml` (ingest job → transform job) and `scrape.yml` (scrape job with git commit-back). A `profiles.yml` committed to the repo root lets dbt read Snowflake credentials from env vars injected by GitHub Secrets. The ingestion script is updated to auto-detect the current season year.

**Tech Stack:** GitHub Actions, dbt 1.11.8 + dbt-snowflake 1.11.4, Python 3.11, Snowflake, Firecrawl API

---

## File Map

| Action | Path |
|--------|------|
| Modify | `ingestion/extract_mlb_stats.py` line 31 |
| Create | `profiles.yml` |
| Create | `.github/workflows/pipeline.yml` |
| Create | `.github/workflows/scrape.yml` |

---

### Task 1: Auto-detect season year

**Files:**
- Modify: `ingestion/extract_mlb_stats.py:31`

- [ ] **Step 1: Update SEASON to use current year**

Open `ingestion/extract_mlb_stats.py`. Line 31 currently reads:

```python
SEASON = "2024"
```

Change it to:

```python
SEASON = str(datetime.now().year)
```

`datetime` is already imported at the top of the file (`from datetime import datetime, timezone`), so no new import is needed.

- [ ] **Step 2: Verify the change**

```bash
python -c "
import sys
sys.path.insert(0, '.')
from datetime import datetime
season = str(datetime.now().year)
print('SEASON =', season)
assert len(season) == 4 and season.isdigit()
print('OK')
"
```

Expected output:
```
SEASON = 2026
OK
```

- [ ] **Step 3: Commit**

```bash
git add ingestion/extract_mlb_stats.py
git commit -m "Auto-detect current season year in extract_mlb_stats"
```

---

### Task 2: Create profiles.yml for CI

**Files:**
- Create: `profiles.yml`

dbt looks for `profiles.yml` in `~/.dbt/` by default, which doesn't exist on a GitHub Actions runner. Committing one to the repo root and passing `--profiles-dir .` to dbt commands solves this. Every credential field must use `env_var()` — no hardcoded values.

- [ ] **Step 1: Create `profiles.yml` in the repo root**

```yaml
sf_giants_analytics:
  target: ci
  outputs:
    ci:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: ACCOUNTADMIN
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}"
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}"
      schema: RAW
      threads: 4
```

`schema: RAW` is the default — the `generate_schema_name` macro in `macros/generate_schema_name.sql` overrides this to `STAGING` or `MART` for individual models.

- [ ] **Step 2: Validate YAML syntax**

```bash
python -c "import yaml; yaml.safe_load(open('profiles.yml')); print('valid YAML')"
```

Expected:
```
valid YAML
```

- [ ] **Step 3: Verify dbt can parse it with env vars set**

```bash
export SNOWFLAKE_ACCOUNT=wlgoqiq-psc32625
export SNOWFLAKE_USER=emmasprankle
export SNOWFLAKE_PASSWORD=your_password_here
export SNOWFLAKE_DATABASE=SF_GIANTS_DB
export SNOWFLAKE_WAREHOUSE=SF_GIANTS_WH
dbt debug --profiles-dir .
```

Expected last line:
```
All checks passed!
```

Unset env vars after:
```bash
unset SNOWFLAKE_ACCOUNT SNOWFLAKE_USER SNOWFLAKE_PASSWORD SNOWFLAKE_DATABASE SNOWFLAKE_WAREHOUSE
```

- [ ] **Step 4: Commit**

```bash
git add profiles.yml
git commit -m "Add CI profiles.yml using env_var() for all Snowflake credentials"
```

---

### Task 3: Create pipeline.yml

**Files:**
- Create: `.github/workflows/pipeline.yml`

Two jobs: `ingest` runs the Python extraction script, `transform` runs `dbt run` and `dbt test`. `transform` only starts if `ingest` succeeds (`needs: ingest`). Both jobs read Snowflake credentials from GitHub Secrets injected as env vars.

- [ ] **Step 1: Create `.github/workflows/` directory and `pipeline.yml`**

```yaml
name: Pipeline — MLB Stats + dbt

on:
  schedule:
    - cron: '0 9 * 4-9 *'
  workflow_dispatch:

jobs:
  ingest:
    runs-on: ubuntu-latest
    env:
      SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
      SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
      SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
      SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
      SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python ingestion/extract_mlb_stats.py

  transform:
    needs: ingest
    runs-on: ubuntu-latest
    env:
      SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
      SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
      SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
      SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
      SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: dbt run --profiles-dir .
      - run: dbt test --profiles-dir .
```

- [ ] **Step 2: Validate YAML syntax**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/pipeline.yml')); print('valid YAML')"
```

Expected:
```
valid YAML
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/pipeline.yml
git commit -m "Add pipeline.yml GitHub Actions workflow (ingest + dbt transform)"
```

---

### Task 4: Create scrape.yml

**Files:**
- Create: `.github/workflows/scrape.yml`

One job: runs the Firecrawl scrape then commits the resulting markdown files back to `main`. Two guards matter here:
- `[skip ci]` in the commit message prevents the pushed commit from re-triggering this workflow (infinite loop prevention).
- `git diff --staged --quiet ||` skips the commit entirely if no files changed (no empty commits).

- [ ] **Step 1: Create `.github/workflows/scrape.yml`**

```yaml
name: Scrape — FanGraphs

on:
  schedule:
    - cron: '0 9 * 4-9 *'
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    env:
      FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python ingestion/extract_fangraphs.py
      - name: Commit scraped files
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add knowledge/raw/
          git diff --staged --quiet || git commit -m "chore: update scraped FanGraphs data [skip ci]"
          git push
```

- [ ] **Step 2: Validate YAML syntax**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/scrape.yml')); print('valid YAML')"
```

Expected:
```
valid YAML
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/scrape.yml
git commit -m "Add scrape.yml GitHub Actions workflow (Firecrawl + commit-back)"
```

---

### Task 5: Add GitHub Secrets and validate

**Files:** none — configuration in GitHub UI

GitHub Secrets are set at: **repo → Settings → Secrets and variables → Actions → New repository secret**

- [ ] **Step 1: Add the five Snowflake secrets**

Add each of these, copying values from your local `.env`:

| Secret name | Value from `.env` |
|---|---|
| `SNOWFLAKE_ACCOUNT` | `wlgoqiq-psc32625` |
| `SNOWFLAKE_USER` | `emmasprankle` |
| `SNOWFLAKE_PASSWORD` | *(your password)* |
| `SNOWFLAKE_WAREHOUSE` | `SF_GIANTS_WH` |
| `SNOWFLAKE_DATABASE` | `SF_GIANTS_DB` |

- [ ] **Step 2: Add the Firecrawl secret**

| Secret name | Value from `.env` |
|---|---|
| `FIRECRAWL_API_KEY` | *(your Firecrawl key)* |

- [ ] **Step 3: Push all commits and trigger pipeline.yml manually**

```bash
git push
```

Then go to **repo → Actions → Pipeline — MLB Stats + dbt → Run workflow** and trigger it manually via `workflow_dispatch`. Watch the `ingest` job, then `transform` job run in sequence.

Expected: both jobs show green checkmarks. If either fails, the job log shows which step errored.

- [ ] **Step 4: Trigger scrape.yml manually**

Go to **repo → Actions → Scrape — FanGraphs → Run workflow** and trigger via `workflow_dispatch`.

Expected: `scrape` job runs, FanGraphs pages are fetched, a commit appears on `main` with message `chore: update scraped FanGraphs data [skip ci]`, and no second workflow run is triggered.
