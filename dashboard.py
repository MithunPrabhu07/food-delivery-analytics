"""Food Delivery Operations — Streamlit dashboard for the cleaned EDA CSV.
Run: python -m streamlit run dashboard.py
"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Food Delivery | Operations Intelligence", page_icon="🍱", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).resolve().parent
CATEGORIES = ["city_type", "road_traffic_density", "weather", "type_of_order", "type_of_vehicle"]
LABELS = {"city_type": "City type", "road_traffic_density": "Traffic density", "weather": "Weather", "type_of_order": "Order type", "type_of_vehicle": "Vehicle type"}
TRAFFIC_ORDER = ["Low", "Medium", "High", "Jam", "Unknown"]
BG = "#0b1020"
PAPER = "#141c31"
FONT = "#e7edf9"
ACCENT = "#70d6c2"
PALETTE = ["#70d6c2", "#70a9ff", "#f4b86a", "#a79bff", "#ef86ac", "#83c6ea", "#b0b7c3"]

st.markdown("""<style>
  .stApp {background: linear-gradient(145deg, #0b1020 0%, #10182a 70%, #101522 100%);}
  section[data-testid="stSidebar"] {background-color:#11192b; border-right:1px solid #27334d;}
  div[data-testid="stMetric"] {background:#172139;border:1px solid #2a3954;padding:17px 18px;border-radius:15px;}
  div[data-testid="stMetricLabel"] {color:#b6c4da;}
  div[data-testid="stMetricValue"] {color:#f3f8ff;}
  .block-container {max-width:1500px;padding-top:1.8rem;padding-bottom:3rem;}
  h1,h2,h3 {letter-spacing:-0.025em;}
  div[data-testid="stVerticalBlockBorderWrapper"] {border-color:#293650;}
  .hero {padding:25px 28px;border:1px solid #30415d;border-radius:20px;
    background:linear-gradient(110deg,#1a2e49,#132239 56%,#142c36);margin-bottom:18px;}
  .hero-eyebrow {font-size:0.78rem;color:#70d6c2;letter-spacing:0.18em;font-weight:800;}
  .hero-title {font-size:2.2rem;color:#f1f7ff;font-weight:800;line-height:1.15;margin:10px 0;}
  .hero-subtitle {color:#b8c8dc;font-size:.95rem;max-width:850px;}
  .section-note {color:#a3b2c7;font-size:.9rem;margin-bottom:.8rem;}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_csv(src):
    d = pd.read_csv(src, low_memory=False)
    if "delivery_minutes" not in d.columns:
        raise ValueError("The file must be food_delivery_cleaned.csv containing delivery_minutes. Run the EDA notebook first.")
    d["delivery_minutes"] = pd.to_numeric(d["delivery_minutes"], errors="coerce")
    d = d.dropna(subset=["delivery_minutes"]).copy()
    for col in CATEGORIES:
        if col in d:
            d[col] = d[col].fillna("Unknown").astype(str).str.strip().replace({"": "Unknown"})
    if "city_type" in d:
        d["city_type"] = d["city_type"].replace({"Metropolitian": "Metropolitan"})
    for col in ["straight_line_km", "delivery_person_rating", "order_hour"]:
        if col in d:
            d[col] = pd.to_numeric(d[col], errors="coerce")
    if "order_date" in d:
        d["order_date"] = pd.to_datetime(d["order_date"], errors="coerce")
    return d

st.markdown('''<div class="hero"><div class="hero-eyebrow">OPERATIONS INTELLIGENCE · PYTHON EDA</div>
<div class="hero-title">🍱 Food Delivery Analytics</div>
<div class="hero-subtitle">Explore delivery efficiency, traffic congestion, weather, vehicle performance and city patterns. All visuals respond to your filters.</div></div>''', unsafe_allow_html=True)

local_file = ROOT / "food_delivery_cleaned.csv"
with st.sidebar:
    st.markdown("### 🎛️ Explore your data")
    st.caption("Filters apply across all tabs and metrics.")
    if local_file.exists():
        source = str(local_file)
        st.success("Cleaned CSV loaded automatically", icon="✅")
    else:
        upload = st.file_uploader("Upload food_delivery_cleaned.csv", type="csv")
        if upload is None:
            st.info("Put food_delivery_cleaned.csv in the same folder as dashboard.py, or upload it here.")
            st.stop()
        source = upload

try:
    full = load_csv(source)
except Exception as exc:
    st.error(f"Could not load the CSV: {exc}")
    st.stop()

filtered = full.copy()
with st.sidebar:
    for column in CATEGORIES:
        if column not in full:
            continue
        choices = sorted(full[column].unique().tolist())
        options = st.multiselect(LABELS[column], choices, default=choices, key=f"filter_{column}")
        filtered = filtered[filtered[column].isin(options)]
    st.divider()
    st.caption(f"**{len(filtered):,}** of {len(full):,} records selected")
    st.caption("Unknown = unavailable or invalid category in source data.")

if filtered.empty:
    st.warning("No matching deliveries. Change one or more filters on the left.")
    st.stop()

# All plots share the same visual language and consistent layout heights.
def polished(fig, height=365, *, percent=False):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        font=dict(family="Arial, sans-serif", color=FONT, size=12),
        title=dict(font=dict(size=16, color="#f4f8ff"), x=0.04, y=0.96),
        height=height, margin=dict(l=32, r=22, t=65, b=45),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
        hoverlabel=dict(bgcolor="#273550", font_size=12),
        colorway=PALETTE,
    )
    fig.update_xaxes(gridcolor="#2b3750", zeroline=False, title_font=dict(color="#b8c9dc"))
    fig.update_yaxes(gridcolor="#2b3750", zeroline=False, title_font=dict(color="#b8c9dc"))
    return fig

def chart(fig, key):
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": False}, key=key)

st.markdown("#### Performance at a glance")
metrics = st.columns(4)
metrics[0].metric("Deliveries", f"{len(filtered):,}")
metrics[1].metric("Average delivery", f"{filtered.delivery_minutes.mean():.1f} min")
metrics[2].metric("Median delivery", f"{filtered.delivery_minutes.median():.1f} min")
metrics[3].metric("Over 35 minutes", f"{filtered.delivery_minutes.gt(35).mean():.1%}", help="A project-defined threshold, not an official company delivery guarantee.")
st.write("")

t_overview, t_performance, t_conditions, t_trends, t_data = st.tabs([
    "📊 Overview", "🏍️ Vehicles & Cities", "🌦️ Traffic & Weather", "📅 Orders & Trends", "🗃️ Data Explorer"
])

with t_overview:
    st.markdown("<div class='section-note'>A quick view of the distribution of delivery durations and order categories.</div>", unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    with a:
        fig = px.histogram(filtered, x="delivery_minutes", nbins=32, title="Delivery time distribution", labels={"delivery_minutes":"Delivery duration (minutes)", "count":"Deliveries"}, color_discrete_sequence=[ACCENT])
        fig.update_traces(hovertemplate="Duration: %{x:.0f} min<br>Deliveries: %{y:,}<extra></extra>")
        chart(polished(fig), "duration_hist")
    with b:
        if "type_of_order" in filtered:
            counts = filtered["type_of_order"].value_counts().rename_axis("Order category").reset_index(name="Deliveries")
            fig = px.pie(counts, names="Order category", values="Deliveries", hole=.55, title="Order categories", color_discrete_sequence=PALETTE)
            fig.update_traces(textinfo="percent+label", textposition="outside", hovertemplate="%{label}<br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>")
            chart(polished(fig), "order_mix")
    st.info("**How to read:** Time distribution shows the most common delivery durations; category share describes this dataset, not the overall Indian food-delivery market.")

with t_performance:
    st.markdown("<div class='section-note'>Compare delivery speeds by vehicle and the number of records in each city category. City type is a classification, not an individual restaurant or city.</div>", unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    with a:
        if "type_of_vehicle" in filtered:
            v = (filtered.groupby("type_of_vehicle")["delivery_minutes"].agg(mean="mean", count="size", median="median").reset_index().sort_values("mean", ascending=True))
            fig = px.bar(v, x="mean", y="type_of_vehicle", orientation="h", title="Vehicle type performance · avg minutes", text="mean", custom_data=["count", "median"], labels={"mean":"Avg delivery (min)", "type_of_vehicle":"Vehicle"}, color="mean", color_continuous_scale=["#70d6c2", "#70a9ff", "#f4b86a"])
            fig.update_traces(texttemplate="%{text:.1f} min", textposition="outside", hovertemplate="Vehicle: %{y}<br>Average: %{x:.1f} min<br>Median: %{customdata[1]:.1f} min<br>Deliveries: %{customdata[0]:,}<extra></extra>")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(range=[0, max(v["mean"]) * 1.23])
            chart(polished(fig), "vehicle_performance")
    with b:
        if "city_type" in filtered:
            c = filtered["city_type"].value_counts().rename_axis("City type").reset_index(name="Deliveries").sort_values("Deliveries", ascending=True)
            fig = px.bar(c, x="Deliveries", y="City type", orientation="h", title="City type distribution · order count", text="Deliveries", color="City type", color_discrete_sequence=PALETTE)
            fig.update_traces(texttemplate="%{text:,}", textposition="outside", hovertemplate="%{y}<br>Deliveries: %{x:,}<extra></extra>")
            fig.update_layout(showlegend=False)
            fig.update_xaxes(range=[0, max(c["Deliveries"]) * 1.24])
            chart(polished(fig), "city_distribution")
    a, b = st.columns(2, gap="medium")
    with a:
        if "city_type" in filtered:
            ct = filtered.groupby("city_type").delivery_minutes.agg(mean="mean", n="size").reset_index().sort_values("mean")
            fig = px.bar(ct, x="city_type", y="mean", title="Average delivery time by city type", text="mean", custom_data=["n"], labels={"city_type":"City type", "mean":"Average minutes"}, color_discrete_sequence=["#70a9ff"])
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", hovertemplate="%{x}<br>Average: %{y:.1f} min<br>Orders: %{customdata[0]:,}<extra></extra>")
            chart(polished(fig), "city_duration")
    with b:
        if "straight_line_km" in filtered:
            clean = filtered.dropna(subset=["straight_line_km", "delivery_minutes"])
            clean = clean[(clean.straight_line_km >= 0) & (clean.straight_line_km <= 150)]
            if len(clean):
                sample = clean.sample(n=min(len(clean), 2500), random_state=42)
                fig = px.scatter(sample, x="straight_line_km", y="delivery_minutes", color="road_traffic_density" if "road_traffic_density" in sample else None, opacity=.55, title="Distance vs delivery time · sample", labels={"straight_line_km":"Straight-line distance (km)", "delivery_minutes":"Delivery minutes", "road_traffic_density":"Traffic"}, color_discrete_sequence=PALETTE)
                chart(polished(fig), "distance_time")
    st.caption("Vehicle comparisons are descriptive; vehicle assignment, route length and traffic can affect differences. Distance is straight-line approximation, not road distance.")

with t_conditions:
    st.markdown("<div class='section-note'>Investigate how traffic and weather conditions are associated with delivery duration.</div>", unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    with a:
        if "road_traffic_density" in filtered:
            t = filtered.groupby("road_traffic_density").delivery_minutes.agg(mean="mean", n="size").reset_index()
            t["road_traffic_density"] = pd.Categorical(t["road_traffic_density"], categories=TRAFFIC_ORDER, ordered=True)
            t = t.sort_values("road_traffic_density")
            fig = px.bar(t, x="road_traffic_density", y="mean", text="mean", custom_data=["n"], title="Average delivery by traffic", labels={"road_traffic_density":"Traffic", "mean":"Mean minutes"}, color_discrete_sequence=["#70a9ff"])
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", hovertemplate="%{x}<br>Average: %{y:.1f} min<br>Deliveries: %{customdata[0]:,}<extra></extra>")
            chart(polished(fig), "traffic_duration")
    with b:
        if "weather" in filtered:
            fig = px.box(filtered, x="weather", y="delivery_minutes", points=False, title="Weather vs delivery duration", labels={"weather":"Weather", "delivery_minutes":"Delivery minutes"}, color_discrete_sequence=["#70d6c2"])
            fig.update_xaxes(tickangle=-25)
            chart(polished(fig), "weather_box")
    if all(c in filtered for c in ["weather", "road_traffic_density"]):
        st.markdown("#### Traffic × weather interaction")
        pivot = filtered.pivot_table(index="weather", columns="road_traffic_density", values="delivery_minutes", aggfunc="mean")
        pivot = pivot.reindex(columns=[c for c in TRAFFIC_ORDER if c in pivot.columns])
        fig = px.imshow(pivot, text_auto=".1f", aspect="auto", color_continuous_scale="YlOrRd", labels=dict(x="Traffic density", y="Weather", color="Mean minutes"), title="Mean delivery time by weather and traffic")
        fig.update_traces(hovertemplate="Traffic: %{x}<br>Weather: %{y}<br>Average: %{z:.1f} min<extra></extra>")
        chart(polished(fig, height=430), "traffic_weather")
        st.caption("Cells are averages; very small groups may give unstable estimates. Unknown does not indicate a real weather or traffic condition.")

with t_trends:
    st.markdown("<div class='section-note'>View time-based patterns in the historical records.</div>", unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    with a:
        if "order_date" in filtered:
            daily = filtered.dropna(subset=["order_date"]).groupby("order_date").size().reset_index(name="deliveries").sort_values("order_date")
            fig = px.line(daily, x="order_date", y="deliveries", title="Daily recorded orders", labels={"order_date":"Date", "deliveries":"Orders"}, markers=True, color_discrete_sequence=[ACCENT])
            fig.update_traces(line_width=2.5, marker_size=5)
            chart(polished(fig), "daily")
    with b:
        if "order_hour" in filtered:
            hourly = filtered.dropna(subset=["order_hour"]).groupby("order_hour").size().reset_index(name="deliveries")
            fig = px.bar(hourly, x="order_hour", y="deliveries", title="Orders by hour of day", labels={"order_hour":"Hour (24h)", "deliveries":"Orders"}, color_discrete_sequence=["#70a9ff"])
            fig.update_xaxes(dtick=2)
            chart(polished(fig), "hourly")
    a, b = st.columns(2, gap="medium")
    with a:
        if "order_weekday" in filtered:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekdays = filtered.groupby("order_weekday").delivery_minutes.mean().reindex(days).dropna().reset_index(name="mean")
            fig = px.bar(weekdays, x="order_weekday", y="mean", title="Average delivery by weekday", labels={"order_weekday":"Weekday", "mean":"Minutes"}, color_discrete_sequence=["#f4b86a"])
            fig.update_xaxes(tickangle=-30)
            chart(polished(fig), "weekday")
    with b:
        if "type_of_order" in filtered:
            types = filtered.groupby("type_of_order").delivery_minutes.mean().reset_index(name="mean").sort_values("mean")
            fig = px.bar(types, x="type_of_order", y="mean", title="Average delivery by order type", labels={"type_of_order":"Order type", "mean":"Minutes"}, text="mean", color_discrete_sequence=["#a79bff"])
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            chart(polished(fig), "order_duration")

with t_data:
    st.markdown("#### Explore and export the filtered dataset")
    st.caption("The table is a preview, but CSV export includes all filtered rows.")
    st.dataframe(filtered.head(500), use_container_width=True, height=360, hide_index=True)
    st.download_button("⬇️ Download filtered CSV", data=filtered.to_csv(index=False).encode("utf-8"), file_name="food_delivery_filtered.csv", mime="text/csv")
    numeric = [c for c in ["delivery_minutes", "delivery_person_age", "delivery_person_rating", "straight_line_km", "multiple_deliveries", "order_hour"] if c in filtered.columns]
    if len(numeric) >= 2:
        corr = filtered[numeric].apply(pd.to_numeric, errors="coerce").corr()
        fig = px.imshow(corr, text_auto=".2f", aspect="auto", zmin=-1, zmax=1, color_continuous_scale="RdBu_r", title="Numeric correlation heatmap")
        chart(polished(fig, height=465), "correlation")
    st.caption("Correlation is not causation. Dataset does not include restaurant-level revenue, food pricing, or customer review scores for individual restaurants.")

st.divider()
st.caption("Built with Python · Pandas · Plotly · Streamlit  |  Source: cleaned Zomato delivery operations records  |  Analyses reflect the selected records only.")


# ==========================================
# NEW FEATURE: DELIVERY PERFORMANCE ANALYSIS
# ==========================================

from pathlib import Path
import pandas as pd
import streamlit as st

st.divider()
st.subheader("🚦 Delivery Performance Classification")

# Load the cleaned dataset directly
csv_path = Path(__file__).resolve().parent / "food_delivery_cleaned.csv"

if not csv_path.exists():
    st.error("food_delivery_cleaned.csv not found in the project folder.")
else:
    performance_df = pd.read_csv(csv_path)

    if "delivery_minutes" not in performance_df.columns:
        st.error("Delivery time column not found in cleaned CSV.")
    else:
        performance_df["delivery_minutes"] = pd.to_numeric(
            performance_df["delivery_minutes"],
            errors="coerce"
        )

        durations = performance_df["delivery_minutes"].dropna()

        # Classify delivery performance
        performance_df["Performance"] = pd.cut(
            performance_df["delivery_minutes"],
            bins=[-float("inf"), 20, 35, float("inf")],
            labels=["Fast", "Moderate", "Delayed"]
        )

        counts = performance_df["Performance"].value_counts(
            sort=False
        ).reindex(["Fast", "Moderate", "Delayed"], fill_value=0)

        total = counts.sum()

        percentages = counts / total * 100 if total else counts * 0

        # Display KPI cards
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🟢 Fast Deliveries",
            f"{counts['Fast']:,}",
            f"{percentages['Fast']:.1f}%"
        )

        col2.metric(
            "🟡 Moderate Deliveries",
            f"{counts['Moderate']:,}",
            f"{percentages['Moderate']:.1f}%"
        )

        col3.metric(
            "🔴 Delayed Deliveries",
            f"{counts['Delayed']:,}",
            f"{percentages['Delayed']:.1f}%"
        )

        # Performance distribution chart
        chart_df = pd.DataFrame({
            "Delivery Category": counts.index.astype(str),
            "Number of Deliveries": counts.values
        })

        st.bar_chart(
            chart_df.set_index("Delivery Category")
        )

        # Summary table
        summary_df = pd.DataFrame({
            "Delivery Category": counts.index.astype(str),
            "Number of Deliveries": counts.values,
            "Percentage (%)": percentages.round(2).values
        })

        st.dataframe(summary_df, use_container_width=True)

        st.caption(
            "Fast: 20 minutes or less | "
            "Moderate: Above 20 up to 35 minutes | "
            "Delayed: Above 35 minutes. "
            "These are project-defined analytical thresholds. "
            "This section uses the full cleaned dataset, "
            "independently of the existing dashboard filters."
        )

# ==============================================
# NEW FEATURE: GEOGRAPHICAL DELIVERY MAP
# ==============================================

import pandas as pd
import streamlit as st
from pathlib import Path

st.divider()
st.header("🗺️ Geographical Delivery Analysis")

# Load the cleaned dataset
geo_path = Path(__file__).resolve().parent / "food_delivery_cleaned.csv"

if not geo_path.exists():
    st.error("Cleaned dataset not found. Check your project folder.")

else:
    geo_df = pd.read_csv(geo_path)

    required_cols = [
        "restaurant_latitude",
        "restaurant_longitude",
        "delivery_latitude",
        "delivery_longitude"
    ]

    missing_cols = [
        col for col in required_cols if col not in geo_df.columns
    ]

    if missing_cols:
        st.error(f"Missing geographical columns: {missing_cols}")

    else:
        # Prepare restaurant pickup locations
        pickup = pd.DataFrame({
            "latitude": geo_df["restaurant_latitude"],
            "longitude": geo_df["restaurant_longitude"]
        })

        # Prepare customer delivery locations
        dropoff = pd.DataFrame({
            "latitude": geo_df["delivery_latitude"],
            "longitude": geo_df["delivery_longitude"]
        })

        # Remove invalid coordinates
        def clean_map_coordinates(points):
            points = points.copy()

            points["latitude"] = pd.to_numeric(
                points["latitude"], errors="coerce"
            )
            points["longitude"] = pd.to_numeric(
                points["longitude"], errors="coerce"
            )

            points = points.dropna(
                subset=["latitude", "longitude"]
            )

            # Valid geographical range for India
            points = points[
                points["latitude"].between(6, 38) &
                points["longitude"].between(68, 98)
            ]

            return points

        pickup = clean_map_coordinates(pickup)
        dropoff = clean_map_coordinates(dropoff)

        # Display location statistics
        col1, col2 = st.columns(2)

        col1.metric(
            "Valid Restaurant Locations",
            f"{len(pickup):,}"
        )

        col2.metric(
            "Valid Delivery Locations",
            f"{len(dropoff):,}"
        )

        st.markdown("### Explore Delivery Locations")

        st.caption(
            "Orange represents restaurant pickup locations. "
            "Blue represents customer delivery locations."
        )

        # Interactive layer selection
        selected_layers = st.multiselect(
            "Select locations to display",
            ["Restaurant Pickup", "Customer Delivery"],
            default=["Restaurant Pickup", "Customer Delivery"],
            key="geographical_map_layers"
        )

        map_frames = []

        # Sample points to keep map rendering responsive
        if "Restaurant Pickup" in selected_layers:
            if not pickup.empty:
                p = pickup.sample(
                    n=min(3500, len(pickup)),
                    random_state=42
                )
                p["point_color"] = "#F59E0B"
                map_frames.append(p)

        if "Customer Delivery" in selected_layers:
            if not dropoff.empty:
                d = dropoff.sample(
                    n=min(3500, len(dropoff)),
                    random_state=42
                )
                d["point_color"] = "#22D3EE"
                map_frames.append(d)

        if map_frames:
            map_data = pd.concat(
                map_frames,
                ignore_index=True
            )

            # Display interactive geographical map
            st.map(
                map_data,
                latitude="latitude",
                longitude="longitude",
                color="point_color",
                size=150,
                width="stretch",
                height=550,
                alt="Restaurant pickup and delivery locations across India"
            )

            st.success(
                f"Displaying {len(map_data):,} sampled location points."
            )

        else:
            st.info("Select at least one location type to display.")

        st.caption(
            "Note: The map displays geographical coordinates from "
            "the dataset, not actual driving routes. Invalid "
            "coordinates have been excluded."
        )
