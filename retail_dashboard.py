import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Retail Executive Dashboard", layout="wide")
df=pd.read_csv("clean_dataset.csv")
df["order_date"]=pd.to_datetime(df["order_date"])

st.title("Retail Executive Dashboard")
st.caption("Interactive KPI dashboard")

st.sidebar.header("Filters")
dates=st.sidebar.date_input("Order Date",(df.order_date.min().date(),df.order_date.max().date()))
f=df.copy()
if isinstance(dates,tuple) and len(dates)==2:
    f=f[(f.order_date.dt.date>=dates[0])&(f.order_date.dt.date<=dates[1])]
for field in ["category","customer_segment","city","payment_status"]:
    opts=sorted(f[field].dropna().astype(str).unique())
    sel=st.sidebar.multiselect(field.replace("_"," ").title(),opts)
    if sel: f=f[f[field].astype(str).isin(sel)]

rev=f.net_sales.sum(); ords=f.order_id.nunique(); cust=f.customer_segment.nunique()
aov=rev/ords if ords else 0
c1,c2,c3,c4=st.columns(4)
c1.metric("Revenue",f"₹{rev:,.2f}"); c2.metric("Orders",f"{ords:,}")
c3.metric("Customer Segments",f"{cust:,}"); c4.metric("Average Order Value",f"₹{aov:,.2f}")

monthly=f.assign(month=f.order_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).net_sales.sum()
st.plotly_chart(px.area(monthly,x="month",y="net_sales",title="Revenue Trend"),use_container_width=True)

a,b=st.columns(2)
with a:
    cat=f.groupby("category",as_index=False).net_sales.sum()
    st.plotly_chart(px.bar(cat,x="category",y="net_sales",title="Revenue by Category"),use_container_width=True)
with b:
    pay=f.payment_status.value_counts().reset_index(); pay.columns=["payment_status","orders"]
    st.plotly_chart(px.pie(pay,names="payment_status",values="orders",title="Payment Status Mix"),use_container_width=True)

st.subheader("Geographic Revenue")
geo=f.groupby("city",as_index=False).net_sales.sum().sort_values("net_sales",ascending=False)
st.plotly_chart(px.bar(geo,x="net_sales",y="city",orientation="h",title="Revenue by City"),use_container_width=True)

st.subheader("Drill-down")
st.dataframe(f.sort_values("order_date",ascending=False),use_container_width=True)
