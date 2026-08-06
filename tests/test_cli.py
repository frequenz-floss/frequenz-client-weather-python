# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Test the weather CLI."""

import sys
from datetime import datetime, timezone

import pytest

from frequenz.client.weather.cli import __main__ as cli


def test_main_requires_auth_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the CLI requires an auth key."""
    monkeypatch.delenv("WEATHER_API_AUTH_KEY", raising=False)
    monkeypatch.delenv("WEATHER_API_SIGN_SECRET", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "weather-cli",
            "--url",
            "grpc://weather.example.com:443",
            "--sign-secret",
            "test-sign-secret",
            "--mode",
            "live",
            "--feature",
            "TEMPERATURE_2_METRE",
            "--location",
            "40,15",
        ],
    )

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 2


def test_main_requires_sign_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the CLI requires a signing secret."""
    monkeypatch.delenv("WEATHER_API_AUTH_KEY", raising=False)
    monkeypatch.delenv("WEATHER_API_SIGN_SECRET", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "weather-cli",
            "--url",
            "grpc://weather.example.com:443",
            "--auth-key",
            "test-auth-key",
            "--mode",
            "live",
            "--feature",
            "TEMPERATURE_2_METRE",
            "--location",
            "40,15",
        ],
    )

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 2


def test_main_uses_environment_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the CLI reads URL and auth credentials from the environment."""
    calls: list[dict[str, object]] = []

    async def fake_run(**kwargs: object) -> None:
        calls.append(kwargs)

    monkeypatch.setenv("WEATHER_API_URL", "grpc://weather.example.com:443")
    monkeypatch.setenv("WEATHER_API_AUTH_KEY", "test-auth-key")
    monkeypatch.setenv("WEATHER_API_SIGN_SECRET", "test-sign-secret")
    monkeypatch.setattr(cli, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "weather-cli",
            "--mode",
            "historical",
            "--feature",
            "TEMPERATURE_2_METRE",
            "--location",
            "40,15",
            "--start",
            "2024-03-14T00:00:00+00:00",
            "--end",
            "2024-03-15T00:00:00+00:00",
        ],
    )

    cli.main()

    assert calls == [
        {
            "service_address": "grpc://weather.example.com:443",
            "auth_key": "test-auth-key",
            "sign_secret": "test-sign-secret",
            "location": (40.0, 15.0),
            "feature_names": ["TEMPERATURE_2_METRE"],
            "start": datetime(2024, 3, 14, tzinfo=timezone.utc),
            "end": datetime(2024, 3, 15, tzinfo=timezone.utc),
            "mode": "historical",
        }
    ]
