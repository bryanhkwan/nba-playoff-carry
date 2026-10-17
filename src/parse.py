"""Turn the downloaded Basketball-Reference pages into two CSVs.

data/playoff_advanced.csv  one row per player per postseason (a "run")
data/team_results.csv      one row per team per postseason: series won, Finals, title
"""
import re
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data"

# Basketball-Reference has renamed some columns over the years; map both spellings.
RENAME = {
    "name_display": "player",
    "name_display_id": "player_id",
    "name_display_href": "player_href",
    "team_name_abbr": "team_id",
    "games": "g",
}
NUMERIC = ["age", "g", "mp", "per", "ts_pct", "trb_pct", "ast_pct", "stl_pct", "blk_pct",
           "tov_pct", "usg_pct", "ows", "dws", "ws", "ws_per_48", "obpm", "dbpm", "bpm", "vorp"]


class TableParser(HTMLParser):
    """Collects a stats table's body rows as {data-stat: text}, keeping each cell's
    first link (as <stat>_href) and Basketball-Reference ID (as <stat>_id)."""

    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell, self.in_body = [], None, None, False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tbody":
            self.in_body = True
        elif tag == "tr" and self.in_body:
            # Long tables repeat their header row inside the body; skip those.
            self.row = None if "thead" in (attrs.get("class") or "") else {}
        elif tag in ("td", "th") and self.row is not None and attrs.get("data-stat"):
            self.cell = attrs["data-stat"]
            self.row[self.cell] = ""
            if attrs.get("data-append-csv"):
                self.row[self.cell + "_id"] = attrs["data-append-csv"]
        elif tag == "a" and self.row is not None and self.cell:
            self.row.setdefault(self.cell + "_href", attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.rows.append(self.row)
            self.row = None
        elif tag == "tbody":
            self.in_body = False

    def handle_data(self, data):
        if self.row is not None and self.cell:
            self.row[self.cell] += data


def table_rows(html, table_id):
    # Some tables ship inside HTML comments; drop the markers so they parse like the rest.
    html = html.replace("<!--", "").replace("-->", "")
    match = re.search(rf'<table[^>]*id="{table_id}".*?</table>', html, re.S)
    if not match:
        return []
    parser = TableParser()
    parser.feed(match.group(0))
    return parser.rows


def id_from_href(href, pattern):
    match = re.search(pattern, href or "")
    return match.group(1) if match else None


def parse_advanced():
    frames = []
    for path in sorted(RAW.glob("NBA_*_advanced.html")):
        season = int(path.stem.split("_")[1])
        html = path.read_text(encoding="utf-8")
        rows = table_rows(html, "advanced_stats") or table_rows(html, "advanced")
        if not rows:
            print(f"no advanced table in {path.name}")
            continue
        df = pd.DataFrame(rows).rename(columns=RENAME)
        if "player_id" not in df:
            df["player_id"] = None
        from_href = df["player_href"].map(lambda h: id_from_href(h, r"/players/\w/(\w+)\.html"))
        df["player_id"] = df["player_id"].fillna(from_href)
        df["player"] = df["player"].str.replace("*", "", regex=False).str.strip()
        df["season"] = season
        frames.append(df)
    runs = pd.concat(frames, ignore_index=True)
    for col in NUMERIC:
        runs[col] = pd.to_numeric(runs.get(col), errors="coerce")
    runs = runs[runs.player_id.notna() & runs.team_id.notna()]
    cols = ["season", "player_id", "player", "team_id"] + NUMERIC
    return runs[cols].sort_values(["season", "team_id", "player"]).reset_index(drop=True)


def parse_series():
    rows = table_rows((RAW / "series.html").read_text(encoding="utf-8"), "playoffs_series")
    records = []
    for r in rows:
        if r.get("lg", "").strip() != "NBA":
            continue
        season = int(r["season"].strip())
        is_finals = r["series"].strip() == "Finals"
        team_pattern = r"/teams/(\w+)/\d{4}\.html"
        winner = id_from_href(r.get("winner_href"), team_pattern)
        loser = id_from_href(r.get("loser_href"), team_pattern)
        wins_w = int(pd.to_numeric(r.get("wins_winner"), errors="coerce") or 0)
        wins_l = int(pd.to_numeric(r.get("wins_loser"), errors="coerce") or 0)
        records.append(dict(season=season, team_id=winner, won=True, finals=is_finals, wins=wins_w, losses=wins_l))
        records.append(dict(season=season, team_id=loser, won=False, finals=is_finals, wins=wins_l, losses=wins_w))
    series = pd.DataFrame(records)
    teams = (series.groupby(["season", "team_id"])
             .agg(series_won=("won", "sum"), series_played=("won", "size"),
                  playoff_wins=("wins", "sum"), playoff_losses=("losses", "sum"),
                  reached_finals=("finals", "any"))
             .reset_index())
    champions = series[series.finals & series.won][["season", "team_id"]].assign(won_title=True)
    teams = teams.merge(champions, how="left", on=["season", "team_id"])
    teams["won_title"] = teams["won_title"].astype("boolean").fillna(False).astype(bool)
    return teams


def main():
    runs = parse_advanced()
    teams = parse_series()
    runs.to_csv(DATA / "playoff_advanced.csv", index=False)
    teams.to_csv(DATA / "team_results.csv", index=False)
    print(f"{len(runs):,} runs across {runs.season.nunique()} postseasons -> data/playoff_advanced.csv")
    print(f"{len(teams):,} team postseasons -> data/team_results.csv")


if __name__ == "__main__":
    main()
