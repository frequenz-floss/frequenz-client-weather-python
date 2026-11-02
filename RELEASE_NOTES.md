# Frequenz Weather API Client Release Notes

## Summary

This release requires signed Weather API requests. The client now requires an
API auth key and signing secret, and `weather-cli` accepts them via
`--auth-key` / `--sign-secret` or `WEATHER_API_AUTH_KEY` /
`WEATHER_API_SIGN_SECRET`.

This release relaxes the API common dependency so it can work up to v1.0.0, as
all v0.x versions should be compatible from v0.8.0 on.

Runtime dependency lower bounds were updated to the current gRPC client stack,
including `frequenz-client-base`, `frequenz-api-common`, `grpcio`, and
`protobuf`.
