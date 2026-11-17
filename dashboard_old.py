from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Food Delivery Analytics", page_icon="🍱", layout="wide")
st.title("🍱 Food Delivery Operations Dashboard")
st.caption("EDA of delivery duration, service factors, geography and operational patterns. Data is observational; correlation does not establish causation.")

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

file = st.file_uploader("Upload the food_delivery_cleaned.csv exported by the notebook",type=["csv"])
if file is None and Path("food_delivery_cleaned.csv").exists():
    data = load_csv("food_delivery_cleaned.csv")
elif file is None:
    st.info("First run the EDA notebook, download food_delivery_cleaned.csv, then upload it here.")
    st.stop()
else:
    data = load_csv(file)

with st.sidebar:
    st.header("Filters")
    for col in ["city_type", "road_traffic_density", "weather", "type_of_order", "type_of_vehicle"]:
        if col in data:
            options = sorted(data[col].dropna().astype(str).unique())
            selected = st.multiselect(col.replace("_", " ").title(), options, default=options)
            data = data[data[col].astype(str).isin(selected)]
if data.empty:
    st.warning("No data matches the filters.")
    st.stop()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Deliveries", f"{len(data):,}")
c2.metric("Mean delivery", f"{data.delivery_minutes.mean():.1f} min")
c3.metric("Median delivery", f"{data.delivery_minutes.median():.1f} min")
c4.metric("More than 35 min", f"{data.delivery_minutes.gt(35).mean():.1%}", help="Illustrative operational threshold, not a documented contractual SLA")

left,right = st.columns(2)
with left:
    fig=px.histogram(data, x="delivery_minutes", nbins=35, title="Delivery duration distribution")
    st.plotly_chart(fig, use_container_width=True)
with right:
    sums=data.groupby("road_traffic_density",dropna=False).delivery_minutes.agg(["mean","size"]).reset_index()
    fig=px.bar(sums,x="road_traffic_density",y="mean",hover_data=["size"],title="Mean delivery duration by traffic")
    st.plotly_chart(fig,use_container_width=True)
left,right=st.columns(2)
with left:
    fig=px.box(data,x="weather",y="delivery_minutes",points=False,title="Weather versus duration")
    st.plotly_chart(fig,use_container_width=True)
with right:
    counts=data["type_of_order"].value_counts().rename_axis("order_type").reset_index(name="deliveries")
    fig=px.pie(counts,names="order_type",values="deliveries",title="Order type share")
    st.plotly_chart(fig,use_container_width=True)
left,right=st.columns(2)
with left:
    if "order_date" in data:
        daily=data.groupby("order_date").size().reset_index(name="deliveries")
        fig=px.line(daily,x="order_date",y="deliveries",title="Daily orders")
        st.plotly_chart(fig,use_container_width=True)
with right:
    if "distance_km" in data:
        subset=data.dropna(subset=["distance_km"]).sample(n=min(3000,data.distance_km.notna().sum()),random_state=42)
        fig=px.scatter(subset,x="distance_km",y="delivery_minutes",color="road_traffic_density",opacity=.4,title="Straight-line distance vs duration (sample)")
        st.plotly_chart(fig,use_container_width=True)

st.subheader("Traffic × Weather")
piv=data.pivot_table(index="weather",columns="road_traffic_density",values="delivery_minutes",aggfunc="mean")
fig=px.imshow(piv,text_auto=".1f",aspect="auto",color_continuous_scale="YlOrRd",labels={"color":"Mean minutes"})
st.plotly_chart(fig,use_container_width=True)

st.subheader("Filtered dataset")
st.dataframe(data.head(300),use_container_width=True)
st.download_button("Download filtered data",data.to_csv(index=False).encode("utf-8"),"food_delivery_filtered.csv","text/csv")
st.caption("Restaurant names, order revenue, and restaurant-level review ratings are not provided by this source dataset.")
