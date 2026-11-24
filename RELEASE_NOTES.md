# Frequenz Weather API Client Release Notes

## Summary

This release adds support for `frequenz-channels` v2.0.0, while still supporting v1 (`frequenz-channels >= 1.6.1, < 3`). It also requires timezone-aware timestamps where naive ones gave ambiguous results.

## Upgrading

* `Forecasts.to_ndarray_vlf()` (`validity_times`) and `Forecasts.upsample_vlf()` (`validity_times` and `target_times`) now raise a `ValueError` for timezone-naive datetimes. Naive datetimes were ambiguous: `upsample_vlf()` treated them as local time. Pass timezone-aware datetimes, for example in UTC.
