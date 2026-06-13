import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://cinemax-movie-recommender.onrender.com" or "http://192.168.1.33:8501"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

# =============================
# STYLES
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.block-container {
    padding-top: 0rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Hero Banner */
.hero {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: -1px;
}
.hero p {
    color: #a0a0c0;
    font-size: 1.05rem;
    margin-top: 0.5rem;
}
.hero span {
    color: #f5a623;
}

/* Section headers */
.section-header {
    font-size: 1.2rem;
    font-weight: 600;
    color: #e0e0e0;
    border-left: 4px solid #f5a623;
    padding-left: 12px;
    margin: 1.5rem 0 1rem 0;
}

/* Movie cards */
.movie-card {
    background: #1a1a2e;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #2a2a4a;
    transition: transform 0.2s;
    height: 100%;
}
.movie-title {
    font-size: 0.82rem;
    color: #d0d0e8;
    line-height: 1.2rem;
    height: 2.4rem;
    overflow: hidden;
    margin-top: 6px;
    font-weight: 500;
}
.small-muted {
    color: #7878a0;
    font-size: 0.88rem;
}

/* Category pills */
.pill {
    display: inline-block;
    background: #2a2a4a;
    color: #a0a0c0;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    margin: 3px;
    border: 1px solid #3a3a6a;
}

/* Details page */
.detail-card {
    background: #1a1a2e;
    border-radius: 16px;
    padding: 1.8rem;
    border: 1px solid #2a2a4a;
}
.movie-detail-title {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.3rem;
}
.genre-tag {
    display: inline-block;
    background: #f5a62322;
    color: #f5a623;
    border: 1px solid #f5a62355;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    margin: 2px;
    font-weight: 500;
}
.rec-section {
    background: #12122a;
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    border: 1px solid #1e1e3e;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1e1e3e;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #c0c0e0 !important;
}

/* Buttons */
.stButton > button {
    background: #f5a623 !important;
    color: #0d0d1a !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    padding: 4px 10px !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #e09518 !important;
    transform: scale(1.02);
}

/* Search input */
.stTextInput > div > div > input {
    background: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid #3a3a6a !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input::placeholder {
    color: #6060a0 !important;
}
.stSelectbox > div > div {
    background: #1a1a2e !important;
    border: 1px solid #3a3a6a !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

/* Divider */
hr { border-color: #2a2a4a !important; }

/* Image rounded */
img { border-radius: 10px !important; }

/* Back button special */
.back-btn .stButton > button {
    background: #2a2a4a !important;
    color: #c0c0e0 !important;
    border: 1px solid #3a3a6a !important;
}
</style>
""", unsafe_allow_html=True)

# =============================
# STATE + ROUTING
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols, gap="small")
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_column_width=True)
                else:
                    st.markdown(
                        "<div style='height:180px;background:#2a2a4a;border-radius:8px;"
                        "display:flex;align-items:center;justify-content:center;"
                        "color:#6060a0;font-size:2rem;'>🎬</div>",
                        unsafe_allow_html=True
                    )
                if st.button("▶ Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)
                st.markdown(f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append({
                "tmdb_id": tmdb["tmdb_id"],
                "title": tmdb.get("title") or x.get("title") or "Untitled",
                "poster_url": tmdb.get("poster_url"),
            })
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()

    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append({
                "tmdb_id": int(tmdb_id),
                "title": title,
                "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                "release_date": m.get("release_date", ""),
            })
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append({
                "tmdb_id": int(tmdb_id),
                "title": title,
                "poster_url": poster_url,
                "release_date": m.get("release_date", ""),
            })
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1.5rem 0 1rem 0;'>
        <div style='font-size:2.5rem;'>🎬</div>
        <div style='font-size:1.1rem; font-weight:700; color:#f5a623; margin-top:4px;'>CineMatch</div>
        <div style='font-size:0.75rem; color:#6060a0; margin-top:2px;'>AI Movie Recommender</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🏠  Home"):
        goto_home()

    st.markdown("<div style='margin-top:1.5rem;'>", unsafe_allow_html=True)
    st.markdown("**Browse Category**")
    home_category = st.selectbox(
        "",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<br>**Grid Columns**", unsafe_allow_html=True)
    grid_cols = st.slider("", 4, 8, 6, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown(
        "<div style='color:#404060; font-size:0.75rem; text-align:center;'>"
        "Powered by TMDB + TF-IDF</div>",
        unsafe_allow_html=True
    )


# =============================
# HOME VIEW
# =============================
if st.session_state.view == "home":

    # Hero Banner
    st.markdown("""
    <div class="hero">
        <h1>🎬 Cine<span>Match</span></h1>
        <p>Discover movies you'll love — powered by AI similarity search & TMDB</p>
    </div>
    """, unsafe_allow_html=True)

    # Search bar centered
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        typed = st.text_input(
            "",
            placeholder="🔍  Search: avenger, batman, love ...",
            label_visibility="collapsed"
        )

    st.divider()

    # SEARCH MODE
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=24)

                if suggestions:
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        selected = st.selectbox("💡 Suggestions", labels, index=0)
                    if selected != "-- Select a movie --":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("<div class='section-header'>Search Results</div>", unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED
    category_labels = {
        "trending": "🔥 Trending Today",
        "popular": "⭐ Popular",
        "top_rated": "🏆 Top Rated",
        "now_playing": "🎥 Now Playing",
        "upcoming": "📅 Upcoming",
    }
    st.markdown(
        f"<div class='section-header'>{category_labels.get(home_category, home_category)}</div>",
        unsafe_allow_html=True
    )

    home_cards, err = api_get_json("/home", params={"category": home_category, "limit": 24})
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")


# =============================
# DETAILS VIEW
# =============================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    # Back button
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← Back"):
            goto_home()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.markdown(
            "<div style='color:#7878a0; font-size:0.9rem; padding-top:0.6rem;'>Movie Details</div>",
            unsafe_allow_html=True
        )

    # Load details
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Backdrop at top (full width)
    if data.get("backdrop_url"):
        st.image(data["backdrop_url"], use_column_width=True)
        st.markdown("<div style='margin-top:-8px;'></div>", unsafe_allow_html=True)

    # Poster + Details row
    left, right = st.columns([1, 2.8], gap="large")

    with left:
        if data.get("poster_url"):
            st.image(data["poster_url"], use_column_width=True)
        else:
            st.markdown(
                "<div style='height:320px;background:#1a1a2e;border-radius:12px;"
                "display:flex;align-items:center;justify-content:center;"
                "color:#3a3a6a;font-size:3rem;'>🎬</div>",
                unsafe_allow_html=True
            )

    with right:
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)

        # Title
        st.markdown(
            f"<div class='movie-detail-title'>{data.get('title','')}</div>",
            unsafe_allow_html=True
        )

        # Release date
        release = data.get("release_date") or "—"
        st.markdown(
            f"<div class='small-muted' style='margin-bottom:12px;'>📅 {release}</div>",
            unsafe_allow_html=True
        )

        # Genre tags
        genres = data.get("genres", [])
        if genres:
            tags_html = "".join(
                [f"<span class='genre-tag'>{g['name']}</span>" for g in genres]
            )
            st.markdown(tags_html, unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

        st.divider()

        # Overview
        st.markdown(
            "<div style='color:#9090b0; font-size:0.82rem; font-weight:600; "
            "text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;'>Overview</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='color:#c0c0d8; font-size:0.95rem; line-height:1.7;'>"
            f"{data.get('overview') or 'No overview available.'}</div>",
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Recommendations
    st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
    title = (data.get("title") or "").strip()

    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown('<div class="rec-section">', unsafe_allow_html=True)
            st.markdown(
                "<div class='section-header'>🔎 Similar Movies (TF-IDF)</div>",
                unsafe_allow_html=True
            )
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="rec-section">', unsafe_allow_html=True)
            st.markdown(
                "<div class='section-header'>🎭 More Like This (Genre)</div>",
                unsafe_allow_html=True
            )
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                st.markdown('<div class="rec-section">', unsafe_allow_html=True)
                poster_grid(genre_only, cols=grid_cols, key_prefix="details_genre_fallback")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")

    st.markdown("</div>", unsafe_allow_html=True)