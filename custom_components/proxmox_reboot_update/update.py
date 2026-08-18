"""Update entity representing a pending Proxmox reboot."""

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_REBOOT_BUTTON, CONF_SOURCE_ENTITY


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Proxmox reboot update entity."""
    async_add_entities(
        [
            ProxmoxRebootUpdate(
                hass=hass,
                source_entity=entry.data[CONF_SOURCE_ENTITY],
                reboot_button=entry.data[CONF_REBOOT_BUTTON],
            )
        ]
    )


class ProxmoxRebootUpdate(UpdateEntity):
    """Expose a pending Proxmox reboot as a Home Assistant update."""

    _attr_name = "Proxmox Neustart erforderlich"
    _attr_unique_id = "proxmox_reboot_required_update"
    _attr_title = "Proxmox VE"
    _attr_icon = "mdi:restart-alert"
    _attr_auto_update = False
    _attr_should_poll = False
    _attr_supported_features = UpdateEntityFeature.INSTALL

    def __init__(
        self,
        hass: HomeAssistant,
        source_entity: str,
        reboot_button: str,
    ) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._source_entity = source_entity
        self._reboot_button = reboot_button
        self._required = False
        self._source_available = False

    async def async_added_to_hass(self) -> None:
        """Register the source-state listener."""
        await super().async_added_to_hass()
        self._update_from_source()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._source_entity],
                self._handle_source_change,
            )
        )

    @callback
    def _handle_source_change(self, event) -> None:
        """Handle reboot status changes."""
        self._update_from_source()
        self.async_write_ha_state()

    @callback
    def _update_from_source(self) -> None:
        """Read the reboot status from the configured helper."""
        state = self.hass.states.get(self._source_entity)

        self._source_available = (
            state is not None
            and state.state not in ("unknown", "unavailable")
        )

        self._required = (
            self._source_available
            and state.state == "on"
        )

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return self._source_available

    @property
    def installed_version(self) -> str:
        """Return the current pseudo-version."""
        return "Update installiert" if self._required else "Aktuell"

    @property
    def latest_version(self) -> str:
        """Return the target pseudo-version."""
        return "Neustart erforderlich" if self._required else "Aktuell"

    @property
    def release_summary(self) -> str:
        """Describe the pending action."""
        if self._required:
            return (
                "Proxmox wurde automatisch aktualisiert. "
                "Ein Neustart des Hosts ist erforderlich. "
                "Beim Neustart werden laufende virtuelle Maschinen und "
                "Container geordnet beendet. Der Host und die darauf "
                "laufenden Dienste können für mehrere Minuten nicht "
                "erreichbar sein."
            )

        return "Kein Neustart erforderlich."

    def version_is_newer(
        self,
        latest_version: str,
        installed_version: str,
    ) -> bool:
        """Tell Home Assistant whether an update should be shown."""
        return self._required

    async def async_install(
        self,
        version: str | None,
        backup: bool,
        **kwargs,
    ) -> None:
        """Use the configured Proxmox reboot button as the update action."""
        if not self._required:
            return

        await self.hass.services.async_call(
            "button",
            "press",
            {"entity_id": self._reboot_button},
            blocking=True,
        )
