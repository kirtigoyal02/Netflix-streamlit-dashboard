"""
Netflix Content Strategy Dashboard — Streamlit
Run with:  streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RED = "#E50914"
TEAL = "#2FB6A8"
AMBER = "#E8A33D"
PURPLE = "#8B8BF0"
INK = "#F2F1ED"
INK_DIM = "#9A9A9F"
PANEL = "#18181A"
GRID = "#2C2C30"

st.set_page_config(
    page_title="Netflix Content Strategy Dashboard",
    page_icon="🎬",
    layout="wide",
)

# ---------------------------------------------------------------- data ----

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/netflix_titles_clean.csv")
    df["rating"] = df["rating"].fillna("Not Rated")
    return df


@st.cache_data
def explode_country(df: pd.DataFrame) -> pd.DataFrame:
    c = df[["show_id", "type", "country"]].dropna(subset=["country"]).copy()
    c["country"] = c["country"].str.split(",")
    c = c.explode("country")
    c["country"] = c["country"].str.strip()
    return c[c["country"] != ""]


@st.cache_data
def explode_genre(df: pd.DataFrame) -> pd.DataFrame:
    g = df[["show_id", "type", "listed_in"]].dropna(subset=["listed_in"]).copy()
    g["genre"] = g["listed_in"].str.split(",")
    g = g.explode("genre")
    g["genre"] = g["genre"].str.strip()
    return g


df = load_data()

# --------------------------------------------------------------- sidebar --

st.sidebar.markdown("## Filters")

type_options = sorted(df["type"].unique().tolist())
selected_types = st.sidebar.multiselect(
    "Content type", options=type_options, default=type_options
)

year_min, year_max = int(df["release_year"].min()), int(df["release_year"].max())
year_range = st.sidebar.slider(
    "Release year",
    min_value=year_min,
    max_value=year_max,
    value=(2000, year_max),
)

top_n = st.sidebar.slider("Top N countries / genres", min_value=5, max_value=20, value=12)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Source: public Netflix titles dataset (2021 snapshot, 7,787 titles). "
    "Filters apply to every chart except the Key Takeaways panel, which "
    "always reflects the full catalog."
)

filtered = df[
    df["type"].isin(selected_types)
    & df["release_year"].between(year_range[0], year_range[1])
]

st.sidebar.markdown(f"**{len(filtered):,}** of {len(df):,} titles match your filters")

csv_bytes = filtered.drop(columns=["description"]).to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    "Download filtered data (CSV)",
    data=csv_bytes,
    file_name="netflix_filtered.csv",
    mime="text/csv",
)

# ---------------------------------------------------------------- header --

st.markdown(
    f"""
    <div style="border-bottom:1px solid {GRID}; padding-bottom:14px; margin-bottom:18px;">
        <div style="color:{RED}; font-weight:800; letter-spacing:0.14em; font-size:14px;">NETFLIX</div>
        <div style="font-size:32px; font-weight:800; line-height:1.1; margin-top:2px;">
            Content Strategy Dashboard
        </div>
        <div style="color:{INK_DIM}; font-size:14px; margin-top:4px;">
            What's actually in the catalog — the movie/series balance, where content comes from,
            what it's rated, and how the library has grown.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No titles match the current filters — widen the release-year range or content type.")
    st.stop()

# ------------------------------------------------------------------ KPIs --

movies_n = int((filtered["type"] == "Movie").sum())
shows_n = int((filtered["type"] == "TV Show").sum())
countries_n = explode_country(filtered)["country"].nunique()
genres_n = explode_genre(filtered)["genre"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Movies", f"{movies_n:,}", f"{movies_n / len(filtered):.0%} of selection")
k2.metric("TV Shows", f"{shows_n:,}", f"{shows_n / len(filtered):.0%} of selection")
k3.metric("Countries represented", f"{countries_n}")
k4.metric("Genre tags in use", f"{genres_n}")

st.write("")

# --------------------------------------------------------------- helpers --

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def style_fig(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK_DIM, size=12),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=INK),
        ),
        hoverlabel=dict(bgcolor=PANEL, font_color=INK, bordercolor=GRID),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


# --------------------------------------------------------- row 1: trend ---

c1, c2 = st.columns([1.6, 1])

with c1:
    st.subheader("Content added by year")
    st.caption("Titles added to Netflix per year, split by type.")
    added = (
        filtered.dropna(subset=["year_added"])
        .groupby(["year_added", "type"])
        .size()
        .reset_index(name="count")
    )
    fig = go.Figure()
    for t, color in [("Movie", RED), ("TV Show", TEAL)]:
        sub = added[added["type"] == t].sort_values("year_added")
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["year_added"], y=sub["count"], mode="lines+markers",
                name=t, line=dict(color=color, width=3),
                marker=dict(color=color, size=6),
                fill="tozeroy", fillcolor=hex_to_rgba(color, 0.12),
            )
        )
    st.plotly_chart(style_fig(fig, 340), width='stretch')

with c2:
    st.subheader("Movies vs. TV shows")
    st.caption("Share of the current selection.")
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Movies", "TV Shows"],
                values=[movies_n, shows_n],
                hole=0.68,
                marker=dict(colors=[RED, TEAL], line=dict(color=PANEL, width=3)),
                textfont=dict(color=INK),
            )
        ]
    )
    st.plotly_chart(style_fig(fig, 340), width='stretch')

# ---------------------------------------------- row 2: countries/genres --

c3, c4 = st.columns(2)

with c3:
    st.subheader("Top content-producing countries")
    st.caption("By production-country credit — a title can list more than one.")
    top_countries = (
        explode_country(filtered)["country"].value_counts().head(top_n).sort_values()
    )
    fig = go.Figure(
        go.Bar(
            x=top_countries.values, y=top_countries.index, orientation="h",
            marker_color=RED,
        )
    )
    st.plotly_chart(style_fig(fig, 340), width='stretch')

with c4:
    st.subheader("Genre distribution")
    st.caption("Top genre tags by number of titles carrying that tag.")
    top_genres = explode_genre(filtered)["genre"].value_counts().head(top_n).sort_values()
    fig = go.Figure(
        go.Bar(
            x=top_genres.values, y=top_genres.index, orientation="h",
            marker_color=AMBER,
        )
    )
    st.plotly_chart(style_fig(fig, 340), width='stretch')

# ----------------------------------------------- row 3: rating/release ---

c5, c6 = st.columns(2)

with c5:
    st.subheader("Content rating breakdown")
    st.caption("Titles by age / content rating.")
    ratings = filtered["rating"].value_counts().sort_values(ascending=False)
    fig = go.Figure(go.Bar(x=ratings.index, y=ratings.values, marker_color=PURPLE))
    st.plotly_chart(style_fig(fig, 300), width='stretch')

with c6:
    st.subheader("Release-year trend")
    st.caption("Original release year of catalog titles.")
    release = filtered["release_year"].value_counts().sort_index()
    fig = go.Figure(
        go.Scatter(
            x=release.index, y=release.values, mode="lines", fill="tozeroy",
            line=dict(color=TEAL, width=3), fillcolor=hex_to_rgba(TEAL, 0.12),
        )
    )
    st.plotly_chart(style_fig(fig, 300), width='stretch')

# -------------------------------------------------------- key takeaways --

st.markdown("---")
st.subheader("Key takeaways")
st.caption("Based on the full 7,787-title catalog, independent of the filters above.")

i1, i2 = st.columns(2)
with i1:
    st.markdown(
        f"""
        **Is Netflix more focused on movies or TV shows?**
        Movies still lead at 69% of titles (5,377 vs. 2,410), but TV shows'
        share of *yearly additions* rose from under 20% in 2013–15 to over 40%
        by 2020 — the library is tilting toward series even though movies
        remain the majority.

        **Which countries produce the most content?**
        The United States dominates with ~3,300 production credits — more
        than 3x India (990) and the UK (723), the next two. A long tail of
        100+ countries beyond that shows a globally-sourced but US-anchored
        catalog.
        """
    )
with i2:
    st.markdown(
        f"""
        **Which genres dominate the platform?**
        International Movies, Dramas, and Comedies are the three largest tags
        by a wide margin, together covering roughly 40% of all genre tags —
        the catalog leans narrative/drama over niche genres.

        **How has the content library evolved?**
        Additions were negligible before 2015, then grew roughly 15x by 2019
        (58 → 1,497 movies added in a year alone) as Netflix scaled
        internationally, before flattening in 2020. The 2021 dip reflects a
        mid-year data snapshot, not a real slowdown.
        """
    )

st.caption("Built with Streamlit + Plotly · static aggregate data, refreshed on filter change.")
