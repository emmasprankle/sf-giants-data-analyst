import os

import altair as alt
import pandas as pd
import snowflake.connector
import streamlit as st
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_pem_private_key,
)
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SF Giants Pitching Analytics",
    page_icon="⚾",
    layout="wide",
)

st.title("⚾ SF Giants Pitching Analytics")
st.caption("2024 Season · Powered by MLB Stats API + Snowflake + dbt")


# ── Connection ────────────────────────────────────────────────────────────────

def _secret(key):
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key)


def _load_private_key():
    pem = _secret("SNOWFLAKE_PRIVATE_KEY")
    if pem is None:
        path = _secret("SNOWFLAKE_PRIVATE_KEY_FILE")
        if path:
            with open(path, "rb") as f:
                pem = f.read()
    if pem is None:
        raise ValueError("SNOWFLAKE_PRIVATE_KEY or SNOWFLAKE_PRIVATE_KEY_FILE must be set")
    if isinstance(pem, str):
        pem = pem.encode()
    key = load_pem_private_key(pem, password=None)
    return key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())


def get_connection():
    return snowflake.connector.connect(
        account=_secret("SNOWFLAKE_ACCOUNT"),
        user=_secret("SNOWFLAKE_USER"),
        private_key=_load_private_key(),
        warehouse=_secret("SNOWFLAKE_WAREHOUSE"),
        database=_secret("SNOWFLAKE_DATABASE"),
        schema="MART",
    )


# ── Queries ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_pitchers():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT player_id, full_name FROM MART.DIM_PITCHER ORDER BY full_name")
        return cur.fetchall()


@st.cache_data(ttl=600)
def load_season_kpis(player_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                s.season_era,
                s.season_whip,
                s.season_k_per_9,
                s.season_bb_per_9,
                ROUND(SUM(f.strikes) / NULLIF(SUM(f.pitches_thrown), 0), 3) AS season_strike_pct
            FROM MART.MART_PITCHER_SEASON s
            JOIN MART.FACT_PITCHER_GAME f ON s.player_id = f.player_id
            WHERE s.player_id = %s
            GROUP BY s.season_era, s.season_whip, s.season_k_per_9, s.season_bb_per_9
            """,
            (player_id,),
        )
        return cur.fetchone()


@st.cache_data(ttl=600)
def load_latest_rolling(player_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT rolling_era, rolling_whip, rolling_k_per_9, rolling_bb_per_9, rolling_strike_pct
            FROM MART.MART_PITCHER_ROLLING
            WHERE player_id = %s
            ORDER BY game_date DESC
            LIMIT 1
            """,
            (player_id,),
        )
        return cur.fetchone()


@st.cache_data(ttl=600)
def load_date_bounds():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT MIN(game_date), MAX(game_date) FROM MART.FACT_PITCHER_GAME")
        row = cur.fetchone()
        return row[0], row[1]


@st.cache_data(ttl=600)
def load_rolling_trend(player_id: int) -> pd.DataFrame:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT game_date, rolling_era, rolling_whip
            FROM MART.MART_PITCHER_ROLLING
            WHERE player_id = %s
            ORDER BY game_date
            """,
            (player_id,),
        )
        rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["game_date", "rolling_era", "rolling_whip"])
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


@st.cache_data(ttl=600)
def load_home_away_split(player_id: int) -> pd.DataFrame:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                CASE WHEN is_home THEN 'Home' ELSE 'Away' END AS venue,
                ROUND((SUM(earned_runs) / NULLIF(SUM(innings_pitched), 0)) * 9, 2) AS era,
                ROUND(
                    (SUM(hits) + SUM(walks)) / NULLIF(SUM(innings_pitched), 0), 3
                ) AS whip,
                ROUND(SUM(strikeouts) / NULLIF(SUM(innings_pitched), 0) * 9, 2) AS k_per_9,
                ROUND(SUM(strikes) / NULLIF(SUM(pitches_thrown), 0), 3) AS strike_pct
            FROM MART.FACT_PITCHER_GAME
            WHERE player_id = %s
            GROUP BY is_home
            ORDER BY is_home DESC
            """,
            (player_id,),
        )
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["venue", "era", "whip", "k_per_9", "strike_pct"])


@st.cache_data(ttl=600)
def load_staff_era_range() -> tuple:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT MIN(season_era), MAX(season_era)
            FROM MART.MART_PITCHER_SEASON
            WHERE season_era IS NOT NULL
            """
        )
        return cur.fetchone()


@st.cache_data(ttl=600)
def load_comparison_stats(player_ids: tuple) -> pd.DataFrame:
    placeholders = ", ".join(["%s"] * len(player_ids))
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT
                s.full_name,
                s.season_era,
                s.season_whip,
                s.season_k_per_9,
                s.season_bb_per_9,
                ROUND(SUM(f.strikes) / NULLIF(SUM(f.pitches_thrown), 0) * 100, 1) AS strike_pct,
                s.total_ip,
                s.games
            FROM MART.MART_PITCHER_SEASON s
            JOIN MART.FACT_PITCHER_GAME f ON s.player_id = f.player_id
            WHERE s.player_id IN ({placeholders})
            GROUP BY s.full_name, s.season_era, s.season_whip, s.season_k_per_9,
                     s.season_bb_per_9, s.total_ip, s.games
            ORDER BY s.season_era
            """,
            player_ids,
        )
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["full_name", "era", "whip", "k_per_9", "bb_per_9", "strike_pct", "total_ip", "games"])


@st.cache_data(ttl=600)
def load_pitcher_era_rankings(start_date, end_date) -> pd.DataFrame:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                full_name,
                ROUND((SUM(earned_runs) / NULLIF(SUM(innings_pitched), 0)) * 9, 2) AS era
            FROM MART.FACT_PITCHER_GAME
            WHERE game_date BETWEEN %s AND %s
            GROUP BY full_name
            HAVING SUM(innings_pitched) >= 10
            ORDER BY era
            """,
            (start_date, end_date),
        )
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["full_name", "era"])


# ── Pitcher selector ──────────────────────────────────────────────────────────

pitchers = load_pitchers()
pitcher_map = {name: pid for pid, name in pitchers}
selected_name = st.selectbox("Select pitcher", list(pitcher_map.keys()))
selected_id = pitcher_map[selected_name]

# ── KPI scorecards ────────────────────────────────────────────────────────────

season = load_season_kpis(selected_id)
rolling = load_latest_rolling(selected_id)

st.subheader(f"{selected_name} — 2024 Season")


def scorecard(col, label, season_val, rolling_val, delta_color, val_fmt, delta_fmt):
    if season_val is None:
        col.metric(label, "—")
        return
    value_str = val_fmt(float(season_val))
    delta_str = None
    if rolling_val is not None:
        delta_str = delta_fmt(float(season_val) - float(rolling_val))
    col.metric(label, value_str, delta=delta_str, delta_color=delta_color)


cols = st.columns(5)

scorecard(
    cols[0], "ERA",
    season[0], rolling[0] if rolling else None,
    delta_color="inverse",
    val_fmt=lambda v: f"{v:.2f}",
    delta_fmt=lambda d: f"{d:+.2f} vs last 5",
)
scorecard(
    cols[1], "WHIP",
    season[1], rolling[1] if rolling else None,
    delta_color="inverse",
    val_fmt=lambda v: f"{v:.3f}",
    delta_fmt=lambda d: f"{d:+.3f} vs last 5",
)
scorecard(
    cols[2], "K/9",
    season[2], rolling[2] if rolling else None,
    delta_color="normal",
    val_fmt=lambda v: f"{v:.2f}",
    delta_fmt=lambda d: f"{d:+.2f} vs last 5",
)
scorecard(
    cols[3], "BB/9",
    season[3], rolling[3] if rolling else None,
    delta_color="inverse",
    val_fmt=lambda v: f"{v:.2f}",
    delta_fmt=lambda d: f"{d:+.2f} vs last 5",
)
scorecard(
    cols[4], "Strike%",
    season[4], rolling[4] if rolling else None,
    delta_color="normal",
    val_fmt=lambda v: f"{v:.1%}",
    delta_fmt=lambda d: f"{d:+.1%} vs last 5",
)

# ── Staff context callout cards ───────────────────────────────────────────────

MLB_AVG_ERA_2024 = 4.33

staff_min_era, staff_max_era = load_staff_era_range()

if season and season[0] is not None:
    player_era = float(season[0])
    era_vs_avg = round(player_era - MLB_AVG_ERA_2024, 2)
    era_spread = round(float(staff_max_era) - float(staff_min_era), 2) if staff_min_era and staff_max_era else None

    ctx_cols = st.columns(2)
    ctx_cols[0].metric("2024 MLB Avg ERA", f"{MLB_AVG_ERA_2024:.2f}")
    if era_spread is not None:
        ctx_cols[1].metric(
            "Staff ERA Spread",
            f"{era_spread:.2f} pts",
            delta=f"{float(staff_min_era):.2f} best → {float(staff_max_era):.2f} worst",
            delta_color="off",
        )

# ── Shared date filter ────────────────────────────────────────────────────────

st.divider()

min_date, max_date = load_date_bounds()

date_range = st.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_date, max_date

# ── Trend charts ──────────────────────────────────────────────────────────────

st.subheader(f"{selected_name} — Rolling 5-Start Trends")

trend_df = load_rolling_trend(selected_id)
filtered = trend_df[
    (trend_df["game_date"].dt.date >= start) & (trend_df["game_date"].dt.date <= end)
]

if filtered.empty:
    st.info("No trend data in the selected date range.")
else:
    era_peak_idx = filtered["rolling_era"].idxmax()
    era_low_idx = filtered["rolling_era"].idxmin()
    peak_era = float(filtered.loc[era_peak_idx, "rolling_era"])
    peak_era_month = filtered.loc[era_peak_idx, "game_date"].strftime("%b")
    low_era = float(filtered.loc[era_low_idx, "rolling_era"])
    low_era_month = filtered.loc[era_low_idx, "game_date"].strftime("%b")

    whip_peak_idx = filtered["rolling_whip"].idxmax()
    whip_low_idx = filtered["rolling_whip"].idxmin()
    peak_whip = float(filtered.loc[whip_peak_idx, "rolling_whip"])
    peak_whip_month = filtered.loc[whip_peak_idx, "game_date"].strftime("%b")
    low_whip = float(filtered.loc[whip_low_idx, "rolling_whip"])
    low_whip_month = filtered.loc[whip_low_idx, "game_date"].strftime("%b")

    def trend_chart(df, y_col, y_title, color):
        return (
            alt.Chart(df)
            .mark_line(color=color, strokeWidth=2, point=alt.OverlayMarkDef(color=color, size=40))
            .encode(
                x=alt.X("game_date:T", title="Date", axis=alt.Axis(format="%b %d")),
                y=alt.Y(f"{y_col}:Q", title=y_title, scale=alt.Scale(zero=False)),
                tooltip=[
                    alt.Tooltip("game_date:T", title="Date", format="%b %d"),
                    alt.Tooltip(f"{y_col}:Q", title=y_title, format=".2f"),
                ],
            )
            .properties(height=280)
        )

    col1, col2 = st.columns(2)
    with col1:
        era_cards = st.columns(3)
        if season and season[0] is not None:
            era_cards[0].metric("Season ERA", f"{float(season[0]):.2f}")
        era_cards[1].metric(f"Rolling ERA Peak ({peak_era_month})", f"{peak_era:.2f}")
        era_cards[2].metric(f"Rolling ERA Low ({low_era_month})", f"{low_era:.2f}")
        st.altair_chart(
            trend_chart(filtered, "rolling_era", "Rolling ERA", "#FD5A1E"),
            use_container_width=True,
        )
    with col2:
        whip_cards = st.columns(3)
        if season and season[1] is not None:
            whip_cards[0].metric("Season WHIP", f"{float(season[1]):.3f}")
        whip_cards[1].metric(f"Rolling WHIP Peak ({peak_whip_month})", f"{peak_whip:.3f}")
        whip_cards[2].metric(f"Rolling WHIP Low ({low_whip_month})", f"{low_whip:.3f}")
        st.altair_chart(
            trend_chart(filtered, "rolling_whip", "Rolling WHIP", "#27251F"),
            use_container_width=True,
        )

# ── Home / Away split ─────────────────────────────────────────────────────────

st.subheader(f"{selected_name} — Home vs. Away Split")

split_df = load_home_away_split(selected_id)

if split_df.empty:
    st.info("No home/away data available for this pitcher.")
else:
    metrics = [
        ("ERA",      "era",       ".2f",  "inverse"),
        ("WHIP",     "whip",      ".3f",  "inverse"),
        ("K/9",      "k_per_9",   ".2f",  "normal"),
        ("Strike%",  "strike_pct",".1%",  "normal"),
    ]

    home_row = split_df[split_df["venue"] == "Home"].iloc[0] if "Home" in split_df["venue"].values else None
    away_row = split_df[split_df["venue"] == "Away"].iloc[0] if "Away" in split_df["venue"].values else None

    if home_row is not None and away_row is not None:
        home_era = float(home_row["era"])
        away_era = float(away_row["era"])
        era_gap = round(away_era - home_era, 2)
        home_whip = float(home_row["whip"])
        away_whip = float(away_row["whip"])
        whip_gap = round(away_whip - home_whip, 3)

        ha_cols = st.columns(4)
        ha_cols[0].metric("Home ERA", f"{home_era:.2f}")
        ha_cols[1].metric("Away ERA", f"{away_era:.2f}")
        ha_cols[2].metric(
            "ERA Gap (Away − Home)",
            f"{abs(era_gap):.2f} pts",
            delta=f"{era_gap:+.2f} on the road",
            delta_color="inverse",
        )
        ha_cols[3].metric(
            "WHIP Gap (Away − Home)",
            f"{abs(whip_gap):.3f} pts",
            delta=f"{whip_gap:+.3f} on the road",
            delta_color="inverse",
        )

    col_labels = st.columns([1] + [1] * len(metrics))
    col_labels[0].markdown("**Venue**")
    for i, (label, _, _, _) in enumerate(metrics):
        col_labels[i + 1].markdown(f"**{label}**")

    for venue, row in [("Home", home_row), ("Away", away_row)]:
        cols = st.columns([1] + [1] * len(metrics))
        cols[0].markdown(f"**{venue}**")
        for i, (_, col, fmt, _) in enumerate(metrics):
            val = row[col] if row is not None else None
            if val is None:
                cols[i + 1].markdown("—")
            elif fmt == ".1%":
                cols[i + 1].markdown(f"{float(val):.1%}")
            else:
                cols[i + 1].markdown(f"{float(val):{fmt}}")

    if home_row is not None and away_row is not None:
        chart_data = split_df.melt(id_vars="venue", value_vars=["era", "whip", "k_per_9", "strike_pct"],
                                   var_name="metric", value_name="value")
        metric_labels = {"era": "ERA", "whip": "WHIP", "k_per_9": "K/9", "strike_pct": "Strike%"}
        chart_data["metric"] = chart_data["metric"].map(metric_labels)

        split_chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X("venue:N", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("value:Q", title="Value", scale=alt.Scale(zero=True)),
                color=alt.Color(
                    "venue:N",
                    scale=alt.Scale(domain=["Home", "Away"], range=["#FD5A1E", "#27251F"]),
                    legend=None,
                ),
                column=alt.Column("metric:N", title=None, header=alt.Header(labelFontSize=13)),
                tooltip=[
                    alt.Tooltip("venue:N", title="Venue"),
                    alt.Tooltip("metric:N", title="Metric"),
                    alt.Tooltip("value:Q", title="Value", format=".3f"),
                ],
            )
            .properties(width=120, height=200)
        )
        st.altair_chart(split_chart)

st.divider()

# ── ERA rankings bar chart ────────────────────────────────────────────────────

st.subheader("All Pitchers — ERA Rankings")

rankings_df = load_pitcher_era_rankings(start, end)

if rankings_df.empty:
    st.info("No pitching data in the selected date range.")
else:
    best_era = float(rankings_df["era"].min())
    worst_era = float(rankings_df["era"].max())
    era_gap = round(worst_era - best_era, 2)
    best_name = rankings_df.loc[rankings_df["era"].idxmin(), "full_name"]
    worst_name = rankings_df.loc[rankings_df["era"].idxmax(), "full_name"]

    gap_cols = st.columns(4)
    gap_cols[0].metric(f"Best ERA ({best_name})", f"{best_era:.2f}")
    gap_cols[1].metric(f"Worst ERA ({worst_name})", f"{worst_era:.2f}")
    gap_cols[2].metric(
        "ERA Gap (Best → Worst)",
        f"{era_gap:.2f} pts",
        delta=f"{best_name} vs {worst_name}",
        delta_color="off",
    )
    if season and season[0] is not None:
        gap_cols[3].metric(
            f"{selected_name} vs. MLB Avg",
            f"{float(season[0]):.2f}",
            delta=f"{era_vs_avg:+.2f} vs MLB avg",
            delta_color="inverse",
        )

    bar_color = alt.condition(
        alt.datum.full_name == selected_name,
        alt.value("#FD5A1E"),
        alt.value("#94a3b8"),
    )

    rankings_chart = (
        alt.Chart(rankings_df)
        .mark_bar()
        .encode(
            x=alt.X("era:Q", title="ERA", scale=alt.Scale(zero=True)),
            y=alt.Y(
                "full_name:N",
                sort=alt.SortField("era", order="ascending"),
                title=None,
            ),
            color=bar_color,
            tooltip=[
                alt.Tooltip("full_name:N", title="Pitcher"),
                alt.Tooltip("era:Q", title="ERA", format=".2f"),
            ],
        )
        .properties(height=max(300, len(rankings_df) * 24))
    )

    st.altair_chart(rankings_chart, use_container_width=True)

st.divider()

# ── Pitcher comparison ────────────────────────────────────────────────────────

st.subheader("Pitcher Comparison")

compare_names = st.multiselect(
    "Select pitchers to compare (minimum 2)",
    options=list(pitcher_map.keys()),
    default=[selected_name],
)

if len(compare_names) < 2:
    st.info("Select at least 2 pitchers to see the comparison.")
else:
    compare_ids = tuple(pitcher_map[n] for n in compare_names)
    comp_df = load_comparison_stats(compare_ids)

    # ── Stats table ───────────────────────────────────────────────────────────
    table_df = comp_df.copy()
    table_df["ERA"]      = table_df["era"].apply(lambda v: f"{float(v):.2f}" if v is not None else "—")
    table_df["WHIP"]     = table_df["whip"].apply(lambda v: f"{float(v):.3f}" if v is not None else "—")
    table_df["K/9"]      = table_df["k_per_9"].apply(lambda v: f"{float(v):.2f}" if v is not None else "—")
    table_df["BB/9"]     = table_df["bb_per_9"].apply(lambda v: f"{float(v):.2f}" if v is not None else "—")
    table_df["Strike%"]  = table_df["strike_pct"].apply(lambda v: f"{float(v):.1f}%" if v is not None else "—")
    table_df["IP"]       = table_df["total_ip"].apply(lambda v: f"{float(v):.1f}" if v is not None else "—")
    table_df["G"]        = table_df["games"].apply(lambda v: str(int(v)) if v is not None else "—")
    table_df = table_df.rename(columns={"full_name": "Pitcher"})
    st.dataframe(
        table_df[["Pitcher", "ERA", "WHIP", "K/9", "BB/9", "Strike%", "IP", "G"]].set_index("Pitcher"),
        use_container_width=True,
    )

    # ── Bar charts per metric ─────────────────────────────────────────────────
    chart_metrics = [
        ("era",        "ERA"),
        ("whip",       "WHIP"),
        ("k_per_9",    "K/9"),
        ("bb_per_9",   "BB/9"),
        ("strike_pct", "Strike%"),
    ]

    melted = comp_df.melt(
        id_vars="full_name",
        value_vars=[m for m, _ in chart_metrics],
        var_name="metric",
        value_name="value",
    )
    metric_label_map = {m: lbl for m, lbl in chart_metrics}
    melted["metric_label"] = melted["metric"].map(metric_label_map)

    comp_chart = (
        alt.Chart(melted)
        .mark_bar()
        .encode(
            x=alt.X("full_name:N", title=None, axis=alt.Axis(labelAngle=-30, labelLimit=120)),
            y=alt.Y("value:Q", title=None, scale=alt.Scale(zero=True)),
            color=alt.Color(
                "full_name:N",
                scale=alt.Scale(scheme="tableau10"),
                legend=alt.Legend(title="Pitcher"),
            ),
            column=alt.Column(
                "metric_label:N",
                title=None,
                header=alt.Header(labelFontSize=13),
                sort=[lbl for _, lbl in chart_metrics],
            ),
            tooltip=[
                alt.Tooltip("full_name:N", title="Pitcher"),
                alt.Tooltip("metric_label:N", title="Metric"),
                alt.Tooltip("value:Q", title="Value", format=".2f"),
            ],
        )
        .properties(width=max(80, 400 // len(compare_names)), height=220)
        .resolve_scale(y="independent")
    )
    st.altair_chart(comp_chart)
