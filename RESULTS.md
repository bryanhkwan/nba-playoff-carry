# Results

Run on 2026-10-17 using the method in [METHOD.md](METHOD.md), which was committed before any data was pulled (commit `f277b98`). Every verdict below follows the rules written there.

## Short version

| The claim | Verdict | What the data says |
|---|---|---|
| His closest comparison is himself | **Mostly holds** | His two nearest runs are his own (2010, 2009), and 5 of his 10 nearest are LeBron runs. |
| The nearest player who isn't him is Larry Bird | **Not reproduced** | The nearest other player is Kevin Durant (2013). No Bird run makes the top 10 at any minute cutoff. |
| Nobody has ever had a run like it | **Not supported** | 2018 LeBron ranks #55 of 2,464 runs on uniqueness. The most unusual runs belong to role players with extreme stat profiles. |
| Largest carry job in playoff history | **Partly supported** | #1 among Finals teams by a wide margin, #4 overall, #3 on supporting-cast gap. |

On LeBron vs. Jordan, it's close and depends on the measure. Jordan's 1988 run edges 2018 LeBron on overall Win Share share. LeBron's 2009 run has the widest gap between a star and his supporting cast since 1978, with Jordan's 1990 run second.

## Data

- 49 postseasons, 1978-2026.
- 1977 was excluded: usage rate needs turnovers, which the NBA didn't track until the 1977-78 season.
- 9,302 player-postseasons from 1978-2026, 2,464 of them with 250+ minutes.
- Every team-season matched to its series results.

## Test 1: Replication

These are the ten runs closest to 2018 LeBron, using the original argument's six stats with each one standardized within its own postseason:

| Rank | Run | Distance |
|---|---|---|
| 1 | LeBron James 2010 | 1.045 |
| 2 | LeBron James 2009 | 1.061 |
| 3 | Kevin Durant 2013 | 1.324 |
| 4 | LeBron James 2020 | 1.326 |
| 5 | Tracy McGrady 2005 | 1.390 |
| 6 | James Harden 2020 | 1.401 |
| 7 | Nikola Jokić 2023 | 1.478 |
| 8 | Luka Dončić 2021 | 1.566 |
| 9 | LeBron James 2013 | 1.638 |
| 10 | LeBron James 2017 | 1.680 |

The "closest comparison is himself" part holds. The Bird part doesn't. The nearest other player is Kevin Durant 2013 at the 250-minute cutoff, Luka Dončić 2020 at 150 minutes and James Harden 2020 at 400 minutes.

The original argument doesn't publish its exact settings, such as the minimum minutes or the precise stat definitions. So this doesn't prove it miscounted its own setup. It shows the Bird result doesn't survive a reasonable rebuild at three different cutoffs.

## Test 2: Was it the most unique run ever?

"Isolation" is the distance from a run to the closest run by any other player.

| Rank | Euclidean (original method) | | Mahalanobis (corrects for stats that move together) | |
|---|---|---|---|---|
| 1 | James Donaldson 1986 | 2.090 | Nate McMillan 1993 | 2.289 |
| 2 | Nate McMillan 1993 | 2.089 | James Donaldson 1986 | 2.108 |
| 3 | Clifford Robinson 1990 | 1.893 | Clifford Robinson 1990 | 2.042 |
| 4 | Ben Wallace 2003 | 1.781 | Ben Wallace 2003 | 1.881 |
| 5 | Tony Allen 2015 | 1.773 | Ausar Thompson 2026 | 1.867 |
| 6 | LeBron James 2009 | 1.705 | Magic Johnson 1982 | 1.860 |

2018 LeBron scores 1.324 (#55) on Euclidean and 1.385 (#67) on Mahalanobis. His most isolated run is 2009 (#6 Euclidean, #14 Mahalanobis).

This is the main problem with using distance to argue greatness: it measures *unusual*, not *dominant*. James Donaldson's 1986 run (7.8% usage, .831 true shooting) is about as far from everyone else as a run can get, and nobody would call it the greatest playoff run ever.

## Test 3: Was it the biggest carry job?

**C1: share of the team's playoff Win Shares, all qualifying runs**

| Rank | Run | Share | How far the team went |
|---|---|---|---|
| 1 | Chris Paul 2011 | 59.1% | out in 1st series |
| 2 | Tracy McGrady 2003 | 54.5% | out in 1st series |
| 3 | Michael Jordan 1988 | 47.7% | won 1 series |
| 4 | **LeBron James 2018** | **46.0%** | lost Finals |
| 5 | Paul Pierce 2005 | 45.9% | out in 1st series |

The top of C1 is mostly first-round exits. A short run means a small team total, which pushes one player's share up. That's why C2 was set up to look at Finals teams separately.

**C2: same measure, Finals teams only**

| Rank | Run | Share | Result |
|---|---|---|---|
| 1 | **LeBron James 2018** | **46.0%** | lost Finals |
| 2 | LeBron James 2014 | 37.1% | lost Finals |
| 3 | Shaquille O'Neal 2000 | 35.3% | won title |
| 4 | Dirk Nowitzki 2006 | 35.3% | lost Finals |
| 5 | Tim Duncan 2003 | 34.9% | won title |

Jordan's best Finals run on this measure is 1993: 31.9%, #13.

**C3: cast gap, the player's BPM minus his teammates' minutes-weighted BPM**

| Rank | Run | Gap | Player BPM | Teammates' BPM |
|---|---|---|---|---|
| 1 | LeBron James 2009 | +17.5 | 17.5 | 0.0 |
| 2 | Michael Jordan 1990 | +14.6 | 13.7 | -0.9 |
| 3 | **LeBron James 2018** | **+14.4** | 12.7 | -1.7 |
| 4 | Kawhi Leonard 2017 | +14.0 | 14.2 | 0.2 |
| 5 | Michael Jordan 1988 | +13.9 | 12.2 | -1.7 |

**Verdict:** under the rule in METHOD.md, 2018 LeBron is #1 in C2 but not in C1, so the claim is **partly supported**.

For context: he played 22 games at 41.9 minutes a game and produced 5.2 Win Shares while his teammates' combined BPM was below zero. Every other run in the C1 top 5 ended in the first or second series.

## LeBron vs. Jordan

Ranks are among all 2,464 qualifying runs.

| Measure | LeBron's best run | Jordan's best run | Runs in the top 25 (LeBron / Jordan) |
|---|---|---|---|
| Win Share share | 2018: 46.0% (#4) | 1988: 47.7% (#3) | 3 / 3 |
| Cast gap | 2009: +17.5 (#1) | 1990: +14.6 (#2) | 3 / 5 |
| Isolation, Euclidean | 2009 (#6) | 1995 (#62) | 1 / 0 |
| Isolation, Mahalanobis | 2009 (#14) | 1995 (#20) | 1 / 1 |

LeBron has 16 qualifying runs and Jordan has 10. Every run is in `results/lebron_vs_jordan.csv`.

## Robustness

| Minimum minutes | Runs | 2018 LeBron isolation rank (Euclid / Mahal) | C1 | C2 | C3 | Nearest other player | Carry verdict |
|---|---|---|---|---|---|---|---|
| 150 | 4,152 | 118 / 202 | 26 | 1 | 6 | Luka Dončić 2020 | partly supported |
| 250 | 2,464 | 55 / 67 | 4 | 1 | 3 | Kevin Durant 2013 | partly supported |
| 400 | 1,321 | 42 / 12 | 2 | 1 | 3 | James Harden 2020 | partly supported |

The headline result holds at every cutoff: #1 among Finals teams, with a "partly supported" verdict.

The overall C1 rank moves the most. At 150 minutes, more short first-round runs qualify and push him down to #26. At 400 minutes, Jordan 1988 is #1 and 2018 LeBron is #2.

## Changes after seeing the data

No changes to the method. Two presentation additions:
- A chart for the C2 ranking.
- "How far the team went" labels on the carry charts.

## Limitations

These were set out in METHOD.md, plus one observed in the results:
- Win Share share is inflated in short runs, as C1 shows. Read it next to C2.
- Box-score stats miss most defense and everything off the ball.
- Win Shares and BPM are estimates built from the box score, not direct measurements.
- Playoff runs are small samples, so a gap of a point or two between runs doesn't mean much.
- Opponent strength isn't adjusted for.

## Files

- `results/summary.json`: every headline number
- `results/*.csv`: the full ranking tables
- `results/fig_*.png`: the charts
