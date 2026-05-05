# Evaluating Public Baseball Research

*Sources: FanGraphs WAR methodology, Baseball Reference pitcher WAR explanation, FanGraphs DIPS glossary.*

## Why This Matters

The SF Giants Baseball Operations Analyst posting explicitly asks for the ability to "evaluate and adapt public baseball research and vendors." This is a distinct skill from knowing what the metrics are. It means: given two competing methodologies that claim to measure the same thing, you can identify what each one assumes, where they agree, where they diverge, and which is appropriate for a given question.

---

## Worked Example: fWAR vs. bWAR for Pitchers

FanGraphs WAR (fWAR) and Baseball Reference WAR (bWAR) are the two dominant public frameworks for pitcher valuation. They reach different conclusions for the same pitchers because they start from different premises.

### What each one measures

**fWAR** starts with FIP — Fielding Independent Pitching. It asks: *how well did this pitcher perform on the outcomes he controls (strikeouts, walks, home runs)?* It deliberately excludes balls in play outcomes because those are heavily influenced by defense and luck (DIPS theory).

**bWAR** starts with runs allowed (RA9) — actual runs scored. It then adjusts for opposition quality, team defense quality, park factors, and starter/reliever role. It asks: *what was the value of what actually happened when this pitcher was on the mound?*

### Concrete case: Logan Webb 2024

Webb: ERA 3.47, FIP 2.95, fWAR 4.4

- fWAR values him at 4.4 — elite, ace-caliber — because his strikeout rate, walk rate, and home run rate are all excellent.
- bWAR would adjust his runs allowed for the Giants' defense, Oracle Park, and opposition quality. Because Webb's actual ERA (3.47) is worse than his FIP (2.95), bWAR gives slightly less credit than fWAR.

The gap between them is an analytical signal: Webb's FIP-to-ERA divergence is real, and fWAR says "credit the pitcher for the defense-independent skill"; bWAR says "give partial credit to the defense that turned those ground balls into outs."

Neither is wrong — they answer different questions.

### Concrete case: hypothetical extreme
Baseball Reference's own documentation uses this comparison to illustrate the divergence:

*Pitcher A throws a perfect game with 20 strikeouts. FIP ≈ −1.40. RA = 0.00.*  
*Pitcher B throws a perfect game with 0 strikeouts. FIP ≈ 3.20. RA = 0.00.*

fWAR rates Pitcher A far higher (elite strikeouts), while bWAR rates them identically (both prevented all runs). The right answer depends on what you're asking: which pitcher showed more repeatable skill (fWAR), or which one was actually more valuable in that game (bWAR).

### When to use each

| Question | Use |
|---|---|
| How good is this pitcher likely to be next year? | fWAR (forward-looking, defense-independent) |
| How much did this pitcher contribute to wins last season? | bWAR (backward-looking, accounts for actual defense) |
| Comparing pitcher across different defensive teams | fWAR |
| Crediting a pitcher for team-specific context (weak defense, extreme park) | bWAR with park/defense adjustments examined directly |
| Contract valuation / free agent projection | fWAR (better at capturing repeatable skill) |
| Historical record analysis | bWAR (measures what actually happened) |

---

## A Framework for Evaluating Any Public Methodology

When you encounter a new metric, model, or research claim, ask these five questions:

**1. What is it actually measuring?**  
Not what the name implies — what are the inputs, and what do they capture? FIP measures strikeout/walk/HR rates. xERA measures contact quality. Both claim to estimate run prevention, but they're built on different data.

**2. What does it assume?**  
Every methodology has assumptions. FIP assumes DIPS theory — that BABIP outcomes are mostly noise. bWAR assumes the team defense adjustment (using Baseball Info Solutions Defensive Runs Saved) correctly isolates pitcher vs. defense contribution. If the assumption is wrong in a specific case, the metric misfires.

**3. How does it stabilize?**  
Some metrics stabilize with 50 plate appearances (SwStr%, walk rate). Others need 300+ IP (ERA, BABIP). Small-sample conclusions from slow-stabilizing metrics are unreliable — not wrong in principle, just noisy in practice.

**4. Where does it agree with competing metrics — and where does it diverge?**  
Agreement across independent methodologies (FIP, xFIP, and xERA all pointing the same direction) is much stronger evidence than any single metric alone. Divergence is where the interesting analysis lives — it means one methodology is picking up something the other isn't.

**5. What context does it ignore?**  
No single metric captures everything. FIP ignores sequencing, contact quality, and park effects. bWAR's defense adjustment uses fielding metrics that have their own measurement error. xERA ignores walk rate. Knowing what a metric omits tells you when to reach for a complementary source.

---

## Applying This to Giants Pitching Analysis

The fWAR vs. bWAR framework is directly relevant to evaluating Giants pitchers because:

- **Oracle Park** creates a structural gap between ERA (park-suppressed) and FIP (not park-suppressed in the same way). When ERA < FIP, the park is doing work.
- **Ground ball profile** means a metric like xERA (contact quality) may not fully capture the value of inducing ground balls to a well-positioned infield.
- **LOB% fluctuations** mean bWAR, which credits actual runs allowed, will diverge from fWAR in seasons with extreme strand rate outcomes (Doval 2024 is the clearest example).

The analyst who can explain *why* these metrics diverge for a specific pitcher — not just report the numbers — is the one who is actually evaluating public research rather than just citing it.
