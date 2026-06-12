# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test the Client class."""

from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from frequenz.api.common.v1 import location_pb2
from frequenz.api.weather.v1 import weather_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from pytest import fixture

from frequenz.client.weather._client import Client
from frequenz.client.weather._types import ForecastFeature, Forecasts, Location


class TestClient:
    """Test the Client."""

    @fixture
    def mock_stub(self) -> AsyncMock:
        """Create a mock gRPC stub."""
        return AsyncMock()

    @fixture
    def client(self, mock_stub: AsyncMock) -> Client:
        """Create a client with a mock stub."""
        client = Client(
            "test-server",
            auth_key="test-auth-key",
            sign_secret="test-sign-secret",
            connect=False,
        )
        # pylint: disable=protected-access
        client._stub = mock_stub
        client._channel = MagicMock()
        # pylint: enable=protected-access
        return client

    def test_init_requires_auth_key(self) -> None:
        """Test that the client requires an auth key."""
        with pytest.raises(TypeError, match="auth_key"):
            # pylint: disable-next=missing-kwoa
            Client(  # type: ignore[call-arg]
                "test-server",
                sign_secret="test-sign-secret",
                connect=False,
            )

    def test_init_requires_sign_secret(self) -> None:
        """Test that the client requires a signing secret."""
        with pytest.raises(TypeError, match="sign_secret"):
            # pylint: disable-next=missing-kwoa
            Client(  # type: ignore[call-arg]
                "test-server",
                auth_key="test-auth-key",
                connect=False,
            )

    @fixture
    def sample_historical_response(
        self,
    ) -> weather_pb2.ReceiveHistoricalWeatherForecastResponse:
        """Create a sample historical weather forecast response."""
        creation_ts = Timestamp()
        creation_ts.FromDatetime(datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc))

        valid_ts = Timestamp()
        valid_ts.FromDatetime(datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc))

        location = location_pb2.Location(
            latitude=42.0, longitude=18.0, country_code="US"
        )

        feature_forecast = weather_pb2.LocationForecast.Forecasts.FeatureForecast(
            feature=weather_pb2.ForecastFeature.FORECAST_FEATURE_TEMPERATURE_2_METRE,
            value=25.5,
        )

        forecasts = weather_pb2.LocationForecast.Forecasts(
            valid_time=valid_ts, features=[feature_forecast]
        )

        location_forecast = weather_pb2.LocationForecast(
            location=location, forecasts=[forecasts], create_time=creation_ts
        )

        response = weather_pb2.ReceiveHistoricalWeatherForecastResponse(
            location_forecasts=[location_forecast]
        )

        return response

    @pytest.mark.asyncio
    async def test_stream_historical_forecast(
        self,
        client: Client,
        mock_stub: AsyncMock,
        sample_historical_response: weather_pb2.ReceiveHistoricalWeatherForecastResponse,
    ) -> None:
        """Test basic functionality of the historical forecast of the client."""
        locations = [Location(latitude=42.0, longitude=18.0, country_code="US")]
        features = [ForecastFeature.TEMPERATURE_2_METRE]
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)

        # Mock the gRPC stream to return our sample response
        async def mock_stream(
            _request: object,
        ) -> AsyncGenerator[weather_pb2.ReceiveHistoricalWeatherForecastResponse, None]:
            yield sample_historical_response

        # Mock the stub method to return the async generator
        mock_stub.ReceiveHistoricalWeatherForecast = mock_stream

        result = await client.stream_historical_forecast(
            locations=locations,
            features=features,
            start=start,
            end=end,
        )

        assert result is not None

        forecasts = []
        async for forecast in result:
            forecasts.append(forecast)

        assert len(forecasts) == 1
        assert isinstance(forecasts[0], Forecasts)

        # pylint: disable=protected-access
        assert forecasts[0]._forecasts_pb == sample_historical_response
        # pylint: enable=protected-access

    @pytest.mark.asyncio
    async def test_stream_historical_forecast_multiple_messages(
        self,
        client: Client,
        mock_stub: AsyncMock,
        sample_historical_response: weather_pb2.ReceiveHistoricalWeatherForecastResponse,
    ) -> None:
        """Test the historical forecast method with multiple messages."""
        locations = [Location(latitude=42.0, longitude=18.0, country_code="US")]
        features = [ForecastFeature.TEMPERATURE_2_METRE]
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)

        second_response = weather_pb2.ReceiveHistoricalWeatherForecastResponse()
        second_response.CopyFrom(sample_historical_response)

        # Mock the gRPC stream to return multiple responses
        async def mock_stream(
            _request: object,
        ) -> AsyncGenerator[weather_pb2.ReceiveHistoricalWeatherForecastResponse, None]:
            yield sample_historical_response
            yield second_response

        # Mock the stub method to return the async generator
        mock_stub.ReceiveHistoricalWeatherForecast = mock_stream

        result = await client.stream_historical_forecast(
            locations=locations,
            features=features,
            start=start,
            end=end,
        )

        forecasts = []
        async for forecast in result:
            forecasts.append(forecast)

        assert len(forecasts) == 2
        assert isinstance(forecasts[0], Forecasts)
        assert isinstance(forecasts[1], Forecasts)

        # pylint: disable=protected-access
        assert forecasts[0]._forecasts_pb == sample_historical_response
        assert forecasts[1]._forecasts_pb == second_response
        # pylint: enable=protected-access
