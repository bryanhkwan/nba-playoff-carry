"""Run the tests in METHOD.md and write the results to results/.

Each function maps to a section of METHOD.md. Nothing here was tuned after seeing
results; any deviation from METHOD.md is logged in RESULTS.md.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"

SIX = ["usg_pct", "ast_pct", "trb_pct", "stl_pct", "blk_pct", "ts_pct"]
Z = ["z_" + s for s in SIX]
PRIMARY_MIN_MP = 250
SENSITIVITY_MIN_MP = [150, 250, 400]
LEBRON, JORDAN, BIRD = "jamesle01", "jordami01", "birdla01"
TARGET_SEASON = 2018
TOP_N = 15
TOP_COUNT = 25  # LeBron vs. Jordan: how many runs land in each ranking's top 25


# --- Data: which postseasons are usable -------------------------------------------

def season_coverage(runs):
    """A postseason is usable if each of the six stats was tracked that year, i.e. it is
    present for at least one run with 150+ minutes (the lowest threshold used anywhere)."""
    big = runs[runs.mp >= min(SENSITIVITY_MIN_MP)]
    tracked = big.groupby("season")[SIX].agg(lambda s: s.notna().any())
    usable = tracked.all(axis=1)
    return sorted(usable[usable].index), sorted(usable[~usable].index)


# --- Who counts + six-number profile ----------------------------------------------

def qualify(runs, min_mp):
    q = runs[(runs.mp >= min_mp) & runs[SIX].notna().all(axis=1)].copy()
    by_season = q.groupby("season")
    for stat, z in zip(SIX, Z):
        mean = by_season[stat].transform("mean")
        sd = by_season[stat].transform(lambda s: s.std(ddof=0))
        q[z] = (q[stat] - mean) / sd
    return q.reset_index(drop=True)


def labels(df):
    return [f"{p} {s}" for p, s in zip(df.player, df.season)]


# --- Test 2: isolation -------------------------------------------------------------

def mahalanobis_whiten(z):
    """Linear transform after which plain Euclidean distance equals Mahalanobis
    distance under the pooled covariance of the z-scores."""
    vals, vecs = np.linalg.eigh(np.cov(z, rowvar=False))
    return z @ (vecs @ np.diag(vals ** -0.5) @ vecs.T)


def add_isolation(q):
    ids = q.player_id.to_numpy()
    same_player = ids[:, None] == ids[None, :]
    names = labels(q)
    z = q[Z].to_numpy()
    for name, x in (("euclid", z), ("mahal", mahalanobis_whiten(z))):
        d = cdist(x, x)
        d[same_player] = np.inf
        nearest = d.argmin(axis=1)
        q[f"iso_{name}"] = d[np.arange(len(q)), nearest]
        q[f"iso_{name}_nearest"] = [names[i] for i in nearest]
        q[f"iso_{name}_rank"] = q[f"iso_{name}"].rank(ascending=False, method="min").astype(int)
    return q


# --- Test 3: carry -----------------------------------------------------------------

def team_context(runs, teams):
    """Win Share share and cast gap use every player on the team, not just qualifiers."""
    r = runs.copy()
    key = ["season", "team_id"]
    r["ws_pos"] = r.ws.clip(lower=0)
    has_bpm = r.bpm.notna() & r.mp.notna()
    r["bpm_x_mp"] = np.where(has_bpm, r.bpm * r.mp, 0.0)
    r["mp_with_bpm"] = np.where(has_bpm, r.mp, 0.0)
    g = r.groupby(key)
    team_pos_ws = g.ws_pos.transform("sum")
    r["ws_share"] = r.ws / team_pos_ws.where(team_pos_ws > 0)
    mates_bpm_x_mp = g.bpm_x_mp.transform("sum") - r.bpm_x_mp
    mates_mp = g.mp_with_bpm.transform("sum") - r.mp_with_bpm
    r["mates_bpm"] = mates_bpm_x_mp / mates_mp.where(mates_mp > 0)
    r["cast_gap"] = r.bpm - r.mates_bpm
    r = r.merge(teams, how="left", on=key)
    r["reached_finals"] = r.reached_finals.astype("boolean").fillna(False).astype(bool)
    r["won_title"] = r.won_title.astype("boolean").fillna(False).astype(bool)
    r["mpg"] = r.mp / r.g
    keep = ["season", "player_id", "ws_share", "mates_bpm", "cast_gap", "mpg",
            "series_won", "playoff_wins", "playoff_losses", "reached_finals", "won_title"]
    return r[keep]


def analyze(runs, teams, min_mp):
    q = add_isolation(qualify(runs, min_mp))
    q = q.merge(team_context(runs, teams), how="left", on=["season", "player_id"])
    q["c1_rank"] = q.ws_share.rank(ascending=False, method="min")
    q["c2_rank"] = q.ws_share.where(q.reached_finals).rank(ascending=False, method="min")
    q["c3_rank"] = q.cast_gap.rank(ascending=False, method="min")
    return q


def target_index(q):
    hit = q.index[(q.player_id == LEBRON) & (q.season == TARGET_SEASON)]
    if len(hit) != 1:
        raise SystemExit(f"expected exactly one LeBron {TARGET_SEASON} run, found {len(hit)}")
    return hit[0]


# --- Test 1: replication -----------------------------------------------------------

def replication(q):
    t = target_index(q)
    d = cdist(q.loc[[t], Z].to_numpy(), q[Z].to_numpy())[0]
    order = [i for i in np.argsort(d, kind="stable") if i != t]
    nearest10 = q.loc[order[:10], ["player", "season", "team_id"] + SIX].assign(distance=d[order[:10]])
    other = next(i for i in order if q.player_id[i] != LEBRON)
    return nearest10, q.loc[other], d[other]


# --- Verdicts ------------------------------------------------------------------------

def carry_verdict(row):
    if row.c1_rank == 1:
        return "supported"
    if row.c2_rank == 1 or row.c3_rank == 1:
        return "partly supported"
    return "not supported"


def head_to_head(q):
    pair = q[q.player_id.isin([LEBRON, JORDAN])]
    measures = {
        "iso_euclid": "iso_euclid_rank",
        "iso_mahal": "iso_mahal_rank",
        "ws_share": "c1_rank",
        "cast_gap": "c3_rank",
    }
    summary = {}
    for pid, name in ((LEBRON, "LeBron James"), (JORDAN, "Michael Jordan")):
        mine = pair[pair.player_id == pid]
        summary[name] = {"qualifying_runs": int(len(mine))}
        for measure, rank_col in measures.items():
            best = mine.loc[mine[measure].idxmax()]
            summary[name][measure] = {
                "best_run": int(best.season),
                "best_value": round(float(best[measure]), 3),
                "best_rank": int(best[rank_col]),
                f"runs_in_top_{TOP_COUNT}": int((mine[rank_col] <= TOP_COUNT).sum()),
            }
    return pair, summary


def main():
    RESULTS.mkdir(exist_ok=True)
    runs = pd.read_csv(DATA / "playoff_advanced.csv")
    teams = pd.read_csv(DATA / "team_results.csv")

    usable, excluded = season_coverage(runs)
    runs = runs[runs.season.isin(usable)]
    unmatched_teams = sorted(set(map(tuple, runs[["season", "team_id"]].drop_duplicates().to_numpy()))
                             - set(map(tuple, teams[["season", "team_id"]].to_numpy())))

    q = analyze(runs, teams, PRIMARY_MIN_MP)
    q.to_csv(DATA / "qualifying_runs.csv", index=False)  # full table stays local (data/ is gitignored)
    t = target_index(q)
    target = q.loc[t]

    nearest10, other, other_dist = replication(q)
    nearest10.round(3).to_csv(RESULTS / "replication_neighbors.csv", index=False)

    show = ["player", "season", "team_id", "mp", "mpg"] + SIX
    iso_cols = {"euclid": ["iso_euclid", "iso_euclid_nearest"], "mahal": ["iso_mahal", "iso_mahal_nearest"]}
    for name, cols in iso_cols.items():
        top = q.sort_values(f"iso_{name}", ascending=False).head(TOP_N)
        top[show + cols].round(3).to_csv(RESULTS / f"isolation_{name}_top{TOP_N}.csv", index=False)

    carry_cols = ["player", "season", "team_id", "mpg", "ws", "ws_share", "bpm", "mates_bpm",
                  "cast_gap", "series_won", "reached_finals", "won_title"]
    q.sort_values("ws_share", ascending=False).head(TOP_N)[carry_cols].round(3) \
        .to_csv(RESULTS / f"carry_c1_top{TOP_N}.csv", index=False)
    q[q.reached_finals].sort_values("ws_share", ascending=False).head(TOP_N)[carry_cols].round(3) \
        .to_csv(RESULTS / f"carry_c2_finals_top{TOP_N}.csv", index=False)
    q.sort_values("cast_gap", ascending=False).head(TOP_N)[carry_cols].round(3) \
        .to_csv(RESULTS / f"carry_c3_top{TOP_N}.csv", index=False)

    pair, h2h = head_to_head(q)
    pair_cols = ["player", "season", "team_id", "mp", "mpg"] + SIX + [
        "iso_euclid", "iso_euclid_rank", "iso_mahal", "iso_mahal_rank", "ws", "ws_share", "c1_rank",
        "bpm", "mates_bpm", "cast_gap", "c3_rank", "series_won", "reached_finals", "won_title"]
    pair.sort_values(["player", "season"])[pair_cols].round(3).to_csv(RESULTS / "lebron_vs_jordan.csv", index=False)

    sensitivity = []
    for min_mp in SENSITIVITY_MIN_MP:
        qs = analyze(runs, teams, min_mp)
        row = qs.loc[target_index(qs)]
        _, other_s, dist_s = replication(qs)
        sensitivity.append({
            "min_minutes": min_mp, "qualifying_runs": len(qs),
            "iso_euclid_rank": int(row.iso_euclid_rank), "iso_mahal_rank": int(row.iso_mahal_rank),
            "c1_rank": int(row.c1_rank), "c2_rank": int(row.c2_rank), "c3_rank": int(row.c3_rank),
            "nearest_other_player": f"{other_s.player} {other_s.season}", "nearest_other_distance": round(float(dist_s), 3),
            "carry_verdict": carry_verdict(row),
        })
    pd.DataFrame(sensitivity).to_csv(RESULTS / "sensitivity.csv", index=False)

    summary = {
        "postseasons_used": [int(usable[0]), int(usable[-1]), len(usable)],
        "postseasons_excluded": [int(s) for s in excluded],
        "team_seasons_without_series_data": [f"{s} {t}" for s, t in unmatched_teams],
        "qualifying_runs": int(len(q)),
        "target": {
            "stats": {s: float(target[s]) for s in SIX},
            "z": {z: round(float(target[z]), 2) for z in Z},
            "mpg": round(float(target.mpg), 1), "ws": float(target.ws), "ws_share": round(float(target.ws_share), 3),
            "bpm": float(target.bpm), "mates_bpm": round(float(target.mates_bpm), 2),
            "cast_gap": round(float(target.cast_gap), 2),
            "iso_euclid": round(float(target.iso_euclid), 3), "iso_euclid_rank": int(target.iso_euclid_rank),
            "iso_mahal": round(float(target.iso_mahal), 3), "iso_mahal_rank": int(target.iso_mahal_rank),
            "c1_rank": int(target.c1_rank), "c2_rank": int(target.c2_rank), "c3_rank": int(target.c3_rank),
        },
        "test1_nearest_other_player": {"run": f"{other.player} {other.season}", "distance": round(float(other_dist), 3),
                                        "bird_claim_confirmed": bool(other.player_id == BIRD)},
        "test2_most_unique_euclid": bool(target.iso_euclid_rank == 1),
        "test3_carry_verdict": carry_verdict(target),
        "lebron_vs_jordan": h2h,
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
