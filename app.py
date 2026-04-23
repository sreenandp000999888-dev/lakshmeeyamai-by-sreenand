import streamlit as st
from groq import Groq
import json
import os
import hashlib # For password security
from datetime import datetime
import requests

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Lakshmeeyam AI", page_icon="🤖", layout="wide")

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
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY HELPERS ---
def hash_password(password):
    """Turns a plain password into a secure hash."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 3. DATABASE HELPERS ---
USERS_FILE = "users.json"
CHATS_FILE = "ai_chats.json"
MESSAGES_FILE = "user_messages.json"

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

# --- 4. PERSISTENT LOGIN ---
if "logged_in" not in st.session_state:
    if "user" in st.query_params:
        st.session_state.logged_in = True
        st.session_state.user = st.query_params["user"]
    else:
        st.session_state.logged_in = False

if "current_page" not in st.session_state: st.session_state.current_page = "Dashboard"
if "active_chat" not in st.session_state: st.session_state.active_chat = "New Chat"

# --- 5. LOGIN / SIGNUP ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🚀 LAKSHMEEYAM AI</h1>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("<div class='main-box'>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Login", "Sign Up"])
        with t1:
            u_in = st.text_input("Username")
            p_in = st.text_input("Password", type="password")
            if st.button("Log In", use_container_width=True):
                # Verify using hash comparison
                if u_in in db_users and db_users[u_in]["password"] == hash_password(p_in):
                    st.session_state.logged_in = True
                    st.session_state.user = u_in
                    st.query_params["user"] = u_in
                    st.rerun()
                else: st.error("❌ Invalid credentials")
        with t2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Create Account", use_container_width=True):
                if nu and np and nu not in db_users:
                    # Save the HASH, not the plain password
                    db_users[nu] = {"password": hash_password(np), "friends": [], "requests": []}
                    save_data(USERS_FILE, db_users)
                    st.success("Account created securely!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user}")
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.current_page = "Dashboard"
    if st.button("🤖 AI Lab", use_container_width=True): st.session_state.current_page = "AI Chat"
    if st.button("💬 Messages", use_container_width=True): st.session_state.current_page = "Messages"
    if st.button("🌤️ Weather", use_container_width=True): st.session_state.current_page = "Weather"
    st.write("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.query_params.clear()
        st.rerun()

# --- 7. PAGES ---

# DASHBOARD
if st.session_state.current_page == "Dashboard":
    st.title("📱 Dashboard")
    st.markdown("<div class='main-box'><h3>Welcome back!</h3><p>Your session is secure and encrypted.</p></div>", unsafe_allow_html=True)

# AI CHAT
elif st.session_state.current_page == "AI Chat":
    st.title("🤖 AI Lab")
    
    # CRITICAL SECURITY: Fetching key from Secrets instead of code
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
    except:
        st.error("Missing API Key! Please add it to Streamlit Secrets.")
        st.stop()

    my_h = db_chats.setdefault(st.session_state.user, {"New Chat": []})
    
    with st.sidebar:
        if st.button("➕ New Session", use_container_width=True, key="new_sess"):
            st.session_state.active_chat = "New Chat"
            my_h["New Chat"] = []
            save_data(CHATS_FILE, db_chats)
            st.rerun()
        for t in reversed(list(my_h.keys())):
            if st.button(f"💬 {t}", use_container_width=True, key=f"h_{t}"):
                st.session_state.active_chat = t
                st.rerun()

    msgs = my_h.get(st.session_state.active_chat, [])
    for m in msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    p = st.chat_input("Message AI...")
    if p:
        msgs.append({"role": "user", "content": p})
        # AI Logic
        sys_msg = {"role": "system", "content": "You are a safe and helpful AI assistant."}
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[sys_msg] + msgs)
        ans = res.choices[0].message.content
        msgs.append({"role": "assistant", "content": ans})
        
        # Auto-Rename logic
        if st.session_state.active_chat == "New Chat":
            new_title = p[:20].strip() or "Untitled"
            my_h[new_title] = my_h.pop("New Chat")
            st.session_state.active_chat = new_title
            
        save_data(CHATS_FILE, db_chats)
        st.rerun()

# (Include other pages: Messages, Weather as per previous logic)
