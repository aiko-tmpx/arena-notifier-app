import pytest
from localization import LOCALIZATION, t, get_supported_languages


def test_supported_languages():
    langs = get_supported_languages()
    assert "en" in langs
    assert "ru" in langs


def test_localization_keys_parity():
    en_keys = set(LOCALIZATION["en"].keys())
    ru_keys = set(LOCALIZATION["ru"].keys())
    
    missing_in_ru = en_keys - ru_keys
    missing_in_en = ru_keys - en_keys
    
    assert not missing_in_ru, f"Keys missing in Russian translation: {missing_in_ru}"
    assert not missing_in_en, f"Keys missing in English translation: {missing_in_en}"


def test_translation_function():
    # English test
    assert t("app_title", "en") == "AikoArenaNotifier"
    assert t("status_idle", "en") == "IDLE"
    assert t("status_scanning", "en") == "SCANNING"
    
    # Russian test
    assert t("status_idle", "ru") == "ОЖИДАНИЕ"
    assert t("status_scanning", "ru") == "СКАНИРОВАНИЕ"


def test_translation_fallback():
    # Unknown language falls back to English
    assert t("status_idle", "fr") == "IDLE"
    
    # Unknown key returns key itself
    assert t("non_existent_key_12345", "en") == "non_existent_key_12345"


def test_guide_steps_present():
    for lang in ("en", "ru"):
        assert "guide_step1_title" in LOCALIZATION[lang]
        assert "guide_step1_body" in LOCALIZATION[lang]
        assert "guide_step2_title" in LOCALIZATION[lang]
        assert "guide_step2_body" in LOCALIZATION[lang]
        assert "guide_step3_title" in LOCALIZATION[lang]
        assert "guide_step3_body" in LOCALIZATION[lang]
        assert "guide_step4_title" in LOCALIZATION[lang]
        assert "guide_step4_body" in LOCALIZATION[lang]
