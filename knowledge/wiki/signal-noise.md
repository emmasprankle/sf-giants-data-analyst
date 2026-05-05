# Signal vs. Noise in Pitching Evaluation

*Sources: FanGraphs glossaries (DIPS, FIP, xFIP, BABIP, LOB%, park factors), Baseball Reference pitcher WAR, Baseball Savant expected stats.*

## The Core Framework: DIPS

Defense-Independent Pitching Statistics (DIPS) — developed by Voros McCracken — established that pitchers have much less control over what happens to balls in play than previously assumed. When a ball is put in play (not a strikeout, walk, or home run), the outcome is largely determined by the defense and randomness, not the pitcher.

**What pitchers control (signal):**
- Strikeout rate (K/9, K%)
- Walk rate (BB/9, BB%)
- Hit batters (HBP)
- Home runs allowed (though HR/FB rate has some luck component)
- Ground ball rate (partially — inducing weak contact is a repeatable skill)

**What pitchers don't control (noise):**
- Batting average on balls in play (BABIP) — stabilizes slowly, heavily influenced by defense and luck
- Left on base percentage (LOB%, strand rate) — highly variable year to year
- Whether a hit becomes a single vs. double vs. triple — sequencing and defense

This is why FIP exists: it measures only the outcomes pitchers control.

## The Metrics Hierarchy

### ERA — Outcome metric (most noise)
ERA counts all earned runs, regardless of whether the pitcher caused them. A poor defensive play that extends an inning, followed by a home run, charges the pitcher for runs that weren't his fault. ERA also reflects strand rate, which is volatile.

**When to use:** Historical context, team-level run prevention. Not for comparing individual pitchers across contexts.

### FIP — Defense-independent estimate (less noise)
`FIP = ((13×HR) + (3×(BB+HBP-IBB)) − (2×K)) / IP + constant`

FIP uses only the outcomes pitchers control. The constant (≈3.10) puts FIP on the same scale as ERA. A pitcher with ERA 4.50 and FIP 3.20 likely got unlucky or had poor defense behind him — expect ERA to improve.

**When to use:** Evaluating true run prevention ability, projecting future ERA, comparing pitchers across defensive contexts.

### xFIP — Stabilized FIP (even less noise)
xFIP replaces the pitcher's actual HR/FB rate with the league-average HR/FB rate. Home run rates fluctuate year to year even for pitchers with consistent fly ball rates. xFIP strips that volatility out.

**When to use:** When you suspect the HR/FB rate is an outlier — especially for small samples or pitchers in their first full season.

### xERA (Statcast) — Quality-of-contact estimate
xERA is built from Statcast contact quality metrics (exit velocity, launch angle, barrel rate). It estimates what a pitcher's ERA "should" be based on the actual quality of contact allowed, not just the infield/outfield split.

xERA is orthogonal to FIP — it captures things FIP misses (soft contact induction) but doesn't capture command (walk rate). A pitcher can have a good FIP and a bad xERA if they strike out batters but the balls they do allow are hit hard.

**When to use:** Identifying pitchers who allow weak contact (skills) vs. those whose ERA is driven by walk rate or HR suppression.

## BABIP and LOB% as Noise Flags

**BABIP**: The league-average BABIP is around .290–.300. Pitchers have limited ability to sustain extreme BABIPs. A pitcher with ERA 4.50 and BABIP .350 is a regression candidate (ERA should improve). A pitcher with ERA 3.00 and BABIP .240 may be due for regression upward.

**LOB% (Left on Base %)**: League average is ≈72%. Elite strand rates (>78%) are usually unsustainable. Collapsed strand rates (<65%) often rebound. LOB% fluctuates because sequencing — which hits come with runners on base — is not fully controlled by the pitcher.

## Oracle Park as Confounding Variable

Oracle Park (San Francisco) runs among the most pitcher-friendly parks in MLB. Park factor around 95 (pitcher's park; 100 = neutral). Contributing factors:
- Cold, dense marine air off San Francisco Bay suppresses ball carry
- Large foul territory generates extra outs
- Deep power alleys reduce home runs

**Practical effect:** Giants starters carry consistently lower ERAs at home than on the road. This is a structural park effect, not individual skill. FIP and xFIP adjust for this implicitly (home run suppression is already in FIP). ERA does not adjust automatically.

**When analyzing Giants pitchers:** Always compare ERA to FIP and xFIP. If ERA < FIP, investigate how much is park effect vs. genuine sequencing skill vs. random variance.

## Giants-Specific Examples (2024)

### Logan Webb — ERA understates true skill
Webb: ERA 3.47, FIP 2.95, xFIP 3.28, xERA 4.37

The FIP-ERA gap (-0.52) suggests Webb outperforms expectations in run prevention — likely a combination of elite ground ball rate (56.8% GB%), Oracle Park's HR suppression, and legitimate sequencing ability. His xERA (4.37) is higher than his ERA because Statcast sees harder contact than outcomes show — this is the park effect in action. FIP and xFIP are more predictive of 2025 performance than ERA; xERA likely overstates regression risk because it doesn't account for ground ball profile.

### Camilo Doval — ERA overstates true struggles
Doval: ERA 4.88, FIP 3.71, xERA 3.32

Doval's ERA (4.88) is almost a full run above his FIP (3.71) and nearly 1.6 runs above his xERA (3.32). The contact quality he allowed was actually average-to-good (xERA 3.32); the runs came from strand rate collapse — runners he put on base scored at an unusually high rate. This pattern is a strong regression signal: ERA should improve without any change in underlying skill, as long as LOB% normalizes.

### Ryan Walker — ERA likely to regress upward
Walker: ERA 1.91, FIP 2.52, xFIP 2.80, LOB% 82.9%

Walker's ERA (1.91) is well below his FIP (2.52) and xFIP (2.80). An 82.9% LOB% is elite — and almost certainly unsustainable. The underlying metrics suggest Walker is genuinely good, but a full-season ERA near 2.00 reflects favorable sequencing on top of real skill. Project him closer to his FIP than his ERA.
