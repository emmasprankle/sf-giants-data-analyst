# Pitching Metrics Reference

*Sources: FanGraphs glossaries (ERA, FIP, xFIP, WHIP, BABIP, LOB%, park factors), Baseball Savant Statcast glossary, MLB glossary.*

*Format: definition → scale → when to use it → when not to.*

---

## Rate / Traditional Stats

### ERA (Earned Run Average)
Earned runs allowed per 9 innings. Excludes unearned runs (errors). Scale: lower is better; MLB average ≈4.00–4.20 in recent seasons.

**Use when:** Communicating with non-technical audiences; historical comparisons; measuring actual run output for team-level analysis.  
**Don't use when:** Comparing pitchers across different defensive contexts, park environments, or sample sizes under 50 IP. ERA is the noisiest common pitching stat.

### WHIP (Walks + Hits per Inning Pitched)
(BB + H) / IP. Measures base runner rate. Scale: ≤1.00 is elite; ≥1.40 is poor; MLB average ≈1.25–1.30.

**Use when:** Quick reads on baserunner traffic; fantasy-adjacent discussions. Simple to compute and communicate.  
**Don't use when:** You need to separate walk-driven WHIP from hit-driven WHIP, or distinguish hard-hit singles from weak ones.

### K/9 (Strikeouts per 9 Innings)
K × 9 / IP. Strikeout rate on a per-inning scale. Also expressed as K% (K / batters faced — preferred for cross-era comparison).

**Use when:** Evaluating swing-and-miss profile; projecting performance in smaller samples.  
**Don't use when:** Comparing across eras (strikeout rates have risen dramatically since the 2010s); use K% for era-adjusted comparisons.

### BB/9 (Walks per 9 Innings)
BB × 9 / IP. Walk rate on a per-inning scale. Also expressed as BB% (BB / batters faced).

**Use when:** Evaluating command; flagging injury or mechanical concerns (walk rates spike before velocity does). Low BB/9 is one of the most reliable predictors of sustained success.

### HR/9 (Home Runs per 9 Innings)
HR × 9 / IP. Home run rate. Subject to HR/FB rate volatility (see xFIP).

**Use when:** Identifying extreme HR outliers. Otherwise, look at HR/FB rate as the underlying driver.

### GB% (Ground Ball Rate)
Ground balls / balls in play. MLB average ≈44%. 50%+ is ground ball pitcher; 40%- is fly ball pitcher.

**Use when:** Evaluating Oracle Park fit (ground balls avoid outfield entirely); assessing defense dependency; projecting HR rates.  
**Note:** GB% is one of the most stable year-to-year metrics — it's a genuine skill signal.

---

## Defense-Independent Metrics

### FIP (Fielding Independent Pitching)
`((13×HR) + (3×(BB+HBP−IBB)) − (2×K)) / IP + constant`  
ERA-scale metric using only pitcher-controlled outcomes. Constant ≈3.10 (league-calibrated annually).

**Use when:** Comparing pitchers across different defensive contexts; projecting future ERA; identifying luck-driven ERA over/underperformance.  
**Don't use when:** The sample is under 30 IP (HR component is too volatile); when the pitcher has a documented soft-contact skill that FIP doesn't capture.

### xFIP (Expected Fielding Independent Pitching)
FIP with HR replaced by (FB × league-average HR/FB rate). Removes HR/FB rate volatility.

**Use when:** Small samples; evaluating first-year starters; when a pitcher's HR/FB rate is far from league average (11–12% is avg) without an obvious fly ball profile explanation.  
**Don't use when:** The pitcher is a documented extreme fly ball or extreme ground ball pitcher — their actual HR/FB rate has a real structural component.

### xERA (Expected ERA — Statcast)
Estimated ERA based on quality of contact allowed (exit velocity, launch angle, barrel rate). Different methodology from FIP — captures soft contact induction, not just walk/K/HR rates.

**Use when:** Identifying pitchers who allow consistently weak contact (a real but FIP-invisible skill); pairing with FIP for a fuller picture.  
**Don't use when:** Treating it as simply "better ERA." xERA and FIP answer different questions and sometimes point in opposite directions.

---

## Stability / Luck Indicators

### BABIP (Batting Average on Balls in Play)
H excluding HR / (AB − K − HR + SF). League average ≈.295–.300. Pitchers have limited control over this.

**Use when:** Diagnosing ERA over/underperformance. A pitcher with BABIP .350 is likely due for improvement; BABIP .230 signals likely regression.  
**Don't use when:** Using it as a standalone metric — it only has meaning relative to FIP and ERA context.

### LOB% (Left on Base %, Strand Rate)
Percentage of runners who reach base that don't score. League average ≈72%. 78%+ is unsustainably high; 65%- is unsustainably low.

**Use when:** Identifying sequencing luck — high LOB% suppresses ERA below FIP; low LOB% inflates ERA above FIP.  
**Don't use when:** Projecting — LOB% has almost no year-to-year correlation. It's a diagnostic tool, not a predictive one.

### HR/FB Rate
Home runs as a percentage of fly balls allowed. League average ≈10–11%. Above 14% or below 7% usually regresses.

**Use when:** Explaining ERA vs. FIP gaps driven by home runs. Useful for identifying park effect contributions.

---

## Plate Discipline Metrics (Statcast / FanGraphs)

### SwStr% (Swinging Strike Rate)
Swinging strikes / total pitches. Measures swing-and-miss. 10%+ is good; 13%+ is elite.

**Use when:** Evaluating pure stuff quality; identifying strikeout potential before it shows up in full-season K rate.  
**Note:** One of the fastest-stabilizing metrics — reliable in smaller samples.

### CSW% (Called + Swinging Strike Rate)
(Called strikes + swinging strikes) / total pitches. Broader than SwStr% — captures command (called strikes) and stuff (swinging strikes). 28%+ is good; 30%+ is elite.

**Use when:** Evaluating both stuff and command together. Better than SwStr% alone for pitchers who win with location over raw stuff.

### O-Swing% (Chase Rate)
Swings on pitches outside the strike zone / pitches outside the zone. High O-Swing% means batters are chasing.

**Use when:** Evaluating deception and breaking ball effectiveness. Elite pitchers generate chases; good command sets up the chase with strikes.

### Z-Swing% (Zone Contact Rate)
Swings on pitches inside the strike zone / pitches inside the zone. 

**Use when:** Paired with O-Swing% — you want batters swinging outside the zone and missing inside the zone.

---

## Value Metrics

### fWAR (FanGraphs WAR — Pitchers)
Built on FIP: converts defense-independent run prevention to wins above replacement. Replacement level ≈0 WAR.

Scale: 0–1 fringe, 1–2 average, 2–4 good starter, 4+ ace/all-star, 6+ MVP-caliber.

**Use when:** Cross-pitcher comparison independent of team defense; projecting future value.

### bWAR (Baseball Reference WAR — Pitchers)
Built on runs allowed (RA9), adjusted for opposition quality, team defense, and park. Measures what actually happened, not what was expected.

**Use when:** Historical analysis; evaluating pitchers with strong contact management skills that FIP doesn't capture; crediting/debiting actual run prevention.

**Key distinction:** fWAR and bWAR diverge most for pitchers with large ERA-FIP gaps. Webb's fWAR > bWAR reflects that FIP (2.95) is better than ERA (3.47), making the FIP-based measure more favorable. For full discussion, see `research-evaluation.md`.

### Park Factors
Index of run-scoring environment relative to league average. 100 = neutral; >100 = hitter-friendly; <100 = pitcher-friendly. Oracle Park ≈95 (pitcher-friendly). Applied as a 3-5 year average to reduce single-season volatility.

**Use when:** Adjusting ERA for context; explaining home/road ERA splits; comparing pitchers across franchises.
