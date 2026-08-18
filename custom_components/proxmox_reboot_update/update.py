"""Update entity representing a pending Proxmox reboot."""

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device import async_entity_id_to_device
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ProxmoxRebootConfigEntry
from .const import CONF_REBOOT_BUTTON, SIGNAL_REBOOT_STATUS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ProxmoxRebootConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Proxmox reboot update entity."""
    async_add_entities([ProxmoxRebootUpdate(hass, entry)])


class ProxmoxRebootUpdate(UpdateEntity):
    """Expose a pending Proxmox reboot as a Home Assistant update."""

    _attr_translation_key = "reboot_required"
    _attr_has_entity_name = True
    _attr_unique_id = "proxmox_reboot_required_update"
    _attr_title = "Proxmox VE"
    _attr_icon = "mdi:restart-alert"
    _attr_auto_update = False
    _attr_should_poll = False
    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ProxmoxRebootConfigEntry,
    ) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._entry = entry
        self._reboot_button = entry.options.get(
            CONF_REBOOT_BUTTON,
            entry.data[CONF_REBOOT_BUTTON],
        )

        self.device_entry = async_entity_id_to_device(
            hass,
            self._reboot_button,
        )

    async def async_added_to_hass(self) -> None:
        """Register the runtime-state listener."""
        await super().async_added_to_hass()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{SIGNAL_REBOOT_STATUS}_{self._entry.entry_id}",
                self._handle_status_update,
            )
        )

    @callback
    def _handle_status_update(self) -> None:
        """Handle a reboot status update."""
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return whether the Proxmox host has reported its status."""
        return self._entry.runtime_data.status_received

    @property
    def installed_version(self) -> str:
        """Return a language-neutral state token."""
        return "current"

    @property
    def latest_version(self) -> str:
        """Return a language-neutral state token."""
        if self._entry.runtime_data.reboot_required:
            return "reboot_required"
        return "current"

    @property
    def release_summary(self) -> str | None:
        """Return a warning token while a reboot is pending."""
        if self._entry.runtime_data.reboot_required:
            return "reboot_warning"
        return None

    def version_is_newer(
        self,
        latest_version: str,
        installed_version: str,
    ) -> bool:
        """Tell Home Assistant whether an update should be shown."""
        return self._entry.runtime_data.reboot_required

    async def async_install(
        self,
        version: str | None,
        backup: bool,
        **kwargs,
    ) -> None:
        """Use the configured Proxmox reboot button as the update action."""
        if not self._entry.runtime_data.reboot_required:
            return

        await self.hass.services.async_call(
            "button",
            "press",
            {"entity_id": self._reboot_button},
            blocking=True,
        )
