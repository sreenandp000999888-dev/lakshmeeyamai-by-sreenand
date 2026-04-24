import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import json
import os
import secrets
from datetime import datetime
import requests
import hashlib

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Lakshmeeyam AI", page_icon="🤖", layout="wide")

# --- 2. GOOGLE VERIFICATION WORKAROUND ---
# Using your new token: DmWLc_BbgGyevRBWmBNOqCWf2zc5RMxIJJoSm8xaGo0
components.html(
    """
    <script>
        if (!window.parent.document.querySelector('meta[name="google-site-verification"]')) {
            const meta = window.parent.document.createElement('meta');
            meta.name = "google-site-verification";
            meta.content = "DmWLc_BbgGyevRBWmBNOqCWf2zc5RMxIJJoSm8xaGo0";
            window.parent.document.head.appendChild(meta);
        }
    </script>
    """,
    height=0,
    width=0,
)

# --- 3. FUTURISTIC STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=2072");
        background-size: cover;
    }
    .main-box {
        background-color: rgba(0, 0, 0, 0.85);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #00d4ff;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0px 0px 15px rgba(0, 212, 255, 0.3);
    }
    .stAppDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATABASE HELPERS ---
USERS_FILE = "users.json"
CHATS_FILE = "ai_chats.json"
MESSAGES_FILE = "user_messages.json"

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_data(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f)
        return default
    with open(file, "r") as f:
        try: return json.load(f)
        except: return default

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f)

db_users = load_data(USERS_FILE, {})
db_chats = load_data(CHATS_FILE, {})
db_messages = load_data(MESSAGES_FILE, {})

# --- 5. SESSION STATE & LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    url_token = st.query_params.get("token")
    if url_token:
        for username, data in db_users.items():
            if data.get("token") == url_token:
                st.session_state.logged_in = True
                st.session_state.user = username
                break

if "current_page" not in st.session_state: st.session_state.current_page = "Dashboard"
if "active_chat" not in st.session_state: st.session_state.active_chat = "New Chat"
if "processing" not in st.session_state: st.session_state.processing = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🚀 LAKSHMEEYAM AI</h1>", unsafe_allow_html=True)
    col_l, _, col_r = st.columns([1.5, 0.1, 1])
    with col_l:
        st.markdown("""
        <div class='main-box'>
            <h2 style='color: #00d4ff;'>👨‍💻 About the Creator</h2>
            <p><b>Lakshmeeyam AI</b> is a digital ecosystem built as a custom hobby project.</p>
            <hr style='border-color: #333;'>
            <ul>
                <li><b>Custom AI:</b> Powered by Groq Llama 3.1</li>
                <li><b>Status:</b> Beta Version</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_r:
        st.markdown("<div class='main-box'>", unsafe_allow_html=True)
        st.subheader("🔐 Access Portal")
        t1, t2 = st.tabs(["Login", "Sign Up"])
        with t1:
            u_in = st.text_input("Username")
            p_in = st.text_input("Password", type="password")
            if st.button("Log In", use_container_width=True):
                if u_in in db_users:
                    stored_pw = db_users[u_in]["password"]
                    if stored_pw == p_in or stored_pw == hash_password(p_in):
                        new_token = secrets.token_hex(16)
                        db_users[u_in]["token"] = new_token
                        save_data(USERS_FILE, db_users)
                        st.session_state.logged_in = True
                        st.session_state.user = u_in
                        st.query_params["token"] = new_token
                        if u_in not in db_chats: db_chats[u_in] = {"New Chat": []}
                        save_data(CHATS_FILE, db_chats)
                        st.rerun()
                st.error("❌ Invalid Credentials")
        with t2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Create Account", use_container_width=True):
                if nu and np and nu not in db_users:
                    db_users[nu] = {"password": hash_password(np), "friends": [], "requests": [], "token": ""}
                    save_data(USERS_FILE, db_users)
                    st.success("Account Ready!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. NAVIGATION & PAGES ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#00d4ff;'>{st.session_state.user}</h2>", unsafe_allow_html=True)
    if st.button("🏠 Dashboard"): st.session_state.current_page = "Dashboard"
    if st.button("🤖 AI Lab"): st.session_state.current_page = "AI Chat"
    if st.button("💬 Messaging"): st.session_state.current_page = "Messages"
    if st.button("🌤️ Weather"): st.session_state.current_page = "Weather"
    st.write("---")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.query_params.clear()
        st.rerun()

if st.session_state.current_page == "Dashboard":
    st.title("📱 Tech Dashboard")
    st.write("Welcome to the Lakshmeeyam digital ecosystem.")

elif st.session_state.current_page == "AI Chat":
    st.title("🤖 AI Lab")
    client = Groq(api_key="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")
    # Chat logic continues here...
    st.info("AI Lab is active.")

elif st.session_state.current_page == "Messages":
    st.title("📫 Communication Center")

elif st.session_state.current_page == "Weather":
    st.title("🌤️ SkyView Weather")
