from burnorm import convert
from burnorm.zg_repair import repair_zawgyi


def test_repair_space_before_marks():
    assert " " not in repair_zawgyi("န႔ ဲ")
    assert repair_zawgyi("န႔ ဲ") == "နဲ႔"


def test_repair_tekwa():
    assert repair_zawgyi("ေတကြ") == "ေတြ"
    assert repair_zawgyi("ေတကြို") == "ေတြကို"


def test_repair_keeps_word_spaces():
    out = repair_zawgyi("အေၾကာင္း ပတ္သက္")
    assert " " in out


def test_user_sample_convert_improves():
    raw = (
        "Artificial Neural Network အေၾကာင္းန႔ ဲ ပတ္သက္လို႔ အရင္ကလဲ "
        "ဟိုတစ္စ ဒီတစ္စ ေရးခ့ဖဲ ူးျပီးပါျပီ...\n"
        "ဒါေပမယ့္ အ့ဒဲ ါေတကြ ANN ရ႔ ဲ အတြင္းပိုင္းက "
        "အလုပ္လုပ္ပုံေတကြ ို ေျပာထားတာေတကြ မ်ားပါတယ္..."
    )
    out = convert(raw, auto=True)
    assert "နဲ့" in out
    assert "တွေ" in out
    assert "ရဲ့" in out
    assert "ရေးခဲ့ဖူး" in out
    assert "တေကွ" not in out
