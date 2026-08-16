from app.providers import HEURISTIC_ID, PROVIDERS, default_provider, is_configured, list_providers


def _clear_all_provider_keys(monkeypatch):
    for info in PROVIDERS.values():
        monkeypatch.delenv(info["env"], raising=False)


def test_default_provider_is_heuristic_when_nothing_configured(monkeypatch):
    _clear_all_provider_keys(monkeypatch)
    assert default_provider() == HEURISTIC_ID


def test_default_provider_picks_first_configured(monkeypatch):
    _clear_all_provider_keys(monkeypatch)
    monkeypatch.setenv(PROVIDERS["deepseek"]["env"], "test-key")
    assert default_provider() == "deepseek"


def test_list_providers_reports_availability(monkeypatch):
    _clear_all_provider_keys(monkeypatch)
    monkeypatch.setenv(PROVIDERS["gpt"]["env"], "test-key")

    providers = list_providers()
    by_id = {p["id"]: p for p in providers}

    assert by_id["gpt"]["available"] is True
    assert by_id["claude"]["available"] is False
    assert by_id[HEURISTIC_ID]["available"] is True
    assert is_configured("gpt") is True
    assert is_configured("claude") is False
