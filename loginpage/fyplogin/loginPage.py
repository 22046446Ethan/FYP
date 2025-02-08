import streamlit as st
from google_auth_oauthlib.flow import Flow
import os

# Set the page configuration for Streamlit app
st.set_page_config(page_title="A Kind Place Login Page", page_icon="🔒", layout="centered")

# Custom CSS for styling the UI with a soft pink theme
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #f8bbd0, #f48fb1);
        color: #4a4a4a;
    }
    .main {
        background: rgba(255, 204, 213, 0.9);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(to right, #f06292, #ec407a);
        color: white;
        font-size: 16px;
        padding: 12px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: transform 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(to right, #d81b60, #f06292);
    }
    .icon {
        font-size: 50px;
        color: #d81b60;
        animation: bounce 1.5s infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load Google OAuth credentials securely from Streamlit secrets
CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["google_oauth"]["client_id"],
        "client_secret": st.secrets["google_oauth"]["client_secret"],
        "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]],
        "auth_uri": st.secrets["google_oauth"]["auth_uri"],
        "token_uri": st.secrets["google_oauth"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google_oauth"]["auth_provider_x509_cert_url"],
    }
}

# Define a list of allowed emails for authentication
ALLOWED_EMAILS = ["dodonpear@gmail.com"]

def google_login():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"]
    )
    flow.redirect_uri = "http://localhost:8501"
    auth_url, _ = flow.authorization_url(prompt="consent")
    return flow, auth_url

st.markdown("<h1 style='text-align: center; font-size: 28px; color: #880e4f;'>🔒 A Kind Place Login Page</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6a1b9a;'>Please log in using your Google account.</p>", unsafe_allow_html=True)
st.markdown("<p class='icon' style='text-align:center;'>💖</p>", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    user_email = st.session_state.user["email"]
    st.success(f"✅ Welcome, **{user_email}**!")
    if user_email in ALLOWED_EMAILS:
        st.markdown("<h3 style='text-align: center; color: green;'>✅ Access Granted</h3>", unsafe_allow_html=True)
        if st.button("📂 Proceed to Upload Page"):
            os.system("streamlit run uploadFile.py")
    else:
        st.error("❌ Access Denied! Your email is not authorized.")
        st.session_state.user = None
        st.stop()
else:
    flow, auth_url = google_login()
    st.markdown(
        f'<a href="{auth_url}" target="_self">'
        '<button style="background-color:#f48fb1;color:white;padding:12px;border:none;border-radius:8px;font-size:16px;cursor:pointer;">'
        '🔗 Login with Google</button></a>', unsafe_allow_html=True)

query_params = st.query_params
if "code" in query_params:
    try:
        flow, _ = google_login()
        flow.fetch_token(code=query_params.get("code", ""))
        session = flow.authorized_session()
        user_info = session.get("https://www.googleapis.com/oauth2/v1/userinfo").json()
        if user_info.get("email", "") in ALLOWED_EMAILS:
            st.session_state.user = user_info
            st.rerun()
        else:
            st.error("❌ Access Denied!")
            st.stop()
    except Exception as e:
        st.stop()
