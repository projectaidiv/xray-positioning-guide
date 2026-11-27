"""منطق الاختبار — بيتولّد من نفس بيانات الفحوصات (مفيش أسئلة مكتوبة يدويًا)."""
import random

from data.exams import EXAMS

SID_OPTIONS = [100, 120, 150, 180]


def _pick_options(correct, pool, rng, k=4):
    """يرجّع k اختيارات مختلفة تحتوي الإجابة الصحيحة."""
    others = [p for p in dict.fromkeys(pool) if p != correct]
    rng.shuffle(others)
    opts = [correct] + others[: k - 1]
    rng.shuffle(opts)
    return opts


def build_questions(lang: str, n: int = 10, seed: int | None = None):
    rng = random.Random(seed)
    exams = rng.sample(EXAMS, k=min(n, len(EXAMS)))
    questions = []
    for ex in exams:
        d = ex[lang]
        kind = rng.choice(["cr", "sid", "position"])
        if kind == "cr":
            correct = d["cr"]
            opts = _pick_options(correct, [e[lang]["cr"] for e in EXAMS], rng)
            q = {"ar": f"ما نقطة تمركز الشعاع المركزي (CR) في فحص: {d['name']}؟",
                 "en": f"Where is the central ray (CR) centred for: {d['name']}?"}[lang]
        elif kind == "sid":
            correct = f"{ex['sid']} cm"
            opts = [f"{s} cm" for s in SID_OPTIONS]
            q = {"ar": f"ما مسافة المصدر للديتكتور (SID) المناسبة لفحص: {d['name']}؟",
                 "en": f"What is the appropriate SID for: {d['name']}?"}[lang]
        else:
            correct = d["name"]
            opts = _pick_options(correct, [e[lang]["name"] for e in EXAMS], rng)
            q = {"ar": f"أي فحص تنطبق عليه هذه الوضعية؟\n\n«{d['position']}»",
                 "en": f"Which exam does this patient position belong to?\n\n\u201c{d['position']}\u201d"}[lang]
        questions.append({"q": q, "options": opts, "answer": opts.index(correct),
                          "exam_id": ex["id"], "exam_name": d["name"]})
    return questions
