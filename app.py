import uuid

import streamlit as st

from memory.conversation_memory import ConversationMemoryManager


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Conversational Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


if "memory_manager" not in st.session_state:
    st.session_state.memory_manager = ConversationMemoryManager(
        session_id=st.session_state.session_id
    )


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# APPLICATION NAVIGATION
# ============================================================

pages = [
    st.Page(
        "pages/chat.py",
        title="Chat",
        icon="💬",
        default=True,
    ),
]


pg = st.navigation(
    pages,
    position="sidebar",
    expanded=True,
)


# ============================================================
# RUN APPLICATION
# ============================================================

pg.run()