"""دليل وضعيات التصوير الشعاعي — شغّله بالأمر:  streamlit run app.py"""
from pathlib import Path

import streamlit as st

from config import FOOTER_CREDIT_AR, FOOTER_CREDIT_EN, QUIZ_LENGTH
from data.exams import EXAMS, REGIONS
from diagrams import svg_data_uri
from quiz import build_questions
from translations import REGION_NAMES, TEXTS

IMG_DIR = Path(__file__).parent / "assets" / "images"

st.set_page_config(page_title="X-ray Positioning Guide", page_icon="🩻", layout="wide")

# ---------------- اللغة والتنقل ----------------
st.sidebar.markdown("### 🩻 X-ray Guide")
lang_choice = st.sidebar.radio("🌐", ["العربية", "English"], horizontal=True, key="lang_choice",
                               label_visibility="collapsed")
lang = "ar" if lang_choice == "العربية" else "en"
t = TEXTS[lang]
regions = REGION_NAMES[lang]

page = st.sidebar.radio(t["nav"], ["guide", "quiz", "about"], format_func=lambda k: t["nav_" + k], key="page")
st.sidebar.info(t["disclaimer"])

# ---------------- الشكل (CSS) ----------------
rtl_css = """
.block-container, [data-testid="stSidebarUserContent"] { direction: rtl; text-align: right; }
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label { direction: rtl; }
""" if lang == "ar" else ""

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
html, body, .stApp, .stMarkdown, button, label, p, h1, h2, h3, h4, input {{ font-family: 'Tajawal', 'Segoe UI', sans-serif; }}
.block-container {{ max-width: 1100px; padding-top: 1.5rem; }}
{rtl_css}
.hero {{
    background: linear-gradient(120deg, #0f766e 0%, #0e7490 100%); color: #fff;
    border-radius: 18px; padding: 1.6rem 1.8rem; margin-bottom: 1.2rem;
}}
.hero h1 {{ color: #fff; font-size: 2rem; margin: 0 0 .4rem; padding: 0; }}
.hero p {{ margin: 0; opacity: .92; font-size: 1.05rem; line-height: 1.8; }}
.hero .stats {{ margin-top: 1rem; display: flex; gap: .7rem; flex-wrap: wrap; }}
.hero .stat {{ background: rgba(255,255,255,.16); border-radius: 12px; padding: .35rem .9rem; font-weight: 700; }}
.exam-head {{
    border-inline-start: 6px solid #0f766e; background: #fff; border-radius: 12px;
    padding: .9rem 1.2rem; margin: 1.2rem 0 1rem; box-shadow: 0 1px 4px rgba(15,118,110,.12);
}}
.exam-head .title {{ font-size: 1.45rem; font-weight: 800; color: #0f766e; }}
.badge {{ display: inline-block; margin-top: .3rem; background: #ccfbf1; color: #0f766e;
          border-radius: 999px; padding: .1rem .8rem; font-weight: 700; font-size: .85rem; }}
.fact {{ background: #fff; border: 1px solid #cfe7e4; border-radius: 12px; padding: .7rem 1rem; margin-bottom: .6rem; }}
.fact .k {{ font-size: .82rem; font-weight: 700; color: #0e7490; margin-bottom: .15rem; }}
.fact .v {{ font-size: 1rem; line-height: 1.7; }}
.diagram img {{ width: 100%; border-radius: 14px; border: 1px solid #cfe7e4; background: #fff; }}
.small-note {{ font-size: .8rem; opacity: .7; margin-top: .3rem; }}
.footer {{ text-align: center; opacity: .65; font-size: .85rem; margin-top: 2.5rem; }}
div.stButton > button {{ border-radius: 12px; font-weight: 700; width: 100%; }}
</style>
""",
    unsafe_allow_html=True,
)


def fact(label, value):
    st.markdown(f'<div class="fact"><div class="k">{label}</div><div class="v">{value}</div></div>',
                unsafe_allow_html=True)


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
        f"""<div class="hero"><h1>🩻 {t['hero_title']}</h1><p>{t['hero_text']}</p>
        <div class="stats"><span class="stat">{len(EXAMS)} {t['stat_exams']}</span>
        <span class="stat">{len(REGIONS)} {t['stat_regions']}</span></div></div>""",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 1.4])
    query = c1.text_input(t["search_label"], placeholder=t["search_ph"]).strip().lower()
    region_key = c2.radio(
        t["region_label"], ["all"] + REGIONS, horizontal=True,
        format_func=lambda k: t["region_all"] if k == "all" else regions[k],
    )

    shown = [
        e for e in EXAMS
        if (region_key == "all" or e["region"] == region_key)
        and (not query or query in e["ar"]["name"].lower() or query in e["en"]["name"].lower())
    ]
    if not shown:
        st.warning(t["no_results"])
        return

    if st.session_state.get("sel") not in [e["id"] for e in shown]:
        st.session_state["sel"] = None

    st.caption(f"{t['results_count']}: {len(shown)}")
    cols = st.columns(3)
    for i, e in enumerate(shown):
        is_sel = st.session_state.get("sel") == e["id"]
        if cols[i % 3].button(e[lang]["name"], key=f"btn_{e['id']}", type="primary" if is_sel else "secondary"):
            st.session_state["sel"] = e["id"]
            is_sel = True

    exam = next((e for e in shown if e["id"] == st.session_state.get("sel")), None)
    if exam is None:
        st.info(t["choose_hint"])
        return
    show_exam(exam)


def show_exam(exam):
    d = exam[lang]
    st.markdown(
        f'<div class="exam-head"><div class="title">{d["name"]}</div>'
        f'<span class="badge">{regions[exam["region"]]}</span></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown(f"**{t['diagram_title']}**")
        st.markdown(f'<div class="diagram"><img src="{svg_data_uri(exam["diagram"], exam["sid"])}" alt="diagram"></div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="small-note">{t["diagram_note"]}</div>', unsafe_allow_html=True)
        real = find_real_image(exam["id"])
        if real:
            st.image(str(real), caption=t["real_image"], use_container_width=True)
    with right:
        st.markdown(f"**{t['quick_facts']}**")
        fact(t["f_position"], d["position"])
        fact(t["f_beam"], d["beam"])
        fact(t["f_detector"], d["detector"])
        fact(t["f_cr"], d["cr"])
        fact(t["f_sid"], f"{exam['sid']} cm")

    tab_before, tab_quality = st.tabs([t["tab_before"], t["tab_quality"]])
    with tab_before:
        st.markdown(f"**{t['specific_title']}**")
        for i, item in enumerate(d["before"]):
            st.checkbox(item, key=f"chk_{exam['id']}_{lang}_s{i}")
        st.markdown(f"**{t['general_title']}**")
        for i, item in enumerate(t["general_before"]):
            st.checkbox(item, key=f"chk_{exam['id']}_{lang}_g{i}")
    with tab_quality:
        for item in d["quality"]:
            st.markdown(f"- {item}")

    st.warning(t["disclaimer"])


# ---------------- صفحة الاختبار ----------------
def quiz_page():
    st.title(f"📝 {t['quiz_title']}")
    state = st.session_state.get("quiz")
    if state is not None and state["lang"] != lang:  # تغيير اللغة يبدأ اختبار جديد
        state = None
        st.session_state.pop("quiz", None)

    if state is None:
        st.write(t["quiz_intro"])
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
    st.markdown(f"**{t['quiz_q']} {i + 1} {t['quiz_of']} {len(qs)}**")
    st.markdown(q["q"])
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
    st.title(t["about_title"])
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
