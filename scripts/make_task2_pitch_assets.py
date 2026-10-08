"""Generate chart-first PNG visuals for Task-2 jury pitch.

Run from repo root:
    python scripts/make_task2_pitch_assets.py

All numbers from results/* — no invented data.
Colors: navy + teal + orange (same as Task 1).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "_pitch" / "presentation_assets"
RESULTS = ROOT / "results"

C_BG = "#f4f6f8"
C_INK = "#1a2332"
C_NAVY = "#1e3a5f"
C_TEAL = "#2a6f6a"
C_ORANGE = "#c45c26"
C_MUTED = "#6b7280"
C_CARD = "#ffffff"
C_LINE = "#d0d5dd"
C_GOLD = "#b08900"
C_OK = "#2e7d4f"
C_BAD = "#a33b2b"

# Documented pre-leakage MAE (from results/forecast_mae_post_leakage.md).
# Backup folder was not shipped; values are exact from that audit table.
OLD_MAE = {
    # (cluster, horizon, model) -> MAE
    (0, 3, "prophet"): 22807.8,
    (1, 3, "prophet"): 39107.5,
    (1, 3, "lgbm_trends"): 3878.0,
    (0, 1, "prophet"): 2493.24,
    (1, 1, "prophet"): 6216.0,
}


def _style():
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor": C_CARD,
        "axes.edgecolor": C_LINE,
        "axes.labelcolor": C_INK,
        "text.color": C_INK,
        "xtick.color": C_INK,
        "ytick.color": C_INK,
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "figure.dpi": 150,
    })


def _save(fig, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor=C_BG, pad_inches=0.15)
    plt.close(fig)
    print(f"  -> {path.name}")
    return path


def _card(ax, x, y, w, h, ec=C_NAVY, fc=C_CARD, lw=2.0):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02",
        facecolor=fc, edgecolor=ec, linewidth=lw,
    ))


def load_data():
    fc = pd.read_csv(RESULTS / "forecast_all_models.csv")
    cons = pd.read_csv(RESULTS / "changepoints_consensus.csv")
    dyn = json.loads((RESULTS / "dynamic_summary.json").read_text(encoding="utf-8"))
    foundation = pd.read_csv(RESULTS / "forecast_foundation.csv")
    news = pd.read_csv(RESULTS / "forecast_news.csv")

    models = [
        "naive", "seasonal", "mean", "prophet",
        "lgbm", "lgbm_trends", "catboost", "catboost_trends",
    ]
    winners = []
    for _, row in fc.iterrows():
        best_m, best_v = None, np.inf
        for m in models:
            v = row.get(f"MAE_{m}")
            if pd.notna(v) and float(v) < best_v:
                best_v, best_m = float(v), m
        winners.append({
            "cluster": int(row["cluster"]),
            "name": str(row["cluster_name"]),
            "H": int(row["horizon"]),
            "winner": best_m,
            "MAE": best_v,
        })
    return {
        "fc": fc, "cons": cons, "dyn": dyn, "foundation": foundation,
        "news": news, "models": models, "winners": winners,
    }


def slide01_hook(d):
    fig, ax = plt.subplots(figsize=(12.8, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch(
        (0, 0.52), 1.0, 0.48, boxstyle="square,pad=0",
        facecolor=C_NAVY, edgecolor="none",
    ))
    ax.text(
        0.5, 0.82,
        "Можно ли предсказать расходы —\nи поймать момент, когда режим меняется?",
        ha="center", va="center", fontsize=22, fontweight="bold",
        color="white", linespacing=1.35,
    )
    ax.text(
        0.5, 0.60,
        "280 МО СЗФО  ·  2 режима потребления  ·  ≈24 месяца",
        ha="center", va="center", fontsize=13, color="#c8d4e4",
    )

    for x, title, sub, col in [
        (0.08, "Прогноз", "что будет с расходами\nна H = 1 / 3 / 6 / 12", C_TEAL),
        (0.52, "Сдвиги режима", "когда спектральный\nсигнал переломился", C_ORANGE),
    ]:
        _card(ax, x, 0.10, 0.40, 0.34, ec=col, lw=2.5)
        ax.text(x + 0.20, 0.35, title, ha="center", fontsize=16,
                fontweight="bold", color=col)
        ax.text(x + 0.20, 0.20, sub, ha="center", fontsize=12,
                color=C_INK, linespacing=1.35)

    return _save(fig, "slide01_hook.png")


def slide02_bakeoff(d):
    fig, ax = plt.subplots(figsize=(12.8, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _card(ax, 0.08, 0.72, 0.84, 0.18, ec=C_NAVY, fc="#e8eef5", lw=2)
    ax.text(
        0.50, 0.81,
        "280 МО → 2 режима (140 / 140) → два независимых ответа",
        ha="center", fontsize=13, fontweight="bold", color=C_NAVY,
    )

    _card(ax, 0.05, 0.18, 0.42, 0.48, ec=C_TEAL, lw=2.5)
    ax.text(0.26, 0.58, "A · ПРОГНОЗ", ha="center", fontsize=15,
            fontweight="bold", color=C_TEAL)
    ax.text(
        0.26, 0.38,
        "naive · seasonal · mean\nProphet · LGBM · CatBoost\n± Trends · Chronos\n→ MAE по H×типу",
        ha="center", va="center", fontsize=12, color=C_INK, linespacing=1.45,
    )

    _card(ax, 0.53, 0.18, 0.42, 0.48, ec=C_ORANGE, lw=2.5)
    ax.text(0.74, 0.58, "B · CHANGEPOINTS", ha="center", fontsize=15,
            fontweight="bold", color=C_ORANGE)
    ax.text(
        0.74, 0.38,
        "сигнал [λ₁…λ₅, PR₊]\n9 методов ruptures\nконсенсус ≥ 50%\n→ даты сдвигов",
        ha="center", va="center", fontsize=12, color=C_INK, linespacing=1.45,
    )

    ax.text(
        0.50, 0.06,
        "Тип A — сельский паттерн (↑ grocery)  ·  Тип B — городской (↑ food / transport)",
        ha="center", fontsize=11, color=C_MUTED,
    )
    return _save(fig, "slide02_bakeoff.png")


def slide03_leakage(d):
    fc = d["fc"]

    def _new(cl, h, col):
        return float(fc[(fc.cluster == cl) & (fc.horizon == h)][col].iloc[0])

    pairs = [
        ("Городские H=3\nLGBM + Trends",
         OLD_MAE[(1, 3, "lgbm_trends")], _new(1, 3, "MAE_lgbm_trends"),
         "утечка завышала выгоду Trends"),
        ("Сельские H=3\nProphet",
         OLD_MAE[(0, 3, "prophet")], _new(0, 3, "MAE_prophet"),
         "катастрофа Prophet исправлена"),
        ("Городские H=3\nProphet",
         OLD_MAE[(1, 3, "prophet")], _new(1, 3, "MAE_prophet"),
         "катастрофа Prophet исправлена"),
    ]

    fig = plt.figure(figsize=(12.8, 7.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 2.5], hspace=0.22)
    ax_top = fig.add_subplot(gs[0])
    ax_bot = fig.add_subplot(gs[1])

    ax_top.set_xlim(0, 1)
    ax_top.set_ylim(0, 1)
    ax_top.axis("off")

    _card(ax_top, 0.04, 0.12, 0.42, 0.76, ec=C_ORANGE, lw=2)
    ax_top.text(0.25, 0.68, "БЫЛО", ha="center", fontsize=13,
                fontweight="bold", color=C_ORANGE)
    ax_top.text(0.25, 0.38, "start_dt ≤ ds\nокна «видели» будущее",
                ha="center", va="center", fontsize=12, color=C_INK, linespacing=1.4)

    _card(ax_top, 0.54, 0.12, 0.42, 0.76, ec=C_TEAL, lw=2)
    ax_top.text(0.75, 0.68, "СТАЛО", ha="center", fontsize=13,
                fontweight="bold", color=C_TEAL)
    ax_top.text(0.75, 0.38, "end_dt < ds\nокно закончилось до ds",
                ha="center", va="center", fontsize=12, color=C_INK, linespacing=1.4)
    ax_top.annotate("", xy=(0.52, 0.50), xytext=(0.48, 0.50),
                    arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=2.5))

    ax_bot.set_xlim(0, 1)
    ax_bot.set_ylim(0, 1)
    ax_bot.axis("off")

    for i, (label, old_v, new_v, note) in enumerate(pairs):
        x0 = 0.04 + i * 0.32
        _card(ax_bot, x0, 0.08, 0.30, 0.84, ec=C_LINE, lw=1.5)
        ax_bot.text(x0 + 0.15, 0.82, label, ha="center", va="top",
                    fontsize=11, fontweight="bold", color=C_NAVY, linespacing=1.25)
        ax_bot.text(x0 + 0.07, 0.55, "до", ha="center", fontsize=9, color=C_MUTED)
        ax_bot.text(x0 + 0.07, 0.40, f"{old_v:.0f}", ha="center", fontsize=17,
                    fontweight="bold", color=C_ORANGE if old_v > 10000 else C_INK)
        ax_bot.annotate("", xy=(x0 + 0.20, 0.46), xytext=(x0 + 0.12, 0.46),
                        arrowprops=dict(arrowstyle="->", color=C_MUTED, lw=1.5))
        ax_bot.text(x0 + 0.24, 0.55, "после", ha="center", fontsize=9, color=C_MUTED)
        new_col = C_TEAL if new_v < old_v else C_ORANGE
        ax_bot.text(x0 + 0.24, 0.40, f"{new_v:.0f}", ha="center", fontsize=17,
                    fontweight="bold", color=new_col)
        ax_bot.text(x0 + 0.15, 0.16, note, ha="center", fontsize=9,
                    color=C_MUTED, style="italic")

    return _save(fig, "slide03_leakage.png")


def slide04_mae_grid(d):
    """Big real MAE heatmap-style chart from forecast_all_models.csv."""
    fc = d["fc"]
    winners = d["winners"]
    models_show = ["naive", "seasonal", "prophet", "lgbm", "lgbm_trends", "catboost"]
    labels = ["naive", "seasonal", "prophet", "lgbm", "lgbm+tr", "catboost"]

    fig, axes = plt.subplots(1, 2, figsize=(13.0, 6.8), sharey=True)
    for ax, cl, title in [
        (axes[0], 0, "Тип A · сельский паттерн"),
        (axes[1], 1, "Тип B · городской паттерн"),
    ]:
        sub = fc[fc["cluster"] == cl].sort_values("horizon")
        mat = []
        for _, row in sub.iterrows():
            mat.append([
                float(row[f"MAE_{m}"]) if pd.notna(row.get(f"MAE_{m}")) else np.nan
                for m in models_show
            ])
        mat = np.array(mat)
        im = ax.imshow(mat, aspect="auto", cmap="YlGnBu_r")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=10)
        ax.set_yticks(range(len(sub)))
        ax.set_yticklabels([f"H={int(h)}" for h in sub["horizon"]], fontsize=11)
        ax.set_title(title, color=C_NAVY, fontsize=13, fontweight="bold")
        for i in range(mat.shape[0]):
            h = int(sub.iloc[i]["horizon"])
            w = next(x for x in winners if x["cluster"] == cl and x["H"] == h)
            for j in range(mat.shape[1]):
                v = mat[i, j]
                if np.isnan(v):
                    ax.text(j, i, "—", ha="center", va="center",
                            color=C_MUTED, fontsize=9)
                    continue
                is_win = models_show[j] == w["winner"] or (
                    w["winner"] == "lgbm_trends" and models_show[j] == "lgbm_trends"
                )
                # mark winner cell
                if models_show[j] == w["winner"]:
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                            fontsize=10, fontweight="bold", color=C_ORANGE)
                else:
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                            fontsize=9, color=C_INK)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="MAE")

    fig.suptitle(
        "MAE после end_dt < ds — универсального победителя нет",
        color=C_NAVY, fontsize=14, fontweight="bold", y=1.02,
    )
    fig.tight_layout()
    return _save(fig, "slide04_mae_grid.png")


def slide05_winners(d):
    winners = d["winners"]
    fig, ax = plt.subplots(figsize=(12.8, 6.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    horizons = [1, 3, 6, 12]
    win_colors = {
        "prophet": C_NAVY, "lgbm": C_TEAL, "naive": C_MUTED,
        "seasonal": C_GOLD, "catboost": "#5c6bc0",
    }

    _card(ax, 0.04, 0.78, 0.72, 0.14, ec=C_LINE, fc="#e8eef5", lw=1)
    ax.text(0.12, 0.85, "Тип", ha="center", fontsize=12, fontweight="bold", color=C_NAVY)
    for j, h in enumerate(horizons):
        ax.text(0.26 + j * 0.13, 0.85, f"H={h}", ha="center",
                fontsize=12, fontweight="bold", color=C_NAVY)

    for i, (cl, tname) in enumerate([(0, "A · сельские"), (1, "B · городские")]):
        y = 0.55 - i * 0.24
        _card(ax, 0.04, y, 0.72, 0.20, ec=C_LINE, lw=1.2)
        ax.text(0.12, y + 0.10, tname, ha="center", va="center",
                fontsize=11, fontweight="bold", color=C_INK)
        for j, h in enumerate(horizons):
            w = next(x for x in winners if x["cluster"] == cl and x["H"] == h)
            col = win_colors.get(w["winner"], C_INK)
            ax.text(
                0.26 + j * 0.13, y + 0.10,
                f"{w['winner']}\n{w['MAE']:.0f}",
                ha="center", va="center", fontsize=11,
                fontweight="bold", color=col, linespacing=1.25,
            )

    _card(ax, 0.80, 0.28, 0.18, 0.54, ec=C_ORANGE, fc="#f8efe9", lw=2)
    ax.text(
        0.89, 0.55,
        "Prophet\nчасто\nгородские;\nLGBM —\nсельские\nH=3",
        ha="center", va="center", fontsize=11,
        fontweight="bold", color=C_ORANGE, linespacing=1.4,
    )

    ax.text(
        0.40, 0.08,
        "Источник: results/forecast_all_models.csv  ·  winner = min MAE",
        ha="center", fontsize=10, color=C_MUTED,
    )
    return _save(fig, "slide05_winners.png")


def slide06_rural_case(d):
    fc = d["fc"]
    row_a = fc[(fc["cluster"] == 0) & (fc["horizon"] == 3)].iloc[0]
    row_b = fc[(fc["cluster"] == 1) & (fc["horizon"] == 3)].iloc[0]

    fig = plt.figure(figsize=(12.8, 6.8))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.28)
    ax = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    models = ["naive", "prophet", "lgbm"]
    labels = ["Naive", "Prophet", "LGBM"]
    vals_a = [float(row_a[f"MAE_{m}"]) for m in models]
    vals_b = [float(row_b[f"MAE_{m}"]) for m in models]
    x = np.arange(len(labels))
    w = 0.36
    b1 = ax.bar(x - w / 2, vals_a, w, label="Тип A (сельские)", color=C_TEAL)
    b2 = ax.bar(x + w / 2, vals_b, w, label="Тип B (городские)", color=C_NAVY)
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 60,
                    f"{b.get_height():.0f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("MAE")
    ax.set_title("H = 3 · кто выигрывает где", color=C_NAVY, fontsize=13)
    ax.legend(frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, max(vals_a + vals_b) * 1.22)

    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis("off")
    _card(ax2, 0.05, 0.55, 0.90, 0.38, ec=C_TEAL, fc="#eef6f5", lw=2)
    ax2.text(0.50, 0.82, "Тип A: ML локально сильнее", ha="center",
             fontsize=12, fontweight="bold", color=C_TEAL)
    ax2.text(
        0.50, 0.68,
        f"LGBM {vals_a[2]:.0f}  <  Prophet {vals_a[1]:.0f}",
        ha="center", va="center", fontsize=13, color=C_INK, fontweight="bold",
    )

    _card(ax2, 0.05, 0.10, 0.90, 0.38, ec=C_ORANGE, fc="#f8efe9", lw=2)
    ax2.text(0.50, 0.37, "Тип B: Prophet увереннее",
             ha="center", fontsize=12, fontweight="bold", color=C_ORANGE)
    ax2.text(
        0.50, 0.22,
        f"Prophet {vals_b[1]:.0f}  <<  LGBM {vals_b[2]:.0f}",
        ha="center", va="center", fontsize=13, color=C_INK, fontweight="bold",
    )
    return _save(fig, "slide06_rural_case.png")


def slide07_chronos(d):
    fnd = d["foundation"]
    winners = d["winners"]

    chronos_wins = 0
    rows = []
    for _, row in fnd.iterrows():
        cl, h = int(row["cluster"]), int(row["horizon"])
        mae_c = float(row["MAE_chronos"])
        w = next(x for x in winners if x["cluster"] == cl and x["H"] == h)
        if mae_c < w["MAE"]:
            chronos_wins += 1
        name = "сельские" if cl == 0 else "городские"
        rows.append((f"{name}\nH={h}", mae_c, w["MAE"], w["winner"]))

    fig = plt.figure(figsize=(12.8, 6.8))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.35], wspace=0.22)
    ax_l = fig.add_subplot(gs[0])
    ax_r = fig.add_subplot(gs[1])

    ax_l.set_xlim(0, 1)
    ax_l.set_ylim(0, 1)
    ax_l.axis("off")
    _card(ax_l, 0.06, 0.15, 0.88, 0.70, ec=C_ORANGE, fc="#f8efe9", lw=2.5)
    ax_l.text(0.50, 0.72, "Chronos-bolt-tiny", ha="center",
              fontsize=14, fontweight="bold", color=C_ORANGE)
    ax_l.text(0.50, 0.52, f"{chronos_wins} / 8", ha="center",
              fontsize=40, fontweight="bold", color=C_ORANGE)
    ax_l.text(0.50, 0.32, "горизонтов выиграны\nvs лучший классический",
              ha="center", fontsize=12, color=C_INK, linespacing=1.35)

    show = [r for r in rows if "H=3" in r[0] or "H=12" in r[0]]
    y = np.arange(len(show))
    chronos_v = [r[1] for r in show]
    classic_v = [r[2] for r in show]
    labels = [f"{r[0]}\n({r[3]})" for r in show]
    hbar = 0.35
    ax_r.barh(y + hbar / 2, chronos_v, hbar, label="Chronos", color=C_ORANGE, alpha=0.9)
    ax_r.barh(y - hbar / 2, classic_v, hbar, label="лучший классический", color=C_TEAL)
    ax_r.set_yticks(y)
    ax_r.set_yticklabels(labels, fontsize=9)
    ax_r.set_xlabel("MAE")
    ax_r.legend(frameon=False, loc="lower right", fontsize=9)
    ax_r.spines["top"].set_visible(False)
    ax_r.spines["right"].set_visible(False)
    for yi, cv, bv in zip(y, chronos_v, classic_v):
        ax_r.text(cv + 60, yi + hbar / 2, f"{cv:.0f}", va="center", fontsize=8, color=C_ORANGE)
        ax_r.text(bv + 60, yi - hbar / 2, f"{bv:.0f}", va="center", fontsize=8, color=C_TEAL)

    return _save(fig, "slide07_chronos.png")


def slide08_external(d):
    news = d["news"]
    # delta news vs lgbm for urban H=1 (only notable cell)
    row = news[(news.cluster == 1) & (news.horizon == 1)].iloc[0]
    delta_u1 = float(row["delta_news_vs_lgbm"])
    pct = 100.0 * delta_u1 / float(row["MAE_lgbm"])

    # Trends: count how often trends worse than no-trends
    fc = d["fc"]
    worse = 0
    total = 0
    for _, r in fc.iterrows():
        for base in ("lgbm", "catboost"):
            a, b = r.get(f"MAE_{base}"), r.get(f"MAE_{base}_trends")
            if pd.notna(a) and pd.notna(b):
                total += 1
                if float(b) > float(a):
                    worse += 1

    fig, ax = plt.subplots(figsize=(12.8, 6.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _card(ax, 0.04, 0.42, 0.44, 0.48, ec=C_TEAL, lw=2.5)
    ax.text(0.26, 0.82, "Google Trends", ha="center",
            fontsize=14, fontweight="bold", color=C_TEAL)
    ax.text(
        0.26, 0.62,
        f"в {worse}/{total} клетках\n*_trends хуже no-trends",
        ha="center", fontsize=13, color=C_INK, linespacing=1.35, fontweight="bold",
    )
    ax.text(
        0.26, 0.48,
        "один SZFO-ряд на оба типа\nне новости",
        ha="center", fontsize=11, color=C_MUTED, linespacing=1.3,
    )

    _card(ax, 0.52, 0.42, 0.44, 0.48, ec=C_MUTED, lw=2.5)
    ax.text(0.74, 0.82, "GDELT (Russia-wide)", ha="center",
            fontsize=14, fontweight="bold", color=C_MUTED)
    ax.text(
        0.74, 0.62,
        "систематического\nвыигрыша по MAE нет",
        ha="center", fontsize=13, color=C_INK, linespacing=1.35, fontweight="bold",
    )
    ax.text(
        0.74, 0.48,
        f"заметная клетка: городские H=1\nΔ ≈ {delta_u1:.0f} ({pct:.1f}%)",
        ha="center", fontsize=11, color=C_MUTED, linespacing=1.3,
    )

    _card(ax, 0.12, 0.10, 0.76, 0.22, ec=C_NAVY, fc="#e8eef5", lw=2)
    ax.text(
        0.50, 0.21,
        "Тренды ≠ новости. Внешний сигнал не спасает короткий ряд.",
        ha="center", va="center", fontsize=14, fontweight="bold", color=C_NAVY,
    )
    return _save(fig, "slide08_external.png")


def slide09_changepoints(d):
    cons = d["cons"].copy()
    cons["date_s"] = cons["date"].astype(str).str[:7]
    dyn = d["dyn"]
    windows = dyn["windows"]
    sel = [w for w in windows if w["window"] in (15, 16, 17)]
    pr_vals = [w["PR_plus"] for w in sel]

    fig = plt.figure(figsize=(12.8, 7.0))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.2, 1.0], hspace=0.32)
    ax_tl = fig.add_subplot(gs[0])
    ax_bar = fig.add_subplot(gs[1])

    ax_tl.set_xlim(0, 1)
    ax_tl.set_ylim(0, 1)
    ax_tl.axis("off")

    for x, t, col in [
        (0.14, "9 методов", C_MUTED),
        (0.42, "≥5/9  сигнал", C_TEAL),
        (0.72, "7/9  сильный", C_ORANGE),
    ]:
        _card(ax_tl, x - 0.10, 0.70, 0.24, 0.22, ec=col, lw=2)
        ax_tl.text(x + 0.02, 0.81, t, ha="center", fontsize=12,
                   fontweight="bold", color=col)

    events = [
        ("2023-11", "5/9", C_TEAL, False),
        ("2024-04", "5/9", C_TEAL, False),
        ("2024-09", "7/9", C_ORANGE, True),
    ]
    ax_tl.plot([0.12, 0.88], [0.32, 0.32], color=C_LINE, lw=5, solid_capstyle="round")
    xs = [0.20, 0.50, 0.80]
    for x, (date, votes, col, hot) in zip(xs, events):
        ax_tl.plot(x, 0.32, "o", markersize=24 if hot else 16, color=col, zorder=5)
        if hot:
            ax_tl.text(x, 0.32, "!", ha="center", va="center",
                       fontsize=13, color="white", fontweight="bold", zorder=6)
        ax_tl.text(x, 0.52, date, ha="center", fontsize=14,
                   fontweight="bold", color=col)
        ax_tl.text(x, 0.14, votes, ha="center", fontsize=13, color=C_INK)

    cons_plot = cons.sort_values("count", ascending=True)
    colors = [
        C_ORANGE if (r.consensus and r["count"] >= 7)
        else (C_TEAL if r.consensus else C_MUTED)
        for _, r in cons_plot.iterrows()
    ]
    ax_bar.barh(cons_plot["date_s"], cons_plot["count"], color=colors, edgecolor="white")
    ax_bar.axvline(4.5, color=C_GOLD, ls="--", lw=1.4, label="порог 50% (4.5/9)")
    ax_bar.set_xlabel("число методов (из 9)")
    ax_bar.set_title(
        f"PR₊ вокруг 2024-09:  {pr_vals[0]:.3f} → {pr_vals[1]:.3f} → {pr_vals[2]:.3f}",
        color=C_NAVY, fontsize=12,
    )
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.legend(frameon=False, loc="lower right")
    for y, (_, r) in enumerate(cons_plot.iterrows()):
        ax_bar.text(r["count"] + 0.12, y, f"{int(r['count'])}/9",
                    va="center", fontsize=9)
    return _save(fig, "slide09_changepoints.png")


def slide10_value(d):
    fig, ax = plt.subplots(figsize=(12.8, 6.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    cards = [
        (0.05, C_TEAL, "Мониторинг сдвигов",
         "три консенсусные даты\nсильная — 2024-09 (7/9)"),
        (0.35, C_NAVY, "Выбор прогноза",
         "не одна модель:\nProphet / LGBM / naive\nпо типу и горизонту"),
        (0.65, C_ORANGE, "Честная оценка",
         "end_dt < ds\nбез магических фич\nиз будущего"),
    ]
    for x, col, title, body in cards:
        _card(ax, x, 0.22, 0.28, 0.58, ec=col, lw=2.5)
        ax.text(x + 0.14, 0.68, title, ha="center", fontsize=13,
                fontweight="bold", color=col)
        ax.text(x + 0.14, 0.42, body, ha="center", va="center",
                fontsize=12, color=C_INK, linespacing=1.4)

    ax.text(
        0.50, 0.08,
        "Аналитику нужны и число, и сигнал перехода режима.",
        ha="center", fontsize=13, fontweight="bold", color=C_NAVY,
    )
    return _save(fig, "slide10_value.png")


def slide11_finale(d):
    winners = d["winners"]
    n_prophet = sum(1 for w in winners if w["winner"] == "prophet")
    n_lgbm = sum(1 for w in winners if w["winner"] == "lgbm")

    fig, ax = plt.subplots(figsize=(12.8, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch(
        (0, 0.62), 1.0, 0.38, boxstyle="square,pad=0",
        facecolor=C_NAVY, edgecolor="none",
    ))
    ax.text(
        0.50, 0.82,
        "Прогноз зависит от режима и горизонта.\nСдвиги ловим консенсусом, не одной моделью.",
        ha="center", va="center", fontsize=18, fontweight="bold",
        color="white", linespacing=1.35,
    )

    bullets = [
        f"MAE-победители: Prophet {n_prophet}/8 · LGBM {n_lgbm}/8 · остальные — baselines",
        "Chronos: 0/8  ·  GDELT: без систематического win",
        "Changepoints ≥50%: 2023-11 · 2024-04 · 2024-09 (7/9)",
        "Воспроизводимо: configs/ + src/12_ + src/13_ + results/",
    ]
    for i, t in enumerate(bullets):
        y = 0.50 - i * 0.10
        ax.add_patch(Circle((0.08, y), 0.018, facecolor=C_TEAL if i % 2 == 0 else C_ORANGE,
                            edgecolor="none"))
        ax.text(0.12, y, t, ha="left", va="center", fontsize=13, color=C_INK)

    return _save(fig, "slide11_finale.png")


def main():
    _style()
    print("Loading Task 2 artifacts…")
    d = load_data()
    print("Rendering slides…")
    slide01_hook(d)
    slide02_bakeoff(d)
    slide03_leakage(d)
    slide04_mae_grid(d)
    slide05_winners(d)
    slide06_rural_case(d)
    slide07_chronos(d)
    slide08_external(d)
    slide09_changepoints(d)
    slide10_value(d)
    slide11_finale(d)
    print(f"Done -> {OUT}")


if __name__ == "__main__":
    main()
