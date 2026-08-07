import os
import streamlit as st
import pandas as pd

from analytics.data_loader import DataLoader, data_loader
from analytics.engine import analytics_engine
from analytics.visualization import visualization_engine
from config.settings import settings
from llm.client import llm_client
from memory.conversation_memory import ConversationMemoryManager
from utils.logger import logger

# Configure Streamlit Page Settings
st.set_page_config(
    page_title="AI Data Analytics Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (CSS)
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .kpi-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2563EB;
    }
    .kpi-lbl {
        font-size: 0.85rem;
        color: #64748B;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initializes persistent Streamlit session state objects."""
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())

    if "memory_manager" not in st.session_state:
        st.session_state.memory_manager = ConversationMemoryManager(
            session_id=st.session_state.session_id
        )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def render_sidebar():
    """Renders Streamlit sidebar controls, dataset stats, and memory debugger."""
    with st.sidebar:
        st.title("⚙️ Workspace Panel")

        # Section 1: Dataset Upload / Selection
        st.subheader("📁 Data Source")
        uploaded_file = st.file_uploader(
            "Upload Excel or CSV Dataset",
            type=["xlsx", "xls", "csv"],
            help="Upload custom business dataset or use default.",
        )

        if uploaded_file is not None:
            # Save uploaded file temporarily into data directory
            temp_path = settings.DATA_DIR / uploaded_file.name
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            custom_loader = DataLoader(file_path=temp_path)
            custom_loader.load_data()
            analytics_engine.df = custom_loader.df
            st.success(f"Loaded: `{uploaded_file.name}`")
        else:
            if data_loader.df is None:
                data_loader.load_data()
            st.info(f"Using Default: `Dataset for Data Analytics.xlsx`")

        st.divider()

        # Section 2: Executive KPI Metrics Summary
        st.subheader("📊 Executive KPIs")
        kpis = analytics_engine.get_summary_kpis()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
            st.metric("Avg Order Value", f"${kpis['average_order_value']:,.2f}")
        with col2:
            st.metric("Total Orders", f"{kpis['total_orders']:,}")
            st.metric("Cancellation Rate", f"{kpis['cancellation_rate_pct']}%")

        st.divider()

        # Section 3: Conversation Memory Diagnostics
        st.subheader("🧠 Memory Diagnostics")
        mem_stats = st.session_state.memory_manager.get_stats()
        
        st.caption(f"**Session ID**: `{mem_stats['session_id'][:8]}...`")
        st.caption(f"**Messages Stored**: `{mem_stats['total_messages_stored']}`")
        st.caption(f"**Active Window Tokens**: `{mem_stats['active_window_tokens']} / {mem_stats['max_allowed_tokens']}`")

        if st.button("🗑️ Clear Session Memory", use_container_width=True):
            st.session_state.memory_manager.clear_memory()
            st.session_state.chat_history.clear()
            st.rerun()


def main():
    """Main application layout and interaction flow."""
    initialize_session_state()
    render_sidebar()

    # Header Title
    st.markdown('<div class="main-title">🤖 AI Conversational Data Analytics Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ask natural language questions over your business dataset with stateful session memory.</div>', unsafe_allow_html=True)

    # Tabs: Chat Interface vs Interactive Visualizations
    tab_chat, tab_charts = st.tabs(["💬 Conversational Chat", "📈 Interactive Visualizations"])

    with tab_chat:
        # Display existing message history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input Box
        user_input = st.chat_input("Ask a question about revenue, products, monthly trends, or payment methods...")

        if user_input:
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)

            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Generate Assistant Response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing dataset & generating insights..."):
                    response_text = llm_client.generate_response(
                        user_query=user_input,
                        memory_manager=st.session_state.memory_manager,
                    )
                    st.markdown(response_text)

            st.session_state.chat_history.append({"role": "assistant", "content": response_text})

    with tab_charts:
        st.subheader("📊 Dynamic Business Visualizations")
        chart_type = st.selectbox(
            "Select Analytics Chart View:",
            ["Top Products Revenue (Bar Chart)", "Monthly Revenue Trend (Line Chart)", "Order Status Split (Pie Chart)", "Payment Method Breakdown (Donut Chart)"],
        )

        if "Top Products" in chart_type:
            df_prods = analytics_engine.get_revenue_by_product()
            fig = visualization_engine.create_bar_chart(df_prods, "Product", "TotalRevenue", "Top Products by Revenue")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_prods, use_container_width=True)

        elif "Monthly Revenue" in chart_type:
            df_monthly = analytics_engine.get_monthly_sales_trend()
            fig = visualization_engine.create_line_chart(df_monthly, "YearMonth", "TotalRevenue", "Monthly Revenue Sales Trend")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_monthly, use_container_width=True)

        elif "Order Status" in chart_type:
            df_status = analytics_engine.get_order_status_distribution()
            fig = visualization_engine.create_pie_chart(df_status, "OrderStatus", "OrderCount", "Order Status Split")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_status, use_container_width=True)

        elif "Payment Method" in chart_type:
            df_pay = analytics_engine.get_payment_method_distribution()
            fig = visualization_engine.create_pie_chart(df_pay, "PaymentMethod", "OrderCount", "Payment Method Usage Distribution")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_pay, use_container_width=True)


if __name__ == "__main__":
    main()