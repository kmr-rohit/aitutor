import pytest

from app.services.text_refiner import refine_hinglish_text


@pytest.mark.asyncio
async def test_refiner_falls_back_to_normalizer_without_openai() -> None:
    src = "Agar zyada traffic ho to matlab caching useful hai"
    out = await refine_hinglish_text(src)
    assert "अगर" in out
    assert "ज़्यादा" in out
    assert "मतलब" in out
