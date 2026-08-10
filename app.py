import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide", page_icon="💹")


@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True)
    df["ship_date"] = pd.to_datetime(df["ship_date"], dayfirst=True)
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    return df


# ---------- Data source ----------
st.sidebar.header("Data")
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
st.sidebar.header("Filters")
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

# ---------- Main KPIs ----------
st.markdown("## Main KPIs")

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Total Sales", f"${fdf['sales'].sum():,.0f}")
with k2:
    st.metric("Total Orders", f"{fdf['order_id'].nunique():,}")
with k3:
    st.metric("Total Customers", f"{fdf['customer_id'].nunique():,}")

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------- Secondary KPIs ----------
st.markdown("## Secondary KPIs")

k4, k5, k6 = st.columns(3)
with k4:
    st.metric("Avg Sale / Order Line", f"${fdf['sales'].mean():,.2f}")
with k5:
    top_state = fdf.groupby("state")["sales"].sum().idxmax()
    st.metric("Top State", top_state)
with k6:
    top_category = fdf.groupby("category")["sales"].sum().idxmax()
    st.metric("Top Category", top_category)

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------- Chart section 1: Category / Sub-Category ----------
st.markdown("## Sales by Category & Sub-Category")

c1, c2 = st.columns(2)
with c1:
    cat_sales = fdf.groupby("category")["sales"].sum().sort_values(ascending=False)
    st.bar_chart(cat_sales)
with c2:
    subcat_sales = fdf.groupby("sub-category")["sales"].sum().sort_values(ascending=False)
    st.bar_chart(subcat_sales)

# ---------- Chart section 2: Year / State ----------
st.markdown("## Sales by Year & State")

c3, c4 = st.columns(2)
with c3:
    year_sales = fdf.groupby("year")["sales"].sum().sort_index()
    st.bar_chart(year_sales)
with c4:
    state_sales = fdf.groupby("state")["sales"].sum().sort_values(ascending=False).head(15)
    st.bar_chart(state_sales)

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------- Sales by State & Year matrix ----------
st.markdown("## Sales by State & Year")
state_year = fdf.pivot_table(index="state", columns="year", values="sales", aggfunc="sum", fill_value=0)
st.dataframe(state_year.style.format("${:,.0f}"), use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------- Category x Sub-Category table ----------
st.markdown("## Sales by Category & Sub-Category (table)")
cat_subcat = (
    fdf.groupby(["category", "sub-category"])
    .agg(yearly=("year", "first"), sales=("sales", "sum"))
    .sort_values("sales", ascending=False)
)
st.dataframe(cat_subcat, use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------- Top product & top order ----------
st.markdown("## Top Product & Top Order")

t1, t2 = st.columns(2)
with t1:
    st.markdown("**Top Selling Product (single line item)**")
    top_row = fdf.loc[fdf["sales"].idxmax(), ["product_name", "sales"]]
    st.write(top_row)
with t2:
    st.markdown("**Top Order by Total Sales**")
    max_order = (
        fdf.groupby("order_id", as_index=False)
        .agg(customer_name=("customer_name", "first"), total=("sales", "sum"))
        .sort_values("total", ascending=False)
        .head(1)
    )
    st.dataframe(max_order, use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# ---------- Raw data ----------
with st.expander("View filtered raw data"):
    st.dataframe(fdf, use_container_width=True)
