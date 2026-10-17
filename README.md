# Playoff Carry

Was 2018 LeBron James the biggest carry job in NBA playoff history? A viral video said yes, based on how far his stat profile sat from everyone else's. This project rebuilds that analysis and then tests the claim more carefully.

- [METHOD.md](METHOD.md): the method, committed before any data was pulled
- [RESULTS.md](RESULTS.md): what the data says

## Run it

```
python src/scrape.py     # downloads Basketball-Reference pages into data/raw (about 4 seconds per page, on purpose)
python src/parse.py      # builds data/playoff_advanced.csv and data/team_results.csv
python src/analyze.py    # writes rankings to results/
python src/charts.py     # writes charts to results/
```

Data comes from Basketball-Reference (Sports Reference LLC). The raw pages and parsed data aren't committed, so run the scripts to rebuild them.
