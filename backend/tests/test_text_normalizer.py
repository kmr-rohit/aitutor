from app.services.text_normalizer import normalize_hinglish_text


def test_normalize_common_hinglish_words() -> None:
    src = "Agar tum zyada practice karoge to matlab clarity bahut improve hogi"
    out = normalize_hinglish_text(src)
    assert "अगर" in out
    assert "ज़्यादा" in out
    assert "मतलब" in out
    assert "बहुत" in out
