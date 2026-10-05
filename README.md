# NiimBridge

A Home Assistant (HACS) integration that bridges [HomeBox](https://homebox.software/) label printing to a Niimbot printer through the [hass-niimbot](https://github.com/eigger/hass-niimbot) integration.

HomeBox renders a label, NiimBridge receives it, sizes it for your label stock, and calls `niimbot.print`. BLE is handled entirely by hass-niimbot.

> **Status: 0.1.0, early.** The renderer and the webhook handler are tested, but it hasn't been verified against real printer hardware yet. In particular it sends the label to `niimbot.print` as a `data:` URI in a `dlimg` element; if your hass-niimbot version rejects that, please open an issue.

## Requirements

- Home Assistant 2024.6 or newer
- [hass-niimbot](https://github.com/eigger/hass-niimbot) installed with your printer added
- HomeBox with a configurable label print command

## Install

1. HACS → three-dot menu → Custom repositories → add `https://github.com/tmeuze/NiimBridge` as **Integration**.
2. Download NiimBridge and restart Home Assistant.
3. Settings → Devices & services → Add integration → **NiimBridge**.
4. Pick your Niimbot printer and label settings. The last step shows your webhook URL and the exact HomeBox setting to use.

## Inputs

**Webhook (primary).** In HomeBox set:

```
HBOX_LABEL_MAKER_PRINT_COMMAND=curl -fsS -F file=@{{.FileName}} http://<ha>/api/webhook/<id>
```

The label PNG HomeBox generates is scaled and centred to your label size and printed. The webhook also accepts a raw `image/png` body, or JSON for the standard layout:

```json
{"name": "Anker USB-C Charger", "asset_id": "000-042", "location": "Office", "url": "https://homebox.example/item/abc", "copies": 1}
```

**MQTT (optional).** Set a PNG topic and/or a JSON topic in the options. PNG topics take the same image HomeBox would send; JSON topics take the same JSON as above.

**Service.** `niimbridge.print_label` prints the standard layout from an automation, with `preview_only` to render without printing.

## Label settings

| Setting | Notes |
|---|---|
| Label size | Presets are landscape pixels at 203 DPI (30×15, 40×12, 40×30, 50×15, 50×30, 50×80 mm), or custom pixels |
| Rotation | Applied by niimbot when printing. D110-style tape printers typically need 90 |
| Density, label type, copies | Passed through to `niimbot.print` |
| Font, font size | Optional font file (looked up in `/config/www/fonts`); size 0 auto-fits |

The standard layout is a QR code on the left (URL, else asset ID, else name) with the item name, asset ID and location on the right. The **Label preview** image entity shows the last rendered label.

## License

MIT
