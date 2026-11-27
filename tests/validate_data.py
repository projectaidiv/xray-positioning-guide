"""يتأكد إن بيانات كل الفحوصات كاملة وسليمة. شغّله قبل الرفع:  python tests/validate_data.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.exams import EXAMS, REGIONS  # noqa: E402
from diagrams import build_svg  # noqa: E402
from translations import REGION_NAMES  # noqa: E402

FIELDS = ["name", "position", "beam", "detector", "cr"]
LISTS = ["before", "quality"]
errors, seen = [], set()

for e in EXAMS:
    eid = e.get("id", "?")
    if eid in seen:
        errors.append(f"{eid}: id مكرر")
    seen.add(eid)
    if e.get("region") not in REGIONS:
        errors.append(f"{eid}: region غير صحيح")
    if not isinstance(e.get("sid"), int):
        errors.append(f"{eid}: sid لازم يكون رقم")
    for lang in ("ar", "en"):
        d = e.get(lang, {})
        for f in FIELDS:
            if not str(d.get(f, "")).strip():
                errors.append(f"{eid}/{lang}: الحقل {f} فاضي")
        for f in LISTS:
            if not d.get(f):
                errors.append(f"{eid}/{lang}: القائمة {f} فاضية")
    try:
        build_svg(e["diagram"], e["sid"])
    except Exception as ex:  # noqa: BLE001
        errors.append(f"{eid}: مشكلة في الرسم ({ex})")

for lang in ("ar", "en"):
    for r in REGIONS:
        if r not in REGION_NAMES[lang]:
            errors.append(f"اسم المنطقة {r} ناقص في {lang}")

missing = [e["id"] for e in EXAMS if not any((Path(__file__).resolve().parents[1] / "assets" / "images" / f"{e['id']}.{x}").exists() for x in ("jpg", "jpeg", "png", "webp"))]
if missing:
    print("ℹ️ فحوصات بدون صورة (هتظهر برسم SVG بديل):", ", ".join(missing))

if errors:
    print("❌ مشاكل:")
    print("\n".join(" - " + m for m in errors))
    sys.exit(1)
print(f"✅ البيانات سليمة: {len(EXAMS)} فحص، {len(REGIONS)} مناطق.")
