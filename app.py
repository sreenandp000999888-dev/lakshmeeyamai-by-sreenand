import streamlit as st
from groq import Groq
import secrets
import hashlib
import requests
from datetime import datetime, timedelta
from supabase import create_client, Client

# ── Optional packages (install via requirements.txt) ──────────────────────────
try:
    from extra_streamlit_components import CookieManager
    _COOKIES_OK = True
except ImportError:
    _COOKIES_OK = False

try:
    from streamlit_js_eval import get_geolocation
    _GEO_OK = True
except ImportError:
    _GEO_OK = False
# ──────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────
# 1. PAGE CONFIG & STYLING
# ─────────────────────────────────────────
st.set_page_config(page_title="Lakshmeeyam AI", page_icon="🚀", layout="wide")

# ── Google Analytics 4 via streamlit-analytics2 ───────────────────────────────
# Injects GA4 into the real page <head> (not an iframe) so Google detects it.
# Add to requirements.txt: streamlit-analytics2
try:
    import streamlit_analytics2 as streamlit_analytics
    streamlit_analytics.start_tracking(
        ga4_id="G-98JQK90KWX",
        verbose=False,
        unsafe_password=""
    )
    _ANALYTICS_OK = True
except Exception:
    _ANALYTICS_OK = False
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 50%, #0a0a1a 100%);
    min-height: 100vh;
}

.main-box {
    background: rgba(0, 212, 255, 0.05);
    padding: 25px;
    border-radius: 16px;
    border: 1px solid rgba(0, 212, 255, 0.3);
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.1), inset 0 0 20px rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
}

.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff, #7b2fff, #00d4ff);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    animation: shimmer 3s infinite;
    margin-bottom: 0.2rem;
}

.hero-sub {
    text-align: center;
    color: rgba(0,212,255,0.6);
    font-size: 1rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

@keyframes shimmer { 0%{background-position:0%} 50%{background-position:100%} 100%{background-position:0%} }

.stat-card {
    background: rgba(0,212,255,0.07);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
}

.stat-number {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    color: #00d4ff;
}

.chat-bubble-user {
    background: linear-gradient(135deg, #1a1a3e, #2a1a5e);
    border: 1px solid rgba(123,47,255,0.4);
    border-radius: 12px 12px 2px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    color: white;
    max-width: 80%;
    margin-left: auto;
}

.chat-bubble-ai {
    background: linear-gradient(135deg, #0a2a3a, #0a1a2e);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 12px 12px 12px 2px;
    padding: 12px 16px;
    margin: 8px 0;
    color: white;
    max-width: 80%;
}

.stButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,47,255,0.15));
    color: #00d4ff;
    border: 1px solid rgba(0,212,255,0.4);
    border-radius: 8px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 1px;
    transition: all 0.3s;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.3), rgba(123,47,255,0.3));
    border-color: #00d4ff;
    box-shadow: 0 0 15px rgba(0,212,255,0.4);
    transform: translateY(-1px);
}

.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: rgba(0,0,0,0.4) !important;
    color: white !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    border-radius: 8px !important;
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background: rgba(0,212,255,0.05);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 8px;
    color: rgba(255,255,255,0.7);
    font-family: 'Rajdhani', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,212,255,0.15) !important;
    border-color: #00d4ff !important;
    color: #00d4ff !important;
}

[data-testid="stSidebar"] {
    background: rgba(5, 10, 25, 0.95);
    border-right: 1px solid rgba(0,212,255,0.2);
}

.sidebar-logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    color: #00d4ff;
    text-align: center;
    padding: 10px;
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 8px;
    margin-bottom: 15px;
}

.stAppDeployButton { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.weather-card {
    background: linear-gradient(135deg, rgba(0,100,200,0.2), rgba(0,50,100,0.3));
    border: 1px solid rgba(0,150,255,0.4);
    border-radius: 16px;
    padding: 30px;
    text-align: center;
    color: white;
}

.online-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #00ff88;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.gps-btn {
    background: linear-gradient(135deg, rgba(0,255,136,0.15), rgba(0,212,100,0.15)) !important;
    color: #00ff88 !important;
    border: 1px solid rgba(0,255,136,0.4) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 2. SUPABASE CONNECTION
# ─────────────────────────────────────────
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("❌ Could not connect to database. Please check your Supabase secrets (URL and anon key).")
    st.code(str(e))
    st.stop()


# ─────────────────────────────────────────
# 3. COOKIE MANAGER (persistent login)
# ─────────────────────────────────────────
_cookie_manager = None
if _COOKIES_OK:
    try:
        _cookie_manager = CookieManager(key="lakshmeeyam_cookies")
    except Exception:
        _cookie_manager = None

def _get_cookie(name: str):
    if _cookie_manager:
        try:
            return _cookie_manager.get(name)
        except Exception:
            return None
    return None

def _set_cookie(name: str, value: str, days: int = 30):
    if _cookie_manager:
        try:
            _cookie_manager.set(
                name, value,
                expires_at=datetime.now() + timedelta(days=days),
                key=f"set_{name}_{value[:8]}"
            )
        except Exception:
            pass

def _delete_cookie(name: str):
    if _cookie_manager:
        try:
            _cookie_manager.delete(name, key=f"del_{name}")
        except Exception:
            pass


# ─────────────────────────────────────────
# 4. DB HELPER FUNCTIONS
# ─────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username: str):
    try:
        res = supabase.table("users").select("*").eq("username", username).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"DB read error: {e}")
        return None

def save_user(username: str, data: dict):
    try:
        supabase.table("users").upsert({
            "username": username,
            "password": data["password"],
            "token": data.get("token", ""),
            "friends": data.get("friends", []),
            "requests": data.get("requests", [])
        }).execute()
        return True
    except Exception as e:
        st.error(f"DB save error: {e}")
        return False

def get_ai_chats(username: str) -> dict:
    try:
        res = supabase.table("ai_chats").select("*").eq("username", username).execute()
        return {row["chat_title"]: row["messages"] for row in res.data} if res.data else {}
    except:
        return {}

def save_ai_chat(username: str, title: str, messages: list):
    try:
        supabase.table("ai_chats").upsert(
            {"username": username, "chat_title": title, "messages": messages},
            on_conflict="username,chat_title"
        ).execute()
    except Exception as e:
        st.error(f"Chat save error: {e}")

def delete_ai_chat(username: str, title: str):
    try:
        supabase.table("ai_chats").delete().eq("username", username).eq("chat_title", title).execute()
    except:
        pass

def get_messages(chat_id: str) -> list:
    try:
        res = supabase.table("user_messages").select("*").eq("chat_id", chat_id).order("created_at").execute()
        return res.data or []
    except:
        return []

def send_message(chat_id: str, sender: str, text: str):
    try:
        supabase.table("user_messages").insert({
            "chat_id": chat_id, "sender": sender, "text": text
        }).execute()
    except Exception as e:
        st.error(f"Message error: {e}")

# ── Music DB helpers ──────────────────────────────────────────────────────────
def get_liked_songs(username: str) -> list:
    try:
        res = supabase.table("liked_songs").select("*").eq("username", username).order("created_at", desc=True).execute()
        return res.data or []
    except:
        return []

def like_song(username: str, video_id: str, title: str, artist: str, thumbnail: str):
    try:
        supabase.table("liked_songs").upsert(
            {"username": username, "video_id": video_id, "title": title, "artist": artist, "thumbnail": thumbnail},
            on_conflict="username,video_id"
        ).execute()
    except:
        pass

def unlike_song(username: str, video_id: str):
    try:
        supabase.table("liked_songs").delete().eq("username", username).eq("video_id", video_id).execute()
    except:
        pass

def get_playlists(username: str) -> list:
    try:
        res = supabase.table("playlists").select("*").eq("username", username).execute()
        return res.data or []
    except:
        return []

def save_playlist(username: str, name: str, songs: list):
    try:
        supabase.table("playlists").upsert(
            {"username": username, "name": name, "songs": songs},
            on_conflict="username,name"
        ).execute()
    except:
        pass

def delete_playlist(username: str, name: str):
    try:
        supabase.table("playlists").delete().eq("username", username).eq("name", name).execute()
    except:
        pass

def get_jam(username: str) -> dict:
    """Get active jam sent TO this user."""
    try:
        res = supabase.table("jams").select("*").eq("guest", username).eq("active", True).order("created_at", desc=True).limit(1).execute()
        return res.data[0] if res.data else {}
    except:
        return {}

def send_jam(host: str, guest: str, video_id: str, title: str, thumbnail: str):
    try:
        # Deactivate old jams from this host to this guest
        supabase.table("jams").update({"active": False}).eq("host", host).eq("guest", guest).execute()
        supabase.table("jams").insert({
            "host": host, "guest": guest,
            "video_id": video_id, "title": title,
            "thumbnail": thumbnail, "active": True
        }).execute()
    except:
        pass

def youtube_search(query: str, max_results: int = 12) -> list:
    try:
        api_key = st.secrets.get("YOUTUBE_API_KEY", "")
        if not api_key:
            return []
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet", "q": query + " music",
                "type": "video", "videoCategoryId": "10",
                "maxResults": max_results, "key": api_key,
                "safeSearch": "moderate"
            },
            timeout=10
        ).json()
        return resp.get("items", [])
    except:
        return []

def youtube_trending(max_results: int = 12, access_token: str = "") -> list:
    try:
        params = {
            "part": "snippet", "chart": "mostPopular",
            "videoCategoryId": "10", "maxResults": max_results,
            "regionCode": "IN"
        }
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        else:
            params["key"] = st.secrets.get("YOUTUBE_API_KEY", "")
            if not params["key"]:
                return []
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params=params, headers=headers, timeout=10
        ).json()
        items = []
        for item in resp.get("items", []):
            items.append({
                "id": {"videoId": item["id"]},
                "snippet": item["snippet"]
            })
        return items
    except:
        return []

# ── Google OAuth helpers ───────────────────────────────────────────────────────
import urllib.parse

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
YT_API_BASE      = "https://www.googleapis.com/youtube/v3"
REDIRECT_URI     = "https://lakshmeeyamai.streamlit.app"
SCOPES = " ".join([
    "https://www.googleapis.com/auth/youtube.readonly",
    "openid", "email", "profile"
])

def get_google_auth_url() -> str:
    client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": st.session_state.user
    }
    return GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)

def exchange_code_for_tokens(code: str) -> dict:
    client_id     = st.secrets.get("GOOGLE_CLIENT_ID", "")
    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    resp = requests.post(GOOGLE_TOKEN_URL, data={
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }, timeout=10)
    return resp.json()

def refresh_google_token(refresh_token: str) -> str:
    client_id     = st.secrets.get("GOOGLE_CLIENT_ID", "")
    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    resp = requests.post(GOOGLE_TOKEN_URL, data={
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }, timeout=10)
    data = resp.json()
    return data.get("access_token", "")

def save_google_tokens(username: str, access_token: str, refresh_token: str, email: str = ""):
    try:
        supabase.table("google_tokens").upsert({
            "username": username,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "email": email
        }, on_conflict="username").execute()
    except:
        pass

def get_google_tokens(username: str) -> dict:
    try:
        res = supabase.table("google_tokens").select("*").eq("username", username).execute()
        return res.data[0] if res.data else {}
    except:
        return {}

def delete_google_tokens(username: str):
    try:
        supabase.table("google_tokens").delete().eq("username", username).execute()
    except:
        pass

def yt_get(endpoint: str, params: dict, access_token: str) -> dict:
    """Make an authenticated YouTube Data API call."""
    try:
        resp = requests.get(
            YT_API_BASE + endpoint,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        return resp.json()
    except:
        return {}

def get_yt_liked_songs(access_token: str, max_results: int = 50) -> list:
    data = yt_get("/videos", {
        "part": "snippet,contentDetails",
        "myRating": "like",
        "maxResults": max_results,
        "videoCategoryId": "10"
    }, access_token)
    items = []
    for item in data.get("items", []):
        items.append({
            "id": {"videoId": item["id"]},
            "snippet": item["snippet"]
        })
    return items

def get_yt_playlists(access_token: str) -> list:
    data = yt_get("/playlists", {
        "part": "snippet,contentDetails",
        "mine": "true",
        "maxResults": 50
    }, access_token)
    return data.get("items", [])

def get_yt_playlist_items(access_token: str, playlist_id: str, max_results: int = 50) -> list:
    data = yt_get("/playlistItems", {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": max_results
    }, access_token)
    items = []
    for item in data.get("items", []):
        vid_id = item["snippet"].get("resourceId", {}).get("videoId", "")
        if vid_id:
            items.append({
                "id": {"videoId": vid_id},
                "snippet": item["snippet"]
            })
    return items

def get_yt_subscriptions(access_token: str, max_results: int = 20) -> list:
    data = yt_get("/subscriptions", {
        "part": "snippet",
        "mine": "true",
        "maxResults": max_results,
        "order": "relevance"
    }, access_token)
    return data.get("items", [])

def get_yt_recommendations(access_token: str, max_results: int = 12) -> list:
    """Get personalized feed — activities from subscribed channels."""
    data = yt_get("/activities", {
        "part": "snippet,contentDetails",
        "home": "true",
        "maxResults": max_results
    }, access_token)
    items = []
    for item in data.get("items", []):
        cd = item.get("contentDetails", {})
        if "upload" in cd:
            vid_id = cd["upload"].get("videoId", "")
            if vid_id:
                items.append({
                    "id": {"videoId": vid_id},
                    "snippet": item["snippet"]
                })
    return items

def yt_search_authed(query: str, access_token: str, max_results: int = 12) -> list:
    data = yt_get("/search", {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoCategoryId": "10",
        "maxResults": max_results
    }, access_token)
    return data.get("items", [])

def get_yt_user_info(access_token: str) -> dict:
    try:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        return resp.json()
    except:
        return {}
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────
# 5. SESSION STATE DEFAULTS
# ─────────────────────────────────────────
defaults = {
    "logged_in": False,
    "user": "",
    "current_page": "home",
    "active_chat": "New Chat",
    "processing": False,
    "msg_target": None,
    "theme": "cyan",
    "gps_lat": None,
    "gps_lon": None,
    "gps_city": None,
    "gps_country": None,
    "weather_fetched": False,
    # Music player state
    "music_tab": "home",
    "now_playing_id": None,
    "now_playing_title": "",
    "now_playing_artist": "",
    "now_playing_thumb": "",
    "queue": [],
    "music_search_results": [],
    "music_search_query": "",
    "active_playlist_name": None,
    "playlist_add_target": None,
    # Google / YouTube OAuth
    "yt_access_token": "",
    "yt_refresh_token": "",
    "yt_email": "",
    "yt_connected": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────
# 6. PERSISTENT LOGIN CHECK
#    Priority: session → cookie → query param
# ─────────────────────────────────────────
if not st.session_state.logged_in:
    # 6a. Try cookie first (survives tab close)
    cookie_token = _get_cookie("auth_token")
    if cookie_token:
        try:
            res = supabase.table("users").select("*").eq("token", cookie_token).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]["username"]
        except:
            pass

    # 6b. Fallback: URL query param (backward compat)
    if not st.session_state.logged_in:
        url_token = st.query_params.get("token")
        if url_token:
            try:
                res = supabase.table("users").select("*").eq("token", url_token).execute()
                if res.data:
                    st.session_state.logged_in = True
                    st.session_state.user = res.data[0]["username"]
                    # Upgrade: also write to cookie so future visits work without URL param
                    _set_cookie("auth_token", url_token)
            except:
                pass


# ─────────────────────────────────────────
# 6c. GOOGLE OAUTH CALLBACK HANDLER
#     Runs on every page load — picks up ?code= from Google redirect
# ─────────────────────────────────────────
_oauth_code = st.query_params.get("code", "")
_oauth_state = st.query_params.get("state", "")
if _oauth_code and st.session_state.logged_in:
    # Exchange the auth code for tokens (only once)
    if not st.session_state.yt_connected:
        with st.spinner("🔗 Connecting your Google account…"):
            token_data = exchange_code_for_tokens(_oauth_code)
            if "access_token" in token_data:
                access_token  = token_data["access_token"]
                refresh_token = token_data.get("refresh_token", "")
                user_info = get_yt_user_info(access_token)
                email = user_info.get("email", "")
                save_google_tokens(st.session_state.user, access_token, refresh_token, email)
                st.session_state.yt_access_token  = access_token
                st.session_state.yt_refresh_token = refresh_token
                st.session_state.yt_email         = email
                st.session_state.yt_connected     = True
                # Clean URL — remove code & state params
                st.query_params.clear()
                if st.session_state.get("auth_token_val"):
                    st.query_params["token"] = st.session_state.auth_token_val
                st.session_state.current_page = "Music"
                st.rerun()

# If already logged in, try to restore YT tokens from Supabase
if st.session_state.logged_in and not st.session_state.yt_connected:
    _saved = get_google_tokens(st.session_state.user)
    if _saved and _saved.get("access_token"):
        # Try refreshing the token in case it expired
        new_at = refresh_google_token(_saved.get("refresh_token", ""))
        if new_at:
            _saved["access_token"] = new_at
            save_google_tokens(
                st.session_state.user,
                new_at, _saved.get("refresh_token",""), _saved.get("email","")
            )
        st.session_state.yt_access_token  = _saved.get("access_token", "")
        st.session_state.yt_refresh_token = _saved.get("refresh_token", "")
        st.session_state.yt_email         = _saved.get("email", "")
        st.session_state.yt_connected     = bool(st.session_state.yt_access_token)

# ─────────────────────────────────────────
# 7. LOGIN / SIGNUP PAGE
# ─────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("<div class='hero-title'>🚀 LAKSHMEEYAM AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Next-Gen AI Platform by Sreenand</div>", unsafe_allow_html=True)

    col_l, spacer, col_r = st.columns([1.4, 0.1, 1])

    with col_l:
        st.markdown("""
        <div class='main-box'>
            <h2 style='color:#00d4ff; font-family:Orbitron,sans-serif;'>👨‍💻 About</h2>
            <p style='color:rgba(255,255,255,0.8);'>
                <b>Lakshmeeyam AI</b> is a full-stack AI ecosystem built by 
                <span style='color:#00d4ff;'><b>Sreenand</b></span>, a 14-year-old developer from India.
            </p>
            <p style='color:rgba(255,255,255,0.6); font-size:0.9rem;'>
                A hobby project combining AI, social networking, and real-time data.
            </p>
            <hr style='border-color: rgba(0,212,255,0.2); margin: 15px 0;'>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>
                <div style='background:rgba(0,212,255,0.08); padding:12px; border-radius:8px; border:1px solid rgba(0,212,255,0.2);'>
                    <div style='color:#00d4ff; font-size:1.4rem;'>🤖</div>
                    <div style='color:white; font-weight:600;'>AI Chat</div>
                    <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>Llama 3.1 via Groq</div>
                </div>
                <div style='background:rgba(123,47,255,0.08); padding:12px; border-radius:8px; border:1px solid rgba(123,47,255,0.2);'>
                    <div style='color:#7b2fff; font-size:1.4rem;'>💬</div>
                    <div style='color:white; font-weight:600;'>Messaging</div>
                    <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>Real-time DMs</div>
                </div>
                <div style='background:rgba(0,255,136,0.08); padding:12px; border-radius:8px; border:1px solid rgba(0,255,136,0.2);'>
                    <div style='color:#00ff88; font-size:1.4rem;'>🌤️</div>
                    <div style='color:white; font-weight:600;'>Weather</div>
                    <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>GPS + live forecasts</div>
                </div>
                <div style='background:rgba(255,165,0,0.08); padding:12px; border-radius:8px; border:1px solid rgba(255,165,0,0.2);'>
                    <div style='color:#ffa500; font-size:1.4rem;'>🔐</div>
                    <div style='color:white; font-weight:600;'>Secure</div>
                    <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>Hashed passwords</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("<div class='main-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#00d4ff; font-family:Orbitron,sans-serif;'>🔐 Access Portal</h3>", unsafe_allow_html=True)

        t1, t2 = st.tabs(["🔑 Login", "✨ Sign Up"])

        with t1:
            u_in = st.text_input("Username", key="login_user", placeholder="Enter username")
            p_in = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            remember = st.checkbox("Stay logged in (persists after closing tab)", value=True)

            if st.button("LOGIN →", use_container_width=True, key="login_btn"):
                if u_in and p_in:
                    user_data = get_user(u_in)
                    if user_data:
                        stored = user_data["password"]
                        if stored == p_in or stored == hash_password(p_in):
                            new_token = secrets.token_hex(16) if remember else ""
                            user_data["token"] = new_token
                            save_user(u_in, user_data)
                            st.session_state.logged_in = True
                            st.session_state.user = u_in
                            if remember:
                                # ✅ Save to COOKIE (survives tab close)
                                _set_cookie("auth_token", new_token, days=30)
                                # Also set query param for backward compat
                                st.query_params["token"] = new_token
                            st.success("✅ Welcome back!")
                            st.rerun()
                        else:
                            st.error("❌ Wrong password")
                    else:
                        st.error("❌ User not found")
                else:
                    st.warning("Please fill in both fields")

        with t2:
            nu = st.text_input("Choose Username", key="reg_user", placeholder="Pick a username")
            np = st.text_input("Choose Password", type="password", key="reg_pass", placeholder="Min 6 characters")
            np2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Repeat password")

            if st.button("CREATE ACCOUNT →", use_container_width=True, key="reg_btn"):
                if nu and np and np2:
                    if np != np2:
                        st.error("❌ Passwords don't match")
                    elif len(np) < 6:
                        st.error("❌ Password too short (min 6 chars)")
                    elif get_user(nu):
                        st.error("❌ Username already taken")
                    else:
                        new_user = {
                            "password": hash_password(np),
                            "friends": [], "requests": [], "token": ""
                        }
                        if save_user(nu, new_user):
                            st.success("🎉 Account created! Please login.")
                        else:
                            st.error("Failed to create account. Check Supabase connection.")
                else:
                    st.warning("Please fill all fields")

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────
# 8. SIDEBAR (logged in)
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div class='sidebar-logo'>⚡ LAKSHMEEYAM AI</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:rgba(255,255,255,0.5); text-align:center; font-size:0.85rem;'><span class='online-dot'></span>{st.session_state.user}</p>", unsafe_allow_html=True)

    pages = [
        ("🏠", "Home", "home"),
        ("🤖", "AI Chat", "AI Chat"),
        ("💬", "Messages", "Messages"),
        ("🎵", "Music", "Music"),
        ("🌤️", "Weather", "Weather"),
    ]

    for icon, label, page_key in pages:
        if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{page_key}"):
            st.session_state.current_page = page_key
            st.rerun()

    st.markdown("---")

    # AI Chat history in sidebar
    if st.session_state.current_page == "AI Chat":
        if st.button("➕  New Chat", use_container_width=True):
            st.session_state.active_chat = "New Chat"
            st.rerun()

        chats = get_ai_chats(st.session_state.user)
        if chats:
            st.markdown("<p style='color:rgba(255,255,255,0.4); font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;'>Chat History</p>", unsafe_allow_html=True)
            for title in reversed(list(chats.keys())):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    if st.button(f"💬 {title[:18]}{'…' if len(title)>18 else ''}", use_container_width=True, key=f"ch_{title}"):
                        st.session_state.active_chat = title
                        st.rerun()
                with col_b:
                    if st.button("🗑", key=f"del_{title}"):
                        delete_ai_chat(st.session_state.user, title)
                        if st.session_state.active_chat == title:
                            st.session_state.active_chat = "New Chat"
                        st.rerun()

    st.markdown("---")
    if st.button("🔐  Logout", use_container_width=True):
        user_data = get_user(st.session_state.user)
        if user_data:
            user_data["token"] = ""
            save_user(st.session_state.user, user_data)
        # ✅ Clear cookie on logout
        _delete_cookie("auth_token")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.query_params.clear()
        st.rerun()


# ─────────────────────────────────────────
# 9. HOME PAGE
# ─────────────────────────────────────────
if st.session_state.current_page == "home":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>🏠 Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:rgba(255,255,255,0.5);'>Welcome back, <span style='color:#00d4ff;'>{st.session_state.user}</span></p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (c1, "🤖", "AI Lab", "Llama 3.1 • Multi-session chat • Auto-titled history", "#00d4ff", "Open AI", "AI Chat"),
        (c2, "💬", "Messaging", "DMs • Friends • Music Jam sharing", "#7b2fff", "Open Messages", "Messages"),
        (c3, "🎵", "Music", "YouTube Music • Search • Playlists • Jam", "#ff4444", "Open Music", "Music"),
        (c4, "🌤️", "SkyView", "GPS live weather • Temperature • 7-Day Forecast", "#00ff88", "Open Weather", "Weather"),
    ]

    for col, icon, title, desc, color, btn, page in cards:
        with col:
            st.markdown(f"""
            <div class='main-box' style='border-color:{color}40; text-align:center; min-height:160px;'>
                <div style='font-size:2.5rem;'>{icon}</div>
                <h3 style='color:{color}; font-family:Orbitron,sans-serif; margin:8px 0;'>{title}</h3>
                <p style='color:rgba(255,255,255,0.5); font-size:0.85rem;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(btn, use_container_width=True, key=f"home_{page}"):
                st.session_state.current_page = page
                st.rerun()


# ─────────────────────────────────────────
# 10. AI CHAT PAGE
# ─────────────────────────────────────────
elif st.session_state.current_page == "AI Chat":
    try:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        st.error("❌ Groq API key missing. Add GROQ_API_KEY to your Streamlit secrets.")
        st.stop()

    st.markdown("<div class='hero-title' style='font-size:1.8rem;'>🤖 AI Chat</div>", unsafe_allow_html=True)

    col_m1, col_m2 = st.columns([3, 1])
    with col_m2:
        model_choice = st.selectbox("Model", [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ], label_visibility="collapsed")
    with col_m1:
        st.markdown(f"<p style='color:rgba(255,255,255,0.4); padding-top:8px;'>Active model: <span style='color:#00d4ff;'>{model_choice}</span></p>", unsafe_allow_html=True)

    user_history = get_ai_chats(st.session_state.user)
    current_msgs = user_history.get(st.session_state.active_chat, [])

    chat_container = st.container()
    with chat_container:
        if not current_msgs:
            st.markdown("""
            <div style='text-align:center; padding:60px 20px; color:rgba(255,255,255,0.3);'>
                <div style='font-size:3rem;'>🤖</div>
                <p>Start a conversation with Lakshmeeyam AI</p>
                <p style='font-size:0.8rem;'>Powered by Groq • Ultra-fast inference</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for m in current_msgs:
                with st.chat_message(m["role"]):
                    st.write(m["content"])

    prompt = st.chat_input("Ask me anything...")
    if prompt:
        current_msgs.append({"role": "user", "content": prompt})
        st.session_state.processing = True
        save_ai_chat(st.session_state.user, st.session_state.active_chat, current_msgs)
        st.rerun()

    if st.session_state.processing and current_msgs:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # ✅ UPDATED SYSTEM PROMPT — Sreenand identity baked in
                system_prompt = {
                    "role": "system",
                    "content": (
                        "You are Lakshmeeyam AI, a helpful and intelligent assistant. "
                        "You were created by Sreenand. "
                        "If anyone asks who created you, who made you, or who your creator is, "
                        "you must answer: 'I was created by Sreenand.' "
                        "If anyone asks who Sreenand is, you must answer: "
                        "'Sreenand is a 14-year-old boy and a brilliant young developer from India "
                        "who built Lakshmeeyam AI as a passion project.' "
                        "Be concise, friendly, and insightful. "
                        "Format responses with markdown when helpful."
                    )
                }
                try:
                    response = groq_client.chat.completions.create(
                        model=model_choice,
                        messages=[system_prompt] + current_msgs,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    answer = response.choices[0].message.content
                except Exception as e:
                    answer = f"⚠️ Error: {e}"

                current_msgs.append({"role": "assistant", "content": answer})

                active_title = st.session_state.active_chat
                if active_title == "New Chat" and len(current_msgs) >= 2:
                    try:
                        title_res = groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": "Generate a very short 2-3 word title for this conversation. Reply with ONLY the title, nothing else."},
                                {"role": "user", "content": current_msgs[0]["content"]}
                            ],
                            max_tokens=20
                        )
                        new_title = title_res.choices[0].message.content.strip().strip('"').strip("'")
                        if new_title:
                            delete_ai_chat(st.session_state.user, "New Chat")
                            active_title = new_title
                            st.session_state.active_chat = new_title
                    except:
                        pass

                save_ai_chat(st.session_state.user, active_title, current_msgs)
                st.session_state.processing = False
                st.rerun()


# ─────────────────────────────────────────
# 11. MESSAGES PAGE (upgraded)
# ─────────────────────────────────────────
elif st.session_state.current_page == "Messages":
    import streamlit.components.v1 as _comp

    st.markdown("<div class='hero-title' style='font-size:1.8rem;'>💬 Messaging</div>", unsafe_allow_html=True)

    u_data = get_user(st.session_state.user)
    if not u_data:
        st.error("Could not load user data.")
        st.stop()

    friends_list = u_data.get("friends", [])

    # ── Check for incoming jams ───────────────────────────────────────────────
    incoming_jam = get_jam(st.session_state.user)
    if incoming_jam:
        host = incoming_jam.get("host", "")
        jam_vid = incoming_jam.get("video_id", "")
        jam_title = incoming_jam.get("title", "Unknown")
        jam_thumb = incoming_jam.get("thumbnail", "")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(255,68,68,0.15),rgba(123,47,255,0.15));
        border:1px solid rgba(255,68,68,0.5); border-radius:14px; padding:16px;
        display:flex; align-items:center; gap:14px; margin-bottom:18px;'>
            <img src='{jam_thumb}' style='width:60px; height:45px; border-radius:6px; object-fit:cover;'/>
            <div>
                <div style='color:#ff4444; font-weight:700; font-size:0.9rem;'>🎵 {host} is jamming with you!</div>
                <div style='color:white; font-size:0.85rem;'>{jam_title}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎵 Join Jam → Open Music", key="join_jam_btn"):
            st.session_state.now_playing_id = jam_vid
            st.session_state.now_playing_title = jam_title
            st.session_state.now_playing_thumb = jam_thumb
            st.session_state.current_page = "Music"
            st.session_state.music_tab = "jam"
            st.rerun()

    t_chat, t_friends, t_requests = st.tabs(["💬 Chats", "👥 Friends", "📨 Requests"])

    # ── CHATS TAB ─────────────────────────────────────────────────────────────
    with t_chat:
        if not friends_list:
            st.markdown("""
            <div style='text-align:center; padding:60px; color:rgba(255,255,255,0.3);'>
                <div style='font-size:3rem;'>💬</div>
                <p>Add friends first to start chatting</p>
            </div>""", unsafe_allow_html=True)
        else:
            left, right = st.columns([1, 3])
            with left:
                st.markdown("<p style='color:rgba(255,255,255,0.4); font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>Conversations</p>", unsafe_allow_html=True)
                for f in friends_list:
                    active = st.session_state.get("msg_target") == f
                    cid = "_".join(sorted([st.session_state.user, f]))
                    msgs = get_messages(cid)
                    last_msg = msgs[-1]["text"][:20] + "…" if msgs else "Say hi! 👋"
                    badge_color = "#00d4ff" if active else "rgba(255,255,255,0.15)"
                    border_color = "#00d4ff" if active else "rgba(255,255,255,0.1)"
                    st.markdown(f"""
                    <div style='background:{badge_color}20; border:1px solid {border_color};
                    border-radius:10px; padding:10px 12px; margin-bottom:6px; cursor:pointer;'>
                        <div style='color:white; font-weight:600;'>{"🟢" if active else "👤"} {f}</div>
                        <div style='color:rgba(255,255,255,0.4); font-size:0.75rem; margin-top:2px;'>{last_msg}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"Open chat", key=f"dm_{f}", use_container_width=True):
                        st.session_state.msg_target = f
                        st.rerun()

            with right:
                dest = st.session_state.get("msg_target")
                if dest:
                    cid = "_".join(sorted([st.session_state.user, dest]))
                    # Header with jam button
                    hcol1, hcol2 = st.columns([3, 1])
                    with hcol1:
                        st.markdown(f"<h4 style='color:#00d4ff; margin:0;'>💬 {dest}</h4>", unsafe_allow_html=True)
                    with hcol2:
                        if st.session_state.now_playing_id:
                            if st.button("🎵 Share Jam", use_container_width=True, key="share_jam_msg"):
                                send_jam(
                                    st.session_state.user, dest,
                                    st.session_state.now_playing_id,
                                    st.session_state.now_playing_title,
                                    st.session_state.now_playing_thumb
                                )
                                st.success(f"🎵 Jam shared with {dest}!")

                    # Messages
                    messages = get_messages(cid)
                    msg_box = st.container()
                    with msg_box:
                        if not messages:
                            st.markdown(f"<div style='text-align:center; padding:40px; color:rgba(255,255,255,0.3);'>"
                                        f"<div style='font-size:2rem;'>👋</div>"
                                        f"<p>Start your conversation with {dest}</p></div>",
                                        unsafe_allow_html=True)
                        else:
                            for m in messages:
                                is_me = m["sender"] == st.session_state.user
                                ts = m.get("created_at", "")[:16].replace("T", " ") if m.get("created_at") else ""
                                align = "flex-end" if is_me else "flex-start"
                                bubble_bg = "linear-gradient(135deg,#1a1a3e,#2a1a5e)" if is_me else "linear-gradient(135deg,#0a2a3a,#0a1a2e)"
                                border = "rgba(123,47,255,0.4)" if is_me else "rgba(0,212,255,0.3)"
                                radius = "12px 12px 2px 12px" if is_me else "12px 12px 12px 2px"
                                st.markdown(f"""
                                <div style='display:flex; justify-content:{align}; margin:6px 0;'>
                                    <div style='background:{bubble_bg}; border:1px solid {border};
                                    border-radius:{radius}; padding:10px 14px; max-width:70%;'>
                                        <div style='color:white; font-size:0.95rem;'>{m["text"]}</div>
                                        <div style='color:rgba(255,255,255,0.3); font-size:0.7rem; margin-top:4px; text-align:{"right" if is_me else "left"};'>{ts}</div>
                                    </div>
                                </div>""", unsafe_allow_html=True)

                    txt = st.chat_input(f"Message {dest}…")
                    if txt:
                        send_message(cid, st.session_state.user, txt)
                        st.rerun()
                else:
                    st.markdown("""
                    <div style='text-align:center; padding:80px; color:rgba(255,255,255,0.2);'>
                        <div style='font-size:3rem;'>💬</div>
                        <p>Select a conversation on the left</p>
                    </div>""", unsafe_allow_html=True)

    # ── FRIENDS TAB ───────────────────────────────────────────────────────────
    with t_friends:
        add_col, list_col = st.columns([1, 1])
        with add_col:
            st.markdown("<h4 style='color:#00d4ff;'>➕ Add Friend</h4>", unsafe_allow_html=True)
            target = st.text_input("Username to add", placeholder="Enter exact username", key="friend_search")
            if st.button("Send Request →", use_container_width=True, key="send_req_btn"):
                if target and target != st.session_state.user:
                    target_data = get_user(target)
                    if target_data:
                        reqs = target_data.get("requests", [])
                        friends = target_data.get("friends", [])
                        if st.session_state.user in friends:
                            st.info("Already friends!")
                        elif st.session_state.user in reqs:
                            st.info("Request already sent.")
                        else:
                            reqs.append(st.session_state.user)
                            target_data["requests"] = reqs
                            save_user(target, target_data)
                            st.success(f"✅ Request sent to {target}!")
                    else:
                        st.error("❌ User not found")
                else:
                    st.warning("Enter a valid username")

        with list_col:
            st.markdown("<h4 style='color:#00ff88;'>👥 Your Friends</h4>", unsafe_allow_html=True)
            if not friends_list:
                st.markdown("<p style='color:rgba(255,255,255,0.4);'>No friends yet.</p>", unsafe_allow_html=True)
            else:
                for f in friends_list:
                    fc1, fc2 = st.columns([3, 1])
                    with fc1:
                        st.markdown(f"""
                        <div style='background:rgba(0,255,136,0.08); border:1px solid rgba(0,255,136,0.2);
                        border-radius:8px; padding:10px 12px;'>
                            <span style='color:white; font-weight:600;'>👤 {f}</span>
                        </div>""", unsafe_allow_html=True)
                    with fc2:
                        if st.button("Chat", key=f"goto_{f}", use_container_width=True):
                            st.session_state.msg_target = f
                            st.session_state.current_page = "Messages"
                            st.rerun()

    # ── REQUESTS TAB ──────────────────────────────────────────────────────────
    with t_requests:
        st.markdown("<h4 style='color:#7b2fff;'>📨 Incoming Friend Requests</h4>", unsafe_allow_html=True)
        incoming_reqs = u_data.get("requests", [])
        if not incoming_reqs:
            st.markdown("<p style='color:rgba(255,255,255,0.4);'>No pending requests.</p>", unsafe_allow_html=True)
        else:
            for r in incoming_reqs:
                rc1, rc2, rc3 = st.columns([3, 1, 1])
                with rc1:
                    st.markdown(f"""
                    <div style='background:rgba(123,47,255,0.1); border:1px solid rgba(123,47,255,0.3);
                    border-radius:8px; padding:10px 14px;'>
                        <b style='color:white;'>{r}</b>
                        <span style='color:rgba(255,255,255,0.5); margin-left:8px;'>wants to connect</span>
                    </div>""", unsafe_allow_html=True)
                with rc2:
                    if st.button("✅ Accept", key=f"acc_{r}", use_container_width=True):
                        u_data["friends"].append(r)
                        u_data["requests"].remove(r)
                        save_user(st.session_state.user, u_data)
                        r_data = get_user(r)
                        if r_data and st.session_state.user not in r_data.get("friends", []):
                            r_data["friends"].append(st.session_state.user)
                            save_user(r, r_data)
                        st.rerun()
                with rc3:
                    if st.button("❌ Decline", key=f"dec_{r}", use_container_width=True):
                        u_data["requests"].remove(r)
                        save_user(st.session_state.user, u_data)
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 11b. MUSIC PAGE  — YouTube Music UI
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "Music":
    import streamlit.components.v1 as _comp

    # ── YouTube Music CSS overrides ───────────────────────────────────────────
    st.markdown("""
    <style>
    /* Page background */
    .stApp { background:#0f0f0f !important; }

    /* Hide default streamlit chrome on this page */
    [data-testid="stSidebar"] { background:#212121 !important; border-right:1px solid #333 !important; }

    /* YTM Tab pills */
    .ytm-nav { display:flex; gap:8px; padding:12px 0; flex-wrap:wrap; }
    .ytm-nav a {
        background:#212121; color:#aaa; text-decoration:none;
        padding:7px 18px; border-radius:20px; font-size:0.85rem;
        border:1px solid #333; transition:all 0.2s; cursor:pointer;
    }
    .ytm-nav a.active, .ytm-nav a:hover {
        background:#ff0000; color:#fff; border-color:#ff0000;
    }

    /* YTM Card */
    .ytm-card {
        background:#212121; border-radius:8px; overflow:hidden;
        cursor:pointer; transition:background 0.2s; margin-bottom:4px;
    }
    .ytm-card:hover { background:#2a2a2a; }
    .ytm-card img { width:100%; aspect-ratio:16/9; object-fit:cover; display:block; }
    .ytm-card .ytm-card-info { padding:8px 10px 10px; }
    .ytm-card .ytm-card-title {
        color:#fff; font-size:0.83rem; font-weight:500;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }
    .ytm-card .ytm-card-artist { color:#aaa; font-size:0.75rem; margin-top:2px; }

    /* YTM Song row */
    .ytm-row {
        display:flex; align-items:center; gap:12px; padding:8px 12px;
        border-radius:4px; transition:background 0.15s; cursor:pointer;
    }
    .ytm-row:hover { background:#1e1e1e; }
    .ytm-row img { width:48px; height:48px; border-radius:4px; object-fit:cover; }
    .ytm-row .ytm-row-info { flex:1; min-width:0; }
    .ytm-row .ytm-row-title { color:#fff; font-size:0.88rem; font-weight:500;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .ytm-row .ytm-row-artist { color:#aaa; font-size:0.78rem; }

    /* YTM Search bar */
    .ytm-search-wrap { position:relative; }
    .ytm-search-wrap input {
        width:100%; background:#212121 !important; border:1px solid #333 !important;
        border-radius:24px !important; padding:10px 20px !important;
        color:#fff !important; font-size:0.9rem !important;
    }
    .ytm-search-wrap input:focus { border-color:#ff0000 !important; box-shadow:none !important; }

    /* Player bar */
    .ytm-player-outer {
        background:#212121; border-top:1px solid #333; border-radius:12px;
        padding:0; margin-bottom:12px; overflow:hidden;
    }
    .ytm-player-bar {
        display:flex; align-items:center; gap:14px;
        padding:10px 16px; background:#212121;
    }
    .ytm-player-bar img { width:52px; height:52px; border-radius:4px; object-fit:cover; }
    .ytm-player-info { flex:1; min-width:0; }
    .ytm-player-title { color:#fff; font-weight:600; font-size:0.9rem;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .ytm-player-artist { color:#aaa; font-size:0.8rem; }

    /* Section headings */
    .ytm-section-title {
        color:#fff; font-size:1.05rem; font-weight:600; margin:20px 0 12px;
    }

    /* Pill chip */
    .ytm-chip {
        display:inline-block; background:#212121; color:#aaa;
        border:1px solid #333; border-radius:16px;
        padding:5px 14px; font-size:0.78rem; margin:3px; cursor:pointer;
    }
    .ytm-chip:hover { background:#333; color:#fff; }

    /* Subscription badge */
    .ytm-sub-badge {
        background:#212121; border-radius:50%; overflow:hidden;
        width:64px; height:64px; margin:0 auto 6px;
        border:2px solid #333;
    }
    .ytm-sub-badge img { width:100%; height:100%; object-fit:cover; }

    /* Override Streamlit buttons on music page */
    section[data-testid="stMain"] .stButton > button {
        background:#212121 !important; color:#fff !important;
        border:1px solid #333 !important; border-radius:4px !important;
        font-size:0.82rem !important; letter-spacing:0 !important;
    }
    section[data-testid="stMain"] .stButton > button:hover {
        background:#ff0000 !important; border-color:#ff0000 !important;
        box-shadow:none !important; transform:none !important;
    }

    /* Tab bar */
    .stTabs [data-baseweb="tab-list"] { background:transparent !important; gap:4px !important; }
    .stTabs [data-baseweb="tab"] {
        background:#212121 !important; color:#aaa !important;
        border:1px solid #333 !important; border-radius:20px !important;
        font-size:0.82rem !important; padding:4px 16px !important;
    }
    .stTabs [aria-selected="true"] {
        background:#ff0000 !important; color:#fff !important; border-color:#ff0000 !important;
    }

    /* Text input */
    .stTextInput > div > div > input {
        background:#212121 !important; border:1px solid #444 !important;
        border-radius:24px !important; color:#fff !important;
        padding:10px 18px !important;
    }
    .stTextInput > div > div > input:focus { border-color:#ff0000 !important; }

    /* Section dividers */
    hr { border-color:#333 !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Google OAuth setup ────────────────────────────────────────────────────
    _OAUTH_OK = False
    try:
        from streamlit_oauth import OAuth2Component
        GCLIENT_ID     = st.secrets.get("GOOGLE_CLIENT_ID", "")
        GCLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
        REDIRECT_URI   = st.secrets.get("OAUTH_REDIRECT_URI",
                                        "https://lakshmeeyamai.streamlit.app")
        if GCLIENT_ID and GCLIENT_SECRET:
            _oauth2 = OAuth2Component(
                GCLIENT_ID, GCLIENT_SECRET,
                "https://accounts.google.com/o/oauth2/auth",
                "https://accounts.google.com/o/oauth2/token",
                "https://accounts.google.com/o/oauth2/token",
                "https://oauth2.googleapis.com/revoke"
            )
            _OAUTH_OK = True
    except Exception:
        pass

    # ── YouTube OAuth API helpers ─────────────────────────────────────────────
    def _yt_h():
        tok = st.session_state.get("yt_token", {})
        return {"Authorization": f"Bearer {tok.get('access_token', '')}"}

    def _yt_liked(n=50):
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/videos",
                params={"part":"snippet","myRating":"like",
                        "maxResults":n,"videoCategoryId":"10"},
                headers=_yt_h(), timeout=10).json()
            return [{"id":{"videoId":i["id"]},"snippet":i["snippet"]} for i in r.get("items",[])]
        except: return []

    def _yt_playlists(n=50):
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/playlists",
                params={"part":"snippet,contentDetails","mine":"true","maxResults":n},
                headers=_yt_h(), timeout=10).json()
            return r.get("items", [])
        except: return []

    def _yt_pl_items(pid, n=50):
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/playlistItems",
                params={"part":"snippet","playlistId":pid,"maxResults":n},
                headers=_yt_h(), timeout=10).json()
            items = []
            for item in r.get("items",[]):
                sn = item["snippet"]
                vid = sn.get("resourceId",{}).get("videoId","")
                items.append({"id":{"videoId":vid},"snippet":sn})
            return items
        except: return []

    def _yt_subs(n=50):
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/subscriptions",
                params={"part":"snippet","mine":"true","maxResults":n},
                headers=_yt_h(), timeout=10).json()
            return r.get("items", [])
        except: return []

    def _yt_search(q, n=16):
        try:
            r = requests.get("https://www.googleapis.com/youtube/v3/search",
                params={"part":"snippet","q":q+" music","type":"video",
                        "videoCategoryId":"10","maxResults":n},
                headers=_yt_h(), timeout=10).json()
            return r.get("items", [])
        except: return []

    def _yt_trending(n=16):
        try:
            api_key = st.secrets.get("YOUTUBE_API_KEY","")
            params  = {"part":"snippet","chart":"mostPopular",
                       "videoCategoryId":"10","maxResults":n,"regionCode":"IN"}
            if api_key: params["key"] = api_key
            r = requests.get("https://www.googleapis.com/youtube/v3/videos",
                params=params, headers=_yt_h(), timeout=10).json()
            return [{"id":{"videoId":i["id"]},"snippet":i["snippet"]} for i in r.get("items",[])]
        except: return []

    def _play(vid_id, title, artist, thumb):
        st.session_state.now_playing_id     = vid_id
        st.session_state.now_playing_title  = title
        st.session_state.now_playing_artist = artist
        st.session_state.now_playing_thumb  = thumb

    def _thumb(snip):
        t = snip.get("thumbnails", {})
        return (t.get("medium") or t.get("high") or t.get("default") or {}).get("url","")

    # ── Render card grid (YTM style) ──────────────────────────────────────────
    def ytm_grid(items, cols=4, prefix="g"):
        if not items:
            st.markdown("<p style='color:#aaa; text-align:center; padding:40px 0;'>Nothing here yet.</p>",
                        unsafe_allow_html=True)
            return
        rows = [items[i:i+cols] for i in range(0, len(items), cols)]
        for row in rows:
            gcols = st.columns(cols)
            for gi, item in enumerate(row):
                vid   = item["id"]["videoId"]
                snip  = item["snippet"]
                title = snip.get("title","")[:55]
                art   = snip.get("channelTitle","")[:35]
                thumb = _thumb(snip)
                with gcols[gi]:
                    if thumb:
                        st.markdown(f"<img src='{thumb}' style='width:100%;border-radius:6px;"
                                    f"aspect-ratio:16/9;object-fit:cover;display:block;margin-bottom:6px;'>",
                                    unsafe_allow_html=True)
                    st.markdown(f"<div style='color:#fff;font-size:0.82rem;font-weight:500;"
                                f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
                                f"margin-bottom:2px;'>{title}</div>"
                                f"<div style='color:#aaa;font-size:0.74rem;margin-bottom:6px;'>{art}</div>",
                                unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("▶", key=f"{prefix}_{vid}_{gi}_p",
                                     use_container_width=True):
                            _play(vid, title, art, thumb); st.rerun()
                    with b2:
                        if st.button("＋", key=f"{prefix}_{vid}_{gi}_q",
                                     use_container_width=True):
                            st.session_state.queue.append(
                                {"id":vid,"title":title,"artist":art,"thumb":thumb})
                            st.toast(f"Added to queue")

    # ── Render song row list (YTM style) ──────────────────────────────────────
    def ytm_list(items, prefix="l"):
        if not items:
            st.markdown("<p style='color:#aaa;'>Nothing here yet.</p>", unsafe_allow_html=True)
            return
        for i, item in enumerate(items):
            vid   = item["id"]["videoId"]
            snip  = item["snippet"]
            title = snip.get("title","")[:60]
            art   = snip.get("channelTitle","")[:40]
            thumb = _thumb(snip)
            c1,c2,c3,c4 = st.columns([1,5,1,1])
            with c1:
                if thumb:
                    st.markdown(f"<img src='{thumb}' style='width:48px;height:48px;"
                                f"border-radius:4px;object-fit:cover;'>",
                                unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='color:#fff;font-size:0.88rem;font-weight:500;"
                            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
                            f"padding-top:4px;'>{title}</div>"
                            f"<div style='color:#aaa;font-size:0.78rem;'>{art}</div>",
                            unsafe_allow_html=True)
            with c3:
                if st.button("▶", key=f"{prefix}_{vid}_{i}_p", use_container_width=True):
                    _play(vid, title, art, thumb); st.rerun()
            with c4:
                if st.button("＋", key=f"{prefix}_{vid}_{i}_q", use_container_width=True):
                    st.session_state.queue.append(
                        {"id":vid,"title":title,"artist":art,"thumb":thumb})
                    st.toast("Added to queue")
            st.markdown("<div style='height:1px;background:#1e1e1e;margin:2px 0;'></div>",
                        unsafe_allow_html=True)

    is_connected = bool(st.session_state.get("yt_token"))

    # ══════════════════════════════════════════════════════════════════════════
    #  TOP BAR  — Logo · Search · Account
    # ══════════════════════════════════════════════════════════════════════════
    top1, top2, top3 = st.columns([2, 5, 2])
    with top1:
        st.markdown("""
        <div style='display:flex;align-items:center;gap:8px;padding:8px 0;'>
            <div style='background:#ff0000;width:28px;height:28px;border-radius:50%;
            display:flex;align-items:center;justify-content:center;font-size:14px;'>🎵</div>
            <span style='color:#fff;font-weight:700;font-size:1rem;letter-spacing:-0.5px;'>
            YouTube <span style='color:#ff0000;'>Music</span></span>
        </div>""", unsafe_allow_html=True)

    with top2:
        search_q = st.text_input("", placeholder="🔍  Search songs, albums, artists",
                                 label_visibility="collapsed", key="ytm_search_main")
        if search_q and search_q != st.session_state.get("_last_search"):
            st.session_state._last_search = search_q
            fn = _yt_search if is_connected else youtube_search
            with st.spinner(""):
                st.session_state.music_search_results = fn(search_q, 16)
            st.session_state.ytm_nav = "search"
            st.rerun()

    with top3:
        if is_connected:
            email = st.session_state.get("yt_email","Connected")
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:8px;padding-top:8px;'>
                <div style='width:30px;height:30px;background:#ff0000;border-radius:50%;
                display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;'>
                {email[0].upper() if email else "G"}</div>
                <span style='color:#aaa;font-size:0.78rem;'>{email.split("@")[0]}</span>
            </div>""", unsafe_allow_html=True)
            if st.button("Sign out", key="ytm_signout"):
                st.session_state.yt_token = None
                st.session_state.yt_email = ""
                st.rerun()
        else:
            if _OAUTH_OK:
                result = _oauth2.authorize_button(
                    "Sign in", redirect_uri=REDIRECT_URI,
                    scope="openid email profile https://www.googleapis.com/auth/youtube.readonly",
                    key="ytm_oauth_top", icon="https://www.google.com/favicon.ico",
                    use_container_width=True
                )
                if result and "token" in result:
                    st.session_state.yt_token = result["token"]
                    try:
                        info = requests.get("https://www.googleapis.com/oauth2/v3/userinfo",
                            headers={"Authorization":f"Bearer {result['token']['access_token']}"},
                            timeout=8).json()
                        st.session_state.yt_email = info.get("email","")
                        for k in ["yt_liked_cache","yt_playlists_cache","yt_subs_cache","home_trending"]:
                            st.session_state.pop(k, None)
                    except: pass
                    st.rerun()
            else:
                st.markdown("<p style='color:#aaa;font-size:0.8rem;padding-top:10px;'>"
                            "Add OAuth secrets</p>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  NOW PLAYING BAR
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.now_playing_id:
        vid_id    = st.session_state.now_playing_id
        vid_title = st.session_state.now_playing_title
        vid_thumb = st.session_state.now_playing_thumb
        vid_art   = st.session_state.now_playing_artist

        st.markdown(f"""
        <div class='ytm-player-outer'>
            <div class='ytm-player-bar'>
                <img src='{vid_thumb}'/>
                <div class='ytm-player-info'>
                    <div class='ytm-player-title'>{vid_title}</div>
                    <div class='ytm-player-artist'>{vid_art}</div>
                </div>
                <div style='color:#ff0000;font-size:0.78rem;font-weight:600;letter-spacing:1px;'>
                ▶ NOW PLAYING</div>
            </div>
        </div>""", unsafe_allow_html=True)

        _comp.html(f"""
        <div style='background:#181818;'>
        <iframe id='ytplayer' width='100%' height='80'
            src='https://www.youtube-nocookie.com/embed/{vid_id}?autoplay=1&modestbranding=1&rel=0&iv_load_policy=3&showinfo=0&controls=1'
            frameborder='0' allow='autoplay; encrypted-media; picture-in-picture'
            allowfullscreen style='display:block;'>
        </iframe></div>""", height=90)

        if st.session_state.queue:
            nxt = st.session_state.queue[0]
            nc1, nc2, nc3 = st.columns([3,3,1])
            with nc2:
                if st.button(f"⏭  Up next: {nxt['title'][:30]}",
                             use_container_width=True, key="ytm_next"):
                    _play(nxt["id"], nxt["title"], nxt.get("artist",""), nxt.get("thumb",""))
                    st.session_state.queue = st.session_state.queue[1:]
                    st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    #  NAVIGATION  — YTM pill tabs
    # ══════════════════════════════════════════════════════════════════════════
    if "ytm_nav" not in st.session_state:
        st.session_state.ytm_nav = "home"

    nav_items = [
        ("home",    "🏠 Home"),
        ("explore", "🔍 Explore"),
        ("liked",   "❤️ Liked"),
        ("playlists","📚 Playlists"),
        ("subs",    "📺 Subscriptions"),
        ("library", "📋 Library"),
        ("jam",     "🎵 Jam"),
        ("queue",   "🔢 Queue"),
    ]
    nav_cols = st.columns(len(nav_items))
    for ni, (key, label) in enumerate(nav_items):
        with nav_cols[ni]:
            active = st.session_state.ytm_nav == key
            btn_style = "background:#ff0000;border-color:#ff0000;" if active else ""
            if st.button(label, key=f"ytm_nav_{key}", use_container_width=True):
                st.session_state.ytm_nav = key
                st.rerun()

    st.markdown("<div style='height:1px;background:#333;margin:4px 0 16px;'></div>",
                unsafe_allow_html=True)
    nav = st.session_state.ytm_nav

    # ══ HOME ══════════════════════════════════════════════════════════════════
    if nav == "home":
        # Quick genre chips
        genres = ["All","Pop","Hip-Hop","Lo-fi","Tamil","Malayalam",
                  "Bollywood","K-Pop","Indie","Jazz","Classical","Rock"]
        chips_html = "<div style='margin-bottom:16px;'>"
        for g in genres:
            chips_html += f"<span class='ytm-chip'>{g}</span>"
        chips_html += "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)

        rc1, rc2 = st.columns([5,1])
        with rc1:
            st.markdown("<div class='ytm-section-title'>🔥 Trending Music</div>",
                        unsafe_allow_html=True)
        with rc2:
            if st.button("Refresh", key="ytm_refresh_home"):
                st.session_state.pop("ytm_trending", None); st.rerun()

        if "ytm_trending" not in st.session_state:
            with st.spinner("Loading…"):
                st.session_state.ytm_trending = _yt_trending(16)
        ytm_grid(st.session_state.ytm_trending, cols=4, prefix="home")

        if is_connected:
            st.markdown("<div class='ytm-section-title'>🎵 From Your Liked Songs</div>",
                        unsafe_allow_html=True)
            liked_preview = st.session_state.get("yt_liked_cache", [])[:8]
            if liked_preview:
                ytm_list(liked_preview, prefix="home_lk")
            else:
                st.markdown("<p style='color:#aaa;'>Go to Liked tab to load your songs.</p>",
                            unsafe_allow_html=True)

    # ══ EXPLORE / SEARCH ══════════════════════════════════════════════════════
    elif nav in ("explore", "search"):
        st.markdown("<div class='ytm-section-title'>🔍 Search</div>",
                    unsafe_allow_html=True)
        # Genre quick picks
        genres_exp = ["Pop","Hip-Hop","Lo-fi","Tamil","Malayalam",
                      "Bollywood","K-Pop","Jazz","Rock","Classical","Indie","R&B"]
        st.markdown("<p style='color:#aaa;font-size:0.85rem;'>Browse by genre:</p>",
                    unsafe_allow_html=True)
        gcols = st.columns(6)
        colors = ["#ff0000","#7b2fff","#00d4ff","#00ff88","#ffa500","#ff69b4",
                  "#ff0000","#7b2fff","#00d4ff","#00ff88","#ffa500","#ff69b4"]
        for gi2, genre in enumerate(genres_exp):
            with gcols[gi2 % 6]:
                st.markdown(f"""
                <div style='background:{colors[gi2]}22;border:1px solid {colors[gi2]}44;
                border-radius:8px;padding:14px;text-align:center;margin-bottom:8px;cursor:pointer;'>
                    <div style='color:{colors[gi2]};font-weight:600;font-size:0.85rem;'>{genre}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Play {genre}", key=f"genre_exp_{genre}",
                             use_container_width=True):
                    fn = _yt_search if is_connected else youtube_search
                    with st.spinner(""):
                        st.session_state.music_search_results = fn(genre, 16)
                    st.session_state.music_search_query = genre
                    st.session_state.ytm_nav = "search"
                    st.rerun()

        if st.session_state.music_search_results:
            q_label = st.session_state.music_search_query
            st.markdown(f"<div class='ytm-section-title'>Results: {q_label}</div>",
                        unsafe_allow_html=True)
            tab_grid, tab_list = st.tabs(["Grid view", "List view"])
            with tab_grid:
                ytm_grid(st.session_state.music_search_results, cols=4, prefix="exp")
            with tab_list:
                ytm_list(st.session_state.music_search_results, prefix="exp_l")

    # ══ LIKED SONGS ═══════════════════════════════════════════════════════════
    elif nav == "liked":
        lkh1, lkh2, lkh3 = st.columns([4,1,1])
        with lkh1:
            st.markdown("<div class='ytm-section-title'>❤️ Liked Songs</div>",
                        unsafe_allow_html=True)
        with lkh2:
            if st.button("🔄 Refresh", key="ytm_refresh_liked"):
                st.session_state.pop("yt_liked_cache", None); st.rerun()
        with lkh3:
            lk_view = st.selectbox("View", ["Grid","List"],
                                   key="lk_view_sel", label_visibility="collapsed")

        if is_connected:
            if "yt_liked_cache" not in st.session_state:
                with st.spinner("Loading liked songs…"):
                    st.session_state.yt_liked_cache = _yt_liked(50)
            items = st.session_state.yt_liked_cache
            if lk_view == "Grid":
                ytm_grid(items, cols=4, prefix="lk")
            else:
                # Play all banner
                if items:
                    pb1, pb2 = st.columns([1,6])
                    with pb1:
                        if st.button("▶ Play All", use_container_width=True, key="lk_play_all"):
                            first = items[0]
                            _play(first["id"]["videoId"],
                                  first["snippet"].get("title",""),
                                  first["snippet"].get("channelTitle",""),
                                  _thumb(first["snippet"]))
                            st.session_state.queue = [
                                {"id":x["id"]["videoId"],
                                 "title":x["snippet"].get("title",""),
                                 "artist":x["snippet"].get("channelTitle",""),
                                 "thumb":_thumb(x["snippet"])} for x in items[1:]]
                            st.rerun()
                ytm_list(items, prefix="lk_l")
        else:
            # In-app saved songs
            st.markdown("<p style='color:#aaa;margin-bottom:12px;'>Connect Google to see your real YouTube liked songs.</p>",
                        unsafe_allow_html=True)
            saved = get_liked_songs(st.session_state.user)
            if not saved:
                st.markdown("<p style='color:#555;text-align:center;padding:40px;'>"
                            "No saved songs yet. Use ❤️ Save while a track is playing.</p>",
                            unsafe_allow_html=True)
            else:
                for song in saved:
                    sc1,sc2,sc3,sc4 = st.columns([1,5,1,1])
                    with sc1:
                        if song.get("thumbnail"):
                            st.markdown(f"<img src='{song['thumbnail']}' style='width:48px;"
                                        f"height:48px;border-radius:4px;object-fit:cover;'>",
                                        unsafe_allow_html=True)
                    with sc2:
                        st.markdown(f"<div style='color:#fff;font-size:0.88rem;font-weight:500;"
                                    f"padding-top:4px;'>{song['title']}</div>"
                                    f"<div style='color:#aaa;font-size:0.78rem;'>{song['artist']}</div>",
                                    unsafe_allow_html=True)
                    with sc3:
                        if st.button("▶", key=f"sv_p_{song['video_id']}", use_container_width=True):
                            _play(song["video_id"],song["title"],song["artist"],
                                  song.get("thumbnail","")); st.rerun()
                    with sc4:
                        if st.button("🗑", key=f"sv_d_{song['video_id']}", use_container_width=True):
                            unlike_song(st.session_state.user, song["video_id"]); st.rerun()
                    st.markdown("<div style='height:1px;background:#1e1e1e;margin:2px 0;'></div>",
                                unsafe_allow_html=True)

            if st.session_state.now_playing_id:
                st.markdown("---")
                if st.button(f"❤️ Save current: {st.session_state.now_playing_title[:40]}",
                             use_container_width=True, key="save_current_ytm"):
                    like_song(st.session_state.user, st.session_state.now_playing_id,
                              st.session_state.now_playing_title,
                              st.session_state.now_playing_artist,
                              st.session_state.now_playing_thumb)
                    st.success("Saved!"); st.rerun()

    # ══ PLAYLISTS ═════════════════════════════════════════════════════════════
    elif nav == "playlists":
        st.markdown("<div class='ytm-section-title'>📚 Playlists</div>",
                    unsafe_allow_html=True)
        if is_connected:
            prc1, prc2 = st.columns([5,1])
            with prc2:
                if st.button("🔄", key="ytm_ref_pl"):
                    st.session_state.pop("yt_playlists_cache", None)
                    st.session_state.pop("ytm_open_pl", None); st.rerun()

            if "yt_playlists_cache" not in st.session_state:
                with st.spinner("Loading playlists…"):
                    st.session_state.yt_playlists_cache = _yt_playlists(50)

            pls = st.session_state.yt_playlists_cache
            if not pls:
                st.markdown("<p style='color:#555;'>No playlists on your account.</p>",
                            unsafe_allow_html=True)
            else:
                pl_left, pl_right = st.columns([1, 2])
                with pl_left:
                    for pl in pls:
                        pl_id    = pl["id"]
                        pl_title = pl["snippet"]["title"]
                        pl_count = pl.get("contentDetails",{}).get("itemCount","?")
                        pl_thumb = _thumb(pl["snippet"])
                        plc1, plc2 = st.columns([1,3])
                        with plc1:
                            if pl_thumb:
                                st.markdown(f"<img src='{pl_thumb}' style='width:52px;"
                                            f"height:52px;border-radius:4px;object-fit:cover;'>",
                                            unsafe_allow_html=True)
                        with plc2:
                            st.markdown(f"<div style='color:#fff;font-size:0.85rem;"
                                        f"font-weight:500;padding-top:4px;'>{pl_title[:24]}</div>"
                                        f"<div style='color:#aaa;font-size:0.75rem;'>{pl_count} songs</div>",
                                        unsafe_allow_html=True)
                        if st.button(f"Open", key=f"open_ytpl_{pl_id}", use_container_width=True):
                            with st.spinner("Loading…"):
                                st.session_state.ytm_open_pl = {
                                    "id": pl_id, "title": pl_title,
                                    "items": _yt_pl_items(pl_id, 50)
                                }
                            st.rerun()
                        st.markdown("<div style='height:1px;background:#1e1e1e;margin:4px 0;'></div>",
                                    unsafe_allow_html=True)

                with pl_right:
                    open_pl = st.session_state.get("ytm_open_pl")
                    if open_pl:
                        pl_items = open_pl["items"]
                        st.markdown(f"<div class='ytm-section-title'>📀 {open_pl['title']}"
                                    f" <span style='color:#aaa;font-size:0.8rem;font-weight:400;'>"
                                    f"({len(pl_items)} tracks)</span></div>",
                                    unsafe_allow_html=True)
                        if pl_items:
                            if st.button("▶ Play All", use_container_width=True, key="ytpl_all"):
                                f0 = pl_items[0]
                                _play(f0["id"]["videoId"],
                                      f0["snippet"].get("title",""),
                                      f0["snippet"].get("channelTitle",""),
                                      _thumb(f0["snippet"]))
                                st.session_state.queue = [
                                    {"id":x["id"]["videoId"],
                                     "title":x["snippet"].get("title",""),
                                     "artist":x["snippet"].get("channelTitle",""),
                                     "thumb":_thumb(x["snippet"])} for x in pl_items[1:]]
                                st.rerun()
                        ytm_list(pl_items, prefix="ytpl_items")
                    else:
                        st.markdown("<p style='color:#555;padding:40px;text-align:center;'>"
                                    "Select a playlist on the left</p>",
                                    unsafe_allow_html=True)
        else:
            # In-app playlists
            st.markdown("<p style='color:#aaa;margin-bottom:12px;'>Connect Google to access your YouTube playlists.</p>",
                        unsafe_allow_html=True)
            pls_app = get_playlists(st.session_state.user)
            ipl_l, ipl_r = st.columns([1,2])
            with ipl_l:
                new_pl = st.text_input("New playlist name", key="ytm_new_pl",
                                       placeholder="My playlist")
                if st.button("➕ Create", use_container_width=True, key="ytm_create_pl"):
                    if new_pl.strip():
                        save_playlist(st.session_state.user, new_pl.strip(), [])
                        st.success("Created!"); st.rerun()
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                for pl in pls_app:
                    ipc1, ipc2 = st.columns([4,1])
                    with ipc1:
                        if st.button(f"📀 {pl['name']}", key=f"ipl_{pl['name']}",
                                     use_container_width=True):
                            st.session_state.active_playlist_name = pl["name"]; st.rerun()
                    with ipc2:
                        if st.button("✕", key=f"ipl_d_{pl['name']}", use_container_width=True):
                            delete_playlist(st.session_state.user, pl["name"])
                            if st.session_state.active_playlist_name == pl["name"]:
                                st.session_state.active_playlist_name = None
                            st.rerun()
            with ipl_r:
                active_pl = st.session_state.active_playlist_name
                if active_pl:
                    pl_data = next((p for p in pls_app if p["name"]==active_pl), None)
                    if pl_data:
                        songs = pl_data.get("songs",[])
                        st.markdown(f"<div class='ytm-section-title'>📀 {active_pl} "
                                    f"<span style='color:#aaa;font-size:0.8rem;font-weight:400;'>"
                                    f"({len(songs)} tracks)</span></div>",
                                    unsafe_allow_html=True)
                        if st.session_state.now_playing_id:
                            if st.button("➕ Add current track", use_container_width=True,
                                         key="ipl_add_cur"):
                                new_s = {"id":st.session_state.now_playing_id,
                                         "title":st.session_state.now_playing_title,
                                         "artist":st.session_state.now_playing_artist,
                                         "thumb":st.session_state.now_playing_thumb}
                                if not any(s["id"]==new_s["id"] for s in songs):
                                    songs.append(new_s)
                                    save_playlist(st.session_state.user, active_pl, songs)
                                    st.success("Added!"); st.rerun()
                        if songs and st.button("▶ Play All", use_container_width=True,
                                               key="ipl_play_all"):
                            _play(songs[0]["id"],songs[0]["title"],
                                  songs[0].get("artist",""),songs[0].get("thumb",""))
                            st.session_state.queue = songs[1:]; st.rerun()
                        for i,s in enumerate(songs):
                            isc1,isc2,isc3,isc4 = st.columns([1,5,1,1])
                            with isc1:
                                if s.get("thumb"):
                                    st.markdown(f"<img src='{s['thumb']}' style='width:44px;"
                                                f"height:44px;border-radius:4px;object-fit:cover;'>",
                                                unsafe_allow_html=True)
                            with isc2:
                                st.markdown(f"<div style='color:#fff;font-size:0.85rem;"
                                            f"padding-top:4px;'>{s['title']}</div>"
                                            f"<div style='color:#aaa;font-size:0.75rem;'>{s.get('artist','')}</div>",
                                            unsafe_allow_html=True)
                            with isc3:
                                if st.button("▶", key=f"ipl_p_{i}", use_container_width=True):
                                    _play(s["id"],s["title"],s.get("artist",""),s.get("thumb",""))
                                    st.session_state.queue = songs[i+1:]; st.rerun()
                            with isc4:
                                if st.button("✕", key=f"ipl_r_{i}", use_container_width=True):
                                    songs.pop(i)
                                    save_playlist(st.session_state.user, active_pl, songs); st.rerun()
                            st.markdown("<div style='height:1px;background:#1e1e1e;margin:2px 0;'></div>",
                                        unsafe_allow_html=True)

    # ══ SUBSCRIPTIONS ═════════════════════════════════════════════════════════
    elif nav == "subs":
        sc1h, sc2h = st.columns([5,1])
        with sc1h:
            st.markdown("<div class='ytm-section-title'>📺 Subscriptions</div>",
                        unsafe_allow_html=True)
        with sc2h:
            if st.button("🔄", key="ytm_ref_subs"):
                st.session_state.pop("yt_subs_cache", None); st.rerun()

        if is_connected:
            if "yt_subs_cache" not in st.session_state:
                with st.spinner("Loading…"):
                    st.session_state.yt_subs_cache = _yt_subs(50)
            subs = st.session_state.yt_subs_cache
            if not subs:
                st.markdown("<p style='color:#555;'>No subscriptions found.</p>",
                            unsafe_allow_html=True)
            else:
                # Show as badge grid
                n_cols = 6
                rows = [subs[i:i+n_cols] for i in range(0, len(subs), n_cols)]
                for row in rows:
                    sub_cols = st.columns(n_cols)
                    for si, sub in enumerate(row):
                        snip = sub["snippet"]
                        ch   = snip.get("title","")
                        thmb = _thumb(snip)
                        with sub_cols[si]:
                            if thmb:
                                st.markdown(f"""
                                <div style='text-align:center;'>
                                  <img src='{thmb}' style='width:60px;height:60px;
                                  border-radius:50%;object-fit:cover;
                                  border:2px solid #333;margin:0 auto;display:block;'>
                                  <div style='color:#fff;font-size:0.74rem;margin-top:6px;
                                  overflow:hidden;text-overflow:ellipsis;
                                  white-space:nowrap;'>{ch[:16]}</div>
                                </div>""", unsafe_allow_html=True)
                            if st.button("Browse", key=f"sub_{si}_{ch[:8]}",
                                         use_container_width=True):
                                fn = _yt_search if is_connected else youtube_search
                                st.session_state.music_search_results = fn(ch, 16)
                                st.session_state.music_search_query = ch
                                st.session_state.ytm_nav = "search"; st.rerun()
        else:
            st.info("Connect your Google account to see your subscriptions.")

    # ══ LIBRARY ═══════════════════════════════════════════════════════════════
    elif nav == "library":
        st.markdown("<div class='ytm-section-title'>📋 Library</div>",
                    unsafe_allow_html=True)
        if is_connected:
            lib_t1, lib_t2, lib_t3 = st.tabs(["❤️ Liked","📚 Playlists","📺 Subs"])
            with lib_t1:
                items = st.session_state.get("yt_liked_cache",[])
                if items:
                    ytm_list(items[:10], prefix="lib_lk")
                    if st.button("See all liked →", use_container_width=True, key="lib_see_liked"):
                        st.session_state.ytm_nav="liked"; st.rerun()
                else:
                    if st.button("Load liked songs", use_container_width=True, key="lib_load_lk"):
                        with st.spinner(""):
                            st.session_state.yt_liked_cache = _yt_liked(50)
                        st.rerun()
            with lib_t2:
                plc = st.session_state.get("yt_playlists_cache",[])
                for pl in plc[:8]:
                    st.markdown(f"<div style='color:#fff;padding:6px 0;'>📀 {pl['snippet']['title']}"
                                f"<span style='color:#aaa;font-size:0.78rem;margin-left:8px;'>"
                                f"({pl.get('contentDetails',{}).get('itemCount','?')} tracks)</span></div>"
                                f"<div style='height:1px;background:#1e1e1e;'></div>",
                                unsafe_allow_html=True)
                if st.button("See all playlists →", use_container_width=True, key="lib_see_pl"):
                    st.session_state.ytm_nav="playlists"; st.rerun()
            with lib_t3:
                sc2 = st.session_state.get("yt_subs_cache",[])
                st.markdown(f"<p style='color:#aaa;'>{len(sc2)} subscriptions</p>",
                            unsafe_allow_html=True)
                if st.button("See all subscriptions →", use_container_width=True, key="lib_see_subs"):
                    st.session_state.ytm_nav="subs"; st.rerun()
        else:
            st.info("Connect your Google account to access your full library.")

    # ══ JAM ═══════════════════════════════════════════════════════════════════
    elif nav == "jam":
        st.markdown("<div class='ytm-section-title'>🎵 Jam — Listen Together</div>",
                    unsafe_allow_html=True)
        st.markdown("<p style='color:#aaa;'>Share what you're playing with friends in real time.</p>",
                    unsafe_allow_html=True)

        if st.session_state.now_playing_id:
            st.markdown(f"""
            <div style='background:#1e1e1e;border:1px solid #333;border-radius:10px;
            padding:16px;margin-bottom:16px;display:flex;align-items:center;gap:12px;'>
                <img src='{st.session_state.now_playing_thumb}' style='width:64px;height:64px;
                border-radius:6px;object-fit:cover;'>
                <div>
                    <div style='color:#fff;font-weight:600;'>{st.session_state.now_playing_title}</div>
                    <div style='color:#aaa;font-size:0.82rem;'>{st.session_state.now_playing_artist}</div>
                    <div style='color:#ff0000;font-size:0.75rem;margin-top:4px;'>▶ NOW PLAYING</div>
                </div>
            </div>""", unsafe_allow_html=True)
            my_u = get_user(st.session_state.user)
            ftj  = my_u.get("friends",[]) if my_u else []
            if not ftj:
                st.info("Add friends to jam with them.")
            else:
                st.markdown("<p style='color:#aaa;font-size:0.88rem;'>Send jam to:</p>",
                            unsafe_allow_html=True)
                jam_cols = st.columns(min(len(ftj), 5))
                for ji, f in enumerate(ftj):
                    with jam_cols[ji % 5]:
                        if st.button(f"🎵 {f}", key=f"jam_{f}", use_container_width=True):
                            send_jam(st.session_state.user, f,
                                     st.session_state.now_playing_id,
                                     st.session_state.now_playing_title,
                                     st.session_state.now_playing_thumb)
                            st.success(f"Jam sent to {f}!")
        else:
            st.markdown("""
            <div style='text-align:center;padding:60px;color:#555;'>
                <div style='font-size:3rem;'>🎵</div>
                <p>Play a song first, then jam with friends</p>
            </div>""", unsafe_allow_html=True)

        inc_jam = get_jam(st.session_state.user)
        if inc_jam:
            st.markdown("---")
            st.markdown(f"<div style='color:#00ff88;font-weight:600;font-size:0.9rem;'>"
                        f"📨 {inc_jam['host']} is jamming with you!</div>",
                        unsafe_allow_html=True)
            if inc_jam.get("thumbnail"):
                st.markdown(f"<img src='{inc_jam['thumbnail']}' style='width:120px;"
                            f"border-radius:6px;margin:8px 0;'>", unsafe_allow_html=True)
            jt = inc_jam["title"]
            if st.button(f"▶ Join: {jt[:40]}", use_container_width=True, key="join_jam"):
                _play(inc_jam["video_id"], jt, inc_jam["host"], inc_jam.get("thumbnail",""))
                st.rerun()

    # ══ QUEUE ═════════════════════════════════════════════════════════════════
    elif nav == "queue":
        qh1, qh2 = st.columns([5,1])
        with qh1:
            st.markdown(f"<div class='ytm-section-title'>🔢 Queue "
                        f"<span style='color:#aaa;font-size:0.85rem;font-weight:400;'>"
                        f"({len(st.session_state.queue)} tracks)</span></div>",
                        unsafe_allow_html=True)
        with qh2:
            if st.session_state.queue:
                if st.button("Clear all", key="ytm_clear_q", use_container_width=True):
                    st.session_state.queue = []; st.rerun()

        if not st.session_state.queue:
            st.markdown("""
            <div style='text-align:center;padding:60px;color:#555;'>
                <div style='font-size:3rem;🎵</div>
                <p>Your queue is empty — hit ＋ on any track</p>
            </div>""", unsafe_allow_html=True)
        else:
            for qi, track in enumerate(st.session_state.queue):
                qc1,qc2,qc3,qc4,qc5 = st.columns([1,1,4,1,1])
                with qc1:
                    st.markdown(f"<div style='color:#555;text-align:center;padding-top:14px;'>"
                                f"{qi+1}</div>", unsafe_allow_html=True)
                with qc2:
                    if track.get("thumb"):
                        st.markdown(f"<img src='{track['thumb']}' style='width:44px;height:44px;"
                                    f"border-radius:4px;object-fit:cover;'>", unsafe_allow_html=True)
                with qc3:
                    st.markdown(f"<div style='color:#fff;font-size:0.87rem;padding-top:4px;'>"
                                f"{track['title']}</div>"
                                f"<div style='color:#aaa;font-size:0.76rem;'>{track.get('artist','')}</div>",
                                unsafe_allow_html=True)
                with qc4:
                    if st.button("▶", key=f"q_p_{qi}", use_container_width=True):
                        _play(track["id"],track["title"],
                              track.get("artist",""),track.get("thumb",""))
                        st.session_state.queue.pop(qi); st.rerun()
                with qc5:
                    if st.button("✕", key=f"q_r_{qi}", use_container_width=True):
                        st.session_state.queue.pop(qi); st.rerun()
                st.markdown("<div style='height:1px;background:#1e1e1e;margin:2px 0;'></div>",
                            unsafe_allow_html=True)

# ─────────────────────────────────────────
# 12. WEATHER PAGE — GPS only + Charts
# ─────────────────────────────────────────
elif st.session_state.current_page == "Weather":
    import json
    import pandas as pd

    st.markdown("<div class='hero-title' style='font-size:1.8rem;'>🌤️ SkyView Weather</div>", unsafe_allow_html=True)

    WMO_CODES = {
        0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"), 45: ("Foggy", "🌫️"), 48: ("Icy fog", "🌫️"),
        51: ("Light drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy drizzle", "🌧️"),
        61: ("Slight rain", "🌧️"), 63: ("Moderate rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
        71: ("Slight snow", "🌨️"), 73: ("Moderate snow", "❄️"), 75: ("Heavy snow", "❄️"),
        80: ("Rain showers", "🌦️"), 81: ("Heavy showers", "⛈️"), 95: ("Thunderstorm", "⛈️"),
    }

    # ── GPS Button ────────────────────────────────────────────────────────────
    col_btn, col_refresh, _ = st.columns([2, 1, 2])
    with col_btn:
        if _GEO_OK:
            gps_btn = st.button("📍 Detect My Location", use_container_width=True, key="gps_btn")
        else:
            gps_btn = False
            st.error("⚠️ Install streamlit-js-eval for GPS support")
    with col_refresh:
        if st.session_state.weather_fetched:
            if st.button("🔄 Refresh", use_container_width=True, key="refresh_btn"):
                st.session_state.weather_fetched = False
                st.session_state.gps_lat = None
                st.session_state.gps_lon = None
                st.rerun()

    # ── GPS fetch ─────────────────────────────────────────────────────────────
    if gps_btn and _GEO_OK:
        with st.spinner("📍 Getting your location... (allow access if prompted)"):
            try:
                geo_data = get_geolocation()
                if geo_data and "coords" in geo_data:
                    gps_lat = geo_data["coords"]["latitude"]
                    gps_lon = geo_data["coords"]["longitude"]
                    # Reverse geocode — free, no API key
                    rev = requests.get(
                        "https://nominatim.openstreetmap.org/reverse",
                        params={"lat": gps_lat, "lon": gps_lon, "format": "json"},
                        headers={"User-Agent": "LakshmeeyamAI/1.0"},
                        timeout=10
                    ).json()
                    addr = rev.get("address", {})
                    city_name = (
                        addr.get("city") or addr.get("town")
                        or addr.get("village") or addr.get("county")
                        or "Your Location"
                    )
                    country = addr.get("country", "")
                    st.session_state.gps_lat     = gps_lat
                    st.session_state.gps_lon     = gps_lon
                    st.session_state.gps_city    = city_name
                    st.session_state.gps_country = country
                    st.session_state.weather_fetched = True
                    st.rerun()
                else:
                    st.warning("⚠️ Location not received. Please allow location access in your browser and try again.")
            except Exception as e:
                st.error(f"❌ GPS error: {e}")

    # ── Render weather if GPS data available ──────────────────────────────────
    if st.session_state.weather_fetched and st.session_state.gps_lat:
        lat       = st.session_state.gps_lat
        lon       = st.session_state.gps_lon
        city_name = st.session_state.gps_city
        country   = st.session_state.gps_country

        try:
            with st.spinner("⛅ Loading weather data..."):
                weather = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current_weather": "true",
                        "hourly": "temperature_2m,apparent_temperature,relativehumidity_2m,precipitation_probability,windspeed_10m,weathercode",
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                        "forecast_days": 7,
                        "timezone": "auto"
                    },
                    timeout=10
                ).json()

            curr      = weather["current_weather"]
            temp      = curr["temperature"]
            wind      = curr["windspeed"]
            wcode     = int(curr.get("weathercode", 0))
            is_day    = curr.get("is_day", 1)
            condition, w_icon = WMO_CODES.get(wcode, ("Unknown", "🌡️"))

            # ── Current weather card ──────────────────────────────────────────
            st.markdown(f"""
            <div class='weather-card'>
                <div style='display:inline-block; background:rgba(0,255,136,0.15);
                border:1px solid #00ff88; border-radius:20px; padding:2px 12px;
                font-size:0.8rem; color:#00ff88; margin-bottom:10px;'>
                📍 GPS · {city_name}, {country}
                </div>
                <div style='font-size:5rem; line-height:1;'>{w_icon}</div>
                <div style='font-size:4rem; color:#00d4ff;
                font-family:Orbitron,sans-serif; margin:10px 0;'>{temp}°C</div>
                <div style='color:rgba(255,255,255,0.7); font-size:1.1rem;'>
                {'☀️ Daytime' if is_day else '🌙 Nighttime'} · {condition}
                </div>
                <div style='display:flex; justify-content:center; gap:40px;
                margin-top:20px; flex-wrap:wrap;'>
                    <div><div style='color:rgba(255,255,255,0.5); font-size:0.85rem;'>💨 Wind</div>
                         <div style='color:white; font-size:1.3rem;font-weight:600;'>{wind} km/h</div></div>
                    <div><div style='color:rgba(255,255,255,0.5); font-size:0.85rem;'>🌡️ Feels Like</div>
                         <div style='color:white; font-size:1.3rem;font-weight:600;'>
                         {weather["hourly"]["apparent_temperature"][0]}°C</div></div>
                    <div><div style='color:rgba(255,255,255,0.5); font-size:0.85rem;'>💧 Humidity</div>
                         <div style='color:white; font-size:1.3rem;font-weight:600;'>
                         {weather["hourly"]["relativehumidity_2m"][0]}%</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Hourly charts (next 24 hours) ─────────────────────────────────
            hourly   = weather["hourly"]
            # Find index of current hour
            curr_time_str = curr.get("time", "")
            all_times = hourly["time"]
            try:
                start_idx = next(
                    (i for i, t in enumerate(all_times) if t >= curr_time_str), 0
                )
            except Exception:
                start_idx = 0
            end_idx = min(start_idx + 24, len(all_times))

            hours_labels = [t[11:16] for t in all_times[start_idx:end_idx]]
            temps_24     = hourly["temperature_2m"][start_idx:end_idx]
            humidity_24  = hourly["relativehumidity_2m"][start_idx:end_idx]
            precip_24    = hourly["precipitation_probability"][start_idx:end_idx]
            wind_24      = hourly["windspeed_10m"][start_idx:end_idx]

            df_hourly = pd.DataFrame({
                "Hour":        hours_labels,
                "Temp (°C)":   temps_24,
                "Humidity (%)":humidity_24,
                "Rain chance (%)": precip_24,
                "Wind (km/h)": wind_24,
            })

            st.markdown("<h4 style='color:#00d4ff;'>📈 Next 24 Hours</h4>", unsafe_allow_html=True)

            tab_temp, tab_rain, tab_wind, tab_humid = st.tabs([
                "🌡️ Temperature", "🌧️ Rain Chance", "💨 Wind Speed", "💧 Humidity"
            ])

            chart_config = {"displayModeBar": False}

            with tab_temp:
                st.line_chart(
                    df_hourly.set_index("Hour")["Temp (°C)"],
                    color="#00d4ff",
                    use_container_width=True,
                    height=220
                )

            with tab_rain:
                st.bar_chart(
                    df_hourly.set_index("Hour")["Rain chance (%)"],
                    color="#7b2fff",
                    use_container_width=True,
                    height=220
                )

            with tab_wind:
                st.line_chart(
                    df_hourly.set_index("Hour")["Wind (km/h)"],
                    color="#00ff88",
                    use_container_width=True,
                    height=220
                )

            with tab_humid:
                st.area_chart(
                    df_hourly.set_index("Hour")["Humidity (%)"],
                    color="#ffa500",
                    use_container_width=True,
                    height=220
                )

            # ── 7-day forecast cards ──────────────────────────────────────────
            st.markdown("<br><h4 style='color:#00d4ff;'>📅 7-Day Forecast</h4>", unsafe_allow_html=True)
            daily   = weather["daily"]
            d_dates = daily.get("time", [])
            d_max   = daily.get("temperature_2m_max", [])
            d_min   = daily.get("temperature_2m_min", [])
            d_prec  = daily.get("precipitation_sum", [])
            d_codes = daily.get("weathercode", [])

            d_cols = st.columns(len(d_dates))
            for i in range(len(d_dates)):
                dc, dicon = WMO_CODES.get(int(d_codes[i]) if i < len(d_codes) else 0, ("?", "🌡️"))
                day_name  = datetime.strptime(d_dates[i], "%Y-%m-%d").strftime("%a %d")
                prec_val  = round(d_prec[i], 1) if i < len(d_prec) and d_prec[i] else 0
                with d_cols[i]:
                    st.markdown(f"""
                    <div style='background:rgba(0,100,150,0.2);
                    border:1px solid rgba(0,150,255,0.3); border-radius:12px;
                    padding:14px 6px; text-align:center; color:white;'>
                        <div style='color:rgba(255,255,255,0.6); font-size:0.75rem;'>{day_name}</div>
                        <div style='font-size:2rem; margin:6px 0;'>{dicon}</div>
                        <div style='color:#ff6b6b; font-weight:700;'>
                            {d_max[i] if i < len(d_max) else '-'}°</div>
                        <div style='color:#74b9ff; font-size:0.85rem;'>
                            {d_min[i] if i < len(d_min) else '-'}°</div>
                        <div style='color:rgba(150,200,255,0.7); font-size:0.72rem; margin-top:4px;'>
                            💧{prec_val}mm</div>
                    </div>
                    """, unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.error("❌ No internet connection.")
        except Exception as e:
            st.error(f"❌ Error loading weather: {e}")

    # ── Empty state ───────────────────────────────────────────────────────────
    else:
        st.markdown("""
        <div style='text-align:center; padding:80px 20px; color:rgba(255,255,255,0.3);'>
            <div style='font-size:5rem;'>🌍</div>
            <p style='font-size:1.3rem; color:rgba(255,255,255,0.5);'>
                Tap <b style='color:#00ff88;'>📍 Detect My Location</b> above
            </p>
            <p style='font-size:0.85rem;'>
                Uses your device GPS · No typing needed<br>
                Temperature · Rain · Wind · Humidity · 7-Day Forecast
            </p>
        </div>
        """, unsafe_allow_html=True)

# ── End analytics tracking ────────────────────────────────────────────────────
if _ANALYTICS_OK:
    try:
        streamlit_analytics.stop_tracking(
            ga4_id="G-98JQK90KWX",
            unsafe_password=""
        )
    except Exception:
        pass
