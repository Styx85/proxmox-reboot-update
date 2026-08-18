# Proxmox Reboot Update

A small Home Assistant custom integration that exposes a pending Proxmox VE host reboot as an `update.*` entity.

The integration is intended for setups where Proxmox installs package updates automatically (for example with Debian `unattended-upgrades`) and Home Assistant should show a pending reboot in the same Updates section used for Home Assistant Core, add-ons, firmware, and other update entities.

## What it does

- Reads an existing Home Assistant `input_boolean` that represents whether the Proxmox host requires a reboot.
- Exposes that state as `update.proxmox_neustart_erforderlich`.
- Shows **Update installiert → Neustart erforderlich** when a reboot is pending.
- Adds an action to the update entity.
- When the action is pressed, the integration presses the configured Proxmox reboot `button.*` entity.
- Includes a warning that VMs, containers, the host, and hosted services may be unavailable for several minutes.

This integration does **not** detect the reboot requirement on the Proxmox host by itself. You provide the status through an `input_boolean`.

## Requirements

You need:

1. Home Assistant with the Proxmox VE integration configured.
2. A working Proxmox reboot button entity, for example:
   `button.proxmox_neu_starten`
3. An `input_boolean` that is `on` when `/var/run/reboot-required` exists on the Proxmox host.

## Example: report reboot status from Proxmox

One simple approach is a local Home Assistant webhook.

Example script on the Proxmox host:

```bash
#!/bin/bash

HA_URL="http://homeassistant.example:8123"
WEBHOOK_ID="replace-with-your-webhook-id"

if [ -f /var/run/reboot-required ]; then
    REQUIRED=true
else
    REQUIRED=false
fi

curl     --fail     --silent     --show-error     --max-time 10     -X POST     -H "Content-Type: application/json"     -d "{\"required\":${REQUIRED}}"     "${HA_URL}/api/webhook/${WEBHOOK_ID}"
```

The corresponding Home Assistant webhook automation should turn your selected `input_boolean` on or off.

For reliability, run the reporting script periodically with a systemd timer and after boot.

## Installation with HACS

Until this repository is included in the default HACS catalog:

1. Open HACS.
2. Open the menu and choose **Custom repositories**.
3. Add this GitHub repository.
4. Select category **Integration**.
5. Install **Proxmox Reboot Update**.
6. Restart Home Assistant.

Then go to:

**Settings → Devices & services → Add integration → Proxmox Reboot Update**

Select:

- the `input_boolean` that represents the reboot requirement;
- the real Proxmox reboot `button.*` entity.

## Manual installation

Copy:

```text
custom_components/proxmox_reboot_update/
```

to:

```text
/config/custom_components/proxmox_reboot_update/
```

and restart Home Assistant.

## Safety

Pressing the update action triggers the configured reboot button. Depending on the Proxmox configuration, running VMs and containers may be stopped or restarted as part of the host reboot.

Test your Proxmox shutdown/startup configuration before relying on this integration.

## License

MIT
