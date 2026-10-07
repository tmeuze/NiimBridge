# Changelog

## [0.1.0] - 2026-10-06

### Added

- Webhook input that accepts HomeBox's label PNG, a raw PNG body, or JSON.
- Optional MQTT inputs (PNG and JSON topics).
- Standard label layout (QR code, name, asset ID, location) with label-size presets, rotation, density, label type, copies, font, font size and QR size options.
- Label preview image entity.
- `niimbridge.print_label` service.
- Prints through the hass-niimbot `niimbot.print` service; replies to the webhook immediately and prints in the background.
