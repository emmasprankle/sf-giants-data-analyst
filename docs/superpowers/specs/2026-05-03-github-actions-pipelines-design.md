# GitHub Actions Pipelines Design

## Goal

Put both data pipelines on a daily schedule using GitHub Actions: the MLB Stats API ingestion + dbt transformation pipeline, and the Firecrawl FanGraphs scrape pipeline.

## Architecture

Two separate workflow files — one per pipeline. They share the same cron schedule but have different jobs, secrets, and output patterns. Keeping them separate means a Firecrawl failure never shows up alongside a dbt failure in the same run.

---

## Workflow 1: `pipeline.yml` — Stats + dbt

### Triggers
- **Cron:** `0 9 * 4-9 *` — daily at 9am UTC, April–September only. The month range in the cron expression is the off-season guard; the scheduler never fires outside the window.
- **`workflow_dispatch`:** manual trigger available year-round. Bypasses the month guard by design — useful for re-runs and backfills.

### Secrets required (set in GitHub repo → Settings → Secrets)
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`

### Jobs

**`ingest`** (`ubuntu-latest`)
1. Checkout repo
2. Set up Python 3.11
3. `pip install -r requirements.txt`
4. `python ingestion/extract_mlb_stats.py`

All five Snowflake secrets injected as env vars on the job.

**`transform`** (`ubuntu-latest`, `needs: ingest`)
1. Checkout repo
2. Set up Python 3.11
3. `pip install -r requirements.txt`
4. `dbt run --profiles-dir .`
5. `dbt test --profiles-dir .`

Same five Snowflake secrets as env vars. If either dbt command fails, the job fails and GitHub emails the repo owner.

### dbt credentials: `profiles.yml` in repo root

The `~/.dbt/profiles.yml` on the local machine is never committed. A separate `profiles.yml` is committed to the repo root that uses dbt's `env_var()` for every credential field — no hardcoded values. dbt commands use `--profiles-dir .` to find it.

### Code change: auto-detect season year

`ingestion/extract_mlb_stats.py` line 31 changes from:
```python
SEASON = "2024"
```
to:
```python
SEASON = str(datetime.now().year)
```

---

## Workflow 2: `scrape.yml` — Firecrawl FanGraphs

### Triggers
- **Cron:** `0 9 * 4-9 *` — same daily schedule as `pipeline.yml`.
- **`workflow_dispatch`:** manual trigger year-round.

### Secrets required
- `FIRECRAWL_API_KEY`

### Permissions
`contents: write` on the job — required to push the commit-back. Off by default in GitHub Actions.

### Job: `scrape` (`ubuntu-latest`)
1. Checkout repo
2. Set up Python 3.11
3. `pip install -r requirements.txt`
4. `python ingestion/extract_fangraphs.py`
5. Commit scraped files back to `main`:

```bash
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add knowledge/raw/
git diff --staged --quiet || git commit -m "chore: update scraped FanGraphs data [skip ci]"
git push
```

**`[skip ci]`** in the commit message prevents the scrape commit from re-triggering the workflow — without it, the commit would trigger another run, which would commit again, looping indefinitely.

**`git diff --staged --quiet ||`** guard skips the commit entirely if FanGraphs content is unchanged — no empty commits.

---

## File Map

| Action | Path |
|--------|------|
| Create | `.github/workflows/pipeline.yml` |
| Create | `.github/workflows/scrape.yml` |
| Create | `profiles.yml` (repo root) |
| Modify | `ingestion/extract_mlb_stats.py` (season year) |
