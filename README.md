# Frequenz Weather API Client

[![Build Status](https://github.com/frequenz-floss/frequenz-client-weather-python/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-client-weather-python/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-client-weather)](https://pypi.org/project/frequenz-client-weather/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-client-weather-python/)

## Introduction

Weather API Client for Python providing access to historical and live weather forecast data.

## Supported Platforms

The following platforms are officially supported (tested):

- **Python:** 3.11
- **Operating System:** Ubuntu Linux 20.04
- **Architectures:** amd64, arm64

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).

## Usage

### Installation

```bash
pip install frequenz-client-weather
```

### Initialize the client

The Client can optionally be initialized with keep alive options.

```python
from frequenz.client.weather import Client
from frequenz.client.base.channel import ChannelOptions, KeepAliveOptions, SslOptions
from datetime import timedelta

client = Client(
    service_address,
    channel_defaults=ChannelOptions(
        ssl=SslOptions(
            enabled=False,
        ),
        keep_alive=KeepAliveOptions(
            enabled=True,
            timeout=timedelta(minutes=5),
            interval=timedelta(seconds=20),
        ),
    ),
)
```

### Get historical weather forecast

```python
from datetime import datetime
from frequenz.client.weather._types import ForecastFeature, Location

location = [Location(latitude=46.2276, longitude=15.2137, country_code="DE")]
features = [ForecastFeature.TEMPERATURE_2_METRE, ForecastFeature.V_WIND_COMPONENT_10_METRE]
start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)

location_forecast_iterator = client.hist_forecast_iterator(
    features=features, locations=locations, start=start, end=end
)

async for forecasts in location_forecast_iterator:
    print(forecasts)
```

### Get live weather forecast

```python
from datetime import datetime
from frequenz.client.weather._types import ForecastFeature, Location

location = [Location(latitude=46.2276, longitude=15.2137, country_code="DE")]
features = [ForecastFeature.TEMPERATURE_2_METRE, ForecastFeature.V_WIND_COMPONENT_10_METRE]

rx = await client.stream_live_forecast(
    locations=[location],
    features=feature_names,
)

while True:
    forecast = await rx.__anext__()
    print(forecasts)
```

## Command Line Interface

The package also provides a command line interface to get weather forecast data.
Use `-h` to see the available options.

### Get historical weather forecast

```bash
weather-cli \
    --url <service-address> \
    --location <latitude,longitude> \       # e.g. "40, 15"
    --feature <feature-name> \              # e.g. TEMPERATURE_2_METRE
    --start <start-datetime> \              # e.g. 2024-03-14
    --end <end-datetime>                    # e.g. 2024-03-15
```

### Get live weather forecast

```bash
weather-cli \
    --url <service-address> \
    --location <latitude,longitude> \       # e.g. "40, 15"
    --feature <feature-name> \              # e.g. TEMPERATURE_2_METRE
```

