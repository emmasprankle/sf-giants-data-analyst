---
source: https://www.baseball-reference.com/about/war_explained_pitch.shtml
slug: baseball-reference-pitcher-war
---

We're hiring a Scrum Master to join our team! Learn more and [apply here](https://sports-reference-llc.breezy.hr/p/ba2fef1394d1-scrum-master).

**About** Menu

- [About Baseball Reference](https://www.baseball-reference.com/about/)

**Keyboard Shortcuts**

\ to toggle sidebar navigation

/ to toggle search input

[More about this update](https://www.sports-reference.com/blog/2025/11/in-page-navigation-redesign-on-basketball-reference/)

# Pitcher WAR Calculations and Details

## Basic inputs

At its most basic level, our pitching WAR calculation requires only overall
Runs Allowed (both earned and unearned) and Innings Pitched. Since we
are trying to measure the value of the pitcher's performance to his
team, we start with his runs allowed and then
adjust that number to put the runs into a more accurate context.

## Determining what the Average Pitcher would have done

Once we have the pitcher's runs allowed and innings, we set about
figuring out what an average pitcher would have done if placed in the
same setting as the pitcher we are studying.

### xRA, Level of Opposition

Back to 1918, we have gamelogs for every major league pitching
appearance. This means that we can, with certainty, determine which
team's pitchers we're facing. For each season, we also know the average
runs per out for each team and we can adjust this number into a
neutral context using park factors. Then, based on this, we can determine
what the average number of expected runs would be for this set of
teams faced.

This can have a major impact in situations where there is a set of
dominant offensive teams and some pitchers face them multiple times
while others may never face them. For example, pitchers for the 1927
Yankees never faced Murderers Row.

### Handling Interleague

For seasons with interleague play, we only include the non-interleague
games and interleague home games to determine the teams' season average in run
scoring. So this would exclude, on average, nine games from a team's
average. Our reasoning is that including nine games the Red Sox don't
have a DH will skew their offensive averages lower when most pitchers
are facing them with a DH.

To account for these out-of-league road games, we then add or
subtract 0.2 runs to the team's averages depending on whether they have or
do not have a DH in the game. So for the 2011 Red Sox, all AL pitchers or NL
pitchers facing them in Boston are expected to give up 5.49 runs per
game, but if the Red Sox go to Philly we expect them to score 5.29
runs per game.

When we are in-season, we use the run-scoring averages for offenses
for the last 365 days.

The pitcher's expected runs allowed is then the sum of his
opposition's run scoring weighted by the innings he faced each team.
We call this xRA.

### xRA\_def, Adjusting for Team Defense

A great deal of work has recently gone into the study of
Defense-Independent Pitching Stats (DIPS). We agree with the validity
and importance of most all of this work, and some would argue that you
shouldn't charge the pitcher for runs allowed in the way we do since
it is often not the pitcher's fault, but the defense's. Our view is
that, while the pitcher may have been unlucky or lucky in certain ways,
we are trying to measure the value of the recorded performance--not
its repeatability--and that we can account for defense in different
ways.

To account for defense, we find the overall team defensive runs saved,
which uses Baseball Info Solutions' Runs Saved from 2003 on and Total
Zone before 2003. We then compute the number of balls in play allowed
by the team and the number of balls in play allowed by the pitcher, and
assign the negative of the proportional team defensive runs to the
xRA\_ppf values.

`xRA_def = (BIP_pitcher)/(BIP_team) * TeamDefensiveRunsSaved`

### xRA\_sprp, Adjusting Averages for Starters and Relievers

In the current MLB environment, relievers have much lower ERAs than
starters. Relievers come in, throw gas for an inning or less, and
then leave, so for recent years we set this difference league-wide at
.1125 runs/game and then from 1960-1973 it is set at .0583 runs/game. This
adjustment for starter/reliever ERAs is really only applicable since
1960, and if you look at the difference in starter and reliever ERAs,
it is clear that there are two eras of bullpen usage. From 1960-1973
there was a slight starter/reliever effect, and then in 1974 we start
to see the current dichotomy.

Before 1960 there is no starter/reliever adjustment.

### PPF _p_, Custom Park Factors

Since we have gamelogs, we can also customize our park factors to
the parks the pitcher actually pitched in. This can have an impact in
a division like the NL West where you have three fairly extreme
pitcher parks and two fairly extreme hitter parks. Usually, pitchers'
custom park factors are less than a point away from their teams' park
factor, but on occasion it can be multiple points. For pre-gamelog
seasons, we use the team's park factor. All park factors are 3-year average.

## xRA\_final, League Average Pitcher Performance

In computing the player's wins above average, we use

`xRA_final = PPF_custom * (xRA - xRA_def + xRA_sprp_adj)`

## WAA, Converting Runs to Wins

[See Runs to Wins](https://www.baseball-reference.com/about/war_explained_runs_to_wins.shtml). This provides us with WAA (wins above average).

## WAA\_adj, Adjusting for Leverage

As RA\_replacement\_adj currently stands, starters would be far, far
more valuable than relievers; e.g. most average starting pitchers would
be viewed as more valuable than Mariano Rivera in even his best
seasons. The flaw in our reasoning above is that closers and many
relievers are used in the highest leverage situations. These
situations have a much larger ability to impact the outcome of the
game than 0-0 top of the 1st, so we adjust the RA\_replacement\_adj with
a leverage multiplier. An average leverage is 1.0, while many closers
will approach an average of 2.0 for the season while mopup relievers
might be at 0.7. This is applied only for relief innings and the
leverage we use in the leverage at the beginning of the pitcher's
outing. This way a bad pitcher can't bump up his leverage (and WAA)
by walking the bases loaded and striking out the side every time.

`WAA_adj = WAA * (1.00 + leverage_index_pitcher)/2`

The leverage is averaged with 1.00 because of chaining of bullpens.
If the closer goes down, the manager is not going to use the AAA
callup as the closer. The AAA callup will move to the back of the
bullpen while everyone else will move up one slot in the pecking order
and the top setup man will become the closer. Modifying the leverage
in this way accounts for this difference.

[See a full\\
description of leverage and how it is calculated.](https://www.baseball-reference.com/about/wpa.shtml)

One other adjustment occurs here: we re-center WAA for the league at zero, so that the average is exactly zero. This factor is put in this value, which is why you will see some non-zero values in WAA

## WAR\_rep, Setting Replacement Level for all Pitchers

As with the hitters, we have a replacement level set for each
league based on the competitive level of the league. See the [replacement level explanation in\\
the WAR for position players page](https://www.baseball-reference.com/about/war_explained_position.shtml) for a full discussion of the
multipliers.

[See Runs to Wins](https://www.baseball-reference.com/about/war_explained_runs_to_wins.shtml)
for an explanation of how we convert the replacement level into wins
between the average player and the replacement level player (WAR\_rep).

## Fine-Tuning Replacement Level

After we make a first pass through the calculations, we determine
how the league's current total WAA and WAR differs from the desired overall
league WAR. We then add or subtract fractional WAA and replacement runs from
each player's WAA or runs\_replacement total based on their playing time, and
recompute WAR with this adjustment included.

## Computing WAR

`WAR = WAR_rep + WAA + WAA_adj`

## How this Compares to FanGraphs Pitcher WAR

FanGraphs has a [long and detailed rundown of their WAR calculation](http://www.fangraphs.com/library/index.php/misc/war/),
so we won't fully rehash it here. Our WAR starts with runs allowed by
the pitcher and compares it to the league average pitcher (adjusting for
quality of opposition), parks pitched in, and quality of defense behind
the pitcher.

FanGraphs' WAR begins with FIP, which is a fielding independent
pitching stat comparable in scale to ERA that is computed using only
pitcher dependent stats.

`FIP = ((13*HR)+(3*(BB+HBP-IBB))-(2*K))/IP + lg_specific_constant(around 3.20 or so)`

In FIP, hits allowed and non-strikeout outs recorded have no role
in the calculation other than in the number of total innings pitched.
The assumption is that once the ball is put into play (other than a
home run) the entire outcome is determined by random chance and team
defensive quality. This is definitely true to a greater degree than
fans likely believe, but we disagree as to whether this is the best
measure of the value of a pitcher's historical performance.

I've crafted some admittedly extreme cases below to illustrate
situations where the approaches differ. For most situations, FIP and
Runs Allowed Average (RA, essentially what we use) will be very close and
are strongly correlated, but there are a number of cases each year
where there are large disparities between the two metrics.

Situation #1, Pitcher A throws a perfect game with 20 strikeouts, Pitcher B
throws a perfect game with no strikeouts.

FIP: Pitcher A -1.40 FIP, Pitcher B, 3.20 FIP, RA: Pitcher A 0.00 RA,
Pitcher B 0.00 RA.

Situation #2, Pitcher A throws one inning w/ sequence, HR, ground
out, fly out, BB, BB, BB, fly out, Pitcher B throws one inning w/ sequence BB, BB, BB,
HR, SO, SO, SO

FIP: Pitcher A 25.20 FIP, Pitcher B 19.20 FIP, RA:
Pitcher A 9.00 RA, Pitcher B 36.00 RA.

As I said, in the average case the two methods will arrive at
similar results, but on the edge cases the differences can be quite
dramatic.