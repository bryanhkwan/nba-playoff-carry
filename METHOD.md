# Method

Written and committed before any data was pulled or analyzed. If anything has to change after seeing the data, the change and the reason go in RESULTS.md under "Changes after seeing the data", and both versions are reported.

## The claims being tested

A popular argument online says 2018 LeBron James was "the largest carry job in NBA playoff history." It goes like this:

1. Give every playoff run since 1977 six numbers: usage, assists, rebounds, steals, blocks and efficiency.
2. Standardize each season against its own era.
3. Measure the Euclidean distance between runs.

It makes three claims:

1. LeBron's closest comparisons are his own other runs, and the nearest run by anyone else is Larry Bird's.
2. Nobody has ever had a run like it ("practically immeasurable").
3. It was the largest carry job in playoff history.

Claims 1 and 2 are about how *unique* the run was. Claim 3 is about *carrying*, which needs its own measure. This project tests all three.

## Data

- **Source:** Basketball-Reference NBA playoff advanced stats, one page per postseason.
- **Seasons:** from the first postseason where all six stats exist (expected 1978, the first postseason after the NBA started tracking turnovers, which usage rate needs) through 2026. Any postseason missing one of the six stats is excluded and listed in RESULTS.md.
- **Unit:** a "run" is one player's stats in one postseason. Players are identified by their Basketball-Reference ID, not by name.
- **Team results:** series won, Finals appearance and title come from Basketball-Reference's playoff series history.

## Who counts

A run qualifies if the player logged at least **250 playoff minutes**. Sensitivity checks rerun everything at 150 and 400 minutes.

## The six-number profile (replicating the original argument)

The six stats are:
- Usage rate (USG%)
- Assist rate (AST%)
- Total rebound rate (TRB%)
- Steal rate (STL%)
- Block rate (BLK%)
- True shooting (TS%)

Each stat becomes a z-score within its own postseason, using that postseason's qualifying runs (population standard deviation). This puts the 1980s and today on the same scale, the way the original argument does.

## Test 1: Replication

Measure the Euclidean distance on the six z-scores between LeBron's 2018 run and every other qualifying run. Report the 10 nearest runs and the nearest run by a different player.

The Bird claim is confirmed if the nearest run by a different player belongs to Larry Bird.

## Test 2: Was it the most unique run ever?

For every qualifying run, **isolation** is the distance to the nearest run by a different player. All runs are ranked by isolation in two ways:

- **Euclidean distance:** the original argument's method.
- **Mahalanobis distance:** accounts for stats that move together. For example, high-usage players tend to have high assist rates, and Euclidean distance counts that overlap twice. The covariance comes from all qualifying z-scored runs pooled together.

The "nobody has ever done this" claim is supported if 2018 LeBron ranks #1 in isolation under the Euclidean version. The Mahalanobis rank is reported next to it.

Unique doesn't mean great. A specialist with an extreme rebounding or shot-blocking profile can be very isolated without carrying anybody. That's part of what this test is meant to show.

## Test 3: Was it the biggest carry job?

**Primary measure, Win Share share.** The player's playoff Win Shares divided by the sum of *positive* Win Shares across everyone on his team that postseason. Negative teammate Win Shares count as zero, so a share can't pass 100% just because teammates were below zero.

**Secondary measure, cast gap.** The player's playoff Box Plus/Minus (BPM) minus his teammates' minutes-weighted playoff BPM. A big gap means a great player next to a weak supporting cast.

**Context, reported but not scored:** minutes per game, series the team won, whether it reached the Finals, and whether it won the title.

Rankings reported:
- **C1:** top 15 by Win Share share, all qualifying runs
- **C2:** top 15 by Win Share share, Finals teams only
- **C3:** top 15 by cast gap, all qualifying runs

Verdict rule for "largest carry job in playoff history":
- **Supported:** 2018 LeBron is #1 in C1.
- **Partly supported:** #1 in C2 or C3, but not C1.
- **Not supported:** #1 in none of them.

## LeBron vs. Jordan

Every qualifying run by both players goes in one table with the same measures. The report shows each player's best run on each measure, and how many of each player's runs land in the top 25 of each ranking. There is no combined score.

## Robustness

- Minimum minutes: 150, 250 and 400
- Distance: Euclidean and Mahalanobis

If a headline result flips under any of these, RESULTS.md says so.

## Known limitations

- Box-score stats miss most defense and everything off the ball.
- Win Shares and BPM are estimates built from the box score, not direct measurements.
- Playoff runs are small samples. Rankings are point estimates, and small gaps between runs don't mean much.
- Opponent strength isn't adjusted for.
- Z-scores within a postseason depend on who else qualified that year.
