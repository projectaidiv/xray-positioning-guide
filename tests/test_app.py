"""اختبار تشغيل سريع للموقع بدون متصفح:  python tests/test_app.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402


def run():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not at.exception, at.exception
    for lang in ("العربية", "English"):
        at.radio(key="lang_choice").set_value(lang).run()
        # الدليل: اضغط على أول فحص
        at.radio(key="page").set_value("guide").run()
        assert len(at.selectbox) == 1
        for k in range(len(at.selectbox[0].options)):   # جرّب كل الفحوصات
            at.selectbox[0].select_index(k).run()
            assert not at.exception, at.exception
        assert not at.exception, at.exception
        # الاختبار: ابدأ وأجب على كل الأسئلة
        at.radio(key="page").set_value("quiz").run()
        at.button[0].click().run()
        for i in range(10):
            at.radio(key=f"q_{i}").set_value(at.radio(key=f"q_{i}").options[0]).run()
            at.button[0].click().run()   # تأكيد
            at.button[0].click().run()   # التالي
            assert not at.exception, at.exception
        assert any("/ 10" in s.value for s in at.subheader), "مفيش شاشة نتيجة"
        at.radio(key="page").set_value("about").run()
        assert not at.exception, at.exception
    print("✅ الموقع شغال: الدليل والاختبار وعن المشروع بالعربي والإنجليزي.")


if __name__ == "__main__":
    run()
