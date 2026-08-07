import streamlit as st

from services.ai_agent import AIAgent

st.title("🤖 AI Data Analyst")

if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset first.")
    st.stop()

df = st.session_state["df"]

agent = AIAgent(df)

question = st.text_input(
    "Ask anything about your dataset..."
)

if st.button("Ask AI"):

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Analyzing dataset..."):

        answer = agent.ask(question)

    st.markdown(answer)