import streamlit as st

from llm.client import llm_client


# ============================================================
# PAGE TITLE
# ============================================================

st.title("💬 Custom AI Chatbot")

st.caption(
    "A stateful conversational AI chatbot with memory."
)


# ============================================================
# WELCOME MESSAGE
# ============================================================

if not st.session_state.chat_history:

    st.markdown(
        """
        ### 👋 Welcome!

        I am a conversational AI assistant with memory.

        You can have a multi-turn conversation with me,
        and I will maintain the conversation context
        during the current session.

        **Try asking:**

        - Hello, who are you?
        - My name is Vipin.
        - What did I just tell you?
        - Explain machine learning in simple terms.
        """
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.chat_history:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Type your message..."
)


# ============================================================
# PROCESS MESSAGE
# ============================================================

if user_input is not None:

    user_input = user_input.strip()

    if not user_input:

        st.warning(
            "Please enter a message."
        )

        st.stop()


    # --------------------------------------------------------
    # User message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            user_input
        )


    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_input,
        }
    )


    # --------------------------------------------------------
    # AI response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                response = (
                    llm_client.generate_response(
                        user_query=user_input,
                        memory_manager=(
                            st.session_state
                            .memory_manager
                        ),
                    )
                )

                st.markdown(
                    response
                )

            except Exception as error:

                response = (
                    "I couldn't process that message."
                )

                st.error(
                    f"{response}\n\n"
                    f"Error: {error}"
                )


    # --------------------------------------------------------
    # Save response
    # --------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": response,
        }
    )


# ============================================================
# CHAT CONTROLS
# ============================================================

if st.session_state.chat_history:

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.chat_history = []

        st.session_state.memory_manager.clear_memory()

        st.rerun()