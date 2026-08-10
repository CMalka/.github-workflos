import os

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide", page_icon="💹")

# ---------- Custom styling ----------
st.markdown(
    """
    <style>
    .kpi-frame {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 14px;
        background: linear-gradient(135deg, #f0fdfa 0%, #ecfeff 100%);
        border: 1px solid #99f6e4;
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 18px;
    }
    .kpi-card { text-align: center; }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #0f766e;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .kpi-value { font-size: 1.6rem; font-weight: 700; color: #134e4a; }

    .info-card {
        background: #ffffff;
        border: 1px solid #99f6e4;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(15, 118, 110, 0.08);
    }
    .info-card .card-label {
        font-size: 0.85rem;
        font-weight: 700;
        color: #0d9488;
        margin-bottom: 6px;
    }
    .info-card .card-name { font-size: 1.0rem; font-weight: 600; color: #134e4a; }
    .info-card .card-amount { font-size: 1.3rem; font-weight: 700; color: #0f766e; margin-top: 4px; }

    section[data-testid="stSidebar"] { background-color: #ecfdf5; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True)
    df["ship_date"] = pd.to_datetime(df["ship_date"], dayfirst=True)
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    return df


US_STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Puerto Rico": "PR",
}

# ---------- Data source ----------
st.sidebar.header("📂 Data")
uploaded = st.sidebar.file_uploader("Upload a CSV (optional)", type="csv")
default_path = os.path.join(os.path.dirname(__file__), "train.csv")

if uploaded is not None:
    df = load_data(uploaded)
elif os.path.exists(default_path):
    df = load_data(default_path)
else:
    st.warning("Upload a CSV file to get started.")
    st.stop()

# ---------- Filters ----------
st.sidebar.header("🔎 Filters")
years = sorted(df["year"].dropna().unique().tolist())
regions = sorted(df["region"].dropna().unique().tolist())
categories = sorted(df["category"].dropna().unique().tolist())
states = sorted(df["state"].dropna().unique().tolist())

sel_years = st.sidebar.multiselect("Year", years, default=years)
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)
sel_categories = st.sidebar.multiselect("Category", categories, default=categories)
sel_states = st.sidebar.multiselect("State", states, default=states)

mask = (
    df["year"].isin(sel_years)
    & df["region"].isin(sel_regions)
    & df["category"].isin(sel_categories)
    & df["state"].isin(sel_states)
)
fdf = df[mask]

if fdf.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

st.title("💹 Sales Analytics Dashboard")
st.caption(f"{len(fdf):,} order lines · {fdf['order_id'].nunique():,} orders")

# ---------- Shared color palette (category <-> sub-category) ----------
cat_list = sorted(fdf["category"].unique())
palette = px.colors.qualitative.Set2
cat_color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(cat_list)}

# ---------- KPI frame (single card) ----------
top_state = fdf.groupby("state")["sales"].sum().idxmax()
top_category = fdf.groupby("category")["sales"].sum().idxmax()

st.markdown(
    f"""
    <div class="kpi-frame">
        <div class="kpi-card"><div class="kpi-label">Total Sales</div><div class="kpi-value">${fdf['sales'].sum():,.0f}</div></div>
        <div class="kpi-card"><div class="kpi-label">Total Orders</div><div class="kpi-value">{fdf['order_id'].nunique():,}</div></div>
        <div class="kpi-card"><div class="kpi-label">Total Customers</div><div class="kpi-value">{fdf['customer_id'].nunique():,}</div></div>
        <div class="kpi-card"><div class="kpi-label">Avg Sale / Line</div><div class="kpi-value">${fdf['sales'].mean():,.2f}</div></div>
        <div class="kpi-card"><div class="kpi-label">Top State</div><div class="kpi-value">{top_state}</div></div>
        <div class="kpi-card"><div class="kpi-label">Top Category</div><div class="kpi-value">{top_category}</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Category & Sub-Category (matching colors) ----------
st.markdown("## Sales by Category & Sub-Category")

c1, c2 = st.columns(2)
with c1:
    cat_sales = fdf.groupby("category", as_index=False)["sales"].sum().sort_values("sales", ascending=False)
    fig_cat = px.bar(
        cat_sales, x="category", y="sales", color="category",
        color_discrete_map=cat_color_map, text_auto=".2s",
    )
    fig_cat.update_layout(showlegend=False, xaxis_title="", yaxis_title="Sales ($)")
    st.plotly_chart(fig_cat, use_container_width=True)
with c2:
    subcat_sales = (
        fdf.groupby(["category", "sub-category"], as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )
    fig_subcat = px.bar(
        subcat_sales, x="sub-category", y="sales", color="category",
        color_discrete_map=cat_color_map, text_auto=".2s",
    )
    fig_subcat.update_layout(xaxis_title="", yaxis_title="Sales ($)", legend_title="Category")
    st.plotly_chart(fig_subcat, use_container_width=True)

# ---------- Sales by state - USA map ----------
st.markdown("## Sales by State")
state_sales = fdf.groupby("state", as_index=False)["sales"].sum()
state_sales["code"] = state_sales["state"].map(US_STATE_ABBREV)
fig_map = px.choropleth(
    state_sales.dropna(subset=["code"]),
    locations="code", locationmode="USA-states", color="sales",
    scope="usa", color_continuous_scale="Teal", hover_name="state",
    labels={"sales": "Sales ($)"},
)
fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig_map, use_container_width=True)

# ---------- Sales by year ----------
st.markdown("## Sales by Year")
year_sales = fdf.groupby("year", as_index=False)["sales"].sum().sort_values("year")
fig_year = px.bar(
    year_sales, x="year", y="sales", color="year",
    color_continuous_scale="Teal", text_auto=".2s",
)
fig_year.update_layout(xaxis_title="", yaxis_title="Sales ($)", coloraxis_showscale=False)
fig_year.update_xaxes(type="category")
st.plotly_chart(fig_year, use_container_width=True)

# ---------- Top selling product ----------
st.markdown("## Top Selling Product")
top_row = fdf.loc[fdf["sales"].idxmax(), ["product_name", "sales"]]
st.markdown(
    f"""
    <div class="info-card" style="max-width: 460px;">
        <div class="card-name">{top_row['product_name']}</div>
        <div class="card-amount">${top_row['sales']:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Top customer by year ----------
st.markdown("## Top Customer by Year")
year_cust = fdf.groupby(["year", "customer_name"], as_index=False)["sales"].sum()
top_idx = year_cust.groupby("year")["sales"].idxmax()
top_per_year = year_cust.loc[top_idx].sort_values("year")

if len(top_per_year):
    cols = st.columns(len(top_per_year))
    for col, (_, row) in zip(cols, top_per_year.iterrows()):
        with col:
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="card-label">{int(row['year'])}</div>
                    <div class="card-name">{row['customer_name']}</div>
                    <div class="card-amount">${row['sales']:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
