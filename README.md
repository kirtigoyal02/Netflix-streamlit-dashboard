# Netflix Content Strategy Dashboard — Streamlit

An interactive version of the dashboard, built with Streamlit + Plotly on the
public Netflix titles dataset (7,787 titles, 2021 snapshot).

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Opens automatically at `http://localhost:8501`.

## What's inside

- **Sidebar filters** — content type, release-year range, and top-N for the
  country/genre charts. Every chart and KPI reacts live except the Key
  Takeaways panel, which is written against the full catalog on purpose.
- **KPI row** — movie/show counts, countries represented, genre tags in use.
- **Six charts** — content added by year, movie/show split, top
  content-producing countries, genre distribution, rating breakdown,
  release-year trend.
- **Download button** — export the currently-filtered rows as CSV.
- **Netflix-themed dark palette**, set in `.streamlit/config.toml`.

## Deploying it

`streamlit run app.py` is for local use. To share a live link, push this
folder to a GitHub repo and deploy free on
[Streamlit Community Cloud](https://streamlit.io/cloud) — point it at
`app.py`, it auto-installs `requirements.txt`.

## Files

```
app.py                        # the dashboard
requirements.txt              # pinned dependencies
.streamlit/config.toml        # Netflix-branded dark theme
data/netflix_titles_clean.csv # cleaned source data (7,787 rows)
```
