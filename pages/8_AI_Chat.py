import streamlit as st

from ai.config import AIConfig
from ai.agents.chat_agent import ChatAgent, ChatSession
from ai.tools.registry import ToolRegistry
from ai.tools.portfolio_tools import register_portfolio_tools
from ai.tools.market_tools import register_market_tools
from db.database import get_monthly_ai_cost

st.header("AI Portfolio Assistant")
st.caption("Chat with your portfolio using natural language")

# Check AI config
config = AIConfig.from_env()
if not config.is_configured:
    st.warning("AI is not configured. Set AI_API_KEY in your .env file, or set AI_PROVIDER=ollama for local LLM.")
    st.stop()

# Check budget
monthly_cost = get_monthly_ai_cost()
if monthly_cost >= config.max_monthly_budget_usd:
    st.error(f"Monthly AI budget reached (${monthly_cost:.2f} / ${config.max_monthly_budget_usd:.2f}). Increase AI_MONTHLY_BUDGET in .env to continue.")
    st.stop()


# Init agent (cached)
@st.cache_resource
def init_agent():
    cfg = AIConfig.from_env()
    registry = ToolRegistry()
    register_portfolio_tools(registry)
    register_market_tools(registry)
    return ChatAgent(cfg, registry)


agent = init_agent()

# Session state
if "chat_session" not in st.session_state:
    st.session_state.chat_session = ChatSession()
if "chat_display" not in st.session_state:
    st.session_state.chat_display = []

# Sidebar
with st.sidebar:
    st.subheader("Chat Session")
    session = st.session_state.chat_session
    st.metric("Session Cost", f"${session.total_cost_usd:.4f}")
    st.metric("Monthly Cost", f"${monthly_cost:.4f} / ${config.max_monthly_budget_usd:.2f}")
    st.caption(f"Provider: {config.provider} | Model: {config.model_id}")

    if st.button("Clear Chat"):
        st.session_state.chat_session = ChatSession()
        st.session_state.chat_display = []
        st.rerun()

    st.divider()
    st.subheader("Quick Questions")
    quick_questions = [
        "How is my portfolio doing overall?",
        "Which stock gave me the best return?",
        "What is my total gold holding worth?",
        "Show my Indian portfolio performance",
        "Compare SG stocks vs US stocks",
        "Which holdings are near 52-week high?",
    ]
    for q in quick_questions:
        if st.button(q, key=f"quick_{q}"):
            st.session_state.pending_question = q

# Chat history
for role, content in st.session_state.chat_display:
    with st.chat_message(role):
        st.markdown(content)

# Handle input
prompt = st.chat_input("Ask about your portfolio...")
if "pending_question" in st.session_state:
    prompt = st.session_state.pending_question
    del st.session_state.pending_question

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_display.append(("user", prompt))

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your portfolio..."):
            try:
                response = agent.respond(st.session_state.chat_session, prompt)
                st.markdown(response)
                st.session_state.chat_display.append(("assistant", response))
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_display.append(("assistant", error_msg))
