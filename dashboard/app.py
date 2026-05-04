import os

import altair as alt
import pandas as pd
import snowflake.connector
import streamlit as st
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

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="MART",
    )


# ── Queries ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_pitchers():
    cur = get_connection().cursor()
    cur.execute(
        "SELECT player_id, full_name FROM MART.DIM_PITCHER ORDER BY full_name"
    )
    return cur.fetchall()


@st.cache_data(ttl=600)
def load_season_kpis(player_id: int):
    cur = get_connection().cursor()
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
    cur = get_connection().cursor()
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
    cur = get_connection().cursor()
    cur.execute("SELECT MIN(game_date), MAX(game_date) FROM MART.FACT_PITCHER_GAME")
    row = cur.fetchone()
    return row[0], row[1]


@st.cache_data(ttl=600)
def load_rolling_trend(player_id: int) -> pd.DataFrame:
    cur = get_connection().cursor()
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
    cur = get_connection().cursor()
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
def load_pitcher_era_rankings(start_date, end_date) -> pd.DataFrame:
    cur = get_connection().cursor()
    cur.execute(
        """
        SELECT
            full_name,
            ROUND((SUM(earned_runs) / NULLIF(SUM(innings_pitched), 0)) * 9, 2) AS era
        FROM MART.FACT_PITCHER_GAME
        WHERE game_date BETWEEN %s AND %s
        GROUP BY full_name
        HAVING SUM(innings_pitched) > 0
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
        st.altair_chart(
            trend_chart(filtered, "rolling_era", "Rolling ERA", "#FD5A1E"),
            use_container_width=True,
        )
    with col2:
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
