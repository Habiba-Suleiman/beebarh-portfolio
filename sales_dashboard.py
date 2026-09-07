import streamlit as st
import pandas as pd
import plotly.express as px

# ----------- page config -----------
st.set_page_config(page_title="Sales Performanace Dashboard", layout="wide")

# ----------- Load data --------------
@st.cache_data
def load_data():
    df = pd.read_csv("Sales_raw.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df = load_data()

# ------------ Sidebar filters ------------
st.sidebar.header("Filters")

categories = st.sidebar.multiselect(
    "Category", options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)
states = st.sidebar.multiselect(
    "State", options=sorted(df["State"].unique()),
    default=sorted(df["State"].unique())
)
payment_modes = st.sidebar.multiselect(
    "Payment Mode", options=sorted(df["PaymentMode"].unique()),
    default=sorted(df["PaymentMode"].unique())
)
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(df["Order Date"].min(), df["Order Date"].max()),
min_value=df["Order Date"].min(),
max_value=df["Order Date"].max() 
)

# ----------- Apply filters -----------
mask = (
    df["Category"].isin(categories)
    & df["State"].isin(states)
    & df["PaymentMode"].isin(payment_modes)
    & (df["Order Date"] >= pd.to_datetime(date_range[0]))
    & (df["Order Date"] <= pd.to_datetime(date_range[1]))
)
fdf = df.loc[mask]

# ------------- Title ---------------
st.title("Sales Performance Dashboard")
st.caption("Sales Analysis - Nexus Fellowship")

# ------------ KPI row --------------
col1, col2, col3, col4 = st.columns(4)
total_amount = fdf["Amount"].sum()
total_profit = fdf["Profit"].sum()
margin = (total_profit/total_amount * 100) if total_amount else 0
total_orders = fdf["Order ID"].count()

col1.metric("Total Sales", f"${total_amount:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Profit Margin", f"{margin:.1f}%")
col4.metric("Total Line Items",f"{total_orders:,}")

st.divider()

#------------- Row 1: Category sales + Top sub-categories ---------------
c1, c2 = st.columns(2)

with c1:
    cat_sales = fdf.groupby("Category")[["Amount", "Profit"]].sum().reset_index()
    fig= px.bar(cat_sales, x="Category", y="Amount", color="Category",
                title="Sales Amount by Category", text_auto=".2s")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with c2:
    subcat = fdf.groupby("Sub-Category")

#----------- Row 2: Trend + Profitability by category -------------------
c3, c4 = st.columns(2)

with c3:
    trend = fdf.set_index("Order Date").resample("ME")[["Amount", "Profit"]].sum().reset_index()
    fig = px.line(trend, x="Order Date", y=["Amount", "Profit"],
                  title="Sales & Profit Trend Over Time")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    cat_profit = fdf.groupby("Category")["Profit"].sum().reset_index()
    cat_profit["Margin %"] = (
        fdf.groupby("Category").apply(lambda g: g["Profit"].sum() / g["Amount"].sum() * 100)
    ).values
    fig = px.bar(cat_profit, x="Category", y="Profit", color="Margin %",
                 title="Profit & Margin by Category", text_auto=".2s",
                 color_continuous_scale="viridis")
    st.plotly_chart(fig, use_container_width=True)

# ------------- Row 3: State map + Payment mode -------------------
c5, c6 = st.columns(2)

state_abbrev = {
    "carlifonia": "CA", "New York": "NY", "Texas": "TX", "Florida": "FL",
    "Illinois": "IL", "Ohio": "OH"
}

with c5:
    state_profit = fdf.groupby("State")["Profit"].sum().reset_index()
    state_profit["code"] = state_profit["State"].map(state_abbrev)
    fig = px.choropleth(
        state_profit, locations="code", locationmode="USA-states",
        color="Profit", scope="usa", title="Profit by State",
        color_continuous_scale="viridis"
    )
    st.plotly_chart(fig, use_container_width=True)

with c6:
    pay = fdf.groupby("PaymentMode")["Order ID"].count().sort_values(ascending=False).reset_index()
    pay.columns = ["Payment", "Order Count"]
    fig = px.bar(pay, x="Order Count", y="Payment", orientation="h",
                 title="Payment Mode Usage", text_auto=True, color="Payment")
    st.plotly_chart(fig, use_container_width=True)

# ------------------ Row 4: Top customers -------------------
st.subheader("Top 10 Customers by Sales Amount")
top_cust = fdf.groupby("CustomerName")["Amount"].sum().sort_values(ascending=False).head(10).reset_index()
fig = px.bar(top_cust, x="Amount", y="CustomerName", orientation="h", text_auto=".2s")
fig.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

# ---------------- Raw data -------------------
with st.expander("view filtered raw data"):
    st.dataframe(fdf)



















