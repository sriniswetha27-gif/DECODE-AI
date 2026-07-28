from collections import Counter
from difflib import unified_diff
from pathlib import Path

import streamlit as st

from code_reviewer import (
    SUPPORTED_EXTENSIONS,
    ask_about_code,
    extract_improved_code,
    parse_quality_scores,
    review_code,
)

from auth import (
    authenticate_user,
    get_review_history,
    initialize_database,
    register_user,
    save_review,
)

st.set_page_config(
    page_title="DECODE AI",
    page_icon="🧑‍💻",
    layout="wide",
)
initialize_database()

if "current_user" not in st.session_state:
    st.session_state.current_user = None


# ---------- DECODE AI CUSTOM DESIGN ----------
st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --background: #060b18;
        --surface: rgba(17, 25, 46, 0.78);
        --surface-light: rgba(30, 41, 69, 0.72);
        --border: rgba(148, 163, 184, 0.18);
        --primary: #7c3aed;
        --secondary: #2563eb;
        --cyan: #22d3ee;
        --text: #f8fafc;
        --muted: #94a3b8;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main application background */
    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 15% 10%, rgba(124, 58, 237, 0.18), transparent 28%),
            radial-gradient(circle at 85% 15%, rgba(37, 99, 235, 0.17), transparent 25%),
            radial-gradient(circle at 50% 90%, rgba(34, 211, 238, 0.08), transparent 30%),
            var(--background);
        background-attachment: fixed;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        visibility: hidden;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            rgba(12, 18, 35, 0.98),
            rgba(17, 24, 48, 0.98)
        );
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff;
    }

    /* Hero section */
    .decode-hero {
        position: relative;
        overflow: hidden;
        text-align: center;
        padding: 3rem 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid var(--border);
        border-radius: 26px;
        background:
            linear-gradient(
                135deg,
                rgba(124, 58, 237, 0.18),
                rgba(37, 99, 235, 0.12)
            );
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(18px);
    }

    .decode-hero::before {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        top: -130px;
        right: -80px;
        border-radius: 50%;
        background: rgba(34, 211, 238, 0.15);
        filter: blur(15px);
    }

    .decode-badge {
        display: inline-block;
        padding: 0.45rem 1rem;
        margin-bottom: 1rem;
        color: #c4b5fd;
        background: rgba(124, 58, 237, 0.16);
        border: 1px solid rgba(167, 139, 250, 0.32);
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.12rem;
    }

    .decode-hero h1 {
        margin: 0;
        color: #ffffff;
        font-size: clamp(2.7rem, 7vw, 4.8rem);
        font-weight: 800;
        letter-spacing: -0.15rem;
    }

    .decode-hero h1 span {
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .decode-hero h2 {
        margin: 0.8rem 0;
        color: #e2e8f0;
        font-size: clamp(1rem, 2vw, 1.45rem);
        font-weight: 600;
    }

    .decode-hero p {
        margin: 0;
        color: var(--muted);
        font-size: 0.95rem;
        letter-spacing: 0.03rem;
    }

    /* Standard headings */
    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 700;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        padding: 0.4rem;
        border-radius: 18px;
    }

    [data-testid="stFileUploaderDropzone"] {
        min-height: 130px;
        background: rgba(17, 25, 46, 0.75);
        border: 1.5px dashed rgba(96, 165, 250, 0.55);
        border-radius: 18px;
        transition: all 0.25s ease;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        background: rgba(37, 99, 235, 0.12);
        border-color: #22d3ee;
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(34, 211, 238, 0.09);
    }

    /* Textarea for pasted code */
    textarea {
        color: #e2e8f0 !important;
        background: #0b1120 !important;
        border: 1px solid rgba(96, 165, 250, 0.3) !important;
        border-radius: 14px !important;
        font-family: "Consolas", monospace !important;
    }

    textarea:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15) !important;
    }

    /* Select boxes and inputs */
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        color: #f8fafc;
        background: rgba(17, 25, 46, 0.85);
        border-color: var(--border);
        border-radius: 12px;
    }

    /* Radio buttons */
    [data-testid="stRadio"] {
        padding: 0.7rem 1rem;
        background: rgba(17, 25, 46, 0.55);
        border: 1px solid var(--border);
        border-radius: 14px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        min-height: 110px;
        padding: 1.1rem 1.2rem;
        background: linear-gradient(
            145deg,
            rgba(30, 41, 69, 0.85),
            rgba(17, 25, 46, 0.78)
        );
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(34, 211, 238, 0.45);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-weight: 700;
    }

    /* Primary button */
    div.stButton > button {
        min-height: 3.2rem;
        color: #ffffff;
        background: linear-gradient(90deg, #7c3aed, #2563eb);
        border: 0;
        border-radius: 14px;
        font-weight: 700;
        letter-spacing: 0.02rem;
        box-shadow: 0 10px 28px rgba(79, 70, 229, 0.32);
        transition: all 0.25s ease;
    }

    div.stButton > button:hover {
        color: #ffffff;
        background: linear-gradient(90deg, #8b5cf6, #3b82f6);
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(79, 70, 229, 0.42);
    }

    div.stButton > button:active {
        transform: translateY(0);
    }

    /* Download button */
    div.stDownloadButton > button {
        width: 100%;
        color: #dbeafe;
        background: rgba(37, 99, 235, 0.13);
        border: 1px solid rgba(96, 165, 250, 0.45);
        border-radius: 13px;
        font-weight: 600;
    }

    div.stDownloadButton > button:hover {
        color: #ffffff;
        background: rgba(37, 99, 235, 0.25);
        border-color: #60a5fa;
    }

    /* Code preview */
    [data-testid="stCode"] {
        overflow: hidden;
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.25);
    }

    pre {
        border-radius: 16px !important;
    }

    /* Messages */
    [data-testid="stAlert"] {
        border: 1px solid var(--border);
        border-radius: 14px;
        backdrop-filter: blur(10px);
    }

    /* Dividers */
    hr {
        border-color: var(--border);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 9px;
        height: 9px;
    }

    ::-webkit-scrollbar-track {
        background: #070c18;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(#7c3aed, #2563eb);
        border-radius: 10px;
    }

    /* Hide the repeated file extensions inside the uploader */
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        display: none !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }

        .decode-hero {
            padding: 2.2rem 1rem;
            border-radius: 20px;
        }

        .decode-hero h1 {
            letter-spacing: -0.08rem;
        }
    }
    /* Keep the sidebar open control visible */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ---------- END CUSTOM DESIGN ----------

st.markdown(
    """
<style>
/* Centre the authentication section */
[data-testid="stTabs"] {
    width: 100%;
    margin-bottom: 2rem;
}

/* Tab navigation background */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    padding: 0.4rem;
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 15px;
}

/* Individual tabs */
.stTabs [data-baseweb="tab"] {
    flex: 1;
    height: 48px;
    color: #94a3b8;
    background: transparent;
    border-radius: 11px;
    font-weight: 600;
}

/* Selected tab */
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    background: linear-gradient(
        90deg,
        rgba(124, 58, 237, 0.9),
        rgba(37, 99, 235, 0.9)
    ) !important;
}

/* Remove Streamlit's default tab underline */
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}

/* Login and register cards */
[data-testid="stForm"] {
    padding: 2rem;
    margin-top: 1rem;
    background:
        linear-gradient(
            145deg,
            rgba(30, 41, 69, 0.88),
            rgba(15, 23, 42, 0.9)
        );
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 22px;
    box-shadow: 0 22px 55px rgba(0, 0, 0, 0.32);
    backdrop-filter: blur(18px);
}

/* Input labels */
[data-testid="stForm"] label {
    color: #dbeafe !important;
    font-size: 0.88rem;
    font-weight: 600;
}

/* Input containers */
[data-testid="stForm"] [data-baseweb="input"] {
    overflow: hidden;
    background: rgba(8, 15, 30, 0.8);
    border: 1px solid rgba(96, 165, 250, 0.25);
    border-radius: 12px;
    transition: all 0.2s ease;
}

/* Input focus effect */
[data-testid="stForm"] [data-baseweb="input"]:focus-within {
    border-color: #8b5cf6;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.14);
}

/* Input text */
[data-testid="stForm"] input {
    color: #ffffff !important;
}

/* Placeholder text */
[data-testid="stForm"] input::placeholder {
    color: #64748b !important;
}

/* Login and register buttons */
[data-testid="stFormSubmitButton"] button {
    width: 100%;
    min-height: 3.1rem;
    margin-top: 0.6rem;
    color: #ffffff;
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    border: none;
    border-radius: 13px;
    font-weight: 700;
    box-shadow: 0 12px 30px rgba(79, 70, 229, 0.3);
    transition: all 0.25s ease;
}

/* Button hover */
[data-testid="stFormSubmitButton"] button:hover {
    color: #ffffff;
    background: linear-gradient(90deg, #8b5cf6, #3b82f6);
    transform: translateY(-3px);
    box-shadow: 0 16px 36px rgba(79, 70, 229, 0.4);
}

/* Mobile responsiveness */
@media (max-width: 700px) {
    [data-testid="stTabs"] {
        max-width: 100%;
    }

    [data-testid="stForm"] {
        padding: 1.3rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)   


def initialize_session():
    if "review_result" not in st.session_state:
        st.session_state.review_result = ""

    if "review_file_name" not in st.session_state:
        st.session_state.review_file_name = ""

    if "review_source_code" not in st.session_state:
        st.session_state.review_source_code = ""

    if "review_language" not in st.session_state:
        st.session_state.review_language = "text"

    if "code_chat_messages" not in st.session_state:
        st.session_state.code_chat_messages = []


def clear_review_session():
    st.session_state.review_result = ""
    st.session_state.review_file_name = ""
    st.session_state.review_source_code = ""
    st.session_state.review_language = "text"
    st.session_state.code_chat_messages = []

def show_auth_page():
    st.markdown(
        """
<div class="decode-hero">
<div class="decode-badge">WELCOME TO</div>
<h1>DECODE <span>AI</span></h1>
<h2>Your Intelligent Code Review Workspace</h2>
<p>Login or create an account to continue</p>
</div>
""",
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["🔐 Login", "✨ Register"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input(
                "Email address",
                placeholder="Enter your email",
            )

            login_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            login_button = st.form_submit_button(
                "Login to DECODE AI",
                use_container_width=True,
            )

            if login_button:
                user = authenticate_user(
                    login_email,
                    login_password,
                )

                if user:
                    st.session_state.current_user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email address or password.")

    with register_tab:
        with st.form("register_form"):
            register_name = st.text_input(
                "Full name",
                placeholder="Enter your name",
            )

            register_email = st.text_input(
                "Email address",
                placeholder="Enter your email",
            )

            register_password = st.text_input(
                "Create password",
                type="password",
                placeholder="Minimum 8 characters",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Enter the password again",
            )

            register_button = st.form_submit_button(
                "Create Account",
                use_container_width=True,
            )

            if register_button:
                if register_password != confirm_password:
                    st.error("The passwords do not match.")

                else:
                    success, message = register_user(
                        register_name,
                        register_email,
                        register_password,
                    )

                    if success:
                        st.success(message)
                        st.info("Your account is ready. Open the Login tab.")
                    else:
                        st.error(message)


def show_dashboard_page(user):
    st.markdown(f"## 👋 Welcome back, {user['name']}")
    st.caption("Your DECODE AI review activity at a glance.")

    reviews = get_review_history(user["id"])

    if not reviews:
        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Total Reviews", "0")
        metric2.metric("Languages Used", "0")
        metric3.metric("Most Used", "—")
        st.info(
            "You have not completed any reviews yet. "
            "Open Code Reviewer to begin."
        )
        return

    language_counts = Counter(
        str(review["language"]).title()
        for review in reviews
    )
    most_used_language = language_counts.most_common(1)[0][0]
    latest_review = reviews[0]

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Total Reviews", len(reviews))
    metric2.metric("Languages Used", len(language_counts))
    metric3.metric("Most Used", most_used_language)
    metric4.metric(
        "Latest Review",
        str(latest_review["created_at"])[:10],
    )

    st.markdown("### 📊 Reviews by Language")
    chart_data = {
        "Language": list(language_counts.keys()),
        "Reviews": list(language_counts.values()),
    }
    st.bar_chart(
        chart_data,
        x="Language",
        y="Reviews",
        color="#7c3aed",
        height=320,
    )

    st.markdown("### 🕒 Recent Activity")
    recent_reviews = [
        {
            "File": review["file_name"],
            "Language": str(review["language"]).title(),
            "Reviewed On": review["created_at"],
        }
        for review in reviews[:5]
    ]
    st.dataframe(
        recent_reviews,
        width="stretch",
        hide_index=True,
    )


def show_quality_scores(scores):
    if not scores:
        st.info("Quality scores were not returned for this review.")
        return

    overall_score = scores.get("overall", 0)
    st.metric("Overall Code Quality", f"{overall_score}/100")
    st.progress(overall_score / 100)

    score_names = [
        ("Readability", "readability"),
        ("Correctness", "correctness"),
        ("Performance", "performance"),
        ("Security", "security"),
        ("Maintainability", "maintainability"),
    ]
    columns = st.columns(len(score_names))

    for column, (label, key) in zip(columns, score_names):
        score = scores.get(key, 0)
        column.metric(label, f"{score}/100")
        column.progress(score / 100)


def improved_file_name(file_name):
    path = Path(file_name)
    return f"{path.stem}_improved{path.suffix}"


def show_history_page(user):
    st.markdown("## 📚 Review History")
    st.caption("View and download your previous DECODE AI reviews.")

    reviews = get_review_history(user["id"])

    if not reviews:
        st.info("You have not saved any code reviews yet.")
        return

    st.metric("Total Saved Reviews", len(reviews))

    for review in reviews:
        title = (
            f"📝 {review['file_name']} • "
            f"{review['language']} • "
            f"{review['created_at']}"
        )

        with st.expander(title):
            improved_code = extract_improved_code(review["review_text"])
            quality_scores = parse_quality_scores(review["review_text"])
            review_tab, quality_tab, code_tab, improved_tab = st.tabs(
                [
                    "✨ AI Review",
                    "💯 Quality",
                    "💻 Submitted Code",
                    "✅ Improved Code",
                ]
            )

            with review_tab:
                st.markdown(review["review_text"])

                st.download_button(
                    "⬇️ Download Review",
                    data=review["review_text"],
                    file_name=f"decode_review_{review['id']}.md",
                    mime="text/markdown",
                    key=f"download_review_{review['id']}",
                    use_container_width=True,
                )

            with quality_tab:
                show_quality_scores(quality_scores)

            with code_tab:
                st.code(
                    review["code_text"],
                    language=review["language"].lower(),
                )

            with improved_tab:
                if improved_code:
                    st.code(
                        improved_code,
                        language=review["language"].lower(),
                        line_numbers=True,
                    )
                    st.download_button(
                        "⬇️ Download Corrected Code",
                        data=improved_code,
                        file_name=improved_file_name(
                            review["file_name"]
                        ),
                        mime="text/plain",
                        key=f"download_code_{review['id']}",
                        use_container_width=True,
                    )
                else:
                    st.info(
                        "No improved code block was found in this review."
                    )

def main():
    if st.session_state.current_user is None:
        show_auth_page()
        return

    user = st.session_state.current_user
    initialize_session()

    user_column, logout_column = st.columns([5, 1])

    with user_column:
        st.markdown(f"### 👋 Hi, {user['name']}")
        st.caption(user["email"])

    with logout_column:
        if st.button(
            "Logout",
            use_container_width=True,
            key="top_logout_button",
        ):
            clear_review_session()
            st.session_state.current_user = None
            st.rerun()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🧑‍💻 Code Reviewer",
            "📚 Review History",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="main_page_navigation",
    )

    if page == "🏠 Dashboard":
        show_dashboard_page(user)
        return

    if page == "📚 Review History":
        show_history_page(user)
        return

    st.markdown(
    """
    <div class="decode-hero">
        <div class="decode-badge">AI-POWERED DEVELOPER TOOL</div>
        <h1>DECODE <span>AI</span></h1>
        <h2>Intelligent Code Review, Explanation & Optimization</h2>
        <p>Detect • Explain • Correct • Optimize • Debug • Enhance</p>
    </div>
    """,
    unsafe_allow_html=True,
    )
    st.markdown(
    """
<style>
.feature-heading {
    margin: 0.5rem 0 1.2rem;
    text-align: center;
}

.feature-heading h3 {
    margin: 0;
    color: #ffffff;
    font-size: 1.35rem;
}

.feature-heading p {
    margin-top: 0.4rem;
    color: #94a3b8;
    font-size: 0.9rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.feature-card {
    padding: 1.4rem;
    background: linear-gradient(
        145deg,
        rgba(30, 41, 69, 0.85),
        rgba(15, 23, 42, 0.85)
    );
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 18px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
    transition: all 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    border-color: #22d3ee;
    box-shadow: 0 16px 35px rgba(34, 211, 238, 0.12);
}

.feature-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    margin-bottom: 0.9rem;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    border-radius: 14px;
    font-size: 1.35rem;
}

.feature-card h4 {
    margin: 0 0 0.5rem;
    color: #f8fafc;
    font-size: 1rem;
}

.feature-card p {
    margin: 0;
    color: #94a3b8;
    font-size: 0.84rem;
    line-height: 1.5;
}

.language-box {
    padding: 1rem;
    margin-bottom: 1.7rem;
    text-align: center;
    background: rgba(17, 25, 46, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
}

.language-title {
    margin-bottom: 0.8rem;
    color: #c4b5fd;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08rem;
}

.language-pill {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    margin: 0.2rem;
    color: #dbeafe;
    background: rgba(37, 99, 235, 0.14);
    border: 1px solid rgba(96, 165, 250, 0.25);
    border-radius: 50px;
    font-size: 0.72rem;
}

@media (max-width: 768px) {
    .feature-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<div class="feature-heading">
<h3>Everything You Need to Improve Your Code</h3>
<p>A simple three-step intelligent code-review workflow.</p>
</div>

<div class="feature-grid">
<div class="feature-card">
<div class="feature-icon">📤</div>
<h4>Upload or Paste</h4>
<p>Provide a supported source-code file or paste your program directly.</p>
</div>

<div class="feature-card">
<div class="feature-icon">🧠</div>
<h4>Intelligent Analysis</h4>
<p>AI detects bugs, explains logic and identifies possible improvements.</p>
</div>

<div class="feature-card">
<div class="feature-icon">✨</div>
<h4>Improved Code</h4>
<p>Receive corrected code, optimization notes and a downloadable review.</p>
</div>
</div>

<div class="language-box">
<div class="language-title">16 SUPPORTED LANGUAGES</div>
<span class="language-pill">Python</span>
<span class="language-pill">Java</span>
<span class="language-pill">JavaScript</span>
<span class="language-pill">TypeScript</span>
<span class="language-pill">C</span>
<span class="language-pill">C++</span>
<span class="language-pill">C#</span>
<span class="language-pill">HTML</span>
<span class="language-pill">CSS</span>
<span class="language-pill">SQL</span>
<span class="language-pill">PHP</span>
<span class="language-pill">Go</span>
<span class="language-pill">Ruby</span>
<span class="language-pill">Rust</span>
<span class="language-pill">Kotlin</span>
<span class="language-pill">Swift</span>
</div>
""",
    unsafe_allow_html=True,
)

    input_method = st.radio(
        "How would you like to provide the code?",
        ["Upload a file", "Paste code"],
        horizontal=True,
    )

    file_name = ""
    code_text = ""

    if input_method == "Upload a file":
        uploaded_file = st.file_uploader(
            "Upload your code file",
            type=[
                extension.replace(".", "")
                for extension in SUPPORTED_EXTENSIONS
            ],
        )

        if uploaded_file is not None:
            file_name = uploaded_file.name
            code_text = uploaded_file.getvalue().decode(
                "utf-8",
                errors="replace",
            )

    else:
        language = st.selectbox(
            "Select the programming language",
            [
                 "Python",
                 "Java",
                "JavaScript",
                "TypeScript",
                "C",
                "C++",
                "C#",
                "HTML",
                "CSS",
                "SQL",
                "PHP",
                "Go",
                "Ruby",
                "Rust",
                "Kotlin",
                "Swift",
            ],
        )

        file_names = {
            "Python": "pasted_code.py",
            "Java": "PastedCode.java",
            "JavaScript": "pasted_code.js",
            "TypeScript": "pasted_code.ts",
            "C": "pasted_code.c",
            "C++": "pasted_code.cpp",
            "C#": "PastedCode.cs",
            "HTML": "pasted_code.html",
            "CSS": "pasted_code.css",
            "SQL": "pasted_code.sql",
            "PHP": "pasted_code.php",
            "Go": "pasted_code.go",
            "Ruby": "pasted_code.rb",
            "Rust": "pasted_code.rs",
            "Kotlin": "PastedCode.kt",
            "Swift": "PastedCode.swift",
        }

        file_name = file_names[language]

        code_text = st.text_area(
            "Paste your code here",
            height=300,
            placeholder="Enter the code you want DECODE AI to review...",
        )

    if code_text.strip():
        extension = Path(file_name).suffix.lower()
        detected_language = SUPPORTED_EXTENSIONS[extension]

        column1, column2, column3 = st.columns(3)

        column1.metric(
            "Language",
            detected_language.title(),
        )

        column2.metric(
            "Lines",
            len(code_text.splitlines()),
        )

        column3.metric(
            "Characters",
            len(code_text),
        )

        st.subheader("Input Code")

        st.code(
            code_text,
            language=detected_language,
            line_numbers=True,
        )

 
    if st.button(
        "✨ Review Code",
        type="primary",
        use_container_width=True,
        disabled=not bool(code_text.strip()),
        key="main_review_button",
    ):
        with st.spinner("DECODE AI is reviewing your code..."):
            try:
                extension = Path(file_name).suffix.lower()
                detected_language = SUPPORTED_EXTENSIONS[extension]

                review = review_code(
                    file_name=file_name,
                    code_text=code_text,
                )

                save_review(
                    user_id=user["id"],
                    file_name=file_name,
                    language=detected_language,
                    code_text=code_text,
                    review_text=review,
                )

                # These names must match the display section below
                st.session_state.review_result = review
                st.session_state.review_file_name = file_name
                st.session_state.review_source_code = code_text
                st.session_state.review_language = detected_language
                st.session_state.code_chat_messages = []

                st.success("Review completed and saved!")

            except Exception as exc:
                st.error(f"Code review failed: {exc}")


    if st.session_state.review_result:
        st.divider()
        st.subheader("AI Code Review Results")

        improved_code = extract_improved_code(
            st.session_state.review_result
        )
        quality_scores = parse_quality_scores(
            st.session_state.review_result
        )
        original_code = st.session_state.review_source_code
        reviewed_language = st.session_state.review_language
        reviewed_file_name = st.session_state.review_file_name

        review_tab, quality_tab, comparison_tab = st.tabs(
            [
                "✨ Complete Review",
                "💯 Quality Score",
                "🔄 Before vs Improved",
            ]
        )

        with review_tab:
            st.markdown(st.session_state.review_result)

            download_name = (
                f"{Path(reviewed_file_name).stem}_review.md"
            )
            st.download_button(
                label="⬇️ Download Review",
                data=st.session_state.review_result,
                file_name=download_name,
                mime="text/markdown",
                use_container_width=True,
                key="download_current_review",
            )

        with quality_tab:
            show_quality_scores(quality_scores)

        with comparison_tab:
            if improved_code:
                before_column, after_column = st.columns(2)

                with before_column:
                    st.markdown("#### Before")
                    st.code(
                        original_code,
                        language=reviewed_language,
                        line_numbers=True,
                    )

                with after_column:
                    st.markdown("#### Improved")
                    st.code(
                        improved_code,
                        language=reviewed_language,
                        line_numbers=True,
                    )

                st.markdown("#### Line-by-Line Changes")
                diff_text = "\n".join(
                    unified_diff(
                        original_code.splitlines(),
                        improved_code.splitlines(),
                        fromfile=f"original/{reviewed_file_name}",
                        tofile=f"improved/{reviewed_file_name}",
                        lineterm="",
                    )
                )
                st.code(
                    diff_text or "No textual differences found.",
                    language="diff",
                )

                st.download_button(
                    label="⬇️ Download Corrected Code",
                    data=improved_code,
                    file_name=improved_file_name(
                        reviewed_file_name
                    ),
                    mime="text/plain",
                    use_container_width=True,
                    key="download_current_improved_code",
                )
            else:
                st.info(
                    "The AI response did not contain an improved code block."
                )

        st.markdown("### 💬 Ask About This Code")
        st.caption(
            "Ask a follow-up question about the reviewed program or "
            "the suggested improvements."
        )

        for message in st.session_state.code_chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input(
            "Ask a question about this code...",
            key="code_follow_up_question",
        )

        if question:
            st.session_state.code_chat_messages.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            try:
                with st.spinner("DECODE AI is preparing an answer..."):
                    answer = ask_about_code(
                        file_name=reviewed_file_name,
                        code_text=original_code,
                        review_text=st.session_state.review_result,
                        question=question,
                    )
                st.session_state.code_chat_messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )
            except Exception as exc:
                st.session_state.code_chat_messages.append(
                    {
                        "role": "assistant",
                        "content": f"Unable to answer: {exc}",
                    }
                )

            st.rerun()

        if st.button("Clear Review", key="clear_current_review"):
            clear_review_session()
            st.rerun()


if __name__ == "__main__":
    main()