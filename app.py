"""دليل وضعيات التصوير الشعاعي — شغّله بالأمر:  streamlit run app.py"""
from pathlib import Path

import streamlit as st

from config import FOOTER_CREDIT_AR, FOOTER_CREDIT_EN, QUIZ_LENGTH
from data.exams import EXAMS, REGIONS
from diagrams import svg_data_uri
from quiz import build_questions
from translations import REGION_NAMES, TEXTS

IMG_DIR = Path(__file__).parent / "assets" / "images"

st.set_page_config(page_title="X-ray Positioning Guide", page_icon="🩻", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------- الشريط العلوي: الاسم + الثيم + اللغة ----------------
c_brand, c_theme, c_lang = st.columns([3, 1.1, 1.3])
with c_lang:
    lang_choice = st.radio("lang", ["العربية", "English"], horizontal=True, key="lang_choice",
                           label_visibility="collapsed")
with c_theme:  # ☀️ فاتح (الافتراضي) / 🌙 داكن
    theme_choice = st.radio("theme", ["☀️", "🌙"], horizontal=True, key="theme",
                            label_visibility="collapsed")
lang = "ar" if lang_choice == "العربية" else "en"
dark = theme_choice == "🌙"
t = TEXTS[lang]
regions = REGION_NAMES[lang]

# ---------------- الشكل (CSS): ألوان الفاتح والداكن كمتغيرات ----------------
LIGHT_VARS = """--bg:#ffffff; --panel:#f4f7fa; --border:#d3dce6; --text:#14212e; --muted:#5a6a7c;
  --accent:#f59e0b; --accent-text:#b45309; --on-accent:#1a1203; --tint:rgba(217,119,6,.09);
  --lightbox:#eef2f6; --glow:rgba(15,40,70,.10);"""
DARK_VARS = """--bg:#0b0f14; --panel:#131a22; --border:#243040; --text:#e6edf3; --muted:#8b9bb0;
  --accent:#f5b942; --accent-text:#f5b942; --on-accent:#0b0f14; --tint:rgba(245,185,66,.09);
  --lightbox:#e9eef3; --glow:rgba(125,170,220,.14);"""

# تعديلات إضافية في الوضع الداكن فقط (لأن ثيم ستريمليت الأساسي فاتح)
DARK_EXTRA = """
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: var(--bg) !important; }
.stApp, [data-testid="stMarkdownContainer"] { color: var(--text); }
.stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stWidgetLabel"] *, [data-testid="stExpander"] summary *, [data-testid="stCheckbox"] *,
[data-testid="stHeader"] * { color: var(--text); }
[data-baseweb="select"] > div { background: var(--panel) !important; border-color: var(--border) !important; }
[data-baseweb="select"] * { color: var(--text) !important; }
[data-baseweb="popover"], [data-baseweb="popover"] ul, [data-baseweb="popover"] li, [data-baseweb="menu"]
{ background: var(--panel) !important; color: var(--text) !important; }
[data-testid="stExpander"] details { background: var(--panel); border-color: var(--border); }
[data-testid="stAlert"] { background: var(--panel) !important; border: 1px solid var(--border); }
[data-testid="stAlert"] * { color: var(--text) !important; }
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
:root { /*VARS*/ }
html, body, .stApp, .stMarkdown, button, label, p, h1, h2, h3, h4, input, li {
    font-family: 'IBM Plex Sans Arabic', 'IBM Plex Sans', 'Segoe UI', sans-serif;
}
/*DARK*/
[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display: none; }
.block-container { max-width: 1150px; padding-top: 4.2rem; }
/*RTL*/
.brand { display: flex; align-items: center; gap: .8rem; padding: .3rem 0 .6rem; }
.brand .logo {
    width: 46px; height: 46px; border-radius: 10px; display: grid; place-items: center; font-size: 1.5rem;
    background: var(--accent); color: var(--on-accent); box-shadow: 0 4px 18px var(--glow);
}
.brand .name { font-size: 1.35rem; font-weight: 700; line-height: 1.2; }
.brand .sub { font-size: .8rem; color: var(--muted); letter-spacing: .06em; }
/* كل أزرار الاختيار (radio) تتحول لأزرار شكل حبوب */
div[role="radiogroup"] { gap: .45rem; }
div[role="radiogroup"] > label {
    background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: .45rem 1rem;
    transition: border-color .15s, background .15s;
}
div[role="radiogroup"] > label > div:first-child { display: none; }
div[role="radiogroup"] > label:hover { border-color: var(--accent); }
div[role="radiogroup"] > label:has(input:checked) { background: var(--accent); border-color: var(--accent); }
div[role="radiogroup"] > label:has(input:checked) * { color: var(--on-accent) !important; font-weight: 700; }
.title-row { display: flex; align-items: baseline; gap: .8rem; flex-wrap: wrap; margin: 1.2rem 0 .3rem; }
.title-row h1 { font-size: 1.9rem; margin: 0; padding: 0; }
.title-row .pill { border: 1px solid var(--accent-text); color: var(--accent-text); border-radius: 999px;
    padding: .05rem .8rem; font-size: .85rem; font-weight: 600; }
.lead { color: var(--muted); line-height: 1.9; margin-bottom: 1rem; }
.exam-title { font-size: 1.5rem; font-weight: 700; margin: 1.4rem 0 .2rem; }
.exam-title span { color: var(--accent-text); font-size: .95rem; font-weight: 600; margin-inline-start: .7rem; }
.lightbox {
    background: var(--lightbox); border-radius: 14px; padding: 12px; position: relative;
    border: 2px solid var(--border); box-shadow: 0 4px 30px var(--glow);
}
.lightbox img { width: 100%; display: block; border-radius: 8px; }
.lightbox .tag { position: absolute; top: 18px; inset-inline-start: 20px; background: #0b0f14; color: #f5b942;
    font-weight: 700; font-size: .72rem; padding: .1rem .55rem; border-radius: 6px; letter-spacing: .08em; }
.caption { font-size: .8rem; color: var(--muted); margin-top: .4rem; }
.spec { border: 1px solid var(--border); border-radius: 14px; overflow: hidden; background: var(--panel); }
.spec .row { display: grid; grid-template-columns: 9rem 1fr; border-bottom: 1px solid var(--border); }
.spec .row:last-child { border-bottom: none; }
.spec .k { padding: .75rem 1rem; background: var(--tint); color: var(--accent-text); font-weight: 600; font-size: .88rem; }
.spec .v { padding: .75rem 1rem; line-height: 1.8; }
.spec .hl .v { font-weight: 700; }
.qcard { background: var(--panel); border: 1px solid var(--border); border-inline-start: 5px solid var(--accent);
    border-radius: 12px; padding: 1rem 1.3rem; margin: .6rem 0 1rem; line-height: 1.9; }
.qnum { color: var(--accent-text); font-weight: 700; letter-spacing: .05em; }
.footer { text-align: center; color: var(--muted); font-size: .85rem; margin-top: 2.5rem; }
div.stButton > button { border-radius: 10px; font-weight: 700; }
div.stButton > button[kind="primary"] { background: var(--accent); border-color: var(--accent); color: var(--on-accent); }
div.stButton > button[kind="primary"] * { color: var(--on-accent) !important; }
@media (max-width: 700px) { .spec .row { grid-template-columns: 1fr; } }
</style>
"""
rtl_css = ".block-container { direction: rtl; text-align: right; }" if lang == "ar" else ""
st.markdown(
    CSS.replace("/*VARS*/", DARK_VARS if dark else LIGHT_VARS)
       .replace("/*DARK*/", DARK_EXTRA if dark else "")
       .replace("/*RTL*/", rtl_css),
    unsafe_allow_html=True,
)

with c_brand:
    st.markdown(
        f'<div class="brand"><div class="logo">🩻</div><div><div class="name">{t["brand"]}</div>'
        f'<div class="sub">{t["brand_sub"]}</div></div></div>',
        unsafe_allow_html=True,
    )

page = st.radio(t["nav"], ["guide", "quiz", "about"], format_func=lambda k: t["nav_" + k],
                horizontal=True, key="page", label_visibility="collapsed")


def find_real_image(exam_id):
    """لو فيه صورة حقيقية باسم <id>.jpg/.png في assets/images بتتعرض تلقائيًا."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = IMG_DIR / f"{exam_id}.{ext}"
        if p.exists():
            return p
    return None


# ---------------- صفحة الدليل ----------------
def guide_page():
    st.markdown(
        f'<div class="title-row"><h1>{t["hero_title"]}</h1>'
        f'<span class="pill">{len(EXAMS)} {t["stat_exams"]}</span>'
        f'<span class="pill">{len(REGIONS)} {t["stat_regions"]}</span></div>'
        f'<div class="lead">{t["hero_text"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"**{t['region_label']}**")
    region_key = st.radio("region", ["all"] + REGIONS, horizontal=True, key="region",
                          format_func=lambda k: t["region_all"] if k == "all" else regions[k],
                          label_visibility="collapsed")
    shown = [e for e in EXAMS if region_key == "all" or e["region"] == region_key]

    by_name = {e[lang]["name"]: e for e in shown}  # الأسماء فريدة داخل كل لغة
    name = st.selectbox(t["select_exam"], list(by_name), key=f"exam_{region_key}_{lang}")
    show_exam(by_name[name])


def show_exam(exam):
    d = exam[lang]
    st.markdown(f'<div class="exam-title">{d["name"]}<span>{regions[exam["region"]]}</span></div>',
                unsafe_allow_html=True)

    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(
            f'<div class="lightbox"><div class="tag">{t["diagram_title"]}</div>'
            f'<img src="{svg_data_uri(exam["diagram"], exam["sid"])}" alt="diagram"></div>'
            f'<div class="caption">{t["diagram_note"]}</div>',
            unsafe_allow_html=True,
        )
        real = find_real_image(exam["id"])
        if real:
            st.image(str(real), caption=t["real_image"], use_container_width=True)
    with right:
        rows = [("f_position", d["position"], ""), ("f_beam", d["beam"], ""), ("f_detector", d["detector"], ""),
                ("f_cr", d["cr"], "hl"), ("f_sid", f"{exam['sid']} cm", "hl")]
        html = "".join(f'<div class="row {c}"><div class="k">{t[k]}</div><div class="v">{v}</div></div>'
                       for k, v, c in rows)
        st.markdown(f'<div class="spec">{html}</div>', unsafe_allow_html=True)

    with st.expander(t["tab_before"], expanded=True):
        st.markdown(f"**{t['specific_title']}**")
        for i, item in enumerate(d["before"]):
            st.checkbox(item, key=f"chk_{exam['id']}_{lang}_s{i}")
        st.markdown(f"**{t['general_title']}**")
        for i, item in enumerate(t["general_before"]):
            st.checkbox(item, key=f"chk_{exam['id']}_{lang}_g{i}")
    with st.expander(t["tab_quality"], expanded=True):
        for item in d["quality"]:
            st.markdown(f"- {item}")

    st.warning(t["disclaimer"])


# ---------------- صفحة الاختبار ----------------
def quiz_page():
    st.markdown(f'<div class="title-row"><h1>{t["quiz_title"]}</h1></div>', unsafe_allow_html=True)
    state = st.session_state.get("quiz")
    if state is not None and state["lang"] != lang:  # تغيير اللغة يبدأ اختبار جديد
        state = None
        st.session_state.pop("quiz", None)

    if state is None:
        st.markdown(f'<div class="lead">{t["quiz_intro"]}</div>', unsafe_allow_html=True)
        if st.button(t["quiz_start"], type="primary"):
            st.session_state["quiz"] = {
                "qs": build_questions(lang, QUIZ_LENGTH), "i": 0, "score": 0, "answered": None, "lang": lang,
            }
            st.rerun()
        return

    qs, i = state["qs"], state["i"]
    if i >= len(qs):
        pct = state["score"] / len(qs)
        st.subheader(f"{t['quiz_result']}: {state['score']} / {len(qs)}")
        st.progress(pct)
        st.success(t["quiz_excellent"] if pct >= 0.8 else t["quiz_good"] if pct >= 0.5 else t["quiz_retry"])
        if st.button(t["quiz_again"], type="primary"):
            st.session_state.pop("quiz")
            st.rerun()
        return

    q = qs[i]
    st.progress(i / len(qs))
    q_html = q["q"].replace("\n\n", "<br><br>")
    st.markdown(f'<div class="qcard"><div class="qnum">{t["quiz_q"]} {i + 1} {t["quiz_of"]} {len(qs)}</div>{q_html}</div>',
                unsafe_allow_html=True)
    choice = st.radio("answer", q["options"], index=None, key=f"q_{i}",
                      disabled=state["answered"] is not None, label_visibility="collapsed")

    if state["answered"] is None:
        if st.button(t["quiz_submit"], type="primary"):
            if choice is None:
                st.warning(t["quiz_choose"])
            else:
                state["answered"] = q["options"].index(choice)
                state["score"] += int(state["answered"] == q["answer"])
                st.rerun()
    else:
        if state["answered"] == q["answer"]:
            st.success(t["quiz_correct"])
        else:
            st.error(t["quiz_wrong"])
        st.info(f"**{t['quiz_right_answer']}:** {q['options'][q['answer']]}\n\n**{t['quiz_exam']}:** {q['exam_name']}")
        last = i + 1 == len(qs)
        if st.button(t["quiz_finish"] if last else t["quiz_next"], type="primary"):
            state["i"] += 1
            state["answered"] = None
            st.rerun()


# ---------------- صفحة عن المشروع ----------------
def about_page():
    st.markdown(f'<div class="title-row"><h1>{t["about_title"]}</h1></div>', unsafe_allow_html=True)
    st.write(t["about_intro"])
    st.subheader(t["about_how_title"])
    st.markdown("\n".join(f"{n}. {s}" for n, s in enumerate(t["about_how"], 1)))
    st.subheader(t["about_tech_title"])
    st.write(t["about_tech"])
    st.subheader(t["about_logic_title"])
    st.markdown("\n".join(f"- {s}" for s in t["about_logic"]))
    st.subheader(t["about_limits_title"])
    st.markdown("\n".join(f"- {s}" for s in t["about_limits"]))
    st.warning(t["disclaimer"])


if page == "guide":
    guide_page()
elif page == "quiz":
    quiz_page()
else:
    about_page()

credit = FOOTER_CREDIT_AR if lang == "ar" else FOOTER_CREDIT_EN
if credit:
    st.markdown(f'<div class="footer">{credit}</div>', unsafe_allow_html=True)
