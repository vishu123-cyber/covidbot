import time
import streamlit as st
from dotenv import load_dotenv
from src.chatbot import CovidChatbot

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI-based COVID-19 Information Chatbot",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Chatbot Initialization
# -----------------------------
@st.cache_resource
def load_chatbot():
    return CovidChatbot()

chatbot = load_chatbot()

# -----------------------------
# Welcome Message
# -----------------------------
WELCOME_MESSAGE = (
    "Hello. I am your AI-based COVID-19 Information Chatbot.\n\n"
    "You can ask me about COVID-19 symptoms, prevention, testing, vaccination, "
    "isolation, recovery, and related topics."
)

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]

# -----------------------------
# Custom Dark Professional UI
# -----------------------------
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(180deg, #0b0f19 0%, #111827 100%);
    color: #f3f4f6;
}

/* Remove default top padding */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
    max-width: 1100px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Title */
.chat-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.2rem;
}

.chat-subtitle {
    font-size: 1rem;
    color: #94a3b8;
    margin-bottom: 1.5rem;
}

/* Chat message wrappers */
.chat-row {
    display: flex;
    width: 100%;
    margin-bottom: 1rem;
}

.chat-row.user {
    justify-content: flex-end;
}

.chat-row.assistant {
    justify-content: flex-start;
}

/* Chat bubbles */
.chat-bubble {
    max-width: 78%;
    padding: 14px 18px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.6;
    box-shadow: 0 4px 18px rgba(0,0,0,0.18);
    word-wrap: break-word;
    white-space: pre-wrap;
}

.chat-bubble.user {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border-bottom-right-radius: 6px;
}

.chat-bubble.assistant {
    background: #1f2937;
    color: #f9fafb;
    border: 1px solid rgba(255,255,255,0.08);
    border-bottom-left-radius: 6px;
}

/* Avatar badge */
.avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin: 0 10px;
    flex-shrink: 0;
}

.avatar.user {
    background: #2563eb;
    color: white;
}

.avatar.assistant {
    background: #10b981;
    color: white;
}

/* Input box */
.stChatInputContainer {
    background-color: transparent !important;
    border-top: none !important;
}

[data-testid="stChatInput"] {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea {
    color: #f9fafb !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08);
    background: #1f2937;
    color: #f3f4f6;
    font-weight: 500;
    padding: 0.6rem 1rem;
}

.stButton > button:hover {
    background: #374151;
    color: white;
    border: 1px solid rgba(255,255,255,0.15);
}

/* Sidebar cards */
.sidebar-card {
    background: #111827;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 12px;
}

.sidebar-heading {
    font-size: 16px;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
}

.sidebar-text {
    font-size: 14px;
    color: #cbd5e1;
    line-height: 1.5;
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background: rgba(255,255,255,0.08);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 🦠 COVID Chatbot")
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-heading">About</div>
        <div class="sidebar-text">
            This chatbot answers COVID-19 related questions using AI.
            Ask about symptoms, prevention, testing, vaccines, isolation, and recovery.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-heading">Suggested Questions</div>
        <div class="sidebar-text">
            • What are the symptoms of COVID-19?<br>
            • How can I prevent COVID-19?<br>
            • What is isolation?<br>
            • Is COVID vaccine safe?<br>
            • When should I get tested?
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]
        chatbot.reset_history()
        st.rerun()

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="chat-title">AI-based COVID-19 Information Chatbot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="chat-subtitle">Dark professional chat interface inspired by modern AI assistants.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Display Chat Messages
# -----------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-row user">
            <div class="chat-bubble user">{msg["content"]}</div>
            <div class="avatar user">👤</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-row assistant">
            <div class="avatar assistant">🦠</div>
            <div class="chat-bubble assistant">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Chat Input
# -----------------------------
user_input = st.chat_input("Ask a COVID-19 related question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # show user message immediately
    st.markdown(f"""
    <div class="chat-row user">
        <div class="chat-bubble user">{user_input}</div>
        <div class="avatar user">👤</div>
    </div>
    """, unsafe_allow_html=True)

    # keep same full-answer style, but add a natural wait
    with st.spinner("Thinking..."):
        start_time = time.time()
        response = chatbot.get_response(user_input)

        min_delay = 2.0
        elapsed = time.time() - start_time
        if elapsed < min_delay:
            time.sleep(min_delay - elapsed)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()