# Knowledge Base Index — SF Giants Pitching Analytics

*5 wiki pages · 26 raw sources scraped from 5 sites.*

---

## Wiki Pages

### Orientation

| Page | Summary |
|---|---|
| [overview.md](wiki/overview.md) | Org philosophy (ground ball / walk suppression / park exploitation), 2024 rotation and bullpen by tier, structural risks — start here |

### Analytical Framework

| Page | Summary |
|---|---|
| [signal-noise.md](wiki/signal-noise.md) | DIPS theory, what pitchers do and don't control, ERA → FIP → xFIP → xERA hierarchy, Oracle Park as confounding variable, Giants-specific ERA/FIP gap examples |
| [research-evaluation.md](wiki/research-evaluation.md) | How to evaluate competing public methodologies; worked example: fWAR (FIP-based) vs. bWAR (runs allowed) for Webb and Doval; five-question evaluation checklist |

### Reference

| Page | Summary |
|---|---|
| [pitcher-profiles.md](wiki/pitcher-profiles.md) | 9 pitchers (Webb, Snell, Hicks, Harrison, Birdsong, Roupp, Walker, Doval, Rogers) — consistent template: role, 2024 stat line, arsenal, one strength, one limitation |
| [metrics-reference.md](wiki/metrics-reference.md) | Every metric defined with scale, "use when," and "don't use when" — covers rate stats, DIPS metrics, stability indicators, plate discipline, WAR, park factors |

### Cross-Reference Map

```
overview.md
  ├── → pitcher-profiles.md    (per-pitcher stats live there, not in overview)
  ├── → signal-noise.md        (ERA vs. FIP vs. xERA interpretation)
  ├── → metrics-reference.md   (metric definitions on demand)
  └── → research-evaluation.md (fWAR vs. bWAR framework)

signal-noise.md
  └── ← pitcher-profiles.md   (profiles note "see signal-noise.md for ERA/FIP gaps")

metrics-reference.md
  └── → research-evaluation.md (fWAR vs. bWAR entry points there)

research-evaluation.md
  └── (standalone synthesis — no outbound cross-references)
```

---

## Raw Sources

### 2024 Giants Team Data

| File | Source | Summary |
|---|---|---|
| [fangraphs-giants-pitching-dashboard-2024.md](raw/fangraphs-giants-pitching-dashboard-2024.md) | FanGraphs | Full 2024 staff leaderboard — ERA, FIP, xFIP, xERA, WAR, K/9, BB/9, GB%, LOB% for all Giants pitchers |
| [fangraphs-giants-plate-discipline-2024.md](raw/fangraphs-giants-plate-discipline-2024.md) | FanGraphs | 2024 plate discipline leaderboard — O-Swing%, Z-Swing%, SwStr%, CSW% per pitcher |
| [baseball-reference-giants-2024-pitching.md](raw/baseball-reference-giants-2024-pitching.md) | Baseball Reference | Full 2024 team pitching table with traditional and advanced stats (23,912 words) |
| [baseballsavant-expected-stats-giants-2024.md](raw/baseballsavant-expected-stats-giants-2024.md) | Baseball Savant | Statcast expected stats leaderboard — xBA, xSLG, xERA, xwOBA for Giants pitchers in 2024 |

### Individual Pitcher Pages — Baseball Savant

| File | Pitcher | Role |
|---|---|---|
| [baseballsavant-logan-webb.md](raw/baseballsavant-logan-webb.md) | Logan Webb | SP (Ace) |
| [baseballsavant-blake-snell.md](raw/baseballsavant-blake-snell.md) | Blake Snell | SP |
| [baseballsavant-jordan-hicks.md](raw/baseballsavant-jordan-hicks.md) | Jordan Hicks | SP |
| [baseballsavant-kyle-harrison.md](raw/baseballsavant-kyle-harrison.md) | Kyle Harrison | SP |
| [baseballsavant-hayden-birdsong.md](raw/baseballsavant-hayden-birdsong.md) | Hayden Birdsong | SP |
| [baseballsavant-landen-roupp.md](raw/baseballsavant-landen-roupp.md) | Landen Roupp | SP |
| [baseballsavant-ryan-walker.md](raw/baseballsavant-ryan-walker.md) | Ryan Walker | RP |
| [baseballsavant-camilo-doval.md](raw/baseballsavant-camilo-doval.md) | Camilo Doval | CL |

*Note: Savant player pages display live career data. 2024 splits must be filtered by season on the page; the raw markdown captures the full career table.*

### Individual Pitcher Pages — Baseball Reference

| File | Pitcher | Summary |
|---|---|---|
| [baseball-reference-logan-webb.md](raw/baseball-reference-logan-webb.md) | Logan Webb | Full career pitching log, splits, WAR history |
| [baseball-reference-kyle-harrison.md](raw/baseball-reference-kyle-harrison.md) | Kyle Harrison | Career to date, minor league context, 2024 splits |

### Metric Methodology

| File | Source | Summary |
|---|---|---|
| [fangraphs-glossary-dips.md](raw/fangraphs-glossary-dips.md) | FanGraphs Library | DIPS theory — McCracken's original framework; foundation for FIP and xFIP |
| [fangraphs-glossary-fip.md](raw/fangraphs-glossary-fip.md) | FanGraphs Library | FIP definition, formula, historical context, interpretation |
| [fangraphs-glossary-xfip.md](raw/fangraphs-glossary-xfip.md) | FanGraphs Library | xFIP — how it differs from FIP, when to prefer it |
| [fangraphs-glossary-babip.md](raw/fangraphs-glossary-babip.md) | FanGraphs Library | BABIP for pitchers — luck indicator, stabilization timeline |
| [fangraphs-glossary-lob-pct.md](raw/fangraphs-glossary-lob-pct.md) | FanGraphs Library | LOB% (strand rate) — volatility, league average, regression patterns |
| [fangraphs-glossary-whip.md](raw/fangraphs-glossary-whip.md) | FanGraphs Library | WHIP definition and limitations |
| [fangraphs-glossary-park-factors.md](raw/fangraphs-glossary-park-factors.md) | FanGraphs Library | How park factors are calculated, regressed, and applied; Oracle Park context |
| [fangraphs-glossary-war-pitchers.md](raw/fangraphs-glossary-war-pitchers.md) | FanGraphs Library | fWAR calculation methodology — FIP-based, replacement level, leverage adjustment |
| [baseball-reference-pitcher-war.md](raw/baseball-reference-pitcher-war.md) | Baseball Reference | bWAR calculation methodology — RA9-based, defense/opposition/park adjustments, comparison to fWAR |

### Glossaries

| File | Source | Summary |
|---|---|---|
| [baseballsavant-statcast-glossary.md](raw/baseballsavant-statcast-glossary.md) | Baseball Savant | Full Statcast metric glossary — exit velocity, launch angle, barrel rate, sprint speed, and more |
| [mlb-glossary-era.md](raw/mlb-glossary-era.md) | MLB.com | ERA definition and official calculation rules |
| [mlb-statcast-glossary.md](raw/mlb-statcast-glossary.md) | MLB.com | MLB's official Statcast glossary — definitions for xBA, xSLG, xwOBA, xERA, hard hit rate |
