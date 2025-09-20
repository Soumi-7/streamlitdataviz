import streamlit as st  
import pandas as pd
import numpy as np
import plotly.express as px
from urllib.parse import urlparse

st.markdown(
    """
**Page overview.** This page highlights two related views:
1) where documented migrant communities are concentrated by district, and  
2) how the exchange rate evolved over time.  

"""
)

st.set_page_config(page_title="MSBA 325 - Streamlit Demo",layout="centered")
st.title("MSBA 325 - Streamlit Demo")
st.write("by Haytham Duwaji")

@st.cache_data(show_spinner=False)
def load_and_clean(csv_path: str, csv_path2: str = None):
    df = pd.read_csv(csv_path)
    df_ = pd.read_csv(csv_path2)
    df3 = df_.copy()
    df1 = df.copy()

    num_cols = [
        "Number of Egyptian",
        "Number of Ethiopians",
        "Number of Iraqi",
        "Number of Bangladeshi",
        "Number of Sri Lankan",
        "Number of Sudanese",
        "Number of other nationalities",
    ]

    # clean numeric columns
    for c in num_cols:
        df1[c] = (
            df1[c].astype(str)
                  .str.replace(",", "", regex=False)
                  .str.strip()
                  .replace({"": np.nan})
        )
        df1[c] = pd.to_numeric(df1[c], errors="coerce").fillna(0).astype(int)

    # extract District from URI
    def extract_name(uri: str) -> str:
        try:
            name = urlparse(uri).path.split("/")[-1].replace("_", " ").strip()
            return name or uri
        except Exception:
            return uri

    if "District URI" in df1.columns:
        df1["District"] = df1["District URI"].apply(extract_name)
        df1 = df1.drop(columns=["District URI"])

    df1["Total migrants"] = df1[num_cols].sum(axis=1)
    
    df3["Year"] = pd.to_numeric(df3["Year"], errors="coerce")
    df3["Value"] = pd.to_numeric(df3["Value"], errors="coerce")
    df3 = df3.dropna(subset=["Year", "Value"])
    return df1, num_cols, df3


path1 = "92e594ab51adfccc49b1e9bd02bb4708_20241020_022106.csv"
path2 = "a9c0cb61966b5c9fa47a4a9bbd375039_20240906_142928.csv"
df1, num_cols, df3 = load_and_clean(path1, path2)


# ---------------- Charts (both use `filtered`) ----------------
tab1, tab2 = st.tabs(["Top Districts (Bar)", "Exchange Rate (Time-series)"])

with tab1:
    top_n = st.slider("Top N districts (by total)", 5, 20, 10)
    top = df1.sort_values("Total migrants", ascending=False).head(top_n)
    fig1 = px.bar(
        top,
        x="District",
        y="Total migrants",
        title=f"Top {top_n} Districts by Total Migrants",
        labels={"Total migrants": "Total migrants"},
    )
    fig1.update_layout(xaxis_title=None)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown(
            f"""Beirut completely dominates, with 
    well over 120,000 migrants. 
    The second place Matn District doesn’t even come close 
    it’s barely a fraction of Beirut’s number. 
    This tells us that Beirut is by far the main hub for migrants, 
    likely because of its jobs, housing, and services. 
    After Beirut, the distribution flattens out 
    all other districts have much smaller totals."""
        )
    
# ---- Tab 2: Interactive time-series
with tab2:
    st.subheader("Exchange Rate — Year range only")

    # Use ONLY Year & Value, aggregated by year
    ts = (
        df3[["Year", "Value"]]
        .groupby("Year", as_index=False)["Value"].mean()
        .sort_values("Year")
    )

    # Year range control
    min_year, max_year = int(ts["Year"].min()), int(ts["Year"].max())
    year_range = st.slider("Year range", min_year, max_year, (min_year, max_year), step=1)

    # Filter to selected years
    ts_f = ts[(ts["Year"] >= year_range[0]) & (ts["Year"] <= year_range[1])]

    # Plot raw values
    fig = px.line(
        ts_f, x="Year", y="Value", markers=True,
        title="Lebanese Pound per USD (raw)"
    )

    st.markdown(
        f"""The exchange rate of the Lebanese Pound (LBP) to the US Dollar (USD) has seen significant fluctuations over the years. 
        Notably, there was a sharp increase in the exchange rate around 2019-2020, indicating a rapid depreciation of the LBP against the USD. 
        This trend reflects the economic challenges faced by Lebanon during this period."""
    )
    st.plotly_chart(fig, use_container_width=True)