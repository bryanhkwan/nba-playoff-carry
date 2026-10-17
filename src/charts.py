"""Render the charts in results/ from the analysis output.

Static PNGs sized for LinkedIn (4:5 portrait for rankings, square for the map).
LeBron's runs are blue, Jordan's are orange, everyone else is gray. Those two hues
pass the colorblind checks as a pair, and every chart also has a legend or direct
labels, so color is never the only cue.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"

LEBRON, JORDAN = "jamesle01", "jordami01"
SURFACE = "#fcfcfb"
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#c3c2b7"
DPI = 270
SCALE = 2  # the images are rendered at 2x the size LinkedIn displays them, so 1 css px = 2 image px

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 11,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK,
    "axes.labelcolor": INK_2,
    "xtick.color": MUTED,
    "ytick.color": INK,
})


def color_for(player_id):
    return {LEBRON: BLUE, JORDAN: ORANGE}.get(player_id, GRAY)


def style_axes(ax, grid_axis):
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(BASELINE)
    ax.spines["left"].set_linewidth(0.6)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.6, linestyle="-")
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def titles(fig, title, subtitle, source):
    fig.text(0.04, 0.975, title, fontsize=19, fontweight="semibold", color=INK, va="top")
    fig.text(0.04, 0.935, subtitle, fontsize=11.5, color=INK_2, va="top", linespacing=1.4)
    fig.text(0.04, 0.018, source, fontsize=9, color=MUTED, va="bottom")


def legend(target, entries, **placement):
    """target is an Axes (legend inside the plot) or a Figure (legend in a row above it)."""
    handles = [plt.Line2D([], [], marker="s", linestyle="", markersize=9, color=c, label=l) for l, c in entries]
    leg = target.legend(handles=handles, frameon=False, fontsize=10.5, handletextpad=0.4, **placement)
    for text in leg.get_texts():
        text.set_color(INK_2)


def rounded_hbars(ax, values, colors, bar_px=22):
    """Horizontal bars, at most 24 css px thick: rounded (4 px) at the data end,
    square at the baseline."""
    n = len(values)
    ax.set_ylim(n - 0.4, -0.6)
    ax.set_xlim(0, max(values) * 1.16)
    ax.figure.canvas.draw()
    bbox = ax.get_window_extent()
    x_per_px = (ax.get_xlim()[1] - ax.get_xlim()[0]) / bbox.width
    y_per_px = abs(ax.get_ylim()[1] - ax.get_ylim()[0]) / bbox.height
    height = bar_px * SCALE * y_per_px
    radius = 4 * SCALE * x_per_px
    for i, (value, color) in enumerate(zip(values, colors)):
        y = i - height / 2
        ax.add_patch(FancyBboxPatch((0, y), value, height, boxstyle=f"round,pad=0,rounding_size={radius}",
                                    mutation_aspect=y_per_px / x_per_px, facecolor=color, edgecolor="none"))
        ax.add_patch(Rectangle((0, y), min(radius, value), height, facecolor=color, edgecolor="none"))


def how_far(row):
    if row.won_title:
        return "won title"
    if row.reached_finals:
        return "lost Finals"
    return "out in 1st series" if row.series_won == 0 else f"won {int(row.series_won)} series"


def ranking_chart(df, value_col, fmt, path, title, subtitle, show_legend=True, notes=None):
    df = df.reset_index(drop=True)
    fig = plt.figure(figsize=(8, 10), dpi=DPI)
    ax = fig.add_axes([0.36, 0.08, 0.58, 0.76])
    values = df[value_col].tolist()
    rounded_hbars(ax, values, [color_for(p) for p in df.player_id])
    if notes:
        ax.set_xlim(0, max(values) * 1.45)  # room for the "how far" note after each value
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([f"{p} {s}" for p, s in zip(df.player, df.season)], fontsize=11.5)
    for i, v in enumerate(values):
        label = fmt(v) if not notes else f"{fmt(v)}  ·  {notes[i]}"
        ax.text(v + max(values) * 0.015, i, label, va="center", fontsize=10.5, color=INK_2)
    ax.set_xticks([])  # every bar carries its value, so the x-axis would only repeat them
    style_axes(ax, None)
    titles(fig, title, subtitle, "Data: Basketball-Reference, NBA playoffs 1978-2026, runs with 250+ minutes. Method: github.com/bryanhkwan/playoff-carry")
    if show_legend:
        present = [(l, c) for pid, l, c in ((LEBRON, "LeBron James", BLUE), (JORDAN, "Michael Jordan", ORANGE))
                   if (df.player_id == pid).any()]
        legend(fig, present + [("Everyone else", GRAY)], loc="upper left",
               bbox_to_anchor=(0.03, 0.885), ncol=3, columnspacing=1.6)
    fig.savefig(path)
    plt.close(fig)


def map_chart(q, path, label_runs):
    fig = plt.figure(figsize=(9, 9), dpi=DPI)
    ax = fig.add_axes([0.1, 0.09, 0.85, 0.76])
    rest = q[~q.player_id.isin([LEBRON, JORDAN])]
    ax.scatter(rest.z_usg_pct, rest.z_ts_pct, s=14, color=GRAY, edgecolors=SURFACE, linewidths=0.5, zorder=2)
    for pid, color in ((JORDAN, ORANGE), (LEBRON, BLUE)):
        mine = q[q.player_id == pid]
        ax.scatter(mine.z_usg_pct, mine.z_ts_pct, s=70, color=color, edgecolors=SURFACE, linewidths=1.2, zorder=3)
    # The two labelled runs sit close together, so each label goes out to open space
    # with a leader line instead of being nudged beside its dot.
    for pid, season, (dx, dy) in label_runs:
        row = q[(q.player_id == pid) & (q.season == season)].iloc[0]
        ax.annotate(f"{row.player} {season}", (row.z_usg_pct, row.z_ts_pct),
                    xytext=(row.z_usg_pct + dx, row.z_ts_pct + dy), ha="center", fontsize=11,
                    color=INK, fontweight="semibold", zorder=4,
                    arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.8, shrinkA=3, shrinkB=6))
    ax.axhline(0, color=BASELINE, linewidth=0.6, zorder=1)
    ax.axvline(0, color=BASELINE, linewidth=0.6, zorder=1)
    style_axes(ax, "both")
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Usage rate vs. that postseason (standard deviations)", fontsize=11)
    ax.set_ylabel("True shooting vs. that postseason (standard deviations)", fontsize=11)
    titles(fig, "Workload vs. efficiency, every playoff run since 1978",
           "Each dot is one player's postseason. Further right = carried more of the offense;\nhigher = scored more efficiently. Both are measured against that year's playoffs.",
           "Data: Basketball-Reference, runs with 250+ minutes. Method: github.com/bryanhkwan/playoff-carry")
    legend(ax, [("LeBron James", BLUE), ("Michael Jordan", ORANGE), ("Everyone else", GRAY)], loc="lower left")
    ax.set_xlim(right=max(q.z_usg_pct.max(), 3.3) + 0.35)
    fig.savefig(path)
    plt.close(fig)


def main():
    q = pd.read_csv(DATA / "qualifying_runs.csv")
    ids = q.set_index(["player", "season"]).player_id.to_dict()

    neighbors = pd.read_csv(RESULTS / "replication_neighbors.csv")
    neighbors["player_id"] = [ids.get((p, s)) for p, s in zip(neighbors.player, neighbors.season)]
    ranking_chart(neighbors, "distance", lambda v: f"{v:.2f}", RESULTS / "fig_neighbors.png",
                  "Who's closest to 2018 LeBron?",
                  "The 10 nearest playoff runs across six era-adjusted stats\n(usage, assists, rebounds, steals, blocks, true shooting). Shorter = more similar.")

    for name, label in (("euclid", "the video's method"), ("mahal", "correcting for stats that move together")):
        top = q.sort_values(f"iso_{name}", ascending=False).head(15)
        ranking_chart(top, f"iso_{name}", lambda v: f"{v:.2f}", RESULTS / f"fig_isolation_{name}.png",
                      "The most one-of-a-kind playoff runs",
                      f"Distance from each run to the closest run by any other player ({label}).\nLonger = nobody else has played like that.")

    top = q.sort_values("ws_share", ascending=False).head(15)
    ranking_chart(top, "ws_share", lambda v: f"{v:.0%}", RESULTS / "fig_carry_ws_share.png",
                  "The biggest playoff carry jobs since 1978",
                  "Share of the team's playoff Win Shares produced by one player.\nTeammates below zero count as zero, so no one gets credit for others' negatives.",
                  notes=[how_far(r) for r in top.itertuples()])

    top = q[q.reached_finals].sort_values("ws_share", ascending=False).head(15)
    ranking_chart(top, "ws_share", lambda v: f"{v:.0%}", RESULTS / "fig_carry_finals.png",
                  "The biggest carry jobs to reach the NBA Finals",
                  "Share of the team's playoff Win Shares produced by one player,\nFinals teams only, 1978-2026.",
                  notes=[how_far(r) for r in top.itertuples()])

    top = q.sort_values("cast_gap", ascending=False).head(15)
    ranking_chart(top, "cast_gap", lambda v: f"+{v:.1f}", RESULTS / "fig_carry_cast_gap.png",
                  "The widest gaps between a star and his supporting cast",
                  "Player's playoff Box Plus/Minus minus his teammates' minutes-weighted BPM.",
                  notes=[how_far(r) for r in top.itertuples()])

    jordan_best = q[q.player_id == JORDAN].sort_values("ws_share", ascending=False).iloc[0]
    map_chart(q, RESULTS / "fig_map.png",
              [(LEBRON, 2018, (-0.6, 2.0)), (JORDAN, int(jordan_best.season), (0.25, -2.6))])
    print("charts written to results/")


if __name__ == "__main__":
    main()
