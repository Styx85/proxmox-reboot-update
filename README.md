# Proxmox Reboot Update

Home Assistant helper integration that exposes a pending Proxmox VE host reboot as a normal `update` entity.

## What it does

- Receives reboot status directly through its own Home Assistant webhook.
- Shows a pending host reboot in Home Assistant's normal Updates UI.
- Uses the selected Proxmox reboot button as the update action.
- Links the update entity to the selected Proxmox device.
- No `input_boolean` and no Home Assistant webhook automation are required.

## Setup

Install through HACS, restart Home Assistant, then add **Proxmox Reboot Update** under **Settings → Devices & services**.

Select the real Proxmox reboot button. The setup flow displays a generated webhook URL. You can retrieve it later with **Reconfigure**.

## Proxmox status script

```bash
#!/bin/bash

HA_WEBHOOK_URL="http://homeassistant.example:8123/api/webhook/GENERATED_ID"

if [ -f /var/run/reboot-required ]; then
    REQUIRED=true
else
    REQUIRED=false
fi

curl \
    --fail \
    --silent \
    --show-error \
    --max-time 10 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{\"required\":${REQUIRED}}" \
    "${HA_WEBHOOK_URL}"
```

Run the script periodically, for example with a systemd timer.

## Upgrading from 1.0.x

Version 1.1 migrates existing configuration automatically. The configured Proxmox reboot button is retained, the old `input_boolean` source is removed, and a webhook ID is generated.

After upgrading, use **Reconfigure** to retrieve the new webhook URL and put it into the Proxmox status script. Once the new webhook works, the old Home Assistant webhook automation and `input_boolean` can be removed.

## License

MIT
