# Baseball Pitching Performance Analytics Pipeline

A end-to-end data analytics pipeline built as a portfolio project targeting a **Baseball Operations Analyst** role with the San Francisco Giants.

## Project Overview

This project demonstrates the full lifecycle of a baseball analytics workflow: ingesting raw MLB pitching data, transforming it into a clean star schema, and surfacing actionable insights through an interactive dashboard. It also builds a Giants-focused knowledge base from press releases and FanGraphs articles.

**Key capabilities:**

- Automated daily ingestion of MLB pitching data via the MLB Stats API
- Multi-layer data transformation (raw → staging → mart) using dbt
- Pitcher performance star schema optimized for analysis
- Interactive Streamlit dashboard for exploring pitching trends
- Knowledge base of summarized Giants and FanGraphs content

## Pipeline Architecture

```mermaid
flowchart LR
    subgraph Sources["Sources"]
        A["MLB Stats API"]
        B["FanGraphs"]
        C["sfgiants.com"]
        D["Baseball Savant"]
    end

    subgraph Ingest["Ingestion · GitHub Actions"]
        E["extract_mlb_stats.py\nPython + requests"]
        F["extract_fangraphs.py\nFirecrawl API"]
    end

    subgraph Raw["Raw · Snowflake RAW schema"]
        G[("RAW.PLAYERS\nRAW.PITCHER_GAME_LOGS")]
        H["knowledge/raw/\n15 markdown files"]
    end

    subgraph Transform["Transform · dbt"]
        I["STAGING\nstg_players\nstg_pitcher_game_logs"]
        J["MART\ndim_pitcher · dim_game · dim_date\nfact_pitcher_game\nmart_pitcher_season · mart_pitcher_rolling"]
    end

    subgraph Serve["Serve"]
        K["Streamlit Dashboard\nStreamlit Community Cloud"]
        L["Knowledge Base"]
    end

    A --> E
    B & C & D --> F
    E --> G
    F --> H
    G --> I
    I --> J
    J --> K
    H --> L
```

## Tech Stack


| Layer          | Tool                        |
| -------------- | --------------------------- |
| Data Warehouse | Snowflake                   |
| Transformation | dbt                         |
| Orchestration  | GitHub Actions              |
| Dashboard      | Streamlit (Community Cloud) |
| Data Source    | MLB Stats API               |


## Repo Structure

```
sf-giants-data-analyst/
├── .github/
│   └── workflows/          # GitHub Actions pipeline (scheduled ingestion + dbt runs)
├── dashboard/              # Streamlit app
├── docs/                   # Project proposal and SF Giants job posting
├── knowledge_base/         # Scraped sources and summarized wiki pages
├── models/                 # dbt models
│   ├── raw/                # Raw source models
│   ├── staging/            # Cleaned and typed staging models
│   └── mart/               # Star schema mart models
├── CLAUDE.md               # Project context for AI-assisted development
└── README.md
```

## Portfolio Note

This project was built independently as a portfolio piece to demonstrate data engineering and baseball analytics skills for a Baseball Operations Analyst role at the San Francisco Giants. It reflects real-world practices in modern data stack tooling, MLB data sourcing, and baseball domain knowledge.