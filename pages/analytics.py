import streamlit as st
from services.analytics_service import AnalyticsService
from services.visualization_service import VisualizationService
st.title("📊 Analytics Dashboard")

# Check if dataset exists
if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset first.")
    st.stop()

# Get dataframe from session
df = st.session_state["df"]

# Create analytics object
analytics = AnalyticsService(df)

# KPI Cards
col1, col2 = st.columns(2)

with col1:
    st.metric("📦 Total Orders", analytics.total_orders())
    st.metric("💰 Total Sales", f"₹{analytics.total_sales():,.2f}")
    st.metric("🏆 Best Selling Product", analytics.best_selling_product())

with col2:
    st.metric("👥 Unique Customers", analytics.unique_customers())
    st.metric("🛒 Average Order Value", f"₹{analytics.average_order_value():,.2f}")
    st.divider()
st.divider()

visual = VisualizationService(df)

st.subheader("📊 Sales by Product")
st.plotly_chart(
    visual.sales_by_product(),
    use_container_width=True
)

st.subheader("🥧 Order Status Distribution")
st.plotly_chart(
    visual.order_status_distribution(),
    use_container_width=True
)

st.subheader("💳 Payment Method Distribution")
st.plotly_chart(
    visual.payment_method_distribution(),
    use_container_width=True
)

st.subheader("📈 Monthly Sales Trend")
st.plotly_chart(
    visual.monthly_sales(),
    use_container_width=True
)

st.subheader("📢 Referral Source Distribution")
st.plotly_chart(
    visual.referral_source_distribution(),
    use_container_width=True
)