# Playoff Carry

Was 2018 LeBron James the biggest carry job in NBA playoff history?

A popular argument online says yes. It gives every playoff run six numbers (usage, assists, rebounds, steals, blocks and true shooting), adjusts them for era, and shows that 2018 LeBron sits far away from everyone else.

Before pulling any data, I wrote down how I'd test the claim and what result would count as support for it ([METHOD.md](METHOD.md)), so the results couldn't shape the method.

## What I found

- **Among teams that reached the Finals, 2018 LeBron carried the biggest share of his team since 1978.** He produced 46% of Cleveland's playoff Win Shares. The next best Finals runs by anyone else are Shaquille O'Neal (2000) and Dirk Nowitzki (2006), both at 35%.
- **Across all playoff runs he's #4.** The three above him are two first-round exits and Michael Jordan's 1988 run (47.7% to 46.0%). Jordan's run lasted 10 games; LeBron's lasted 22.
- **The "nobody has ever played like this" part doesn't hold.** 2018 LeBron ranks #55 of 2,464 runs on how unusual his stat profile was. The most unusual runs belong to role players.
- **Verdict: partly supported.** The full results are in [RESULTS.md](RESULTS.md).

## Measuring similarity: Euclidean vs. Mahalanobis

Each playoff run becomes six numbers. Every stat is a z-score against that postseason's average, which puts a 1988 run and a 2018 run on the same scale. Then the question is how to measure the distance between two runs.

**I started with Euclidean distance,** because that's what the original argument uses. It's the Pythagorean theorem with six terms instead of two: take the difference on each stat, square it, add those up, and take the square root.

The flaw is that it treats the six stats as unrelated, and they aren't. High-usage players usually have high assist rates, and big men tend to both rebound and block shots. When two stats move together, Euclidean distance counts the same trait twice, so a player who's high on both looks more unusual than he really is.

**So I used Mahalanobis distance to fix that.** It first measures how the six stats move together across every run, then measures distance in a way that accounts for it. A common combination (high usage with high assists) counts for less, and a rare combination counts for more.

Here's an analogy. Picture two 7-footers, one at 280 lbs and one at 180 lbs. Stat by stat, the 280-lb one is further from the average weight, so Euclidean distance calls him the more unusual of the two. But tall people are usually heavy, so the 180-lb seven-footer is the one you'd almost never see. Mahalanobis gets that right.

| | Euclidean | Mahalanobis |
|---|---|---|
| How it works | Straight-line distance across the six stats | Same idea, after accounting for which stats move together |
| Pros | Simple to compute and explain. Matches the original argument. | Doesn't double-count traits that go together. Rare combinations stand out. |
| Cons | Treats the stats as unrelated, so correlated stats count twice | Harder to explain. Relies on estimating how the stats relate, and extreme runs can pull that estimate around. |

Switching moved 2018 LeBron from #55 to #67, and the top of the list still belongs to role players with extreme profiles, like Nate McMillan in 1993.

That showed me the bigger problem isn't which distance you use. Distance measures *unusual*, not *great*, so on its own it can't settle a carry argument.

## Measuring carry

So I measured carry directly, two ways:

- **Win Share share:** the player's share of his team's playoff Win Shares, with teammates below zero counted as zero.
- **Cast gap:** the player's Box Plus/Minus minus his teammates' minutes-weighted Box Plus/Minus. A big gap means a great player with a weak supporting cast.

Short playoff runs inflate Win Share share because the team total is small, so I also ranked Finals teams on their own. I reran everything at 150, 250 and 400 minute cutoffs to make sure the answer didn't hinge on that choice.

## Run it

```
python src/scrape.py     # downloads Basketball-Reference pages into data/raw (about 4 seconds per page, on purpose)
python src/parse.py      # builds data/playoff_advanced.csv and data/team_results.csv
python src/analyze.py    # writes rankings to results/
python src/charts.py     # writes charts to results/
```

Data comes from Basketball-Reference (Sports Reference LLC). The raw pages and parsed data aren't committed, so run the scripts to rebuild them.

Built with help from Claude as a coding and stats assistant.
